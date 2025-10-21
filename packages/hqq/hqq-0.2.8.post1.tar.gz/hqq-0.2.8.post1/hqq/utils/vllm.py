# SPDX-License-Identifier: Apache-2.0
# Written by Dr. Hicham Badri @Mobius Labs GmbH - 2024

#re-using some code from vllm Marlin-HQQ, see below.

from typing import Any, Dict, List, Optional
import torch
import logging

from vllm.model_executor.layers.linear import (
    LinearBase,
    LinearMethodBase,
    UnquantizedLinearMethod,
)
from vllm.model_executor.layers.quantization.base_config import (
    QuantizationConfig,
    QuantizeMethodBase,
)

from vllm.model_executor.layers.quantization import register_quantization_config

from vllm.model_executor.layers.quantization.utils.quant_utils import (
    gptq_pack,
    get_pack_factor,
)
from vllm.model_executor.parameter import BasevLLMParameter, PackedvLLMParameter

# HQQ
from vllm.model_executor.layers.quantization.hqq_marlin import (
    HQQMarlinConfig,
    HQQZeroScaleParameter,
    HQQEmptyParameter,
    error_loader,
)
from ..core.quantize import Quantizer, HQQLinear, BaseQuantizeConfig

# Add new linear methods in order to use loader_v2
import vllm.model_executor.layers.linear as vllm_linear

HQQ_LINEAR_METHODS = [
    "HQQGemLiteVLLMLinear",
    "HQQPytorchVLLMLinear",
    "HQQOnTheFlyMethod",
]

for linear_method in HQQ_LINEAR_METHODS:
    if linear_method not in vllm_linear.WEIGHT_LOADER_V2_SUPPORTED:
        vllm_linear.WEIGHT_LOADER_V2_SUPPORTED.append(linear_method)

logger = logging.getLogger(__name__)

# Faster unpacking
def unpack_rows(
    W_q_packed: torch.Tensor,
    W_nbits: int,
    num_output_rows: int,
    num_output_cols: int,
    dtype: torch.dtype = torch.uint8,
) -> torch.Tensor:

    num_rows, num_cols = W_q_packed.shape
    elements_per_sample = num_output_rows // num_rows

    shifts       = torch.arange(elements_per_sample, device=W_q_packed.device, dtype=W_q_packed.dtype) * W_nbits  
    mask         = ((1 << W_nbits) - 1)
    W_q_unpacked = ((W_q_packed.unsqueeze(-1) >> shifts) & mask).to(dtype) 
    W_q_unpacked = W_q_unpacked.permute(0, 2, 1).reshape(num_output_rows, num_cols)
    
    return W_q_unpacked

# Gemlite
try:
    import gemlite
    from gemlite import DType, GemLiteLinear
    from gemlite.core import TORCH_TO_DTYPE

    gemlite_is_available = True

    # Faster gptq_pack
    def gptq_pack(
        q_w: torch.Tensor, num_bits: int, size_k: int, size_n: int
    ) -> torch.Tensor:

        q_w = q_w.cuda()
        out = gemlite.bitpack.pack_weights_over_rows_triton(q_w, num_bits, packing_bitwidth=32, transpose=False)[0]
        del q_w
        torch.cuda.empty_cache()
        return out
        
    # Faster unpacking
    def unpack_rows(
        W_q_packed: torch.Tensor,
        W_nbits: int,
        num_output_rows: int,
        num_output_cols: int,
        dtype: torch.dtype = torch.uint8,
    ) -> torch.Tensor:
        
        return gemlite.bitpack.unpack_over_rows_triton(W_q_packed, W_nbits, num_output_rows, dtype)

except Exception as e:
    logger.warning("Gemlite backend not available. Make sure the lib installed https://github.com/mobiusml/gemlite/", e) 
    gemlite_is_available = False

# Hugging Face config quant name tag
QUANT_NAME = "hqq"


# Override HQQweightParameter to support more nbits.
# TODO: 3-bit support not added yet.
class HQQweightParameter(PackedvLLMParameter):
    def __init__(self, packed_factor: int, packed_dim: int, weight_bits: int, **kwargs):
        super().__init__(packed_factor, packed_dim, None, **kwargs)
        self.weight_bits = weight_bits
        self.packing = Quantizer.bit_to_packing[self.weight_bits]
        self.input_shape = self.shape[self.input_dim] * self.packed_factor
        self.output_shape = self.shape[self.output_dim]

    def load_merged_column_weight(self, loaded_weight: torch.Tensor, **kwargs):
        loaded_weight = Quantizer.unpack[self.packing](loaded_weight, dtype=torch.uint8)
        loaded_weight = loaded_weight.reshape(-1, self.input_shape).transpose(1, 0)
        loaded_weight = gptq_pack(
            loaded_weight,
            self.weight_bits,
            loaded_weight.shape[0],
            loaded_weight.shape[1],
        )
        super().load_merged_column_weight(loaded_weight, **kwargs)

    def load_row_parallel_weight(self, loaded_weight: torch.Tensor):
        loaded_weight = Quantizer.unpack[self.packing](loaded_weight, dtype=torch.uint8)
        loaded_weight = loaded_weight.reshape(self.output_shape, -1).transpose(1, 0)
        loaded_weight = gptq_pack(
            loaded_weight,
            self.weight_bits,
            loaded_weight.shape[0],
            loaded_weight.shape[1],
        )
        super().load_row_parallel_weight(loaded_weight)

    def load_qkv_weight(self, loaded_weight: torch.Tensor, **kwargs):
        loaded_weight = Quantizer.unpack[self.packing](loaded_weight, dtype=torch.uint8)
        loaded_weight = loaded_weight.reshape(-1, self.input_shape).transpose(1, 0)
        loaded_weight = gptq_pack(
            loaded_weight,
            self.weight_bits,
            loaded_weight.shape[0],
            loaded_weight.shape[1],
        )
        super().load_qkv_weight(loaded_weight, **kwargs)


class HQQOnTheFlyweightParameter(PackedvLLMParameter):
    def __init__(self, packed_factor: int, packed_dim: int, weight_bits: int, **kwargs):
        super().__init__(packed_factor, packed_dim, None, **kwargs)
        self.weight_bits = weight_bits
        self.input_shape = self.shape[self.input_dim] * self.packed_factor
        self.output_shape = self.shape[self.output_dim]

    def load_merged_column_weight(self, loaded_weight: torch.Tensor, **kwargs):
        loaded_weight = loaded_weight.view(-1, self.input_shape)
        super().load_merged_column_weight(loaded_weight, **kwargs)

    def load_row_parallel_weight(self, loaded_weight: torch.Tensor):
        loaded_weight = loaded_weight.view(self.output_shape, -1)
        super().load_row_parallel_weight(loaded_weight)

    def load_qkv_weight(self, loaded_weight: torch.Tensor, **kwargs):
        loaded_weight = loaded_weight.view(-1, self.input_shape)
        super().load_qkv_weight(loaded_weight, **kwargs)


#Create alias
@register_quantization_config("hqq_marlin")
class HQQMarlinPrequantizedConfig(HQQMarlinConfig):
    @classmethod
    def get_name(cls) -> str:
        return 'hqq_marlin'

##############################################################################################
#HQQBaseVLLMConfig / HQQBaseVLLMLinear
##############################################################################################
# Base HQQ/VLLM Linear method
class HQQBaseVLLMConfig(QuantizationConfig):
    """Config class for HQQ"""

    def __init__(
        self,
        weight_bits: int,
        group_size: int,
        axis: int = 1,
        skip_modules: Optional[List[str]] = None,
    ) -> None:

        self.weight_bits = weight_bits
        self.group_size = group_size
        self.pack_factor = 32 // weight_bits  # pre-packed into int32 in GPTQ format
        self.skip_modules = skip_modules
        self.packing = Quantizer.bit_to_packing[self.weight_bits]
        self.axis = axis

    def __repr__(self) -> str:
        return (
            f"HQQBaseVLLMConfig(weight_bits={self.weight_bits}, "
            f"group_size={self.group_size})"
        )

    @classmethod
    def get_name(cls) -> str:
        return QUANT_NAME

    @classmethod
    def get_supported_act_dtypes(cls) -> List[torch.dtype]:
        return [torch.float16, torch.bfloat16]

    @classmethod
    def get_min_capability(cls) -> int:
        return 75

    @classmethod
    def get_config_filenames(cls) -> List[str]:
        return ["quantize_config.json"]

    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> "HQQBaseVLLMConfig":
        wq_params = config["quant_config"]["weight_quant_params"]
        weight_bits = cls.get_from_keys(wq_params, ["nbits"])
        axis = cls.get_from_keys(wq_params, ["axis"])
        group_size = cls.get_from_keys(wq_params, ["group_size"])
        skip_modules = config["skip_modules"]
        return cls(weight_bits, group_size, axis, skip_modules)

    def is_layer_skipped(self, prefix: str) -> bool:
        # Split the prefix into its dot-separated components
        components = prefix.split(".")

        # Check if any of the skip modules exactly matches any component
        return self.skip_modules is not None and any(
            module_name in components for module_name in self.skip_modules
        )

    def get_quant_method(
        self, layer: torch.nn.Module, prefix: str
    ) -> Optional["QuantizeMethodBase"]:
        if isinstance(layer, LinearBase):
            if self.is_layer_skipped(prefix):
                return UnquantizedLinearMethod()
            return HQQPytorchVLLMLinear(self)
        return None

class HQQBaseVLLMLinear(LinearMethodBase):
    """Base HQQ Linear VLLM method"""

    def __init__(self, quant_config: QuantizationConfig):
        self.quant_config = quant_config

    def create_weights(
        self,
        layer: torch.nn.Module,
        input_size_per_partition: int,
        output_partition_sizes: List[int],
        input_size: int,
        output_size: int,
        params_dtype: torch.dtype,
        **extra_weight_attrs,
    ) -> None:

        self.output_size_per_partition = sum(output_partition_sizes)
        self.input_size_per_partition = input_size_per_partition

        weight_loader = extra_weight_attrs.get("weight_loader", error_loader)

        self.scales_and_zp_size = (
            input_size_per_partition // self.quant_config.group_size
        )

        # Transposed - GPTQ/GemLited packed
        W_q = HQQweightParameter(
            data=torch.empty(
                self.input_size_per_partition // self.quant_config.pack_factor,
                self.output_size_per_partition,
                dtype=torch.int32,
            ),
            input_dim=0,
            output_dim=1,
            packed_dim=0,
            packed_factor=self.quant_config.pack_factor,
            weight_bits=self.quant_config.weight_bits,
            weight_loader=weight_loader,
        )
        layer.register_parameter("W_q", W_q)

        zero = HQQZeroScaleParameter(
            data=torch.empty(
                self.output_size_per_partition,
                self.scales_and_zp_size,
                dtype=params_dtype,
            ),
            input_dim=1,
            output_dim=0,
            weight_loader=weight_loader,
        )
        layer.register_parameter("zero", zero)

        scale = HQQZeroScaleParameter(
            data=torch.empty(
                self.output_size_per_partition,
                self.scales_and_zp_size,
                dtype=params_dtype,
            ),
            input_dim=1,
            output_dim=0,
            weight_loader=weight_loader,
        )
        layer.register_parameter("scale", scale)

        setattr(
            layer,
            "current_shape",
            [self.output_size_per_partition, self.input_size_per_partition],
        )

        layer.register_parameter(
            "shape",
            BasevLLMParameter(
                data=torch.empty(2, dtype=torch.int), weight_loader=weight_loader
            ),
        )
        layer.register_parameter(
            "nbits",
            BasevLLMParameter(
                data=torch.empty(1, dtype=torch.int), weight_loader=weight_loader
            ),
        )

        ignore_parameters = (
            "axis",
            "channel_wise",
            "compute_dtype",
            "encoded_state_dict",
            "group_size",
            "offload_meta",
            "optimize",
            "packing",
            "quant_scale",
            "quant_zero",
            "round_zero",
            "stores_quant_config",
            "unpack_view_dtype",
            "view_as_float",
        )

        for name in ignore_parameters:
            layer.register_parameter(
                name,
                HQQEmptyParameter(data=torch.empty(0), weight_loader=weight_loader),
            )

    def unpack(self, layer, dtype):
        return unpack_rows(
            layer.W_q,
            self.quant_config.weight_bits,
            self.input_size_per_partition,
            self.output_size_per_partition,
            dtype=dtype,
        )

    def process_weights_after_loading(self, layer: torch.nn.Module) -> None:
        # Shape
        setattr(layer, "orig_shape", torch.Size(layer.shape))
        del layer.shape

        setattr(layer, "W_nbits", int(layer.nbits))
        del layer.nbits

        del layer.compute_dtype
        setattr(layer, "compute_dtype", layer.scale.dtype)


##############################################################################################
#HQQPytorchConfig / HQQPytorchVLLMLinear
##############################################################################################
# Pytorch
class HQQPytorchConfig(HQQBaseVLLMConfig):
    """Config class for HQQ"""

    def __init__(
        self,
        weight_bits: int,
        group_size: int,
        axis: int = 1,
        skip_modules: Optional[List[str]] = None,
    ) -> None:
        super().__init__(weight_bits, group_size, axis, skip_modules)

    @classmethod
    def get_supported_act_dtypes(cls) -> List[torch.dtype]:
        return [torch.float16, torch.bfloat16]

    def get_quant_method(
        self, layer: torch.nn.Module, prefix: str
    ) -> Optional["QuantizeMethodBase"]:
        if isinstance(layer, LinearBase):
            if self.is_layer_skipped(prefix):
                return UnquantizedLinearMethod()
            return HQQPytorchVLLMLinear(self)
        return None

#Create alias
@register_quantization_config("hqq_torch")
class HQQPytorchPrequantizedConfig(HQQPytorchConfig):
    @classmethod
    def get_name(cls) -> str:
        return 'hqq_torch'

class HQQPytorchVLLMLinear(HQQBaseVLLMLinear):
    """Linear HQQ VLLM with Pytorch backend"""

    def __init__(self, quant_config: QuantizationConfig):
        super().__init__(quant_config)

    def process_weights_after_loading(self, layer: torch.nn.Module) -> None:
        super().process_weights_after_loading(layer)

        # Repack for faster dequant
        group_size = self.quant_config.group_size
        W_q = (
            self.unpack(layer, dtype=layer.compute_dtype)
            .T.reshape(-1, group_size)
            .contiguous()
        )

        layer.W_q   = torch.nn.Parameter(Quantizer.pack[self.quant_config.packing](W_q), requires_grad=False)
        layer.scale = torch.nn.Parameter(layer.scale.data, requires_grad=False)
        layer.zero  = torch.nn.Parameter(layer.zero.data, requires_grad=False)
        torch.cuda.empty_cache()

    @torch.compile()
    def dequantize(self, layer):  # Only 8, 4, 2, 1 bit support. 3-bit NOT supported yet
        scale = layer.scale.view(-1, 1)  # non-transposed
        zero = layer.zero.view(-1, 1)  # non-transposed

        group_size = self.quant_config.group_size
        W_q = Quantizer.unpack[self.quant_config.packing](layer.W_q, dtype=layer.compute_dtype)
 
        if(self.quant_config.weight_bits == 3):
            W_q = W_q[: group_size if self.axis == 0 else self.current_shape[0] * self.current_shape[1] // group_size]

        W_q = W_q.view(-1, group_size)
        W_r = ((W_q - zero) * scale).view(layer.current_shape)
        return W_r

    def apply(
        self,
        layer: torch.nn.Module,
        x: torch.Tensor,
        bias: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        W_r = self.dequantize(layer).T
        out = torch.matmul(x, W_r)

        if bias is not None:
            out += bias

        return out


##############################################################################################
#HQQGemLiteConfig / HQQGemLiteVLLMLinear
##############################################################################################
# GemLite
class HQQGemLiteConfig(HQQBaseVLLMConfig):
    """Config class for HQQ"""

    def __init__(
        self,
        weight_bits: int,
        group_size: int,
        axis: int = 1,
        skip_modules: Optional[List[str]] = None,
    ) -> None:
        assert axis == 1, 'Only axis=1 is supported.'
        super().__init__(weight_bits, group_size, 1, skip_modules)

    @classmethod
    def get_supported_act_dtypes(cls) -> List[torch.dtype]:
        return [torch.float16, torch.bfloat16]

    def get_quant_method(
        self, layer: torch.nn.Module, prefix: str
    ) -> Optional["QuantizeMethodBase"]:
        if isinstance(layer, LinearBase):
            if self.is_layer_skipped(prefix):
                return UnquantizedLinearMethod()
            try:
                return HQQGemLiteVLLMLinear(self)
            except:
                return HQQPytorchVLLMLinear(self)
        return None

#Create alias
@register_quantization_config("hqq_gemlite")
class HQQGemLitePrequantizedConfig(HQQGemLiteConfig):
    @classmethod
    def get_name(cls) -> str:
        return 'hqq_gemlite'

class HQQGemLiteVLLMLinear(HQQBaseVLLMLinear):
    """Linear HQQ VLLM with GemLite backend"""

    def __init__(
        self,
        quant_config: QuantizationConfig,
    ):
        super().__init__(quant_config)

    def process_weights_after_loading(self, layer: torch.nn.Module) -> None:
        super().process_weights_after_loading(layer)

        # Gemlite
        dtype = layer.scale.dtype
        gemlite_dtype = TORCH_TO_DTYPE[dtype]
        gemlite_linear = GemLiteLinear(
            self.quant_config.weight_bits,
            group_size=self.quant_config.group_size,
            in_features=self.input_size_per_partition,
            out_features=self.output_size_per_partition,
            input_dtype=gemlite_dtype,
            output_dtype=gemlite_dtype,
            scaled_activations=False,
        )

        gemlite_linear.pack(
            self.unpack(layer, dtype=torch.uint8)
            .T.contiguous()
            .view(layer.current_shape),
            layer.scale.view(-1, 1),
            layer.zero.view(-1, 1),
            bias=None,
        )

        layer.gemlite_linear = gemlite_linear
        del layer.W_q, layer.scale, layer.zero

        torch.cuda.empty_cache()

    def apply(
        self,
        layer: torch.nn.Module,
        x: torch.Tensor,
        bias: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        out = layer.gemlite_linear(x)

        if bias is not None:
            out += bias

        return out

##############################################################################################
#VLLM_HQQ_BACKEND
##############################################################################################
# Backends
class VLLM_HQQ_BACKEND:
    MARLIN = HQQMarlinConfig
    GEMLITE = HQQGemLiteConfig
    PYTORCH = HQQPytorchConfig


DEFAULT_VLLM_HQQ_BACKEND = VLLM_HQQ_BACKEND.GEMLITE
COMPILE_OPTIONS = {}  # {"mode":"max-autotune-no-cudagraphs"}


##############################################################################################
#HQQOnTheFlyConfig
##############################################################################################
# On-the-fly quantization
@register_quantization_config("hqq_onthefly")
class HQQOnTheFlyConfig(QuantizationConfig):
    """Config class for HQQ Marlin"""

    def __init__(
        self,
        weight_bits: int,
        group_size: int,
        quant_mode: str = "static",
        skip_modules: Optional[List[str]] = None,
    ) -> None:
        self.weight_bits = weight_bits
        self.group_size = group_size
        self.quant_mode = quant_mode
        self.skip_modules = skip_modules

    def __repr__(self) -> str:
        return (
            f"HQQOnTheFlyConfig(weight_bits={self.weight_bits}, "
            f"group_size={self.group_size})"
        )

    @classmethod
    def get_name(cls) -> str:
        return "hqq_onthefly"

    @classmethod
    def get_supported_act_dtypes(cls) -> List[torch.dtype]:
        return [torch.float16, torch.bfloat16]

    @classmethod
    def get_min_capability(cls) -> int:
        return 75

    @classmethod
    def get_config_filenames(cls) -> List[str]:
        return ["quantize_config.json"]

    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> "HQQOnTheFlyConfig":
        wq_params = config["quant_config"]["weight_quant_params"]
        weight_bits = cls.get_from_keys(wq_params, ["nbits"])
        quant_mode = cls.get_from_keys(wq_params, ["quant_mode"])
        group_size = cls.get_from_keys(wq_params, ["group_size"])
        skip_modules = config["skip_modules"]

        return cls(weight_bits, group_size, quant_mode, skip_modules)

    def is_layer_skipped(self, prefix: str) -> bool:
        # Split the prefix into its dot-separated components
        components = prefix.split(".")

        # Check if any of the skip modules exactly matches any component
        return self.skip_modules is not None and any(
            module_name in components for module_name in self.skip_modules
        )

    def get_quant_method(
        self, layer: torch.nn.Module, prefix: str
    ) -> Optional["QuantizeMethodBase"]:
        if isinstance(layer, LinearBase):
            if self.is_layer_skipped(prefix):
                return UnquantizedLinearMethod()
            return HQQOnTheFlyMethod(self)
        return None


class HQQOnTheFlyMethod(LinearMethodBase):
    """Linear HQQ"""

    enable_compile = True  # compile the forward pass

    def __init__(self, quant_config: QuantizationConfig):
        self.quant_config = quant_config

    def create_weights(
        self,
        layer: torch.nn.Module,
        input_size_per_partition: int,
        output_partition_sizes: List[int],
        input_size: int,
        output_size: int,
        params_dtype: torch.dtype,
        **extra_weight_attrs,
    ) -> None:
        self.output_size_per_partition = sum(output_partition_sizes)
        self.input_size_per_partition = input_size_per_partition
        self.params_dtype = params_dtype

        weight_loader = extra_weight_attrs.get("weight_loader", error_loader)
        
        weight = HQQOnTheFlyweightParameter(
            data=torch.empty(
                self.output_size_per_partition,
                self.input_size_per_partition,
                dtype=params_dtype,
            ),
            input_dim=1,
            output_dim=0,
            packed_dim=0,
            packed_factor=1,
            weight_bits=16,
            weight_loader=weight_loader,
        )

        layer.register_parameter("weight", weight)

    def process_weights_after_loading(self, layer: torch.nn.Module) -> None:
        global DEFAULT_VLLM_HQQ_BACKEND

        device     = layer.weight.device
        W_nbits    = self.quant_config.weight_bits
        group_size = self.quant_config.group_size
        quant_mode = self.quant_config.quant_mode
        shape      = layer.weight.shape
        tmp_linear = None

        # Marlin
        if DEFAULT_VLLM_HQQ_BACKEND == VLLM_HQQ_BACKEND.MARLIN:
            raise NotImplementedError("MARLIN backend is not implemented yet for on-the-fly quantization.")

        processor_args = {'device': device, 'dtype':self.params_dtype}

        if W_nbits == 8:
            layer.quant_layer = None

            if DEFAULT_VLLM_HQQ_BACKEND == VLLM_HQQ_BACKEND.GEMLITE:
                #8-bit weights
                tmp_linear = torch.nn.Linear(1, 1, bias=False)
                tmp_linear.weight.data = layer.weight
                tmp_linear.in_features = layer.weight.shape[1]
                tmp_linear.out_features = layer.weight.shape[0]
        
                if "dynamic" in quant_mode:
                    processor = gemlite.helper.A8W8_int8_dynamic #default: A8W8 int8
                    if 'fp8' in quant_mode:
                        processor = gemlite.helper.A8W8_fp8_dynamic #A8W8 fp8
                    if 'mxfp8' in quant_mode:
                        processor_args['post_scale'] = True if (group_size is None) else False #MXPF8 x MXPF8
                        processor = gemlite.helper.A8W8_MXFP_dynamic
                else:
                    if('mxfp8' in quant_mode): #A16W8 - weight-only
                        processor = gemlite.helper.A16W8_MXFP
                    else:
                        processor = gemlite.helper.A16W8 
                try:
                    layer.quant_layer = processor(**processor_args).from_linear(tmp_linear)
                except Exception:
                    logger.error(f'Failed gemlite conversion, using Pytorch backend. weights.shape={shape}, processor:{processor}') 

            if DEFAULT_VLLM_HQQ_BACKEND == VLLM_HQQ_BACKEND.PYTORCH or (layer.quant_layer is None):
                layer.quant_layer = HQQLinear.from_weights(
                    layer.weight,
                    bias=None,
                    quant_config=BaseQuantizeConfig(nbits=W_nbits, group_size=group_size, axis=1),
                    compute_dtype=self.params_dtype,
                    device=device,
                )

        elif W_nbits == 4:
            # Quantized weights
            if('mxfp' in quant_mode or 'nvfp' in quant_mode):
                if DEFAULT_VLLM_HQQ_BACKEND != VLLM_HQQ_BACKEND.GEMLITE:
                    raise NotImplementedError('Unsupported backend for MXFP/NVFP')

                tmp_linear = torch.nn.Linear(1, 1, bias=False)
                tmp_linear.weight.data = layer.weight
                tmp_linear.in_features = layer.weight.shape[1]
                tmp_linear.out_features = layer.weight.shape[0]
                layer.quant_layer = tmp_linear

                if('mxfp8' in quant_mode):
                    processor = gemlite.helper.A8W4_MXFP_dynamic #MXFP8 x MXFP4
                if('mxfp4' in quant_mode):
                    if('dynamic' in quant_mode): #MXFP4 x MXPF4
                        processor = gemlite.helper.A4W4_MXFP_dynamic
                    else:
                        processor = gemlite.helper.A16W4_MXFP #MXFP4 weight-only
                elif('nvfp4' in quant_mode):
                    processor = gemlite.helper.A4W4_NVFP_dynamic

            else: #INT mode vvia HQQ
                layer.weight = layer.weight.to(device).contiguous()
                layer.quant_layer = HQQLinear.from_weights(
                    layer.weight,
                    bias=None,
                    quant_config=BaseQuantizeConfig(nbits=W_nbits, group_size=group_size, axis=1),
                    compute_dtype=self.params_dtype,
                    device=device,
                )
                processor = gemlite.helper.A16Wn

            if DEFAULT_VLLM_HQQ_BACKEND == VLLM_HQQ_BACKEND.GEMLITE:
                try:
                    if(isinstance(layer.quant_layer, HQQLinear)):
                        layer.quant_layer = processor(**processor_args).from_hqqlinear(layer.quant_layer)
                    else:
                        layer.quant_layer = processor(**processor_args).from_linear(layer.quant_layer)
                except Exception:
                    logger.error(f'Failed A16Wn gemlite conversion, using Pytorch backend. weights.shape={shape}') 

        #Clean-up
        torch.cuda.empty_cache()

        # Compile
        if HQQOnTheFlyMethod.enable_compile:
            layer.quant_layer.forward = torch.compile(layer.quant_layer.forward, **COMPILE_OPTIONS)

        # Cleanup
        del layer.weight, tmp_linear
        torch.cuda.empty_cache()

    def apply(
        self,
        layer: torch.nn.Module,
        x: torch.Tensor,
        bias: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        out = layer.quant_layer(x)

        if bias is not None:
            out += bias

        return out


##############################################################################################
#Main patching functions
##############################################################################################
# Allows overriding a VLLM quant method with arbitrary configs
def enable_vllm_hqq_quant():
    return 
    
def patch_vllm_quant_method(quant_name: str, quant_config: QuantizationConfig):
    import vllm.model_executor.layers.quantization as vllm_quantization

    get_quantization_config_orig = vllm_quantization.get_quantization_config

    def get_quantization_config_patched(quantization: str):
        if quantization == quant_name:
            return quant_config
        else:
            return get_quantization_config_orig(quantization)

    vllm_quantization.get_quantization_config = get_quantization_config_patched


def set_vllm_hqq_backend(backend: QuantizationConfig):
    global DEFAULT_VLLM_HQQ_BACKEND
    DEFAULT_VLLM_HQQ_BACKEND = backend
    if (not gemlite_is_available) and (backend == VLLM_HQQ_BACKEND.GEMLITE):
        logger.error(
            "The GemLite backend is not availble. Make sure gemlite is installed: https://github.com/mobiusml/gemlite"
        )
    return patch_vllm_quant_method(QUANT_NAME, backend)


# Set's on-the-fly hqq quantization for vllm
def set_vllm_onthefly_hqq_quant(
    weight_bits=4, group_size=64, quant_mode="static", skip_modules=["lm_head", "visual", "vision"]
):
    from vllm.model_executor.layers import linear

    original_init = linear.LinearBase.__init__

    def patched_init(
        self,
        input_size,
        output_size,
        skip_bias_add=False,
        params_dtype=None,
        quant_config=None,
        *args,
        **kwargs,
    ):
        if quant_config is None:
            quant_config = HQQOnTheFlyConfig(
                weight_bits, group_size, quant_mode, skip_modules
            )
        original_init(
            self,
            input_size,
            output_size,
            skip_bias_add,
            params_dtype,
            quant_config,
            *args,
            **kwargs,
        )

    linear.LinearBase.__init__ = patched_init


##############################################################################################
# Model specific patching
##############################################################################################

def patch_mixtral():
    import torch
    import torch.nn as nn
    from typing import Optional
    from vllm.model_executor.layers.linear import RowParallelLinear
    from vllm.model_executor.layers.quantization.base_config import QuantizationConfig
    import vllm.model_executor.models.mixtral_quant as mixtral_quant

    # Mixtral
    class MixtralMLPRowParallel(nn.Module):
        def __init__(
            self,
            num_experts: int,
            hidden_size: int,
            intermediate_size: int,
            quant_config: Optional[QuantizationConfig] = None,
        ) -> None:
            super().__init__()
            self.num_experts = num_experts
            self.ffn_dim = intermediate_size
            self.hidden_dim = hidden_size

            self.w1 = RowParallelLinear(
                self.hidden_dim, self.ffn_dim, bias=False, quant_config=quant_config
            )
            self.w2 = RowParallelLinear(
                self.ffn_dim, self.hidden_dim, bias=False, quant_config=quant_config
            )
            self.w3 = RowParallelLinear(
                self.hidden_dim, self.ffn_dim, bias=False, quant_config=quant_config
            )

            # TODO: Use vllm's SiluAndMul
            self.act_fn = nn.SiLU()

        def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
            w1_out, _ = self.w1(hidden_states)
            w1_out = self.act_fn(w1_out)
            w3_out, _ = self.w3(hidden_states)
            current_hidden_states = w1_out * w3_out
            current_hidden_states, _ = self.w2(current_hidden_states)
            return current_hidden_states

    mixtral_quant.MixtralMLP = MixtralMLPRowParallel
