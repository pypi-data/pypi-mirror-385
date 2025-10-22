import datetime

from envoy.config.core.v3 import http_uri_pb2 as _http_uri_pb2
from envoy.extensions.transport_sockets.tls.v3 import secret_pb2 as _secret_pb2
from google.protobuf import duration_pb2 as _duration_pb2
from xds.annotations.v3 import status_pb2 as _status_pb2
from udpa.annotations import status_pb2 as _status_pb2_1
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class OAuth2(_message.Message):
    __slots__ = ("token_endpoint", "scopes", "client_credentials", "token_fetch_retry_interval")
    class AuthType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        BASIC_AUTH: _ClassVar[OAuth2.AuthType]
        URL_ENCODED_BODY: _ClassVar[OAuth2.AuthType]
    BASIC_AUTH: OAuth2.AuthType
    URL_ENCODED_BODY: OAuth2.AuthType
    class ClientCredentials(_message.Message):
        __slots__ = ("client_id", "client_secret", "auth_type")
        CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
        CLIENT_SECRET_FIELD_NUMBER: _ClassVar[int]
        AUTH_TYPE_FIELD_NUMBER: _ClassVar[int]
        client_id: str
        client_secret: _secret_pb2.SdsSecretConfig
        auth_type: OAuth2.AuthType
        def __init__(self, client_id: _Optional[str] = ..., client_secret: _Optional[_Union[_secret_pb2.SdsSecretConfig, _Mapping]] = ..., auth_type: _Optional[_Union[OAuth2.AuthType, str]] = ...) -> None: ...
    TOKEN_ENDPOINT_FIELD_NUMBER: _ClassVar[int]
    SCOPES_FIELD_NUMBER: _ClassVar[int]
    CLIENT_CREDENTIALS_FIELD_NUMBER: _ClassVar[int]
    TOKEN_FETCH_RETRY_INTERVAL_FIELD_NUMBER: _ClassVar[int]
    token_endpoint: _http_uri_pb2.HttpUri
    scopes: _containers.RepeatedScalarFieldContainer[str]
    client_credentials: OAuth2.ClientCredentials
    token_fetch_retry_interval: _duration_pb2.Duration
    def __init__(self, token_endpoint: _Optional[_Union[_http_uri_pb2.HttpUri, _Mapping]] = ..., scopes: _Optional[_Iterable[str]] = ..., client_credentials: _Optional[_Union[OAuth2.ClientCredentials, _Mapping]] = ..., token_fetch_retry_interval: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ...) -> None: ...
