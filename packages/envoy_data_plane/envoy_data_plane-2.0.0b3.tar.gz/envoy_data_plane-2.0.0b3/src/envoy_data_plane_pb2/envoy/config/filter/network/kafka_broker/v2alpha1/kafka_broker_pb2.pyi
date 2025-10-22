from udpa.annotations import migrate_pb2 as _migrate_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class KafkaBroker(_message.Message):
    __slots__ = ("stat_prefix", "force_response_rewrite", "id_based_broker_address_rewrite_spec", "api_keys_allowed", "api_keys_denied")
    STAT_PREFIX_FIELD_NUMBER: _ClassVar[int]
    FORCE_RESPONSE_REWRITE_FIELD_NUMBER: _ClassVar[int]
    ID_BASED_BROKER_ADDRESS_REWRITE_SPEC_FIELD_NUMBER: _ClassVar[int]
    API_KEYS_ALLOWED_FIELD_NUMBER: _ClassVar[int]
    API_KEYS_DENIED_FIELD_NUMBER: _ClassVar[int]
    stat_prefix: str
    force_response_rewrite: bool
    id_based_broker_address_rewrite_spec: IdBasedBrokerRewriteSpec
    api_keys_allowed: _containers.RepeatedScalarFieldContainer[int]
    api_keys_denied: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, stat_prefix: _Optional[str] = ..., force_response_rewrite: bool = ..., id_based_broker_address_rewrite_spec: _Optional[_Union[IdBasedBrokerRewriteSpec, _Mapping]] = ..., api_keys_allowed: _Optional[_Iterable[int]] = ..., api_keys_denied: _Optional[_Iterable[int]] = ...) -> None: ...

class IdBasedBrokerRewriteSpec(_message.Message):
    __slots__ = ("rules",)
    RULES_FIELD_NUMBER: _ClassVar[int]
    rules: _containers.RepeatedCompositeFieldContainer[IdBasedBrokerRewriteRule]
    def __init__(self, rules: _Optional[_Iterable[_Union[IdBasedBrokerRewriteRule, _Mapping]]] = ...) -> None: ...

class IdBasedBrokerRewriteRule(_message.Message):
    __slots__ = ("id", "host", "port")
    ID_FIELD_NUMBER: _ClassVar[int]
    HOST_FIELD_NUMBER: _ClassVar[int]
    PORT_FIELD_NUMBER: _ClassVar[int]
    id: int
    host: str
    port: int
    def __init__(self, id: _Optional[int] = ..., host: _Optional[str] = ..., port: _Optional[int] = ...) -> None: ...
