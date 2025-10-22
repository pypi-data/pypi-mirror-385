import datetime

from envoy.api.v2.auth import common_pb2 as _common_pb2
from envoy.api.v2.auth import secret_pb2 as _secret_pb2
from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from udpa.annotations import migrate_pb2 as _migrate_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class UpstreamTlsContext(_message.Message):
    __slots__ = ("common_tls_context", "sni", "allow_renegotiation", "max_session_keys")
    COMMON_TLS_CONTEXT_FIELD_NUMBER: _ClassVar[int]
    SNI_FIELD_NUMBER: _ClassVar[int]
    ALLOW_RENEGOTIATION_FIELD_NUMBER: _ClassVar[int]
    MAX_SESSION_KEYS_FIELD_NUMBER: _ClassVar[int]
    common_tls_context: CommonTlsContext
    sni: str
    allow_renegotiation: bool
    max_session_keys: _wrappers_pb2.UInt32Value
    def __init__(self, common_tls_context: _Optional[_Union[CommonTlsContext, _Mapping]] = ..., sni: _Optional[str] = ..., allow_renegotiation: bool = ..., max_session_keys: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ...) -> None: ...

class DownstreamTlsContext(_message.Message):
    __slots__ = ("common_tls_context", "require_client_certificate", "require_sni", "session_ticket_keys", "session_ticket_keys_sds_secret_config", "disable_stateless_session_resumption", "session_timeout")
    COMMON_TLS_CONTEXT_FIELD_NUMBER: _ClassVar[int]
    REQUIRE_CLIENT_CERTIFICATE_FIELD_NUMBER: _ClassVar[int]
    REQUIRE_SNI_FIELD_NUMBER: _ClassVar[int]
    SESSION_TICKET_KEYS_FIELD_NUMBER: _ClassVar[int]
    SESSION_TICKET_KEYS_SDS_SECRET_CONFIG_FIELD_NUMBER: _ClassVar[int]
    DISABLE_STATELESS_SESSION_RESUMPTION_FIELD_NUMBER: _ClassVar[int]
    SESSION_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    common_tls_context: CommonTlsContext
    require_client_certificate: _wrappers_pb2.BoolValue
    require_sni: _wrappers_pb2.BoolValue
    session_ticket_keys: _common_pb2.TlsSessionTicketKeys
    session_ticket_keys_sds_secret_config: _secret_pb2.SdsSecretConfig
    disable_stateless_session_resumption: bool
    session_timeout: _duration_pb2.Duration
    def __init__(self, common_tls_context: _Optional[_Union[CommonTlsContext, _Mapping]] = ..., require_client_certificate: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., require_sni: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., session_ticket_keys: _Optional[_Union[_common_pb2.TlsSessionTicketKeys, _Mapping]] = ..., session_ticket_keys_sds_secret_config: _Optional[_Union[_secret_pb2.SdsSecretConfig, _Mapping]] = ..., disable_stateless_session_resumption: bool = ..., session_timeout: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ...) -> None: ...

class CommonTlsContext(_message.Message):
    __slots__ = ("tls_params", "tls_certificates", "tls_certificate_sds_secret_configs", "validation_context", "validation_context_sds_secret_config", "combined_validation_context", "alpn_protocols")
    class CombinedCertificateValidationContext(_message.Message):
        __slots__ = ("default_validation_context", "validation_context_sds_secret_config")
        DEFAULT_VALIDATION_CONTEXT_FIELD_NUMBER: _ClassVar[int]
        VALIDATION_CONTEXT_SDS_SECRET_CONFIG_FIELD_NUMBER: _ClassVar[int]
        default_validation_context: _common_pb2.CertificateValidationContext
        validation_context_sds_secret_config: _secret_pb2.SdsSecretConfig
        def __init__(self, default_validation_context: _Optional[_Union[_common_pb2.CertificateValidationContext, _Mapping]] = ..., validation_context_sds_secret_config: _Optional[_Union[_secret_pb2.SdsSecretConfig, _Mapping]] = ...) -> None: ...
    TLS_PARAMS_FIELD_NUMBER: _ClassVar[int]
    TLS_CERTIFICATES_FIELD_NUMBER: _ClassVar[int]
    TLS_CERTIFICATE_SDS_SECRET_CONFIGS_FIELD_NUMBER: _ClassVar[int]
    VALIDATION_CONTEXT_FIELD_NUMBER: _ClassVar[int]
    VALIDATION_CONTEXT_SDS_SECRET_CONFIG_FIELD_NUMBER: _ClassVar[int]
    COMBINED_VALIDATION_CONTEXT_FIELD_NUMBER: _ClassVar[int]
    ALPN_PROTOCOLS_FIELD_NUMBER: _ClassVar[int]
    tls_params: _common_pb2.TlsParameters
    tls_certificates: _containers.RepeatedCompositeFieldContainer[_common_pb2.TlsCertificate]
    tls_certificate_sds_secret_configs: _containers.RepeatedCompositeFieldContainer[_secret_pb2.SdsSecretConfig]
    validation_context: _common_pb2.CertificateValidationContext
    validation_context_sds_secret_config: _secret_pb2.SdsSecretConfig
    combined_validation_context: CommonTlsContext.CombinedCertificateValidationContext
    alpn_protocols: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, tls_params: _Optional[_Union[_common_pb2.TlsParameters, _Mapping]] = ..., tls_certificates: _Optional[_Iterable[_Union[_common_pb2.TlsCertificate, _Mapping]]] = ..., tls_certificate_sds_secret_configs: _Optional[_Iterable[_Union[_secret_pb2.SdsSecretConfig, _Mapping]]] = ..., validation_context: _Optional[_Union[_common_pb2.CertificateValidationContext, _Mapping]] = ..., validation_context_sds_secret_config: _Optional[_Union[_secret_pb2.SdsSecretConfig, _Mapping]] = ..., combined_validation_context: _Optional[_Union[CommonTlsContext.CombinedCertificateValidationContext, _Mapping]] = ..., alpn_protocols: _Optional[_Iterable[str]] = ...) -> None: ...
