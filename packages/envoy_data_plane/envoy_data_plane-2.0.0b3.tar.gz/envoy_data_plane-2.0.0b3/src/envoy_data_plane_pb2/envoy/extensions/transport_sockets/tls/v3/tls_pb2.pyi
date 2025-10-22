import datetime

from envoy.config.core.v3 import address_pb2 as _address_pb2
from envoy.config.core.v3 import extension_pb2 as _extension_pb2
from envoy.extensions.transport_sockets.tls.v3 import common_pb2 as _common_pb2
from envoy.extensions.transport_sockets.tls.v3 import secret_pb2 as _secret_pb2
from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from envoy.annotations import deprecation_pb2 as _deprecation_pb2
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

class UpstreamTlsContext(_message.Message):
    __slots__ = ("common_tls_context", "sni", "auto_host_sni", "auto_sni_san_validation", "allow_renegotiation", "max_session_keys", "enforce_rsa_key_usage")
    COMMON_TLS_CONTEXT_FIELD_NUMBER: _ClassVar[int]
    SNI_FIELD_NUMBER: _ClassVar[int]
    AUTO_HOST_SNI_FIELD_NUMBER: _ClassVar[int]
    AUTO_SNI_SAN_VALIDATION_FIELD_NUMBER: _ClassVar[int]
    ALLOW_RENEGOTIATION_FIELD_NUMBER: _ClassVar[int]
    MAX_SESSION_KEYS_FIELD_NUMBER: _ClassVar[int]
    ENFORCE_RSA_KEY_USAGE_FIELD_NUMBER: _ClassVar[int]
    common_tls_context: CommonTlsContext
    sni: str
    auto_host_sni: bool
    auto_sni_san_validation: bool
    allow_renegotiation: bool
    max_session_keys: _wrappers_pb2.UInt32Value
    enforce_rsa_key_usage: _wrappers_pb2.BoolValue
    def __init__(self, common_tls_context: _Optional[_Union[CommonTlsContext, _Mapping]] = ..., sni: _Optional[str] = ..., auto_host_sni: bool = ..., auto_sni_san_validation: bool = ..., allow_renegotiation: bool = ..., max_session_keys: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., enforce_rsa_key_usage: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ...) -> None: ...

class DownstreamTlsContext(_message.Message):
    __slots__ = ("common_tls_context", "require_client_certificate", "require_sni", "session_ticket_keys", "session_ticket_keys_sds_secret_config", "disable_stateless_session_resumption", "disable_stateful_session_resumption", "session_timeout", "ocsp_staple_policy", "full_scan_certs_on_sni_mismatch", "prefer_client_ciphers")
    class OcspStaplePolicy(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        LENIENT_STAPLING: _ClassVar[DownstreamTlsContext.OcspStaplePolicy]
        STRICT_STAPLING: _ClassVar[DownstreamTlsContext.OcspStaplePolicy]
        MUST_STAPLE: _ClassVar[DownstreamTlsContext.OcspStaplePolicy]
    LENIENT_STAPLING: DownstreamTlsContext.OcspStaplePolicy
    STRICT_STAPLING: DownstreamTlsContext.OcspStaplePolicy
    MUST_STAPLE: DownstreamTlsContext.OcspStaplePolicy
    COMMON_TLS_CONTEXT_FIELD_NUMBER: _ClassVar[int]
    REQUIRE_CLIENT_CERTIFICATE_FIELD_NUMBER: _ClassVar[int]
    REQUIRE_SNI_FIELD_NUMBER: _ClassVar[int]
    SESSION_TICKET_KEYS_FIELD_NUMBER: _ClassVar[int]
    SESSION_TICKET_KEYS_SDS_SECRET_CONFIG_FIELD_NUMBER: _ClassVar[int]
    DISABLE_STATELESS_SESSION_RESUMPTION_FIELD_NUMBER: _ClassVar[int]
    DISABLE_STATEFUL_SESSION_RESUMPTION_FIELD_NUMBER: _ClassVar[int]
    SESSION_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    OCSP_STAPLE_POLICY_FIELD_NUMBER: _ClassVar[int]
    FULL_SCAN_CERTS_ON_SNI_MISMATCH_FIELD_NUMBER: _ClassVar[int]
    PREFER_CLIENT_CIPHERS_FIELD_NUMBER: _ClassVar[int]
    common_tls_context: CommonTlsContext
    require_client_certificate: _wrappers_pb2.BoolValue
    require_sni: _wrappers_pb2.BoolValue
    session_ticket_keys: _common_pb2.TlsSessionTicketKeys
    session_ticket_keys_sds_secret_config: _secret_pb2.SdsSecretConfig
    disable_stateless_session_resumption: bool
    disable_stateful_session_resumption: bool
    session_timeout: _duration_pb2.Duration
    ocsp_staple_policy: DownstreamTlsContext.OcspStaplePolicy
    full_scan_certs_on_sni_mismatch: _wrappers_pb2.BoolValue
    prefer_client_ciphers: bool
    def __init__(self, common_tls_context: _Optional[_Union[CommonTlsContext, _Mapping]] = ..., require_client_certificate: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., require_sni: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., session_ticket_keys: _Optional[_Union[_common_pb2.TlsSessionTicketKeys, _Mapping]] = ..., session_ticket_keys_sds_secret_config: _Optional[_Union[_secret_pb2.SdsSecretConfig, _Mapping]] = ..., disable_stateless_session_resumption: bool = ..., disable_stateful_session_resumption: bool = ..., session_timeout: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., ocsp_staple_policy: _Optional[_Union[DownstreamTlsContext.OcspStaplePolicy, str]] = ..., full_scan_certs_on_sni_mismatch: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., prefer_client_ciphers: bool = ...) -> None: ...

class TlsKeyLog(_message.Message):
    __slots__ = ("path", "local_address_range", "remote_address_range")
    PATH_FIELD_NUMBER: _ClassVar[int]
    LOCAL_ADDRESS_RANGE_FIELD_NUMBER: _ClassVar[int]
    REMOTE_ADDRESS_RANGE_FIELD_NUMBER: _ClassVar[int]
    path: str
    local_address_range: _containers.RepeatedCompositeFieldContainer[_address_pb2.CidrRange]
    remote_address_range: _containers.RepeatedCompositeFieldContainer[_address_pb2.CidrRange]
    def __init__(self, path: _Optional[str] = ..., local_address_range: _Optional[_Iterable[_Union[_address_pb2.CidrRange, _Mapping]]] = ..., remote_address_range: _Optional[_Iterable[_Union[_address_pb2.CidrRange, _Mapping]]] = ...) -> None: ...

class CommonTlsContext(_message.Message):
    __slots__ = ("tls_params", "tls_certificates", "tls_certificate_sds_secret_configs", "tls_certificate_provider_instance", "custom_tls_certificate_selector", "tls_certificate_certificate_provider", "tls_certificate_certificate_provider_instance", "validation_context", "validation_context_sds_secret_config", "combined_validation_context", "validation_context_certificate_provider", "validation_context_certificate_provider_instance", "alpn_protocols", "custom_handshaker", "key_log")
    class CertificateProvider(_message.Message):
        __slots__ = ("name", "typed_config")
        NAME_FIELD_NUMBER: _ClassVar[int]
        TYPED_CONFIG_FIELD_NUMBER: _ClassVar[int]
        name: str
        typed_config: _extension_pb2.TypedExtensionConfig
        def __init__(self, name: _Optional[str] = ..., typed_config: _Optional[_Union[_extension_pb2.TypedExtensionConfig, _Mapping]] = ...) -> None: ...
    class CertificateProviderInstance(_message.Message):
        __slots__ = ("instance_name", "certificate_name")
        INSTANCE_NAME_FIELD_NUMBER: _ClassVar[int]
        CERTIFICATE_NAME_FIELD_NUMBER: _ClassVar[int]
        instance_name: str
        certificate_name: str
        def __init__(self, instance_name: _Optional[str] = ..., certificate_name: _Optional[str] = ...) -> None: ...
    class CombinedCertificateValidationContext(_message.Message):
        __slots__ = ("default_validation_context", "validation_context_sds_secret_config", "validation_context_certificate_provider", "validation_context_certificate_provider_instance")
        DEFAULT_VALIDATION_CONTEXT_FIELD_NUMBER: _ClassVar[int]
        VALIDATION_CONTEXT_SDS_SECRET_CONFIG_FIELD_NUMBER: _ClassVar[int]
        VALIDATION_CONTEXT_CERTIFICATE_PROVIDER_FIELD_NUMBER: _ClassVar[int]
        VALIDATION_CONTEXT_CERTIFICATE_PROVIDER_INSTANCE_FIELD_NUMBER: _ClassVar[int]
        default_validation_context: _common_pb2.CertificateValidationContext
        validation_context_sds_secret_config: _secret_pb2.SdsSecretConfig
        validation_context_certificate_provider: CommonTlsContext.CertificateProvider
        validation_context_certificate_provider_instance: CommonTlsContext.CertificateProviderInstance
        def __init__(self, default_validation_context: _Optional[_Union[_common_pb2.CertificateValidationContext, _Mapping]] = ..., validation_context_sds_secret_config: _Optional[_Union[_secret_pb2.SdsSecretConfig, _Mapping]] = ..., validation_context_certificate_provider: _Optional[_Union[CommonTlsContext.CertificateProvider, _Mapping]] = ..., validation_context_certificate_provider_instance: _Optional[_Union[CommonTlsContext.CertificateProviderInstance, _Mapping]] = ...) -> None: ...
    TLS_PARAMS_FIELD_NUMBER: _ClassVar[int]
    TLS_CERTIFICATES_FIELD_NUMBER: _ClassVar[int]
    TLS_CERTIFICATE_SDS_SECRET_CONFIGS_FIELD_NUMBER: _ClassVar[int]
    TLS_CERTIFICATE_PROVIDER_INSTANCE_FIELD_NUMBER: _ClassVar[int]
    CUSTOM_TLS_CERTIFICATE_SELECTOR_FIELD_NUMBER: _ClassVar[int]
    TLS_CERTIFICATE_CERTIFICATE_PROVIDER_FIELD_NUMBER: _ClassVar[int]
    TLS_CERTIFICATE_CERTIFICATE_PROVIDER_INSTANCE_FIELD_NUMBER: _ClassVar[int]
    VALIDATION_CONTEXT_FIELD_NUMBER: _ClassVar[int]
    VALIDATION_CONTEXT_SDS_SECRET_CONFIG_FIELD_NUMBER: _ClassVar[int]
    COMBINED_VALIDATION_CONTEXT_FIELD_NUMBER: _ClassVar[int]
    VALIDATION_CONTEXT_CERTIFICATE_PROVIDER_FIELD_NUMBER: _ClassVar[int]
    VALIDATION_CONTEXT_CERTIFICATE_PROVIDER_INSTANCE_FIELD_NUMBER: _ClassVar[int]
    ALPN_PROTOCOLS_FIELD_NUMBER: _ClassVar[int]
    CUSTOM_HANDSHAKER_FIELD_NUMBER: _ClassVar[int]
    KEY_LOG_FIELD_NUMBER: _ClassVar[int]
    tls_params: _common_pb2.TlsParameters
    tls_certificates: _containers.RepeatedCompositeFieldContainer[_common_pb2.TlsCertificate]
    tls_certificate_sds_secret_configs: _containers.RepeatedCompositeFieldContainer[_secret_pb2.SdsSecretConfig]
    tls_certificate_provider_instance: _common_pb2.CertificateProviderPluginInstance
    custom_tls_certificate_selector: _extension_pb2.TypedExtensionConfig
    tls_certificate_certificate_provider: CommonTlsContext.CertificateProvider
    tls_certificate_certificate_provider_instance: CommonTlsContext.CertificateProviderInstance
    validation_context: _common_pb2.CertificateValidationContext
    validation_context_sds_secret_config: _secret_pb2.SdsSecretConfig
    combined_validation_context: CommonTlsContext.CombinedCertificateValidationContext
    validation_context_certificate_provider: CommonTlsContext.CertificateProvider
    validation_context_certificate_provider_instance: CommonTlsContext.CertificateProviderInstance
    alpn_protocols: _containers.RepeatedScalarFieldContainer[str]
    custom_handshaker: _extension_pb2.TypedExtensionConfig
    key_log: TlsKeyLog
    def __init__(self, tls_params: _Optional[_Union[_common_pb2.TlsParameters, _Mapping]] = ..., tls_certificates: _Optional[_Iterable[_Union[_common_pb2.TlsCertificate, _Mapping]]] = ..., tls_certificate_sds_secret_configs: _Optional[_Iterable[_Union[_secret_pb2.SdsSecretConfig, _Mapping]]] = ..., tls_certificate_provider_instance: _Optional[_Union[_common_pb2.CertificateProviderPluginInstance, _Mapping]] = ..., custom_tls_certificate_selector: _Optional[_Union[_extension_pb2.TypedExtensionConfig, _Mapping]] = ..., tls_certificate_certificate_provider: _Optional[_Union[CommonTlsContext.CertificateProvider, _Mapping]] = ..., tls_certificate_certificate_provider_instance: _Optional[_Union[CommonTlsContext.CertificateProviderInstance, _Mapping]] = ..., validation_context: _Optional[_Union[_common_pb2.CertificateValidationContext, _Mapping]] = ..., validation_context_sds_secret_config: _Optional[_Union[_secret_pb2.SdsSecretConfig, _Mapping]] = ..., combined_validation_context: _Optional[_Union[CommonTlsContext.CombinedCertificateValidationContext, _Mapping]] = ..., validation_context_certificate_provider: _Optional[_Union[CommonTlsContext.CertificateProvider, _Mapping]] = ..., validation_context_certificate_provider_instance: _Optional[_Union[CommonTlsContext.CertificateProviderInstance, _Mapping]] = ..., alpn_protocols: _Optional[_Iterable[str]] = ..., custom_handshaker: _Optional[_Union[_extension_pb2.TypedExtensionConfig, _Mapping]] = ..., key_log: _Optional[_Union[TlsKeyLog, _Mapping]] = ...) -> None: ...
