from envoy.config.core.v3 import http_service_pb2 as _http_service_pb2
from udpa.annotations import status_pb2 as _status_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DynatraceSamplerConfig(_message.Message):
    __slots__ = ("tenant", "cluster_id", "http_service", "root_spans_per_minute")
    TENANT_FIELD_NUMBER: _ClassVar[int]
    CLUSTER_ID_FIELD_NUMBER: _ClassVar[int]
    HTTP_SERVICE_FIELD_NUMBER: _ClassVar[int]
    ROOT_SPANS_PER_MINUTE_FIELD_NUMBER: _ClassVar[int]
    tenant: str
    cluster_id: int
    http_service: _http_service_pb2.HttpService
    root_spans_per_minute: int
    def __init__(self, tenant: _Optional[str] = ..., cluster_id: _Optional[int] = ..., http_service: _Optional[_Union[_http_service_pb2.HttpService, _Mapping]] = ..., root_spans_per_minute: _Optional[int] = ...) -> None: ...
