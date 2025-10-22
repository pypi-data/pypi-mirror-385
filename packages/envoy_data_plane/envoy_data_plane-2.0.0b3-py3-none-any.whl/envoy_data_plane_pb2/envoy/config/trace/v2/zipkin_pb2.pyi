from google.protobuf import wrappers_pb2 as _wrappers_pb2
from envoy.annotations import deprecation_pb2 as _deprecation_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ZipkinConfig(_message.Message):
    __slots__ = ("collector_cluster", "collector_endpoint", "trace_id_128bit", "shared_span_context", "collector_endpoint_version")
    class CollectorEndpointVersion(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        HTTP_JSON_V1: _ClassVar[ZipkinConfig.CollectorEndpointVersion]
        HTTP_JSON: _ClassVar[ZipkinConfig.CollectorEndpointVersion]
        HTTP_PROTO: _ClassVar[ZipkinConfig.CollectorEndpointVersion]
        GRPC: _ClassVar[ZipkinConfig.CollectorEndpointVersion]
    HTTP_JSON_V1: ZipkinConfig.CollectorEndpointVersion
    HTTP_JSON: ZipkinConfig.CollectorEndpointVersion
    HTTP_PROTO: ZipkinConfig.CollectorEndpointVersion
    GRPC: ZipkinConfig.CollectorEndpointVersion
    COLLECTOR_CLUSTER_FIELD_NUMBER: _ClassVar[int]
    COLLECTOR_ENDPOINT_FIELD_NUMBER: _ClassVar[int]
    TRACE_ID_128BIT_FIELD_NUMBER: _ClassVar[int]
    SHARED_SPAN_CONTEXT_FIELD_NUMBER: _ClassVar[int]
    COLLECTOR_ENDPOINT_VERSION_FIELD_NUMBER: _ClassVar[int]
    collector_cluster: str
    collector_endpoint: str
    trace_id_128bit: bool
    shared_span_context: _wrappers_pb2.BoolValue
    collector_endpoint_version: ZipkinConfig.CollectorEndpointVersion
    def __init__(self, collector_cluster: _Optional[str] = ..., collector_endpoint: _Optional[str] = ..., trace_id_128bit: bool = ..., shared_span_context: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., collector_endpoint_version: _Optional[_Union[ZipkinConfig.CollectorEndpointVersion, str]] = ...) -> None: ...
