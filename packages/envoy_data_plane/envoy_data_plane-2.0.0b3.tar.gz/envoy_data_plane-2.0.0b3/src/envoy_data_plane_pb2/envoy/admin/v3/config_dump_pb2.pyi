import datetime

from envoy.admin.v3 import config_dump_shared_pb2 as _config_dump_shared_pb2
from envoy.config.bootstrap.v3 import bootstrap_pb2 as _bootstrap_pb2
from google.protobuf import any_pb2 as _any_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from udpa.annotations import status_pb2 as _status_pb2
from udpa.annotations import versioning_pb2 as _versioning_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ConfigDump(_message.Message):
    __slots__ = ("configs",)
    CONFIGS_FIELD_NUMBER: _ClassVar[int]
    configs: _containers.RepeatedCompositeFieldContainer[_any_pb2.Any]
    def __init__(self, configs: _Optional[_Iterable[_Union[_any_pb2.Any, _Mapping]]] = ...) -> None: ...

class BootstrapConfigDump(_message.Message):
    __slots__ = ("bootstrap", "last_updated")
    BOOTSTRAP_FIELD_NUMBER: _ClassVar[int]
    LAST_UPDATED_FIELD_NUMBER: _ClassVar[int]
    bootstrap: _bootstrap_pb2.Bootstrap
    last_updated: _timestamp_pb2.Timestamp
    def __init__(self, bootstrap: _Optional[_Union[_bootstrap_pb2.Bootstrap, _Mapping]] = ..., last_updated: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class SecretsConfigDump(_message.Message):
    __slots__ = ("static_secrets", "dynamic_active_secrets", "dynamic_warming_secrets")
    class DynamicSecret(_message.Message):
        __slots__ = ("name", "version_info", "last_updated", "secret", "error_state", "client_status")
        NAME_FIELD_NUMBER: _ClassVar[int]
        VERSION_INFO_FIELD_NUMBER: _ClassVar[int]
        LAST_UPDATED_FIELD_NUMBER: _ClassVar[int]
        SECRET_FIELD_NUMBER: _ClassVar[int]
        ERROR_STATE_FIELD_NUMBER: _ClassVar[int]
        CLIENT_STATUS_FIELD_NUMBER: _ClassVar[int]
        name: str
        version_info: str
        last_updated: _timestamp_pb2.Timestamp
        secret: _any_pb2.Any
        error_state: _config_dump_shared_pb2.UpdateFailureState
        client_status: _config_dump_shared_pb2.ClientResourceStatus
        def __init__(self, name: _Optional[str] = ..., version_info: _Optional[str] = ..., last_updated: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., secret: _Optional[_Union[_any_pb2.Any, _Mapping]] = ..., error_state: _Optional[_Union[_config_dump_shared_pb2.UpdateFailureState, _Mapping]] = ..., client_status: _Optional[_Union[_config_dump_shared_pb2.ClientResourceStatus, str]] = ...) -> None: ...
    class StaticSecret(_message.Message):
        __slots__ = ("name", "last_updated", "secret")
        NAME_FIELD_NUMBER: _ClassVar[int]
        LAST_UPDATED_FIELD_NUMBER: _ClassVar[int]
        SECRET_FIELD_NUMBER: _ClassVar[int]
        name: str
        last_updated: _timestamp_pb2.Timestamp
        secret: _any_pb2.Any
        def __init__(self, name: _Optional[str] = ..., last_updated: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., secret: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...
    STATIC_SECRETS_FIELD_NUMBER: _ClassVar[int]
    DYNAMIC_ACTIVE_SECRETS_FIELD_NUMBER: _ClassVar[int]
    DYNAMIC_WARMING_SECRETS_FIELD_NUMBER: _ClassVar[int]
    static_secrets: _containers.RepeatedCompositeFieldContainer[SecretsConfigDump.StaticSecret]
    dynamic_active_secrets: _containers.RepeatedCompositeFieldContainer[SecretsConfigDump.DynamicSecret]
    dynamic_warming_secrets: _containers.RepeatedCompositeFieldContainer[SecretsConfigDump.DynamicSecret]
    def __init__(self, static_secrets: _Optional[_Iterable[_Union[SecretsConfigDump.StaticSecret, _Mapping]]] = ..., dynamic_active_secrets: _Optional[_Iterable[_Union[SecretsConfigDump.DynamicSecret, _Mapping]]] = ..., dynamic_warming_secrets: _Optional[_Iterable[_Union[SecretsConfigDump.DynamicSecret, _Mapping]]] = ...) -> None: ...
