from envoy.config.core.v3 import config_source_pb2 as _config_source_pb2
from envoy.config.core.v3 import grpc_service_pb2 as _grpc_service_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from udpa.annotations import status_pb2 as _status_pb2
from udpa.annotations import versioning_pb2 as _versioning_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class HistogramEmitMode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SUMMARY_AND_HISTOGRAM: _ClassVar[HistogramEmitMode]
    SUMMARY: _ClassVar[HistogramEmitMode]
    HISTOGRAM: _ClassVar[HistogramEmitMode]
SUMMARY_AND_HISTOGRAM: HistogramEmitMode
SUMMARY: HistogramEmitMode
HISTOGRAM: HistogramEmitMode

class MetricsServiceConfig(_message.Message):
    __slots__ = ("grpc_service", "transport_api_version", "report_counters_as_deltas", "emit_tags_as_labels", "histogram_emit_mode")
    GRPC_SERVICE_FIELD_NUMBER: _ClassVar[int]
    TRANSPORT_API_VERSION_FIELD_NUMBER: _ClassVar[int]
    REPORT_COUNTERS_AS_DELTAS_FIELD_NUMBER: _ClassVar[int]
    EMIT_TAGS_AS_LABELS_FIELD_NUMBER: _ClassVar[int]
    HISTOGRAM_EMIT_MODE_FIELD_NUMBER: _ClassVar[int]
    grpc_service: _grpc_service_pb2.GrpcService
    transport_api_version: _config_source_pb2.ApiVersion
    report_counters_as_deltas: _wrappers_pb2.BoolValue
    emit_tags_as_labels: bool
    histogram_emit_mode: HistogramEmitMode
    def __init__(self, grpc_service: _Optional[_Union[_grpc_service_pb2.GrpcService, _Mapping]] = ..., transport_api_version: _Optional[_Union[_config_source_pb2.ApiVersion, str]] = ..., report_counters_as_deltas: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., emit_tags_as_labels: bool = ..., histogram_emit_mode: _Optional[_Union[HistogramEmitMode, str]] = ...) -> None: ...
