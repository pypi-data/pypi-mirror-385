# Copyright 2025 The Levanter Authors
# SPDX-License-Identifier: Apache-2.0

import abc
import contextlib
import dataclasses
import functools
import json
import logging
import os
import shutil
import tempfile
import urllib.parse
import warnings
from dataclasses import dataclass
from functools import cached_property
from typing import Generic, Optional, Tuple, Type, TypeVar, Union, cast, Callable

import draccus
import equinox as eqx
import fsspec
import huggingface_hub
import humanfriendly
import jax
import jax.numpy as jnp
from jax._src.mesh import get_concrete_mesh
import mergedeep
import numpy as np
import transformers.utils.hub
from fsspec import AbstractFileSystem
from fsspec.asyn import get_loop, sync as fsspec_sync
from haliax._src.state_dict import flatten_modules_for_export, to_state_dict
from haliax.jax_utils import is_jax_array_like
from haliax.state_dict import StateDict
from huggingface_hub import HfApi, hf_hub_download, repo_exists, snapshot_download
from huggingface_hub.file_download import repo_folder_name
from huggingface_hub.utils import EntryNotFoundError, GatedRepoError, HFValidationError, RepositoryNotFoundError
from jax import ShapeDtypeStruct
from jax._src.partition_spec import PartitionSpec
from jax.random import PRNGKey
from jaxtyping import Array, PRNGKeyArray
from tqdm_loggable.auto import tqdm

import haliax
from haliax import Axis
from haliax.partitioning import ResourceMapping
from haliax.state_dict import from_torch_compatible_state_dict, save_state_dict

from levanter.callbacks import StepInfo
from levanter.compat.fsspec_safetensor import read_safetensors_fsspec
from levanter.models.asr_model import ASRMixin
from levanter.models.lm_model import LmConfig, LmHeadModel
from levanter.utils.cloud_utils import temp_dir_before_upload
from levanter.utils.hf_utils import HfTokenizer
from levanter.utils.jax_utils import best_effort_sharding, use_cpu_device, sync_global_devices
from levanter.utils.json_utils import ConfigJSONEncoder
from levanter.utils.logging import silence_transformer_nag
from levanter.utils.py_utils import dataclass_with_default_init


silence_transformer_nag()
from transformers import (  # noqa: E402
    AutoConfig,
    AutoModel,
    AutoModelForCausalLM,
    AutoProcessor,
    AutoTokenizer,
    FeatureExtractionMixin,
)
from transformers import PretrainedConfig as HfConfig  # noqa: E402
from transformers import (  # noqa: E402
    PreTrainedTokenizer,
    PreTrainedTokenizerBase,
    PreTrainedTokenizerFast,
    ProcessorMixin,
)
from transformers.dynamic_module_utils import get_class_from_dynamic_module  # noqa: E402
from transformers.models.auto.auto_factory import _get_model_class  # noqa: E402


DEFAULT_MAX_SHARD_SIZE = int(10e9)

logger = logging.getLogger(__name__)


PYTORCH_MODEL = "pytorch_model.bin"
SAFE_TENSORS_MODEL = "model.safetensors"
PYTORCH_WEIGHTS_INDEX_NAME = "pytorch_model.bin.index.json"
SAFE_TENSORS_INDEX_NAME = "model.safetensors.index.json"


@dataclass(frozen=True)
class RepoRef:
    """Represents a reference to a model (or similar) in a remote repository or local file system, and
    optionally a revision. This lets you load particular revisions or branches of a model.

    The string syntax is <model_name_or_path>@<revision>.

    """

    model_name_or_path: str
    revision: Optional[str] = None

    @staticmethod
    def from_string(s: str) -> "RepoRef":
        if "@" not in s:
            return RepoRef(s)
        model_name_or_path, revision = s.split("@")
        return RepoRef(model_name_or_path, revision)

    def __str__(self) -> str:
        if self.revision is None:
            return self.model_name_or_path
        return f"{self.model_name_or_path}@{self.revision}"

    def __repr__(self) -> str:
        return f"RemoteRev({self.model_name_or_path!r}, {self.revision!r})"


# register draccus parsing
draccus.decode.register(RepoRef, RepoRef.from_string)
draccus.encode.register(RepoRef, str)


class HFCompatConfig(LmConfig["LmWithHfSerializationMixin"]):
    @abc.abstractmethod
    def to_hf_config(self, vocab_size: int, config_overrides: Optional[dict] = None) -> HfConfig:
        pass

    @classmethod
    @abc.abstractmethod
    def from_hf_config(cls, hf_config: HfConfig):
        pass

    @abc.abstractmethod
    def hf_checkpoint_converter(cls) -> "HFCheckpointConverter":
        """The default HFCheckpointConverter to use for this config class. We recommend that you
        define this as a @cached_property on your config class."""
        pass


MConfig = TypeVar("MConfig", bound=HFCompatConfig)


class ModelWithHfSerializationMixin(Generic[MConfig]):
    def get_hf_config(self):
        return self.config.to_hf_config(self.Vocab.size)

    @property
    @abc.abstractmethod
    def config(self) -> MConfig:
        pass

    @property
    @abc.abstractmethod
    def Vocab(self) -> Axis:
        pass

    @classmethod
    @abc.abstractmethod
    def init(cls, Vocab: Axis, config: MConfig, *, key: PRNGKeyArray) -> "ModelWithHfSerializationMixin":
        pass


class ASRWithHfSerializationMixin(ASRMixin, ModelWithHfSerializationMixin[MConfig]):
    pass


class LmWithHfSerializationMixin(LmHeadModel, ModelWithHfSerializationMixin[MConfig]):
    @classmethod
    @abc.abstractmethod
    def init(cls, Vocab: Axis, config: MConfig, *, key: PRNGKeyArray) -> "LmWithHfSerializationMixin":
        pass


def _coerce_to_rr(s: Union[str, RepoRef]) -> RepoRef:
    if isinstance(s, RepoRef):
        return s
    else:
        return RepoRef.from_string(s)


LevConfig = TypeVar("LevConfig", bound=HFCompatConfig)

# just for generating unique ids

KEYS_TO_COPY_FROM_BASE_CONFIG = {
    "architectures",
    "auto_map",
}


def _load_torch(path, dtype, fs: AbstractFileSystem | None = None):
    import torch  # noqa: F401

    device = torch.device("cpu")
    with contextlib.ExitStack() as stack:
        load_path = path
        if fs is not None:
            protocol = getattr(fs, "protocol", None)
            if isinstance(protocol, (list, tuple, set)):
                protocols = protocol
            else:
                protocols = (protocol,)
            if not any(p in ("file", "", None) for p in protocols):
                tmp = stack.enter_context(tempfile.NamedTemporaryFile())
                fs.get(path, tmp.name)
                load_path = tmp.name
                if not getattr(_load_torch, "_warned_download", False):
                    warnings.warn("Torch checkpoint loading requires downloading shards locally")
                    _load_torch._warned_download = True  # type: ignore[attr-defined]
            else:
                try:
                    load_path = fs._strip_protocol(path)  # type: ignore[attr-defined]
                except AttributeError:
                    load_path = path

        state_dict = torch.load(load_path, map_location=device)
    d = {}

    for k, v in tqdm(state_dict.items(), total=len(state_dict), desc="Loading weights"):
        v = _convert_to_jnp(v, dtype)
        if v is not None:
            v = _shard_best_effort(v, dtype)
        d[k] = v

    return d


def _load_safe_tensors(path, dtype, fs: AbstractFileSystem | None = None):
    """Stream a safetensors shard from remote storage and return JAX arrays."""
    if fs is None:
        fs, stripped = fsspec.core.url_to_fs(path, asynchronous=True)
        path = stripped
    else:
        try:
            path = fs._strip_protocol(path)  # type: ignore[attr-defined]
        except AttributeError:
            pass

    mesh = get_concrete_mesh()

    loop = get_loop()
    bes = functools.partial(best_effort_sharding, mesh=mesh)

    return fsspec_sync(loop, read_safetensors_fsspec, path, dtype_override=dtype, sharding_fn=bes, fs=fs)


# NB: for large models this will be jitted several times (once for each unique subset of keys at least)
# but it means we get to benefit from dead code elimination and other goodness
@eqx.filter_jit
def _to_state_dict_with_dtype(
    model: ModelWithHfSerializationMixin, dtype, subset: tuple[str, ...] | None
) -> StateDict:
    """
    Convert a model to a torch-compatible state dict, optionally converting floating-point arrays to a given dtype
    and optionally subsetting to a given set of keys.
    """
    # We don't want to directly use to_torch_compatible_state_dict because it will convert everything to numpy.
    # we don't want to do that here because we want to keep things as jax arrays so we can eval_shape and control
    # sharding

    # state_dict = to_torch_compatible_state_dict(model)
    # to_torch_compatible_state_dict is mostly these three steps (except it also converts to numpy)
    model = eqx.filter(model, is_jax_array_like)
    model = flatten_modules_for_export(model)
    state_dict = to_state_dict(model)

    if subset is not None:
        out = {}
        for k in subset:
            out[k] = state_dict[k]
        state_dict = out

    if dtype is not None:
        logger.info(f"Converting floating-point arrays in state_dict to {dtype}")
        for k, v in state_dict.items():
            if jnp.issubdtype(v.dtype, jnp.floating):
                state_dict[k] = v.astype(dtype)
            else:
                logger.debug(f"Skipping dtype conversion for non-floating point array {k} with dtype {v.dtype}")

    # deshard. We could be smarter here and use a process mesh or host offloading, but this is simpler for now
    state_dict = jax.lax.with_sharding_constraint(state_dict, PartitionSpec())

    return state_dict


@dataclass_with_default_init(frozen=True)
class HFCheckpointConverter(Generic[LevConfig]):
    """
    A class to convert between Levanter and HF models. This class establishes a bidirectional mapping
    between Levanter and HF models, and provides methods to convert between configs and loading/saving HF checkpoints.
    It also handles the bundled tokenizer and code, as applicable.

    This mapping supports:
    * translating between Levanter and HF configs
    * loading a Levanter model from an HF checkpoint
    * saving a HF checkpoint from a Levanter model

    HF checkpoints can be saved with params and config, and optionally with the tokenizer and code.
    """

    LevConfigClass: Type[LevConfig]
    reference_checkpoint: Optional[RepoRef]
    "A reference HF Hub checkpoint to extract non-parameter files (like model code an config from)"

    HfConfigClass: Type
    "The HFConfig class to use. If None is provided, will be inferred from the reference_checkpoint"

    tokenizer: PreTrainedTokenizerFast | PreTrainedTokenizer
    "The tokenizer to use. If None, will be inferred from the reference_checkpoint"

    feature_extractor: Optional[FeatureExtractionMixin] = None
    "The non-text preprocessor to use for multi-modality."

    config_overrides: Optional[dict] = None
    "A dictionary of config overrides to apply to the HFConfig when saving. typically used for auto_map"

    trust_remote_code: bool = False
    "If True, will trust the remote code and not download it locally."

    ignore_prefix: Optional[str] = None
    """A prefix to optionally ignore when loading checkpoints. For "gpt2" this is 'transformer' to deal with the
    fact that some models are saved as XXXPreTrainedModel and others are saved as XXXLMHeadModel"""

    def __init__(
        self,
        LevConfigClass: Type[LevConfig],
        reference_checkpoint: Optional[Union[RepoRef, str]] = None,
        HfConfigClass: Optional[Union[str, Type]] = None,
        tokenizer: Optional[Union[str, PreTrainedTokenizer, PreTrainedTokenizerFast]] = None,
        feature_extractor: Optional[FeatureExtractionMixin] = None,
        config_overrides: Optional[dict] = None,
        trust_remote_code: bool = False,
        ignore_prefix: Optional[str] = None,
    ):
        # stupid python won't let you have a custom constructor with a frozen dataclass

        ref = _coerce_to_rr(reference_checkpoint) if reference_checkpoint is not None else None
        HfConfigClass = HFCheckpointConverter._infer_config_class(HfConfigClass, ref, trust_remote_code)
        tokenizer = HFCheckpointConverter._infer_tokenizer(tokenizer, ref, trust_remote_code)

        self.__default_init__(  # type: ignore
            LevConfigClass=LevConfigClass,
            reference_checkpoint=ref,
            HfConfigClass=HfConfigClass,
            tokenizer=tokenizer,
            feature_extractor=feature_extractor,
            config_overrides=config_overrides,
            trust_remote_code=trust_remote_code,
            ignore_prefix=ignore_prefix,
        )

    @staticmethod
    def from_hf(model_name_or_path: Union[RepoRef, str], trust_remote_code: bool = False) -> "HFCheckpointConverter":
        ref = _coerce_to_rr(model_name_or_path)
        config_class = HFCheckpointConverter._infer_config_class(None, ref, trust_remote_code)
        tokenizer = HFCheckpointConverter._infer_tokenizer(None, ref, trust_remote_code)

        # TODO: this is very hacky, we should add another registry or something
        # attempt to find the Levanter config class by checking the registry
        # TODO: hacky hacky
        for k, v in LmConfig.get_known_choices().items():
            if issubclass(v, HFCompatConfig):
                if v().hf_checkpoint_converter().HfConfigClass.__name__ == config_class.__name__:
                    LevConfigClass = v
                    break
        else:
            raise ValueError(f"No Levanter config found for {config_class}")

        return HFCheckpointConverter(
            LevConfigClass=LevConfigClass,
            reference_checkpoint=ref,
            HfConfigClass=config_class,
            tokenizer=tokenizer,
            trust_remote_code=trust_remote_code,
        )

    def replaced(
        self,
        reference_checkpoint: Optional[Union[RepoRef, str]] = None,
        tokenizer: Optional[Union[str, PreTrainedTokenizerBase]] = None,
        feature_extractor: Optional[FeatureExtractionMixin] = None,
        trust_remote_code: Optional[bool] = None,
    ) -> "HFCheckpointConverter":
        replacements: dict = {}
        if reference_checkpoint is not None:
            replacements["reference_checkpoint"] = reference_checkpoint
        if tokenizer is not None:
            replacements["tokenizer"] = tokenizer
        if feature_extractor is not None:
            replacements["feature_extractor"] = feature_extractor
        if trust_remote_code is not None:
            replacements["trust_remote_code"] = trust_remote_code

        return dataclasses.replace(self, **replacements)  # type: ignore

    def with_config_overrides(self, config_overrides: dict, merge: bool = True) -> "HFCheckpointConverter":
        if self.config_overrides is not None and merge:
            config_overrides = mergedeep.merge({}, self.config_overrides, config_overrides)
        return dataclasses.replace(self, config_overrides=config_overrides)  # type: ignore

    @staticmethod
    def _infer_config_class(hf_config_class, ref, trust_remote_code):
        if hf_config_class is None:
            if ref is None:
                raise ValueError("Must provide either config class or reference_checkpoint")
            path, rev = ref.model_name_or_path, ref.revision
            with _patch_hf_hub_download():
                config = AutoConfig.from_pretrained(path, revision=rev, trust_remote_code=trust_remote_code)
            clss = type(config)
        elif isinstance(hf_config_class, str):
            if ref is None:
                raise ValueError("Must provide either config class or reference_checkpoint")
            path, rev = ref.model_name_or_path, ref.revision
            HFConfig = get_class_from_dynamic_module(
                hf_config_class,
                path,
                revision=rev,
                local_files_only=not trust_remote_code,
            )
            clss = HFConfig
        else:
            clss = hf_config_class
        return clss

    @staticmethod
    def _infer_tokenizer(
        tokenizer, ref, trust_remote_code: bool = False
    ) -> Union[PreTrainedTokenizer, PreTrainedTokenizerFast]:
        if tokenizer is None:
            if ref is None:
                raise ValueError("Must provide either tokenizer or reference_checkpoint")
            tokenizer = ref

        if isinstance(tokenizer, (str, RepoRef)):
            ref = _coerce_to_rr(tokenizer)
            path, rev = ref.model_name_or_path, ref.revision
            tokenizer = load_tokenizer(
                path,
                revision=rev,
                trust_remote_code=trust_remote_code,
            )
        else:
            pass

        assert isinstance(tokenizer, (PreTrainedTokenizer, PreTrainedTokenizerFast))

        return tokenizer

    @cached_property
    def default_hf_config(self) -> HfConfig:
        return self.hf_config_from_hf_checkpoint(None)

    @cached_property
    def default_config(self) -> LevConfig:
        return self.config_from_hf_config(self.default_hf_config)

    def HFAutoModelClass(self, auto_class: Type[AutoModel] = AutoModelForCausalLM) -> Type[AutoModel]:
        # first, see if it's a built-in model
        try:
            return auto_class._model_mapping[self.HfConfigClass]
        except KeyError:
            pass

        config = self.default_hf_config
        cls_name = auto_class.__name__
        if hasattr(config, "auto_map") and cls_name in config.auto_map:
            class_ref = config.auto_map[cls_name]
            path, rev = self._get_ref(None)
            model_class = get_class_from_dynamic_module(
                class_ref,
                path,
                revision=rev,
                local_files_only=not self.trust_remote_code,
            )
            return model_class  # type: ignore
        elif type(config) in auto_class._model_mapping.keys():
            model_class = _get_model_class(config, auto_class._model_mapping)
            return model_class

        raise ValueError(f"Could not find model class {auto_class} for {config}")

    @cached_property
    def Vocab(self) -> Axis:
        return Axis("vocab", len(self.tokenizer))

    def config_from_hf_config(self, hf_config, overrides: Optional[dict] = None) -> LevConfig:
        config = self.LevConfigClass.from_hf_config(hf_config)
        if overrides is not None:
            config = dataclasses.replace(config, **overrides)  # type: ignore
        return config

    def hf_config_from_config(self, config: LevConfig, vocab_size: Optional[int] = None) -> HfConfig:
        if vocab_size is None:
            vocab_size = self.Vocab.size
        return config.to_hf_config(vocab_size=vocab_size)

    def config_from_hf_checkpoint(self, ref: Optional[Union[str, RepoRef]] = None) -> LevConfig:
        config = self.hf_config_from_hf_checkpoint(ref)
        return self.config_from_hf_config(config)

    def hf_config_from_hf_checkpoint(self, ref: Optional[Union[str, RepoRef]] = None) -> HfConfig:
        path, rev = self._get_ref(ref)

        with _patch_hf_hub_download():
            config = AutoConfig.from_pretrained(path, revision=rev, trust_remote_code=self.trust_remote_code)
        return config

    def _get_ref(self, ref) -> Tuple[str, Optional[str]]:
        if ref is None:
            if self.reference_checkpoint is None:
                raise ValueError("Must provide a reference checkpoint to load HFConfig from")
            ref = self.reference_checkpoint
        ref = _coerce_to_rr(ref)
        return ref.model_name_or_path, ref.revision

    def load_state_dict(self, ref: Optional[Union[str, RepoRef]] = None, dtype: Optional[jnp.dtype] = None) -> dict:
        """Load a state dict from either HF Hub or a GCS path"""
        if ref is None:
            ref = self.reference_checkpoint
        if ref is None:
            raise ValueError("Must provide a checkpoint to load from")

        id, rev = self._get_ref(ref)

        if "://" in id:
            if rev is not None:
                raise ValueError("Revisions not supported for explicit URLs")
            return self._load_from_remote(id, dtype)

        for index_file in [SAFE_TENSORS_INDEX_NAME, PYTORCH_WEIGHTS_INDEX_NAME]:
            try:
                return self._load_shards(id, index_file, rev, dtype)
            except EntryNotFoundError:
                pass
            except HFValidationError:
                pass

        with _patch_hf_hub_download() as hf_hub_download:
            # TODO: load models from gcs etc.
            if os.path.exists(os.path.join(id, SAFE_TENSORS_MODEL)):
                state_dict = _load_safe_tensors(os.path.join(id, SAFE_TENSORS_MODEL), dtype)
            elif os.path.exists(os.path.join(id, PYTORCH_MODEL)):
                state_dict = _load_torch(os.path.join(id, PYTORCH_MODEL), dtype)
            else:
                try:
                    model_path = hf_hub_download(id, SAFE_TENSORS_MODEL, revision=rev)
                    state_dict = _load_safe_tensors(model_path, dtype)
                except (EntryNotFoundError, HFValidationError):
                    model_path = hf_hub_download(id, PYTORCH_MODEL, revision=rev)
                    state_dict = _load_torch(model_path, dtype)

            return state_dict

    def _load_shards(self, id: str, index_file: str, rev: Optional[str], dtype) -> dict:
        """Load model from sharded files based on the provided index."""
        with _patch_hf_hub_download() as hf_hub_download:
            index_path = os.path.join(id, index_file)
            if not os.path.exists(index_path):
                # Download the index file if not found locally
                index_path = hf_hub_download(id, index_file, revision=rev)

            with open(index_path, "r", encoding="utf-8") as f:
                index = json.load(f)

            # Keep shard order deterministic across hosts.
            shard_files = list(dict.fromkeys(index["weight_map"].values()))
            final_state_dict = {}

            # where we load into memory then update some dict
            if "safetensors" in index_file:
                loader = _load_safe_tensors
            else:
                loader = _load_torch

            for shard_file in shard_files:
                shard_path = os.path.join(id, shard_file)
                if not os.path.exists(shard_path):
                    # Download the shard if not found locally
                    shard_path = hf_hub_download(id, shard_file, revision=rev)

                shard_state_dict = loader(shard_path, dtype)
                final_state_dict.update(shard_state_dict)

        return final_state_dict

    def _load_from_remote(self, url: str, dtype: Optional[jnp.dtype] = None) -> dict:
        """Load a state dict from a remote URL understood by fsspec."""

        final_state_dict = {}

        fs: AbstractFileSystem
        fs, path = fsspec.core.url_to_fs(url)

        shard_files, loader = self._locate_shard_files(fs, path)

        if not shard_files:
            raise FileNotFoundError(f"No HF-ish checkpoint files found in {url}")

        for shard_file in shard_files:
            shard_path = os.path.join(path, shard_file)
            if not fs.exists(shard_path):
                raise FileNotFoundError(f"Shard file {shard_path} not found")

            if loader is _load_safe_tensors:
                shard_state_dict = _load_safe_tensors(shard_path, dtype, fs=fs)
            else:
                assert loader is not None
                shard_state_dict = _load_torch(shard_path, dtype, fs=fs)

            final_state_dict.update(shard_state_dict)

        return final_state_dict

    def _locate_shard_files(self, fs: AbstractFileSystem, path) -> tuple[list[str] | None, Callable]:
        """
        Locate shard files in a GCS path. Returns a list of shard files and a loader function.
        """

        shard_files = None
        loader = None
        # First try to load sharded checkpoint
        for index_file in [SAFE_TENSORS_INDEX_NAME, PYTORCH_WEIGHTS_INDEX_NAME]:
            index_path = os.path.join(path, index_file)
            if fs.exists(index_path):
                with fs.open(index_path, "r") as f:
                    index = json.load(f)

                shard_files = list(dict.fromkeys(index["weight_map"].values()))

                if "safetensors" in index_file:
                    loader = _load_safe_tensors
                else:
                    loader = _load_torch

                break

        # If no index file found, try loading single file checkpoint
        if not shard_files:
            for model_file in [SAFE_TENSORS_MODEL, PYTORCH_MODEL]:
                model_path = os.path.join(path, model_file)
                if fs.exists(model_path):
                    shard_files = [model_file]

                    if model_file == SAFE_TENSORS_MODEL:
                        loader = _load_safe_tensors
                    else:
                        loader = _load_torch

                    break

        return shard_files, loader  # type: ignore

    def load_pretrained(
        self,
        lm_model_cls: Type[ModelWithHfSerializationMixin],
        ref: Optional[Union[str, RepoRef]] = None,
        config: Optional[HFCompatConfig] = None,
        axis_mapping: Optional[ResourceMapping] = None,
        resize_vocab_to_match_tokenizer: bool = True,
        dtype: Optional[jnp.dtype] = None,
    ) -> ModelWithHfSerializationMixin:
        """
        Loads a levanter model from a huggingface checkpoint.

        Args:
            config: The config to use to load the model class
            ref: The reference to load from. If None, will use the reference_checkpoint
            axis_mapping: The axis mapping to use for sharding. If None, will use the context axis mapping
        """

        hf_config = self.hf_config_from_hf_checkpoint(ref)
        if config is None:
            config = self.config_from_hf_config(hf_config)
        lm_model_cls = config.model_type

        # Vocab: first we have to resize the vocab as loaded from the checkpoint
        tokenizer_Vocab = self.Vocab
        Vocab = tokenizer_Vocab.resize(hf_config.vocab_size)

        # TODO: in an ideal world, we would only load the part of the array we needed, but
        # AFAICT neither torch state dicts nor safetensors support this.
        state_dict = self.load_state_dict(ref, dtype)

        ignore_prefix: Optional[str] = None
        if self.ignore_prefix:
            for k in state_dict.keys():
                if k.startswith(f"{self.ignore_prefix}."):
                    ignore_prefix = self.ignore_prefix
                    break

        def load_from_state_dict(template, state_dict):
            lev_model = from_torch_compatible_state_dict(template, state_dict, prefix=ignore_prefix)

            # However, this might miss some buffers that don't get persisted in the state dict
            # (e.g. pytorch buffers with persistent=false), so we have to reinitialize them. We then init the model
            # again, this time keeping only the (missing) buffers, and then combine the two models.
            lev_model = _patch_missing_buffers_for_deser(
                lev_model, lm_model_cls, Vocab, config, PRNGKey(0), axis_mapping
            )

            if Vocab.size != tokenizer_Vocab.size:
                if resize_vocab_to_match_tokenizer:
                    logger.info(
                        f"Resizing model from {Vocab.size} to {tokenizer_Vocab.size} to match tokenizer vocab size"
                    )
                    lev_model = lev_model.resize_vocab(tokenizer_Vocab.size)
                else:
                    logger.warning(
                        f"Model vocab size ({Vocab.size}) does not match tokenizer vocab size ({tokenizer_Vocab.size})"
                    )

            lev_model = haliax.shard_with_axis_mapping(lev_model, axis_mapping)

            return lev_model

        load_from_state_dict = haliax.named_jit(
            load_from_state_dict, axis_resources=axis_mapping, out_axis_resources=axis_mapping, donate_args=(True,)
        )
        lev_model = eqx.filter_eval_shape(lm_model_cls.init, Vocab, config, key=PRNGKey(0))
        lev_model = load_from_state_dict(lev_model, state_dict)

        return lev_model

    def _resolve_save_reference_code(self, save_reference_code: Optional[bool]) -> bool:
        """Determine whether reference code should be bundled with the checkpoint."""
        #  the way we determine this is if the config class is in the HF package or not
        if save_reference_code is None:
            return not self.HfConfigClass.__module__.startswith("transformers.")

        return save_reference_code

    def _build_hf_config_dict(self, model: ModelWithHfSerializationMixin) -> dict:
        """Construct the Hugging Face config dictionary for the provided model."""
        config = model.config.to_hf_config(model.Vocab.size)
        dict_config = config.to_dict()

        try:
            for k in KEYS_TO_COPY_FROM_BASE_CONFIG:
                attr = getattr(self.default_hf_config, k, None)
                if attr is not None:
                    dict_config[k] = attr
        except Exception as e:  # noqa: BLE001
            if isinstance(e, GatedRepoError) or isinstance(e.__cause__, GatedRepoError):
                warnings.warn("Could not copy keys from base config because the repo is gated. Making assumptions.")
                dict_config["auto_map"] = {
                    "AutoModelForCausalLM": self.HFAutoModelClass(AutoModelForCausalLM).__qualname__,
                    "AutoConfig": self.HfConfigClass.__qualname__,
                }
                dict_config["architectures"] = [self.HFAutoModelClass(AutoModelForCausalLM).__name__]
            else:
                raise

        if self.tokenizer:
            tokenizer_dependent_config = {}
            suppress_tokens = []
            if self.tokenizer.pad_token_id is not None:
                tokenizer_dependent_config["pad_token_id"] = self.tokenizer.pad_token_id
                suppress_tokens.append(self.tokenizer.pad_token_id)
            if self.tokenizer.eos_token_id is not None:
                tokenizer_dependent_config["eos_token_id"] = self.tokenizer.eos_token_id
                suppress_tokens.append(self.tokenizer.eos_token_id)
            if self.tokenizer.bos_token_id is not None:
                tokenizer_dependent_config["bos_token_id"] = self.tokenizer.bos_token_id
                tokenizer_dependent_config["decoder_start_token_id"] = self.tokenizer.bos_token_id
                suppress_tokens.append(self.tokenizer.bos_token_id)
            if len(suppress_tokens) > 0:
                tokenizer_dependent_config["begin_suppress_tokens"] = list(set(suppress_tokens))
            dict_config = mergedeep.merge({}, dict_config, tokenizer_dependent_config)

        if self.config_overrides:
            dict_config = mergedeep.merge({}, dict_config, self.config_overrides)

        return dict_config

    def save_pretrained(
        self,
        model: ModelWithHfSerializationMixin,
        path,
        upload_to_hf: Union[bool, str, RepoRef] = False,
        save_reference_code: Optional[bool] = None,
        save_tokenizer: bool = True,
        max_shard_size: int = DEFAULT_MAX_SHARD_SIZE,
        save_feature_extractor: bool = False,
        dtype: Optional[jnp.dtype] = None,
        **hf_upload_kwargs,
    ):
        """
        Saves a Levanter model to a huggingface "pretrained model" checkpoint.

        If hf_repo is provided, this will upload the checkpoint to the huggingface hub, passing
        any additional kwargs to the huggingface_hub.upload_folder function. A new private model
        repository will be created in the huggingface hub if one does not exist already.

        :param path: the path to save the checkpoint to. path may be a GCS bucket path or other fsspec path,
        in which case the checkpoint will be uploaded to GCS after being written to a tmpdir
        :param model: the model to save
        :param hf_repo: if provided, the checkpoint will be uploaded to the huggingface hub. If True, will use
        the reference_checkpoint as the repo name
        :param hf_upload_kwargs: any additional kwargs to pass to huggingface_hub.upload_folder
        :param save_reference_code: if True, will save the reference code (from reference_checkpoint) to the checkpoint.
        This is useful when using custom architectures, as it will allow the model to be loaded without the custom
        architecture code being present (using trust_remote_code=True). "Code" here means anything not stored in LFS.
        If None, will save code for models that aren't in the HF repo.
        """
        logger.info(f"Saving HF-compatible checkpoint to {path}")

        save_reference_code_flag = self._resolve_save_reference_code(save_reference_code)
        dict_config = self._build_hf_config_dict(model)

        if not _is_url_like(path):
            os.makedirs(path, exist_ok=True)

        hf_repo_ref: Optional[RepoRef] = None
        if upload_to_hf is True:
            if self.reference_checkpoint is None:
                raise ValueError("No reference checkpoint provided, so no repo name to upload to")
            upload_to_hf = self.reference_checkpoint

        if not isinstance(upload_to_hf, bool):
            repo_ref = _coerce_to_rr(upload_to_hf)
            if not repo_exists(repo_ref.model_name_or_path, repo_type="model"):
                api = HfApi()
                api.create_repo(repo_id=repo_ref.model_name_or_path, repo_type="model", exist_ok=True, private=True)
            hf_repo_ref = repo_ref

        if hf_repo_ref is None:
            logger.info(f"Saving checkpoint to {path}")
        else:
            logger.info(f"Uploading checkpoint to {hf_repo_ref} from {path}")

        state_dict_shape = eqx.filter_eval_shape(_to_state_dict_with_dtype, model, dtype, None)
        model_size = sum(v.size * v.dtype.itemsize for v in state_dict_shape.values())
        pbar = tqdm(
            total=model_size,
            unit="B",
            unit_scale=True,
            desc="Checkpoint size",
        )

        shards, index = _shard_hf_checkpoint(state_dict_shape, max_shard_size, SAFE_TENSORS_MODEL)

        shard_specs = [(shard_name, tuple(weight_map.keys())) for shard_name, weight_map in shards.items()]
        this_max_shard_size = max(
            sum(v.size * v.dtype.itemsize for v in shards[shard_name].values()) for shard_name in shards.keys()
        )
        logger.info(
            "Will save %d shards with max size %s", len(shard_specs), humanfriendly.format_size(this_max_shard_size)
        )

        def _maybe_upload(
            local_dir: str,
            *,
            files: Optional[list[str]] = None,
            commit_message: Optional[str] = None,
            source_is_temp: bool,
        ):
            if hf_repo_ref is None:
                return

            upload_kwargs = hf_upload_kwargs.copy()
            if commit_message is not None and "commit_message" not in upload_kwargs:
                upload_kwargs["commit_message"] = commit_message

            if files is not None and len(files) == 0:
                return

            if files is None or source_is_temp:
                upload_to_hub(local_dir, hf_repo_ref, **upload_kwargs)
                return

            # if we're not sure source_is_temp, we have to be more careful to only upload the files we want

            repo_type = upload_kwargs.pop("repo_type", "model")
            token = upload_kwargs.pop("token", None)
            revision = upload_kwargs.pop("revision", hf_repo_ref.revision)
            create_pr = upload_kwargs.pop("create_pr", False)
            commit_message_arg = upload_kwargs.pop("commit_message", None) or commit_message

            for relative_path in files:
                file_path = os.path.join(local_dir, relative_path)
                huggingface_hub.upload_file(
                    path_or_fileobj=file_path,
                    path_in_repo=relative_path,
                    repo_id=hf_repo_ref.model_name_or_path,
                    repo_type=repo_type,
                    token=token,
                    revision=revision,
                    commit_message=commit_message_arg,
                    create_pr=create_pr,
                )

        def _list_relative_files(directory: str) -> set[str]:
            rel_files: set[str] = set()
            for root, _, filenames in os.walk(directory):
                for filename in filenames:
                    full_path = os.path.join(root, filename)
                    rel_files.add(os.path.relpath(full_path, directory))
            return rel_files

        for shard_name, subset_keys in shard_specs:
            with temp_dir_before_upload(path) as local_path:
                if path != local_path:
                    logger.info(f"Saving shard {shard_name} to {path} via temp path {local_path}")

                os.makedirs(local_path, exist_ok=True)
                subset_arg: Optional[tuple[str, ...]]
                if len(subset_keys) == 0:
                    subset_arg = None
                else:
                    subset_arg = subset_keys

                shard_weights = _to_state_dict_with_dtype(model, dtype, subset_arg)
                shard_numpy = {k: np.asarray(v) for k, v in shard_weights.items()}
                bytes_this_time = sum(v.nbytes for v in shard_numpy.values())
                logger.info(
                    "Saving shard %s (%s, %.2f%% of model)",
                    shard_name,
                    humanfriendly.format_size(bytes_this_time),
                    100 * bytes_this_time / model_size,
                )
                save_state_dict(shard_numpy, os.path.join(local_path, shard_name))

                _maybe_upload(
                    local_path,
                    files=[shard_name],
                    commit_message=f"Upload shard {shard_name} from Levanter",
                    source_is_temp=path != local_path,
                )
                pbar.update(bytes_this_time)

        if index is not None:
            logger.info(
                f"Saved a sharded checkpoint with {len(shard_specs)} shards, max size {humanfriendly.format_size(this_max_shard_size)}"
            )

        with temp_dir_before_upload(path) as local_path:
            if path != local_path:
                logger.info(f"Saving metadata to {path} via temp path {local_path}")

            os.makedirs(local_path, exist_ok=True)

            files_before = _list_relative_files(local_path)

            if save_reference_code_flag:
                logger.info(f"Copying reference code from {self.reference_checkpoint}")
                self._save_code_local(local_path)

            if save_tokenizer:
                logger.info("Saving tokenizer")
                self.tokenizer.save_pretrained(local_path)

            if save_feature_extractor and self.feature_extractor is not None:
                logger.info("Saving feature extractor")
                self.feature_extractor.save_pretrained(local_path)

            with open(os.path.join(local_path, "config.json"), "w") as f:
                json.dump(dict_config, f, cls=ConfigJSONEncoder)

            if index is not None:
                with open(os.path.join(local_path, SAFE_TENSORS_INDEX_NAME), "w") as f:
                    json.dump(index, f)

            files_after = _list_relative_files(local_path)
            new_files = sorted(files_after - files_before)

            _maybe_upload(
                local_path,
                files=new_files,
                commit_message="Upload config and metadata from Levanter",
                source_is_temp=path != local_path,
            )

        logger.info(f"Finished saving HF-compatible checkpoint to {path}")

    def _save_code_local(self, path):
        if self.reference_checkpoint is None:
            warnings.warn("No reference checkpoint provided, so no code will be saved")
            return

        repo, revision = self._get_ref(self.reference_checkpoint)

        # first we're going to decide what code to save
        # as a heuristic, we'll use .gitattributes to decide what to save: anything not in LFS will be saved
        # need to also save the .gitattributes file itself
        # TODO: .gitignore too? it's not used a lot with the hub
        if os.path.exists(repo):
            # local path
            if revision is not None:
                warnings.warn("Ignoring revision because this is a local path. We don't handle this case well yet")
            attributes_path = os.path.join(repo, ".gitattributes")
            if not os.path.exists(attributes_path):
                attributes_path = None
        else:
            # check hub
            try:
                attributes_path = hf_hub_download(repo_id=repo, filename=".gitattributes", revision=revision)
            except EntryNotFoundError:
                attributes_path = None
            except GatedRepoError:
                attributes_path = None

        if attributes_path is None:
            warnings.warn("HF Export - No .gitattributes file found, using a heuristic to decide what to save")
            ignore_files = [
                ".git",
                "*.bin.*",
                "*.lfs.*",
                "*.bin",
                "*.h5",
                "*.tflite",
                "*.tar.gz",
                "*.ot",
                "*.onnx",
                "*.msgpack",
                "model.safetensors",
            ]
        else:
            # read the attributes file and get the globs
            with open(attributes_path) as f:
                attributes = f.read()
            ignore_files = [".git"]
            for line in attributes.split("\n"):
                line = line.strip()
                if line.startswith("#") or line == "":
                    continue
                # NB: this is not a full implementation of .gitattributes, but it's good enough for our purposes
                if "filter=lfs" in line:
                    ignore_files.append(line.split()[0])

        if os.path.exists(repo):
            local_code_path = repo
        else:
            local_code_path = snapshot_download(repo, revision=revision, ignore_patterns=ignore_files)

        # now we'll save the code
        os.makedirs(path, exist_ok=True)

        shutil_ignore = shutil.ignore_patterns(*ignore_files)
        shutil.copytree(local_code_path, path, ignore=shutil_ignore, dirs_exist_ok=True)

        logger.debug(f"Saved code to {path}")


def _is_url_like(path):
    return urllib.parse.urlparse(path).scheme != ""


def save_hf_checkpoint_callback(
    base_path,
    converter: HFCheckpointConverter,
    upload_to_hf: Union[bool, str, RepoRef] = False,
    save_dtype: Optional[jnp.dtype] = None,
    **hf_upload_kwargs,
):
    """
    If hf_repo is provided, this will upload the checkpoint to the huggingface hub, passing
    any additional kwargs to the huggingface_hub.upload_folder function.

    :param base_path: the base path to save the checkpoint to. `/step-<step>` will be appended to this. base_path
    may be a GCS bucket path, in which case the checkpoint will be uploaded to GCS after being written to a tmp
    :param upload_to_hf:
    :param hf_upload_kwargs:
    :return:
    """

    def cb(step: StepInfo):
        nonlocal hf_upload_kwargs
        if step.step == 0:
            return
        if upload_to_hf is not None and "commit_message" not in hf_upload_kwargs:
            my_upload_kwargs = hf_upload_kwargs.copy()
            my_upload_kwargs["commit_message"] = f"Upload for step {step.step} from Levanter"
        else:
            my_upload_kwargs = hf_upload_kwargs
        converter.save_pretrained(
            cast(ModelWithHfSerializationMixin, step.eval_model),
            os.path.join(base_path, f"step-{step.step}"),
            upload_to_hf=upload_to_hf,
            dtype=save_dtype,
            **my_upload_kwargs,
        )

    return cb


def load_tokenizer(model_name_or_path, revision=None, local_cache_dir=None, trust_remote_code=True) -> HfTokenizer:
    """Like AutoTokenizer.from_pretrained, but works with gs:// paths or anything on fsspec"""
    with _patch_hf_hub_download():
        return AutoTokenizer.from_pretrained(
            model_name_or_path, revision=revision, cache_dir=local_cache_dir, trust_remote_code=trust_remote_code
        )


def load_processor(model_name_or_path, revision=None, local_cache_dir=None, trust_remote_code=True) -> ProcessorMixin:
    """Like AutoProcessor.from_pretrained, but works with gs:// paths or anything on fsspec"""
    with _patch_hf_hub_download():
        return AutoProcessor.from_pretrained(
            model_name_or_path, revision=revision, cache_dir=local_cache_dir, trust_remote_code=trust_remote_code
        )


_sync_count = 0


def upload_to_hub(local_path: str, repo_ref: Union[str, RepoRef], **hf_upload_kwargs):
    ref = _coerce_to_rr(repo_ref)

    if jax.process_index() == 0:
        logger.info(f"Uploading HF-compatible checkpoint to {ref.model_name_or_path}")
        huggingface_hub.upload_folder(
            folder_path=local_path, repo_id=(ref.model_name_or_path), revision=(ref.revision), **hf_upload_kwargs
        )
        logger.info(f"Finished uploading HF-compatible checkpoint to {ref.model_name_or_path}")
    else:
        logger.info(f"Finished waiting for rank 0 to upload checkpoint to {ref.model_name_or_path}")

    global _sync_count
    sync_global_devices(f"upload? {ref.model_name_or_path}{ref.revision} {_sync_count}")
    _sync_count += 1


def _convert_to_jnp(v, dtype):
    import torch

    # we'd rather not convert to float32 to conserve memory, so we convert direct to jax.numpy
    with use_cpu_device():
        if v is None:
            return None
        elif v.dtype == torch.bfloat16:
            arr = jax.numpy.array(v.cpu().view(torch.float16).numpy()).view(jax.numpy.bfloat16)
        else:
            arr = jax.numpy.array(v.cpu().numpy())

        if dtype is not None:
            arr = arr.astype(dtype)

        return arr


def _patch_missing_buffers_for_deser(lev_model, lm_model_cls, Vocab, config, key, axis_mapping):
    """
    State dict serialization doesn't always save buffers, so when we initialize a model from a state dict, we might
    need to re-initialize the buffers. We do this by rerunning the constructor, but only save the buffers.
    JAX jit will avoid actually doing the computation.
    """
    dtype_structs, real_arrays = eqx.partition(lev_model, lambda x: isinstance(x, jax.ShapeDtypeStruct))

    buffer_leaves = jax.tree_util.tree_leaves(dtype_structs)
    if len(buffer_leaves) == 0:
        return lev_model

    # ok, we now want to re-initialize the buffers by running the constructor for real, getting only the missing
    # arrays. We're relying on jit to do all the work in eliminating the unnecessary computation/memory
    @haliax.named_jit(axis_resources=axis_mapping)
    def _init_buffers():
        new_model = lm_model_cls.init(Vocab, config, key=key)

        def select_if_missing(missing_leaf, new_value):
            if isinstance(missing_leaf, jax.ShapeDtypeStruct):
                return new_value
            else:
                return None

        return jax.tree.map(select_if_missing, dtype_structs, new_model, is_leaf=lambda x: x is None)

    new_buffers = _init_buffers()

    result = eqx.combine(real_arrays, new_buffers)
    return result


# copied/adapted from HF Transformers
# Apache 2.0 License


def _shard_hf_checkpoint(
    state_dict: dict[str, Array | ShapeDtypeStruct],
    max_shard_size: int = DEFAULT_MAX_SHARD_SIZE,
    weights_name: str = SAFE_TENSORS_MODEL,
) -> tuple[dict[str, dict[str, Array]], dict | None]:
    """
    Splits a model state dictionary in sub-checkpoints so that the final size of each sub-checkpoint does not exceed a
    given size.

    The sub-checkpoints are determined by iterating through the `state_dict` in the order of its keys, so there is no
    optimization made to make each sub-checkpoint as close as possible to the maximum size passed. For example, if the
    limit is 10GB and we have weights of sizes [6GB, 6GB, 2GB, 6GB, 2GB, 2GB] they will get sharded as [6GB], [6+2GB],
    [6+2+2GB] and not [6+2+2GB], [6+2GB], [6GB].

    <Tip warning={true}>

    If one of the model's weight is bigger than `max_shard_size`, it will end up in its own sub-checkpoint which will
    have a size greater than `max_shard_size`.

    </Tip>

    Args:
        state_dict (`dict[str, Array]`): The state dictionary of a model to save.
        max_shard_size (`int`):
            The maximum size of each sub-checkpoint.
        weights_name (`str`, *optional*, defaults to `"pytorch_model.bin"`):
            The name of the model save file.

    Returns:
        A tuple comprising the sharded state dictionaries and the index. The index is a dictionary with two keys:
        - `"metadata"`: a dictionary containing the total size of the model and the number of shards.
        - `"weight_map"`: a dictionary mapping each weight to the sub-checkpoint it is saved in.

        The index may be None if there is only one shard.
    """
    sharded_state_dicts: list[dict[str, Array]] = [{}]
    last_block_size = 0
    total_size = 0

    for key, weight in state_dict.items():
        weight_size = weight.size * weight.dtype.itemsize

        # If this weight is going to tip up over the maximal size, we split, but only if we have put at least one
        # weight in the current shard.
        if last_block_size + weight_size > max_shard_size and len(sharded_state_dicts[-1]) > 0:
            sharded_state_dicts.append({})
            last_block_size = 0

        sharded_state_dicts[-1][key] = weight
        last_block_size += weight_size
        total_size += weight_size

    # If we only have one shard, we return it
    if len(sharded_state_dicts) == 1:
        return {weights_name: sharded_state_dicts[0]}, None

    # Otherwise, let's build the index
    weight_map = {}
    shards: dict[str, dict[str, Array]] = {}
    for idx, shard in enumerate(sharded_state_dicts):
        # NOTE(dlwh): this is how it is in the HF code. it hurts me
        shard_file = weights_name.replace(".bin", f"-{idx + 1:05d}-of-{len(sharded_state_dicts):05d}.bin")
        shard_file = shard_file.replace(
            ".safetensors", f"-{idx + 1:05d}-of-{len(sharded_state_dicts):05d}.safetensors"
        )
        shards[shard_file] = shard
        for key in shard.keys():
            weight_map[key] = shard_file

    # Add the metadata
    metadata = {"total_size": total_size}
    index = {"metadata": metadata, "weight_map": weight_map}
    return shards, index


def _shard_best_effort(array_or_slice, dtype) -> jax.Array:
    # get_shape is for safetensors, shape is for numpy arrays
    # (there's no exported type for the safetensors array, so we just duck type)
    if hasattr(array_or_slice, "get_shape"):
        shape = array_or_slice.get_shape()
    else:
        shape = array_or_slice.shape

    sharding = best_effort_sharding(shape)

    def get_slice(indices):
        arr = array_or_slice[indices]
        if dtype is not None:
            arr = arr.astype(dtype)

        return arr

    return jax.make_array_from_callback(tuple(shape), sharding, get_slice)


def _is_hf_hub_model(ref: RepoRef):
    api = HfApi()

    try:
        api.model_info(repo_id=ref.model_name_or_path)
        return True
    except RepositoryNotFoundError:
        return False


@contextlib.contextmanager
def _patch_hf_hub_download():
    """
    Temporarily monkeypatch `hf_hub_download` to handle fsspec URLs, ensuring the temporary directory
    persists for the lifetime of the context manager.
    """
    original_hf_hub_download = transformers.utils.hub.hf_hub_download

    # Create a temporary directory that persists through the context manager
    with tempfile.TemporaryDirectory() as tmpdir:

        def custom_hf_hub_download(*args, **kwargs):
            """
            Custom implementation of hf_hub_download to handle fsspec URLs.
            """
            repo_id = kwargs.get("repo_id", args[0] if len(args) > 0 else None)
            filename = kwargs.get("filename", args[1] if len(args) > 1 else None)
            cache_dir = kwargs.get("cache_dir", tmpdir)
            repo_type = kwargs.get("repo_type")
            revision = kwargs.get("revision")
            if repo_type is None:
                repo_type = "model"

            if revision is None:
                revision = "main"

            if repo_id and filename and _is_url_like(repo_id):
                fs, path = fsspec.core.url_to_fs(repo_id)
                remote_path = os.path.join(path, filename)
                # local_path = os.path.join(tmpdir, filename)
                local_path = os.path.join(
                    cache_dir, repo_folder_name(repo_id=repo_id, repo_type=repo_type), "snapshots", revision, filename
                )

                if not fs.exists(remote_path):
                    raise EntryNotFoundError(f"File {remote_path} not found")

                fs.get(remote_path, local_path)
                return local_path

            # Fallback to the original implementation
            return original_hf_hub_download(*args, **kwargs)

        # Monkeypatch hf_hub_download
        transformers.utils.hub.hf_hub_download = custom_hf_hub_download

        # we also need to monkeypatch huggingface_hub/utils/_validators.py:106 validate_repo_id
        # to allow fsspec paths
        original_validate_repo_id = huggingface_hub.utils._validators.validate_repo_id

        def custom_validate_repo_id(repo_id):
            if _is_url_like(repo_id):
                return
            return original_validate_repo_id(repo_id)

        huggingface_hub.utils._validators.validate_repo_id = custom_validate_repo_id

        try:
            yield custom_hf_hub_download
        finally:
            # Restore the original implementation
            transformers.utils.hub.hf_hub_download = original_hf_hub_download
            huggingface_hub.utils._validators.validate_repo_id = original_validate_repo_id
