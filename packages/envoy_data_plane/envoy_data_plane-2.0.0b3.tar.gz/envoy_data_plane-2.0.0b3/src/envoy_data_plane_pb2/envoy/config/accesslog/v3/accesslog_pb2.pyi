from envoy.config.core.v3 import base_pb2 as _base_pb2
from envoy.config.route.v3 import route_components_pb2 as _route_components_pb2
from envoy.data.accesslog.v3 import accesslog_pb2 as _accesslog_pb2
from envoy.type.matcher.v3 import metadata_pb2 as _metadata_pb2
from envoy.type.v3 import percent_pb2 as _percent_pb2
from google.protobuf import any_pb2 as _any_pb2
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

class AccessLog(_message.Message):
    __slots__ = ("name", "filter", "typed_config")
    NAME_FIELD_NUMBER: _ClassVar[int]
    FILTER_FIELD_NUMBER: _ClassVar[int]
    TYPED_CONFIG_FIELD_NUMBER: _ClassVar[int]
    name: str
    filter: AccessLogFilter
    typed_config: _any_pb2.Any
    def __init__(self, name: _Optional[str] = ..., filter: _Optional[_Union[AccessLogFilter, _Mapping]] = ..., typed_config: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...

class AccessLogFilter(_message.Message):
    __slots__ = ("status_code_filter", "duration_filter", "not_health_check_filter", "traceable_filter", "runtime_filter", "and_filter", "or_filter", "header_filter", "response_flag_filter", "grpc_status_filter", "extension_filter", "metadata_filter", "log_type_filter")
    STATUS_CODE_FILTER_FIELD_NUMBER: _ClassVar[int]
    DURATION_FILTER_FIELD_NUMBER: _ClassVar[int]
    NOT_HEALTH_CHECK_FILTER_FIELD_NUMBER: _ClassVar[int]
    TRACEABLE_FILTER_FIELD_NUMBER: _ClassVar[int]
    RUNTIME_FILTER_FIELD_NUMBER: _ClassVar[int]
    AND_FILTER_FIELD_NUMBER: _ClassVar[int]
    OR_FILTER_FIELD_NUMBER: _ClassVar[int]
    HEADER_FILTER_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_FLAG_FILTER_FIELD_NUMBER: _ClassVar[int]
    GRPC_STATUS_FILTER_FIELD_NUMBER: _ClassVar[int]
    EXTENSION_FILTER_FIELD_NUMBER: _ClassVar[int]
    METADATA_FILTER_FIELD_NUMBER: _ClassVar[int]
    LOG_TYPE_FILTER_FIELD_NUMBER: _ClassVar[int]
    status_code_filter: StatusCodeFilter
    duration_filter: DurationFilter
    not_health_check_filter: NotHealthCheckFilter
    traceable_filter: TraceableFilter
    runtime_filter: RuntimeFilter
    and_filter: AndFilter
    or_filter: OrFilter
    header_filter: HeaderFilter
    response_flag_filter: ResponseFlagFilter
    grpc_status_filter: GrpcStatusFilter
    extension_filter: ExtensionFilter
    metadata_filter: MetadataFilter
    log_type_filter: LogTypeFilter
    def __init__(self, status_code_filter: _Optional[_Union[StatusCodeFilter, _Mapping]] = ..., duration_filter: _Optional[_Union[DurationFilter, _Mapping]] = ..., not_health_check_filter: _Optional[_Union[NotHealthCheckFilter, _Mapping]] = ..., traceable_filter: _Optional[_Union[TraceableFilter, _Mapping]] = ..., runtime_filter: _Optional[_Union[RuntimeFilter, _Mapping]] = ..., and_filter: _Optional[_Union[AndFilter, _Mapping]] = ..., or_filter: _Optional[_Union[OrFilter, _Mapping]] = ..., header_filter: _Optional[_Union[HeaderFilter, _Mapping]] = ..., response_flag_filter: _Optional[_Union[ResponseFlagFilter, _Mapping]] = ..., grpc_status_filter: _Optional[_Union[GrpcStatusFilter, _Mapping]] = ..., extension_filter: _Optional[_Union[ExtensionFilter, _Mapping]] = ..., metadata_filter: _Optional[_Union[MetadataFilter, _Mapping]] = ..., log_type_filter: _Optional[_Union[LogTypeFilter, _Mapping]] = ...) -> None: ...

class ComparisonFilter(_message.Message):
    __slots__ = ("op", "value")
    class Op(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        EQ: _ClassVar[ComparisonFilter.Op]
        GE: _ClassVar[ComparisonFilter.Op]
        LE: _ClassVar[ComparisonFilter.Op]
    EQ: ComparisonFilter.Op
    GE: ComparisonFilter.Op
    LE: ComparisonFilter.Op
    OP_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    op: ComparisonFilter.Op
    value: _base_pb2.RuntimeUInt32
    def __init__(self, op: _Optional[_Union[ComparisonFilter.Op, str]] = ..., value: _Optional[_Union[_base_pb2.RuntimeUInt32, _Mapping]] = ...) -> None: ...

class StatusCodeFilter(_message.Message):
    __slots__ = ("comparison",)
    COMPARISON_FIELD_NUMBER: _ClassVar[int]
    comparison: ComparisonFilter
    def __init__(self, comparison: _Optional[_Union[ComparisonFilter, _Mapping]] = ...) -> None: ...

class DurationFilter(_message.Message):
    __slots__ = ("comparison",)
    COMPARISON_FIELD_NUMBER: _ClassVar[int]
    comparison: ComparisonFilter
    def __init__(self, comparison: _Optional[_Union[ComparisonFilter, _Mapping]] = ...) -> None: ...

class NotHealthCheckFilter(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class TraceableFilter(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class RuntimeFilter(_message.Message):
    __slots__ = ("runtime_key", "percent_sampled", "use_independent_randomness")
    RUNTIME_KEY_FIELD_NUMBER: _ClassVar[int]
    PERCENT_SAMPLED_FIELD_NUMBER: _ClassVar[int]
    USE_INDEPENDENT_RANDOMNESS_FIELD_NUMBER: _ClassVar[int]
    runtime_key: str
    percent_sampled: _percent_pb2.FractionalPercent
    use_independent_randomness: bool
    def __init__(self, runtime_key: _Optional[str] = ..., percent_sampled: _Optional[_Union[_percent_pb2.FractionalPercent, _Mapping]] = ..., use_independent_randomness: bool = ...) -> None: ...

class AndFilter(_message.Message):
    __slots__ = ("filters",)
    FILTERS_FIELD_NUMBER: _ClassVar[int]
    filters: _containers.RepeatedCompositeFieldContainer[AccessLogFilter]
    def __init__(self, filters: _Optional[_Iterable[_Union[AccessLogFilter, _Mapping]]] = ...) -> None: ...

class OrFilter(_message.Message):
    __slots__ = ("filters",)
    FILTERS_FIELD_NUMBER: _ClassVar[int]
    filters: _containers.RepeatedCompositeFieldContainer[AccessLogFilter]
    def __init__(self, filters: _Optional[_Iterable[_Union[AccessLogFilter, _Mapping]]] = ...) -> None: ...

class HeaderFilter(_message.Message):
    __slots__ = ("header",)
    HEADER_FIELD_NUMBER: _ClassVar[int]
    header: _route_components_pb2.HeaderMatcher
    def __init__(self, header: _Optional[_Union[_route_components_pb2.HeaderMatcher, _Mapping]] = ...) -> None: ...

class ResponseFlagFilter(_message.Message):
    __slots__ = ("flags",)
    FLAGS_FIELD_NUMBER: _ClassVar[int]
    flags: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, flags: _Optional[_Iterable[str]] = ...) -> None: ...

class GrpcStatusFilter(_message.Message):
    __slots__ = ("statuses", "exclude")
    class Status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        OK: _ClassVar[GrpcStatusFilter.Status]
        CANCELED: _ClassVar[GrpcStatusFilter.Status]
        UNKNOWN: _ClassVar[GrpcStatusFilter.Status]
        INVALID_ARGUMENT: _ClassVar[GrpcStatusFilter.Status]
        DEADLINE_EXCEEDED: _ClassVar[GrpcStatusFilter.Status]
        NOT_FOUND: _ClassVar[GrpcStatusFilter.Status]
        ALREADY_EXISTS: _ClassVar[GrpcStatusFilter.Status]
        PERMISSION_DENIED: _ClassVar[GrpcStatusFilter.Status]
        RESOURCE_EXHAUSTED: _ClassVar[GrpcStatusFilter.Status]
        FAILED_PRECONDITION: _ClassVar[GrpcStatusFilter.Status]
        ABORTED: _ClassVar[GrpcStatusFilter.Status]
        OUT_OF_RANGE: _ClassVar[GrpcStatusFilter.Status]
        UNIMPLEMENTED: _ClassVar[GrpcStatusFilter.Status]
        INTERNAL: _ClassVar[GrpcStatusFilter.Status]
        UNAVAILABLE: _ClassVar[GrpcStatusFilter.Status]
        DATA_LOSS: _ClassVar[GrpcStatusFilter.Status]
        UNAUTHENTICATED: _ClassVar[GrpcStatusFilter.Status]
    OK: GrpcStatusFilter.Status
    CANCELED: GrpcStatusFilter.Status
    UNKNOWN: GrpcStatusFilter.Status
    INVALID_ARGUMENT: GrpcStatusFilter.Status
    DEADLINE_EXCEEDED: GrpcStatusFilter.Status
    NOT_FOUND: GrpcStatusFilter.Status
    ALREADY_EXISTS: GrpcStatusFilter.Status
    PERMISSION_DENIED: GrpcStatusFilter.Status
    RESOURCE_EXHAUSTED: GrpcStatusFilter.Status
    FAILED_PRECONDITION: GrpcStatusFilter.Status
    ABORTED: GrpcStatusFilter.Status
    OUT_OF_RANGE: GrpcStatusFilter.Status
    UNIMPLEMENTED: GrpcStatusFilter.Status
    INTERNAL: GrpcStatusFilter.Status
    UNAVAILABLE: GrpcStatusFilter.Status
    DATA_LOSS: GrpcStatusFilter.Status
    UNAUTHENTICATED: GrpcStatusFilter.Status
    STATUSES_FIELD_NUMBER: _ClassVar[int]
    EXCLUDE_FIELD_NUMBER: _ClassVar[int]
    statuses: _containers.RepeatedScalarFieldContainer[GrpcStatusFilter.Status]
    exclude: bool
    def __init__(self, statuses: _Optional[_Iterable[_Union[GrpcStatusFilter.Status, str]]] = ..., exclude: bool = ...) -> None: ...

class MetadataFilter(_message.Message):
    __slots__ = ("matcher", "match_if_key_not_found")
    MATCHER_FIELD_NUMBER: _ClassVar[int]
    MATCH_IF_KEY_NOT_FOUND_FIELD_NUMBER: _ClassVar[int]
    matcher: _metadata_pb2.MetadataMatcher
    match_if_key_not_found: _wrappers_pb2.BoolValue
    def __init__(self, matcher: _Optional[_Union[_metadata_pb2.MetadataMatcher, _Mapping]] = ..., match_if_key_not_found: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ...) -> None: ...

class LogTypeFilter(_message.Message):
    __slots__ = ("types", "exclude")
    TYPES_FIELD_NUMBER: _ClassVar[int]
    EXCLUDE_FIELD_NUMBER: _ClassVar[int]
    types: _containers.RepeatedScalarFieldContainer[_accesslog_pb2.AccessLogType]
    exclude: bool
    def __init__(self, types: _Optional[_Iterable[_Union[_accesslog_pb2.AccessLogType, str]]] = ..., exclude: bool = ...) -> None: ...

class ExtensionFilter(_message.Message):
    __slots__ = ("name", "typed_config")
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPED_CONFIG_FIELD_NUMBER: _ClassVar[int]
    name: str
    typed_config: _any_pb2.Any
    def __init__(self, name: _Optional[str] = ..., typed_config: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...
