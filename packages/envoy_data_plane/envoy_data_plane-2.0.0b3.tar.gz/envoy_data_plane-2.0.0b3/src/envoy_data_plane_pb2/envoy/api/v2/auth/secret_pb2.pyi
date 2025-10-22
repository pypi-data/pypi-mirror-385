from envoy.api.v2.auth import common_pb2 as _common_pb2
from envoy.api.v2.core import base_pb2 as _base_pb2
from envoy.api.v2.core import socket_option_pb2 as _socket_option_pb2
from envoy.api.v2.core import config_source_pb2 as _config_source_pb2
from udpa.annotations import migrate_pb2 as _migrate_pb2
from udpa.annotations import sensitive_pb2 as _sensitive_pb2
from udpa.annotations import status_pb2 as _status_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GenericSecret(_message.Message):
    __slots__ = ("secret",)
    SECRET_FIELD_NUMBER: _ClassVar[int]
    secret: _base_pb2.DataSource
    def __init__(self, secret: _Optional[_Union[_base_pb2.DataSource, _Mapping]] = ...) -> None: ...

class SdsSecretConfig(_message.Message):
    __slots__ = ("name", "sds_config")
    NAME_FIELD_NUMBER: _ClassVar[int]
    SDS_CONFIG_FIELD_NUMBER: _ClassVar[int]
    name: str
    sds_config: _config_source_pb2.ConfigSource
    def __init__(self, name: _Optional[str] = ..., sds_config: _Optional[_Union[_config_source_pb2.ConfigSource, _Mapping]] = ...) -> None: ...

class Secret(_message.Message):
    __slots__ = ("name", "tls_certificate", "session_ticket_keys", "validation_context", "generic_secret")
    NAME_FIELD_NUMBER: _ClassVar[int]
    TLS_CERTIFICATE_FIELD_NUMBER: _ClassVar[int]
    SESSION_TICKET_KEYS_FIELD_NUMBER: _ClassVar[int]
    VALIDATION_CONTEXT_FIELD_NUMBER: _ClassVar[int]
    GENERIC_SECRET_FIELD_NUMBER: _ClassVar[int]
    name: str
    tls_certificate: _common_pb2.TlsCertificate
    session_ticket_keys: _common_pb2.TlsSessionTicketKeys
    validation_context: _common_pb2.CertificateValidationContext
    generic_secret: GenericSecret
    def __init__(self, name: _Optional[str] = ..., tls_certificate: _Optional[_Union[_common_pb2.TlsCertificate, _Mapping]] = ..., session_ticket_keys: _Optional[_Union[_common_pb2.TlsSessionTicketKeys, _Mapping]] = ..., validation_context: _Optional[_Union[_common_pb2.CertificateValidationContext, _Mapping]] = ..., generic_secret: _Optional[_Union[GenericSecret, _Mapping]] = ...) -> None: ...
