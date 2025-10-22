import datetime

from envoy.config.core.v3 import base_pb2 as _base_pb2
from envoy.config.core.v3 import http_uri_pb2 as _http_uri_pb2
from envoy.config.route.v3 import route_components_pb2 as _route_components_pb2
from envoy.extensions.transport_sockets.tls.v3 import secret_pb2 as _secret_pb2
from envoy.type.matcher.v3 import path_pb2 as _path_pb2
from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CookieConfig(_message.Message):
    __slots__ = ("same_site",)
    class SameSite(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DISABLED: _ClassVar[CookieConfig.SameSite]
        STRICT: _ClassVar[CookieConfig.SameSite]
        LAX: _ClassVar[CookieConfig.SameSite]
        NONE: _ClassVar[CookieConfig.SameSite]
    DISABLED: CookieConfig.SameSite
    STRICT: CookieConfig.SameSite
    LAX: CookieConfig.SameSite
    NONE: CookieConfig.SameSite
    SAME_SITE_FIELD_NUMBER: _ClassVar[int]
    same_site: CookieConfig.SameSite
    def __init__(self, same_site: _Optional[_Union[CookieConfig.SameSite, str]] = ...) -> None: ...

class CookieConfigs(_message.Message):
    __slots__ = ("bearer_token_cookie_config", "oauth_hmac_cookie_config", "oauth_expires_cookie_config", "id_token_cookie_config", "refresh_token_cookie_config", "oauth_nonce_cookie_config", "code_verifier_cookie_config")
    BEARER_TOKEN_COOKIE_CONFIG_FIELD_NUMBER: _ClassVar[int]
    OAUTH_HMAC_COOKIE_CONFIG_FIELD_NUMBER: _ClassVar[int]
    OAUTH_EXPIRES_COOKIE_CONFIG_FIELD_NUMBER: _ClassVar[int]
    ID_TOKEN_COOKIE_CONFIG_FIELD_NUMBER: _ClassVar[int]
    REFRESH_TOKEN_COOKIE_CONFIG_FIELD_NUMBER: _ClassVar[int]
    OAUTH_NONCE_COOKIE_CONFIG_FIELD_NUMBER: _ClassVar[int]
    CODE_VERIFIER_COOKIE_CONFIG_FIELD_NUMBER: _ClassVar[int]
    bearer_token_cookie_config: CookieConfig
    oauth_hmac_cookie_config: CookieConfig
    oauth_expires_cookie_config: CookieConfig
    id_token_cookie_config: CookieConfig
    refresh_token_cookie_config: CookieConfig
    oauth_nonce_cookie_config: CookieConfig
    code_verifier_cookie_config: CookieConfig
    def __init__(self, bearer_token_cookie_config: _Optional[_Union[CookieConfig, _Mapping]] = ..., oauth_hmac_cookie_config: _Optional[_Union[CookieConfig, _Mapping]] = ..., oauth_expires_cookie_config: _Optional[_Union[CookieConfig, _Mapping]] = ..., id_token_cookie_config: _Optional[_Union[CookieConfig, _Mapping]] = ..., refresh_token_cookie_config: _Optional[_Union[CookieConfig, _Mapping]] = ..., oauth_nonce_cookie_config: _Optional[_Union[CookieConfig, _Mapping]] = ..., code_verifier_cookie_config: _Optional[_Union[CookieConfig, _Mapping]] = ...) -> None: ...

class OAuth2Credentials(_message.Message):
    __slots__ = ("client_id", "token_secret", "hmac_secret", "cookie_names", "cookie_domain")
    class CookieNames(_message.Message):
        __slots__ = ("bearer_token", "oauth_hmac", "oauth_expires", "id_token", "refresh_token", "oauth_nonce", "code_verifier")
        BEARER_TOKEN_FIELD_NUMBER: _ClassVar[int]
        OAUTH_HMAC_FIELD_NUMBER: _ClassVar[int]
        OAUTH_EXPIRES_FIELD_NUMBER: _ClassVar[int]
        ID_TOKEN_FIELD_NUMBER: _ClassVar[int]
        REFRESH_TOKEN_FIELD_NUMBER: _ClassVar[int]
        OAUTH_NONCE_FIELD_NUMBER: _ClassVar[int]
        CODE_VERIFIER_FIELD_NUMBER: _ClassVar[int]
        bearer_token: str
        oauth_hmac: str
        oauth_expires: str
        id_token: str
        refresh_token: str
        oauth_nonce: str
        code_verifier: str
        def __init__(self, bearer_token: _Optional[str] = ..., oauth_hmac: _Optional[str] = ..., oauth_expires: _Optional[str] = ..., id_token: _Optional[str] = ..., refresh_token: _Optional[str] = ..., oauth_nonce: _Optional[str] = ..., code_verifier: _Optional[str] = ...) -> None: ...
    CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    TOKEN_SECRET_FIELD_NUMBER: _ClassVar[int]
    HMAC_SECRET_FIELD_NUMBER: _ClassVar[int]
    COOKIE_NAMES_FIELD_NUMBER: _ClassVar[int]
    COOKIE_DOMAIN_FIELD_NUMBER: _ClassVar[int]
    client_id: str
    token_secret: _secret_pb2.SdsSecretConfig
    hmac_secret: _secret_pb2.SdsSecretConfig
    cookie_names: OAuth2Credentials.CookieNames
    cookie_domain: str
    def __init__(self, client_id: _Optional[str] = ..., token_secret: _Optional[_Union[_secret_pb2.SdsSecretConfig, _Mapping]] = ..., hmac_secret: _Optional[_Union[_secret_pb2.SdsSecretConfig, _Mapping]] = ..., cookie_names: _Optional[_Union[OAuth2Credentials.CookieNames, _Mapping]] = ..., cookie_domain: _Optional[str] = ...) -> None: ...

class OAuth2Config(_message.Message):
    __slots__ = ("token_endpoint", "retry_policy", "authorization_endpoint", "end_session_endpoint", "credentials", "redirect_uri", "redirect_path_matcher", "signout_path", "forward_bearer_token", "preserve_authorization_header", "pass_through_matcher", "auth_scopes", "resources", "auth_type", "use_refresh_token", "default_expires_in", "deny_redirect_matcher", "default_refresh_token_expires_in", "disable_id_token_set_cookie", "disable_access_token_set_cookie", "disable_refresh_token_set_cookie", "cookie_configs", "stat_prefix", "csrf_token_expires_in", "code_verifier_token_expires_in", "disable_token_encryption")
    class AuthType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        URL_ENCODED_BODY: _ClassVar[OAuth2Config.AuthType]
        BASIC_AUTH: _ClassVar[OAuth2Config.AuthType]
    URL_ENCODED_BODY: OAuth2Config.AuthType
    BASIC_AUTH: OAuth2Config.AuthType
    TOKEN_ENDPOINT_FIELD_NUMBER: _ClassVar[int]
    RETRY_POLICY_FIELD_NUMBER: _ClassVar[int]
    AUTHORIZATION_ENDPOINT_FIELD_NUMBER: _ClassVar[int]
    END_SESSION_ENDPOINT_FIELD_NUMBER: _ClassVar[int]
    CREDENTIALS_FIELD_NUMBER: _ClassVar[int]
    REDIRECT_URI_FIELD_NUMBER: _ClassVar[int]
    REDIRECT_PATH_MATCHER_FIELD_NUMBER: _ClassVar[int]
    SIGNOUT_PATH_FIELD_NUMBER: _ClassVar[int]
    FORWARD_BEARER_TOKEN_FIELD_NUMBER: _ClassVar[int]
    PRESERVE_AUTHORIZATION_HEADER_FIELD_NUMBER: _ClassVar[int]
    PASS_THROUGH_MATCHER_FIELD_NUMBER: _ClassVar[int]
    AUTH_SCOPES_FIELD_NUMBER: _ClassVar[int]
    RESOURCES_FIELD_NUMBER: _ClassVar[int]
    AUTH_TYPE_FIELD_NUMBER: _ClassVar[int]
    USE_REFRESH_TOKEN_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_EXPIRES_IN_FIELD_NUMBER: _ClassVar[int]
    DENY_REDIRECT_MATCHER_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_REFRESH_TOKEN_EXPIRES_IN_FIELD_NUMBER: _ClassVar[int]
    DISABLE_ID_TOKEN_SET_COOKIE_FIELD_NUMBER: _ClassVar[int]
    DISABLE_ACCESS_TOKEN_SET_COOKIE_FIELD_NUMBER: _ClassVar[int]
    DISABLE_REFRESH_TOKEN_SET_COOKIE_FIELD_NUMBER: _ClassVar[int]
    COOKIE_CONFIGS_FIELD_NUMBER: _ClassVar[int]
    STAT_PREFIX_FIELD_NUMBER: _ClassVar[int]
    CSRF_TOKEN_EXPIRES_IN_FIELD_NUMBER: _ClassVar[int]
    CODE_VERIFIER_TOKEN_EXPIRES_IN_FIELD_NUMBER: _ClassVar[int]
    DISABLE_TOKEN_ENCRYPTION_FIELD_NUMBER: _ClassVar[int]
    token_endpoint: _http_uri_pb2.HttpUri
    retry_policy: _base_pb2.RetryPolicy
    authorization_endpoint: str
    end_session_endpoint: str
    credentials: OAuth2Credentials
    redirect_uri: str
    redirect_path_matcher: _path_pb2.PathMatcher
    signout_path: _path_pb2.PathMatcher
    forward_bearer_token: bool
    preserve_authorization_header: bool
    pass_through_matcher: _containers.RepeatedCompositeFieldContainer[_route_components_pb2.HeaderMatcher]
    auth_scopes: _containers.RepeatedScalarFieldContainer[str]
    resources: _containers.RepeatedScalarFieldContainer[str]
    auth_type: OAuth2Config.AuthType
    use_refresh_token: _wrappers_pb2.BoolValue
    default_expires_in: _duration_pb2.Duration
    deny_redirect_matcher: _containers.RepeatedCompositeFieldContainer[_route_components_pb2.HeaderMatcher]
    default_refresh_token_expires_in: _duration_pb2.Duration
    disable_id_token_set_cookie: bool
    disable_access_token_set_cookie: bool
    disable_refresh_token_set_cookie: bool
    cookie_configs: CookieConfigs
    stat_prefix: str
    csrf_token_expires_in: _duration_pb2.Duration
    code_verifier_token_expires_in: _duration_pb2.Duration
    disable_token_encryption: bool
    def __init__(self, token_endpoint: _Optional[_Union[_http_uri_pb2.HttpUri, _Mapping]] = ..., retry_policy: _Optional[_Union[_base_pb2.RetryPolicy, _Mapping]] = ..., authorization_endpoint: _Optional[str] = ..., end_session_endpoint: _Optional[str] = ..., credentials: _Optional[_Union[OAuth2Credentials, _Mapping]] = ..., redirect_uri: _Optional[str] = ..., redirect_path_matcher: _Optional[_Union[_path_pb2.PathMatcher, _Mapping]] = ..., signout_path: _Optional[_Union[_path_pb2.PathMatcher, _Mapping]] = ..., forward_bearer_token: bool = ..., preserve_authorization_header: bool = ..., pass_through_matcher: _Optional[_Iterable[_Union[_route_components_pb2.HeaderMatcher, _Mapping]]] = ..., auth_scopes: _Optional[_Iterable[str]] = ..., resources: _Optional[_Iterable[str]] = ..., auth_type: _Optional[_Union[OAuth2Config.AuthType, str]] = ..., use_refresh_token: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., default_expires_in: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., deny_redirect_matcher: _Optional[_Iterable[_Union[_route_components_pb2.HeaderMatcher, _Mapping]]] = ..., default_refresh_token_expires_in: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., disable_id_token_set_cookie: bool = ..., disable_access_token_set_cookie: bool = ..., disable_refresh_token_set_cookie: bool = ..., cookie_configs: _Optional[_Union[CookieConfigs, _Mapping]] = ..., stat_prefix: _Optional[str] = ..., csrf_token_expires_in: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., code_verifier_token_expires_in: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., disable_token_encryption: bool = ...) -> None: ...

class OAuth2(_message.Message):
    __slots__ = ("config",)
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    config: OAuth2Config
    def __init__(self, config: _Optional[_Union[OAuth2Config, _Mapping]] = ...) -> None: ...
