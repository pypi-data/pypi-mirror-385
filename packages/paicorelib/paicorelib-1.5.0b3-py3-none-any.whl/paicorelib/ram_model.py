import operator
import warnings
from collections.abc import Iterable
from typing import Annotated, TypeVar

import numpy as np
from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    InstanceOf,
    PlainSerializer,
    ValidationInfo,
    field_validator,
    model_validator,
)
from pydantic.type_adapter import TypeAdapter
from pydantic.types import NonNegativeInt

# Use `typing_extensions.TypedDict`
from typing_extensions import TypedDict

from .ram_defs import LeakComparisonMode as LCMode
from .ram_defs import LeakDirectionMode as LDMode
from .ram_defs import LeakIntegrationMode as LIMode
from .ram_defs import NegativeThresholdMode as NTMode
from .ram_defs import OfflineRAMDefs as OffRAMDefs
from .ram_defs import OnlineRAMDefs as OnRAMDefs
from .ram_defs import OnlineRAMDefs_WW1 as OnRAMDefs_WW1
from .ram_defs import OnlineRAMDefs_WWn as OnRAMDefs_WWn
from .ram_defs import RAMDefs, ResetMode
from .ram_defs import SynapticIntegrationMode as SIMode
from .reg_defs import WeightWidth

__all__ = [
    "NeuDestInfo",
    "OfflineNeuDestInfo",
    "OnlineNeuDestInfo",
    "NeuAttrs",
    "OfflineNeuAttrs",
    "OnlineNeuAttrs",
    "OfflineNeuConf",
    "OnlineNeuConf",
]

COORD_MAX = RAMDefs.COORD_MAX


class NeuDestInfo(BaseModel):
    model_config = ConfigDict(extra="ignore", frozen=True, strict=True)

    addr_chip_x: Annotated[
        NonNegativeInt,
        Field(
            le=COORD_MAX, description="X coordinate of the target chip of the neuron."
        ),
    ]

    addr_chip_y: Annotated[
        NonNegativeInt,
        Field(
            le=COORD_MAX, description="Y coordinate of the target chip of the neuron."
        ),
    ]

    addr_core_x: Annotated[
        NonNegativeInt,
        Field(
            le=COORD_MAX, description="X coordinate of the target core of the neuron."
        ),
    ]

    addr_core_y: Annotated[
        NonNegativeInt,
        Field(
            le=COORD_MAX, description="Y coordinate of the target core of the neuron."
        ),
    ]

    addr_core_x_ex: Annotated[
        NonNegativeInt,
        Field(le=COORD_MAX, description="X replication identifier of the neuron."),
    ]

    addr_core_y_ex: Annotated[
        NonNegativeInt,
        Field(le=COORD_MAX, description="Y replication identifier of the neuron."),
    ]

    tick_relative: Annotated[
        list[InstanceOf[NonNegativeInt]], Field(description="Destination timeslot.")
    ]

    addr_axon: Annotated[
        list[InstanceOf[NonNegativeInt]], Field(description="Destination axon address.")
    ]

    @model_validator(mode="after")
    def length_match_check(self):
        if len(self.tick_relative) != len(self.addr_axon):
            raise ValueError(
                "parameter 'tick_relative' & 'addr_axon' must have the same length, "
                f"but {len(self.tick_relative)} != {len(self.addr_axon)}."
            )

        return self


_IT = TypeVar("_IT", bound=Iterable)


def _range_check(param: _IT, field: str, min_val: int, max_val: int) -> _IT:
    if any(item > max_val or item < min_val for item in param):
        # DO NOT change the type of exception `ValueError` in the validators below.
        raise ValueError(f"parameter '{field}' out of range [{min_val}, {max_val}].")

    return param


def _ndarray_custom_serializer(value: int | np.ndarray) -> int | list[int]:
    return value if isinstance(value, int) else value.tolist()


class OfflineNeuDestInfo(NeuDestInfo):
    @field_validator("tick_relative")
    @classmethod
    def tick_relative_check(cls, v):
        return _range_check(v, "tick relative", 0, OffRAMDefs.ADDR_TS_MAX)

    @field_validator("addr_axon")
    @classmethod
    def addr_axon_check(cls, v):
        # NOTE: When offline core -> online core, the upper limit of `addr_axon` is `OnRAMDefs.ADDR_AXON_MAX`.
        # Use `max` to cover both cases.
        return _range_check(
            v, "addr_axon", 0, max(OffRAMDefs.ADDR_AXON_MAX, OnRAMDefs.ADDR_AXON_MAX)
        )


class OnlineNeuDestInfo(NeuDestInfo):
    @field_validator("tick_relative")
    @classmethod
    def tick_relative_check(cls, v):
        return _range_check(v, "tick relative", 0, OnRAMDefs.ADDR_TS_MAX)

    @field_validator("addr_axon")
    @classmethod
    def addr_axon_check(cls, v):
        # NOTE: When online core -> offline core, the upper limit of `addr_axon` is `OffRAMDefs.ADDR_AXON_MAX`
        # Use `max` to cover both cases.
        return _range_check(
            v, "addr_axon", 0, max(OffRAMDefs.ADDR_AXON_MAX, OnRAMDefs.ADDR_AXON_MAX)
        )


class NeuAttrs(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
        frozen=True,
        arbitrary_types_allowed=True,
        use_enum_values=True,
        strict=True,
    )


class OfflineNeuAttrs(NeuAttrs):
    reset_mode: Annotated[ResetMode, Field(description="Reset mode of neuron.")]

    reset_v: Annotated[
        int,
        Field(
            ge=OffRAMDefs.RESET_V_MIN,
            le=OffRAMDefs.RESET_V_MAX,
            description="Reset voltage, 30-bit signed integer.",
        ),
    ]

    leak_comparison: Annotated[
        LCMode,
        Field(
            serialization_alias="leak_post",
            description="Leak after threshold comparison or before.",
        ),
    ]

    thres_mask_bits: Annotated[
        NonNegativeInt,
        Field(
            le=OffRAMDefs.THRES_MASK_BITS_MAX,
            serialization_alias="threshold_mask_ctrl",
            description="Bit mask for random threshold.",
        ),
    ]

    neg_thres_mode: Annotated[
        NTMode,
        Field(
            serialization_alias="threshold_neg_mode",
            description="Mode of negative threshold.",
        ),
    ]

    neg_threshold: Annotated[
        NonNegativeInt,
        Field(
            le=OffRAMDefs.NEG_THRES_MAX,
            serialization_alias="threshold_neg",
            description="Negative threshold, 29-bit unsigned integer.",
        ),
    ]

    pos_threshold: Annotated[
        NonNegativeInt,
        Field(
            le=OffRAMDefs.POS_THRES_MAX,
            serialization_alias="threshold_pos",
            description="Positive threshold, 29-bit unsigned integer.",
        ),
    ]

    leak_direction: Annotated[
        LDMode,
        Field(
            serialization_alias="leak_reversal_flag",
            description="Direction of leak, forward or reversal.",
        ),
    ]

    leak_integration_mode: Annotated[
        LIMode,
        Field(
            serialization_alias="leak_det_stoch",
            description="Mode of leak integration, deterministic or stochastic.",
        ),
    ]

    leak_v: Annotated[
        int | np.ndarray,
        Field(description="Leak voltage, 30-bit signed integer or a np.int32 array."),
        PlainSerializer(_ndarray_custom_serializer, when_used="json"),
    ]

    syn_integration_mode: Annotated[
        SIMode,
        Field(
            serialization_alias="weight_det_stoch",
            description="Mode of synaptic integration, deterministic or stochastic.",
        ),
    ]

    bit_trunc: Annotated[
        NonNegativeInt,
        Field(
            le=OffRAMDefs.BIT_TRUNC_MAX,
            serialization_alias="bit_truncate",
            description="Position of truncation, 5-bit unsigned integer.",
        ),
    ]

    voltage: Annotated[
        int,
        Field(
            default=0,
            description="Initial voltage, 30-bit signed integer. Fixed at 0 at initialization.",
        ),
        BeforeValidator(int),
    ]


class OfflineNeuConf(BaseModel):
    attrs: OfflineNeuAttrs
    dest_info: OfflineNeuDestInfo


val_range_name = {
    "leak_v": ("LEAK_V_MIN", "LEAK_V_MAX"),
    "pos_threshold": ("THRES_MIN", "THRES_MAX"),
    "neg_threshold": ("FLOOR_THRES_MIN", "FLOOR_THRES_MAX"),
    "reset_v": ("RESET_V_MIN", "RESET_V_MAX"),
    "init_v": ("INIT_V_MIN", "INIT_V_MAX"),
    "voltage": ("VOLTAGE_MIN", "VOLTAGE_MAX"),
}

_VT = TypeVar("_VT", int, np.ndarray)


def _validate_range(field: str, value: _VT, info: ValidationInfo) -> _VT:
    if info.context is None:
        warnings.warn(
            "context 'weight_width' is not provided. Assuming 8-bit weight width.",
            UserWarning,
        )
        ww = WeightWidth.WEIGHT_WIDTH_8BIT
    else:
        assert isinstance(
            info.context, dict
        ), f"context must be dict, but got {type(info.context).__name__}."
        if "weight_width" not in info.context:
            warnings.warn(
                "context 'weight_width' is not provided. Assuming 8-bit weight width.",
                UserWarning,
            )
            ww = WeightWidth.WEIGHT_WIDTH_8BIT
        else:
            ww = info.context["weight_width"]
            if not isinstance(ww, WeightWidth):
                raise TypeError(
                    f"context 'weight_width' must be of type 'WeightWidth', but got {type(ww).__name__}."
                )

    if field not in val_range_name:
        raise ValueError(f"invalid field name: {field}")

    min_attr, max_attr = val_range_name[field]
    getter = operator.attrgetter(min_attr, max_attr)

    if ww == WeightWidth.WEIGHT_WIDTH_1BIT:
        min_val, max_val = getter(OnRAMDefs_WW1)
    else:
        min_val, max_val = getter(OnRAMDefs_WWn)

    if isinstance(value, int):
        if not (min_val <= value <= max_val):
            raise ValueError(f"parameter '{field}' out of range [{min_val}, {max_val}]")
    else:
        _min, _max = np.min(value), np.max(value)
        if not (min_val <= _min <= _max <= max_val):
            raise ValueError(f"parameter '{field}' out of range [{min_val}, {max_val}]")

        if field in ("leak_v", "init_v"):
            value = value.astype(np.int32)

    return value


class OnlineNeuAttrs(NeuAttrs):
    leak_v: Annotated[
        int | np.ndarray,
        Field(
            serialization_alias="leakage_reg",
            description="Leak voltage, 15-/32-bit signed integer or a np.int32 array.",
        ),
        PlainSerializer(_ndarray_custom_serializer, when_used="json"),
    ]

    pos_threshold: Annotated[
        int,
        Field(
            serialization_alias="threshold_reg",
            description="Pos threshold, 15-/32-bit signed integer.",
        ),
    ]

    neg_threshold: Annotated[
        int,
        Field(
            serialization_alias="floor_threshold_reg",
            description="Floor threshold, 7-/32-bit signed integer.",
        ),
    ]

    reset_v: Annotated[
        int,
        Field(
            serialization_alias="reset_potential_reg",
            description="Reset voltage, 6-/32-bit signed integer.",
        ),
    ]

    init_v: Annotated[
        int | np.ndarray,
        Field(
            default=0,
            serialization_alias="initital_potential_reg",
            description="Initial voltage, 6-/32-bit signed integer.",
        ),
        PlainSerializer(_ndarray_custom_serializer, when_used="json"),
    ]

    voltage: Annotated[
        int,
        Field(
            default=0,
            serialization_alias="potential_reg",
            description="Initial voltage, 15-/32-bit signed integer. Fixed at 0.",
        ),
        BeforeValidator(int),
    ]

    plasticity_start: Annotated[
        NonNegativeInt,
        Field(
            default=0,
            le=OnRAMDefs.PLASTICITY_START_MAX,
            description="Position where plasticity starts.",
        ),
    ]

    plasticity_end: Annotated[
        NonNegativeInt,
        Field(
            default=OnRAMDefs.PLASTICITY_END_MAX,
            le=OnRAMDefs.PLASTICITY_END_MAX,
            description="Position where plasticity ends.",
        ),
    ]

    @field_validator(*["leak_v", "reset_v", "pos_threshold", "neg_threshold", "init_v"])
    @classmethod
    def validate_ranges(cls, v: _VT, info: ValidationInfo) -> _VT:
        if info.field_name is None:
            raise ValueError("'field_name' is None")

        return _validate_range(info.field_name, v, info)

    @model_validator(mode="after")
    def plasticity_range_check(self):
        if self.plasticity_start > self.plasticity_end:
            raise ValueError(
                "'plasticity_start' must be less than or equal to 'plasticity_end', but got "
                f"{self.plasticity_start} > {self.plasticity_end}"
            )

        return self


class OnlineNeuConf(BaseModel):
    attrs: OnlineNeuAttrs
    dest_info: OnlineNeuDestInfo


class NeuDestInfoDict(TypedDict):
    """Typed dictionary of `NeuronDestInfo` for typing check."""

    addr_core_x: NonNegativeInt
    addr_core_y: NonNegativeInt
    addr_core_x_ex: NonNegativeInt
    addr_core_y_ex: NonNegativeInt
    addr_chip_x: NonNegativeInt
    addr_chip_y: NonNegativeInt
    tick_relative: list[InstanceOf[NonNegativeInt]]
    addr_axon: list[InstanceOf[NonNegativeInt]]


OfflineNeuDestInfoChecker = TypeAdapter(OfflineNeuDestInfo)
OnlineNeuDestInfoChecker = TypeAdapter(OnlineNeuDestInfo)
