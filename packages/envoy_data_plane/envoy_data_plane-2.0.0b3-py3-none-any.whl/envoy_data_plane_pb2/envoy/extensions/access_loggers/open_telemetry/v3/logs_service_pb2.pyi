from envoy.config.core.v3 import extension_pb2 as _extension_pb2
from envoy.extensions.access_loggers.grpc.v3 import als_pb2 as _als_pb2
from opentelemetry.proto.common.v1 import common_pb2 as _common_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class OpenTelemetryAccessLogConfig(_message.Message):
    __slots__ = ("common_config", "disable_builtin_labels", "resource_attributes", "body", "attributes", "stat_prefix", "formatters")
    COMMON_CONFIG_FIELD_NUMBER: _ClassVar[int]
    DISABLE_BUILTIN_LABELS_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    STAT_PREFIX_FIELD_NUMBER: _ClassVar[int]
    FORMATTERS_FIELD_NUMBER: _ClassVar[int]
    common_config: _als_pb2.CommonGrpcAccessLogConfig
    disable_builtin_labels: bool
    resource_attributes: _common_pb2.KeyValueList
    body: _common_pb2.AnyValue
    attributes: _common_pb2.KeyValueList
    stat_prefix: str
    formatters: _containers.RepeatedCompositeFieldContainer[_extension_pb2.TypedExtensionConfig]
    def __init__(self, common_config: _Optional[_Union[_als_pb2.CommonGrpcAccessLogConfig, _Mapping]] = ..., disable_builtin_labels: bool = ..., resource_attributes: _Optional[_Union[_common_pb2.KeyValueList, _Mapping]] = ..., body: _Optional[_Union[_common_pb2.AnyValue, _Mapping]] = ..., attributes: _Optional[_Union[_common_pb2.KeyValueList, _Mapping]] = ..., stat_prefix: _Optional[str] = ..., formatters: _Optional[_Iterable[_Union[_extension_pb2.TypedExtensionConfig, _Mapping]]] = ...) -> None: ...
