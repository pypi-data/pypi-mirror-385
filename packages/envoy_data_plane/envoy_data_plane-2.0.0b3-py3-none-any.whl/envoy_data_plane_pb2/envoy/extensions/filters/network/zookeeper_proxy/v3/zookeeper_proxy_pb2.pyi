import datetime

from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from udpa.annotations import status_pb2 as _status_pb2
from udpa.annotations import versioning_pb2 as _versioning_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ZooKeeperProxy(_message.Message):
    __slots__ = ("stat_prefix", "access_log", "max_packet_bytes", "enable_latency_threshold_metrics", "default_latency_threshold", "latency_threshold_overrides", "enable_per_opcode_request_bytes_metrics", "enable_per_opcode_response_bytes_metrics", "enable_per_opcode_decoder_error_metrics")
    STAT_PREFIX_FIELD_NUMBER: _ClassVar[int]
    ACCESS_LOG_FIELD_NUMBER: _ClassVar[int]
    MAX_PACKET_BYTES_FIELD_NUMBER: _ClassVar[int]
    ENABLE_LATENCY_THRESHOLD_METRICS_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_LATENCY_THRESHOLD_FIELD_NUMBER: _ClassVar[int]
    LATENCY_THRESHOLD_OVERRIDES_FIELD_NUMBER: _ClassVar[int]
    ENABLE_PER_OPCODE_REQUEST_BYTES_METRICS_FIELD_NUMBER: _ClassVar[int]
    ENABLE_PER_OPCODE_RESPONSE_BYTES_METRICS_FIELD_NUMBER: _ClassVar[int]
    ENABLE_PER_OPCODE_DECODER_ERROR_METRICS_FIELD_NUMBER: _ClassVar[int]
    stat_prefix: str
    access_log: str
    max_packet_bytes: _wrappers_pb2.UInt32Value
    enable_latency_threshold_metrics: bool
    default_latency_threshold: _duration_pb2.Duration
    latency_threshold_overrides: _containers.RepeatedCompositeFieldContainer[LatencyThresholdOverride]
    enable_per_opcode_request_bytes_metrics: bool
    enable_per_opcode_response_bytes_metrics: bool
    enable_per_opcode_decoder_error_metrics: bool
    def __init__(self, stat_prefix: _Optional[str] = ..., access_log: _Optional[str] = ..., max_packet_bytes: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., enable_latency_threshold_metrics: bool = ..., default_latency_threshold: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., latency_threshold_overrides: _Optional[_Iterable[_Union[LatencyThresholdOverride, _Mapping]]] = ..., enable_per_opcode_request_bytes_metrics: bool = ..., enable_per_opcode_response_bytes_metrics: bool = ..., enable_per_opcode_decoder_error_metrics: bool = ...) -> None: ...

class LatencyThresholdOverride(_message.Message):
    __slots__ = ("opcode", "threshold")
    class Opcode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        Connect: _ClassVar[LatencyThresholdOverride.Opcode]
        Create: _ClassVar[LatencyThresholdOverride.Opcode]
        Delete: _ClassVar[LatencyThresholdOverride.Opcode]
        Exists: _ClassVar[LatencyThresholdOverride.Opcode]
        GetData: _ClassVar[LatencyThresholdOverride.Opcode]
        SetData: _ClassVar[LatencyThresholdOverride.Opcode]
        GetAcl: _ClassVar[LatencyThresholdOverride.Opcode]
        SetAcl: _ClassVar[LatencyThresholdOverride.Opcode]
        GetChildren: _ClassVar[LatencyThresholdOverride.Opcode]
        Sync: _ClassVar[LatencyThresholdOverride.Opcode]
        Ping: _ClassVar[LatencyThresholdOverride.Opcode]
        GetChildren2: _ClassVar[LatencyThresholdOverride.Opcode]
        Check: _ClassVar[LatencyThresholdOverride.Opcode]
        Multi: _ClassVar[LatencyThresholdOverride.Opcode]
        Create2: _ClassVar[LatencyThresholdOverride.Opcode]
        Reconfig: _ClassVar[LatencyThresholdOverride.Opcode]
        CheckWatches: _ClassVar[LatencyThresholdOverride.Opcode]
        RemoveWatches: _ClassVar[LatencyThresholdOverride.Opcode]
        CreateContainer: _ClassVar[LatencyThresholdOverride.Opcode]
        CreateTtl: _ClassVar[LatencyThresholdOverride.Opcode]
        Close: _ClassVar[LatencyThresholdOverride.Opcode]
        SetAuth: _ClassVar[LatencyThresholdOverride.Opcode]
        SetWatches: _ClassVar[LatencyThresholdOverride.Opcode]
        GetEphemerals: _ClassVar[LatencyThresholdOverride.Opcode]
        GetAllChildrenNumber: _ClassVar[LatencyThresholdOverride.Opcode]
        SetWatches2: _ClassVar[LatencyThresholdOverride.Opcode]
        AddWatch: _ClassVar[LatencyThresholdOverride.Opcode]
    Connect: LatencyThresholdOverride.Opcode
    Create: LatencyThresholdOverride.Opcode
    Delete: LatencyThresholdOverride.Opcode
    Exists: LatencyThresholdOverride.Opcode
    GetData: LatencyThresholdOverride.Opcode
    SetData: LatencyThresholdOverride.Opcode
    GetAcl: LatencyThresholdOverride.Opcode
    SetAcl: LatencyThresholdOverride.Opcode
    GetChildren: LatencyThresholdOverride.Opcode
    Sync: LatencyThresholdOverride.Opcode
    Ping: LatencyThresholdOverride.Opcode
    GetChildren2: LatencyThresholdOverride.Opcode
    Check: LatencyThresholdOverride.Opcode
    Multi: LatencyThresholdOverride.Opcode
    Create2: LatencyThresholdOverride.Opcode
    Reconfig: LatencyThresholdOverride.Opcode
    CheckWatches: LatencyThresholdOverride.Opcode
    RemoveWatches: LatencyThresholdOverride.Opcode
    CreateContainer: LatencyThresholdOverride.Opcode
    CreateTtl: LatencyThresholdOverride.Opcode
    Close: LatencyThresholdOverride.Opcode
    SetAuth: LatencyThresholdOverride.Opcode
    SetWatches: LatencyThresholdOverride.Opcode
    GetEphemerals: LatencyThresholdOverride.Opcode
    GetAllChildrenNumber: LatencyThresholdOverride.Opcode
    SetWatches2: LatencyThresholdOverride.Opcode
    AddWatch: LatencyThresholdOverride.Opcode
    OPCODE_FIELD_NUMBER: _ClassVar[int]
    THRESHOLD_FIELD_NUMBER: _ClassVar[int]
    opcode: LatencyThresholdOverride.Opcode
    threshold: _duration_pb2.Duration
    def __init__(self, opcode: _Optional[_Union[LatencyThresholdOverride.Opcode, str]] = ..., threshold: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ...) -> None: ...
