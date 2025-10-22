from envoy.api.v2.core import address_pb2 as _address_pb2
from envoy.api.v2.core import backoff_pb2 as _backoff_pb2
from envoy.api.v2.core import http_uri_pb2 as _http_uri_pb2
from envoy.type import percent_pb2 as _percent_pb2
from envoy.type import semantic_version_pb2 as _semantic_version_pb2
from google.protobuf import any_pb2 as _any_pb2
from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from udpa.annotations import migrate_pb2 as _migrate_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from envoy.api.v2.core import socket_option_pb2 as _socket_option_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union
from envoy.api.v2.core.socket_option_pb2 import SocketOption as SocketOption

DESCRIPTOR: _descriptor.FileDescriptor

class RoutingPriority(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    DEFAULT: _ClassVar[RoutingPriority]
    HIGH: _ClassVar[RoutingPriority]

class RequestMethod(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    METHOD_UNSPECIFIED: _ClassVar[RequestMethod]
    GET: _ClassVar[RequestMethod]
    HEAD: _ClassVar[RequestMethod]
    POST: _ClassVar[RequestMethod]
    PUT: _ClassVar[RequestMethod]
    DELETE: _ClassVar[RequestMethod]
    CONNECT: _ClassVar[RequestMethod]
    OPTIONS: _ClassVar[RequestMethod]
    TRACE: _ClassVar[RequestMethod]
    PATCH: _ClassVar[RequestMethod]

class TrafficDirection(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNSPECIFIED: _ClassVar[TrafficDirection]
    INBOUND: _ClassVar[TrafficDirection]
    OUTBOUND: _ClassVar[TrafficDirection]
DEFAULT: RoutingPriority
HIGH: RoutingPriority
METHOD_UNSPECIFIED: RequestMethod
GET: RequestMethod
HEAD: RequestMethod
POST: RequestMethod
PUT: RequestMethod
DELETE: RequestMethod
CONNECT: RequestMethod
OPTIONS: RequestMethod
TRACE: RequestMethod
PATCH: RequestMethod
UNSPECIFIED: TrafficDirection
INBOUND: TrafficDirection
OUTBOUND: TrafficDirection

class Locality(_message.Message):
    __slots__ = ("region", "zone", "sub_zone")
    REGION_FIELD_NUMBER: _ClassVar[int]
    ZONE_FIELD_NUMBER: _ClassVar[int]
    SUB_ZONE_FIELD_NUMBER: _ClassVar[int]
    region: str
    zone: str
    sub_zone: str
    def __init__(self, region: _Optional[str] = ..., zone: _Optional[str] = ..., sub_zone: _Optional[str] = ...) -> None: ...

class BuildVersion(_message.Message):
    __slots__ = ("version", "metadata")
    VERSION_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    version: _semantic_version_pb2.SemanticVersion
    metadata: _struct_pb2.Struct
    def __init__(self, version: _Optional[_Union[_semantic_version_pb2.SemanticVersion, _Mapping]] = ..., metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class Extension(_message.Message):
    __slots__ = ("name", "category", "type_descriptor", "version", "disabled")
    NAME_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    TYPE_DESCRIPTOR_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    DISABLED_FIELD_NUMBER: _ClassVar[int]
    name: str
    category: str
    type_descriptor: str
    version: BuildVersion
    disabled: bool
    def __init__(self, name: _Optional[str] = ..., category: _Optional[str] = ..., type_descriptor: _Optional[str] = ..., version: _Optional[_Union[BuildVersion, _Mapping]] = ..., disabled: bool = ...) -> None: ...

class Node(_message.Message):
    __slots__ = ("id", "cluster", "metadata", "locality", "build_version", "user_agent_name", "user_agent_version", "user_agent_build_version", "extensions", "client_features", "listening_addresses")
    ID_FIELD_NUMBER: _ClassVar[int]
    CLUSTER_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    LOCALITY_FIELD_NUMBER: _ClassVar[int]
    BUILD_VERSION_FIELD_NUMBER: _ClassVar[int]
    USER_AGENT_NAME_FIELD_NUMBER: _ClassVar[int]
    USER_AGENT_VERSION_FIELD_NUMBER: _ClassVar[int]
    USER_AGENT_BUILD_VERSION_FIELD_NUMBER: _ClassVar[int]
    EXTENSIONS_FIELD_NUMBER: _ClassVar[int]
    CLIENT_FEATURES_FIELD_NUMBER: _ClassVar[int]
    LISTENING_ADDRESSES_FIELD_NUMBER: _ClassVar[int]
    id: str
    cluster: str
    metadata: _struct_pb2.Struct
    locality: Locality
    build_version: str
    user_agent_name: str
    user_agent_version: str
    user_agent_build_version: BuildVersion
    extensions: _containers.RepeatedCompositeFieldContainer[Extension]
    client_features: _containers.RepeatedScalarFieldContainer[str]
    listening_addresses: _containers.RepeatedCompositeFieldContainer[_address_pb2.Address]
    def __init__(self, id: _Optional[str] = ..., cluster: _Optional[str] = ..., metadata: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., locality: _Optional[_Union[Locality, _Mapping]] = ..., build_version: _Optional[str] = ..., user_agent_name: _Optional[str] = ..., user_agent_version: _Optional[str] = ..., user_agent_build_version: _Optional[_Union[BuildVersion, _Mapping]] = ..., extensions: _Optional[_Iterable[_Union[Extension, _Mapping]]] = ..., client_features: _Optional[_Iterable[str]] = ..., listening_addresses: _Optional[_Iterable[_Union[_address_pb2.Address, _Mapping]]] = ...) -> None: ...

class Metadata(_message.Message):
    __slots__ = ("filter_metadata",)
    class FilterMetadataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _struct_pb2.Struct
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...
    FILTER_METADATA_FIELD_NUMBER: _ClassVar[int]
    filter_metadata: _containers.MessageMap[str, _struct_pb2.Struct]
    def __init__(self, filter_metadata: _Optional[_Mapping[str, _struct_pb2.Struct]] = ...) -> None: ...

class RuntimeUInt32(_message.Message):
    __slots__ = ("default_value", "runtime_key")
    DEFAULT_VALUE_FIELD_NUMBER: _ClassVar[int]
    RUNTIME_KEY_FIELD_NUMBER: _ClassVar[int]
    default_value: int
    runtime_key: str
    def __init__(self, default_value: _Optional[int] = ..., runtime_key: _Optional[str] = ...) -> None: ...

class RuntimeDouble(_message.Message):
    __slots__ = ("default_value", "runtime_key")
    DEFAULT_VALUE_FIELD_NUMBER: _ClassVar[int]
    RUNTIME_KEY_FIELD_NUMBER: _ClassVar[int]
    default_value: float
    runtime_key: str
    def __init__(self, default_value: _Optional[float] = ..., runtime_key: _Optional[str] = ...) -> None: ...

class RuntimeFeatureFlag(_message.Message):
    __slots__ = ("default_value", "runtime_key")
    DEFAULT_VALUE_FIELD_NUMBER: _ClassVar[int]
    RUNTIME_KEY_FIELD_NUMBER: _ClassVar[int]
    default_value: _wrappers_pb2.BoolValue
    runtime_key: str
    def __init__(self, default_value: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., runtime_key: _Optional[str] = ...) -> None: ...

class HeaderValue(_message.Message):
    __slots__ = ("key", "value")
    KEY_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    key: str
    value: str
    def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...

class HeaderValueOption(_message.Message):
    __slots__ = ("header", "append")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    APPEND_FIELD_NUMBER: _ClassVar[int]
    header: HeaderValue
    append: _wrappers_pb2.BoolValue
    def __init__(self, header: _Optional[_Union[HeaderValue, _Mapping]] = ..., append: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ...) -> None: ...

class HeaderMap(_message.Message):
    __slots__ = ("headers",)
    HEADERS_FIELD_NUMBER: _ClassVar[int]
    headers: _containers.RepeatedCompositeFieldContainer[HeaderValue]
    def __init__(self, headers: _Optional[_Iterable[_Union[HeaderValue, _Mapping]]] = ...) -> None: ...

class DataSource(_message.Message):
    __slots__ = ("filename", "inline_bytes", "inline_string")
    FILENAME_FIELD_NUMBER: _ClassVar[int]
    INLINE_BYTES_FIELD_NUMBER: _ClassVar[int]
    INLINE_STRING_FIELD_NUMBER: _ClassVar[int]
    filename: str
    inline_bytes: bytes
    inline_string: str
    def __init__(self, filename: _Optional[str] = ..., inline_bytes: _Optional[bytes] = ..., inline_string: _Optional[str] = ...) -> None: ...

class RetryPolicy(_message.Message):
    __slots__ = ("retry_back_off", "num_retries")
    RETRY_BACK_OFF_FIELD_NUMBER: _ClassVar[int]
    NUM_RETRIES_FIELD_NUMBER: _ClassVar[int]
    retry_back_off: _backoff_pb2.BackoffStrategy
    num_retries: _wrappers_pb2.UInt32Value
    def __init__(self, retry_back_off: _Optional[_Union[_backoff_pb2.BackoffStrategy, _Mapping]] = ..., num_retries: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ...) -> None: ...

class RemoteDataSource(_message.Message):
    __slots__ = ("http_uri", "sha256", "retry_policy")
    HTTP_URI_FIELD_NUMBER: _ClassVar[int]
    SHA256_FIELD_NUMBER: _ClassVar[int]
    RETRY_POLICY_FIELD_NUMBER: _ClassVar[int]
    http_uri: _http_uri_pb2.HttpUri
    sha256: str
    retry_policy: RetryPolicy
    def __init__(self, http_uri: _Optional[_Union[_http_uri_pb2.HttpUri, _Mapping]] = ..., sha256: _Optional[str] = ..., retry_policy: _Optional[_Union[RetryPolicy, _Mapping]] = ...) -> None: ...

class AsyncDataSource(_message.Message):
    __slots__ = ("local", "remote")
    LOCAL_FIELD_NUMBER: _ClassVar[int]
    REMOTE_FIELD_NUMBER: _ClassVar[int]
    local: DataSource
    remote: RemoteDataSource
    def __init__(self, local: _Optional[_Union[DataSource, _Mapping]] = ..., remote: _Optional[_Union[RemoteDataSource, _Mapping]] = ...) -> None: ...

class TransportSocket(_message.Message):
    __slots__ = ("name", "config", "typed_config")
    NAME_FIELD_NUMBER: _ClassVar[int]
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    TYPED_CONFIG_FIELD_NUMBER: _ClassVar[int]
    name: str
    config: _struct_pb2.Struct
    typed_config: _any_pb2.Any
    def __init__(self, name: _Optional[str] = ..., config: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., typed_config: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...

class RuntimeFractionalPercent(_message.Message):
    __slots__ = ("default_value", "runtime_key")
    DEFAULT_VALUE_FIELD_NUMBER: _ClassVar[int]
    RUNTIME_KEY_FIELD_NUMBER: _ClassVar[int]
    default_value: _percent_pb2.FractionalPercent
    runtime_key: str
    def __init__(self, default_value: _Optional[_Union[_percent_pb2.FractionalPercent, _Mapping]] = ..., runtime_key: _Optional[str] = ...) -> None: ...

class ControlPlane(_message.Message):
    __slots__ = ("identifier",)
    IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    identifier: str
    def __init__(self, identifier: _Optional[str] = ...) -> None: ...
