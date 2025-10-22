from envoy.config.core.v3 import base_pb2 as _base_pb2
from envoy.config.core.v3 import extension_pb2 as _extension_pb2
from envoy.type.matcher.v3 import string_pb2 as _string_pb2
from google.protobuf import any_pb2 as _any_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from envoy.annotations import deprecation_pb2 as _deprecation_pb2
from udpa.annotations import migrate_pb2 as _migrate_pb2
from udpa.annotations import sensitive_pb2 as _sensitive_pb2
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

class TlsParameters(_message.Message):
    __slots__ = ("tls_minimum_protocol_version", "tls_maximum_protocol_version", "cipher_suites", "ecdh_curves", "signature_algorithms", "compliance_policies")
    class TlsProtocol(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TLS_AUTO: _ClassVar[TlsParameters.TlsProtocol]
        TLSv1_0: _ClassVar[TlsParameters.TlsProtocol]
        TLSv1_1: _ClassVar[TlsParameters.TlsProtocol]
        TLSv1_2: _ClassVar[TlsParameters.TlsProtocol]
        TLSv1_3: _ClassVar[TlsParameters.TlsProtocol]
    TLS_AUTO: TlsParameters.TlsProtocol
    TLSv1_0: TlsParameters.TlsProtocol
    TLSv1_1: TlsParameters.TlsProtocol
    TLSv1_2: TlsParameters.TlsProtocol
    TLSv1_3: TlsParameters.TlsProtocol
    class CompliancePolicy(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        FIPS_202205: _ClassVar[TlsParameters.CompliancePolicy]
    FIPS_202205: TlsParameters.CompliancePolicy
    TLS_MINIMUM_PROTOCOL_VERSION_FIELD_NUMBER: _ClassVar[int]
    TLS_MAXIMUM_PROTOCOL_VERSION_FIELD_NUMBER: _ClassVar[int]
    CIPHER_SUITES_FIELD_NUMBER: _ClassVar[int]
    ECDH_CURVES_FIELD_NUMBER: _ClassVar[int]
    SIGNATURE_ALGORITHMS_FIELD_NUMBER: _ClassVar[int]
    COMPLIANCE_POLICIES_FIELD_NUMBER: _ClassVar[int]
    tls_minimum_protocol_version: TlsParameters.TlsProtocol
    tls_maximum_protocol_version: TlsParameters.TlsProtocol
    cipher_suites: _containers.RepeatedScalarFieldContainer[str]
    ecdh_curves: _containers.RepeatedScalarFieldContainer[str]
    signature_algorithms: _containers.RepeatedScalarFieldContainer[str]
    compliance_policies: _containers.RepeatedScalarFieldContainer[TlsParameters.CompliancePolicy]
    def __init__(self, tls_minimum_protocol_version: _Optional[_Union[TlsParameters.TlsProtocol, str]] = ..., tls_maximum_protocol_version: _Optional[_Union[TlsParameters.TlsProtocol, str]] = ..., cipher_suites: _Optional[_Iterable[str]] = ..., ecdh_curves: _Optional[_Iterable[str]] = ..., signature_algorithms: _Optional[_Iterable[str]] = ..., compliance_policies: _Optional[_Iterable[_Union[TlsParameters.CompliancePolicy, str]]] = ...) -> None: ...

class PrivateKeyProvider(_message.Message):
    __slots__ = ("provider_name", "typed_config", "fallback")
    PROVIDER_NAME_FIELD_NUMBER: _ClassVar[int]
    TYPED_CONFIG_FIELD_NUMBER: _ClassVar[int]
    FALLBACK_FIELD_NUMBER: _ClassVar[int]
    provider_name: str
    typed_config: _any_pb2.Any
    fallback: bool
    def __init__(self, provider_name: _Optional[str] = ..., typed_config: _Optional[_Union[_any_pb2.Any, _Mapping]] = ..., fallback: bool = ...) -> None: ...

class TlsCertificate(_message.Message):
    __slots__ = ("certificate_chain", "private_key", "pkcs12", "watched_directory", "private_key_provider", "password", "ocsp_staple", "signed_certificate_timestamp")
    CERTIFICATE_CHAIN_FIELD_NUMBER: _ClassVar[int]
    PRIVATE_KEY_FIELD_NUMBER: _ClassVar[int]
    PKCS12_FIELD_NUMBER: _ClassVar[int]
    WATCHED_DIRECTORY_FIELD_NUMBER: _ClassVar[int]
    PRIVATE_KEY_PROVIDER_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    OCSP_STAPLE_FIELD_NUMBER: _ClassVar[int]
    SIGNED_CERTIFICATE_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    certificate_chain: _base_pb2.DataSource
    private_key: _base_pb2.DataSource
    pkcs12: _base_pb2.DataSource
    watched_directory: _base_pb2.WatchedDirectory
    private_key_provider: PrivateKeyProvider
    password: _base_pb2.DataSource
    ocsp_staple: _base_pb2.DataSource
    signed_certificate_timestamp: _containers.RepeatedCompositeFieldContainer[_base_pb2.DataSource]
    def __init__(self, certificate_chain: _Optional[_Union[_base_pb2.DataSource, _Mapping]] = ..., private_key: _Optional[_Union[_base_pb2.DataSource, _Mapping]] = ..., pkcs12: _Optional[_Union[_base_pb2.DataSource, _Mapping]] = ..., watched_directory: _Optional[_Union[_base_pb2.WatchedDirectory, _Mapping]] = ..., private_key_provider: _Optional[_Union[PrivateKeyProvider, _Mapping]] = ..., password: _Optional[_Union[_base_pb2.DataSource, _Mapping]] = ..., ocsp_staple: _Optional[_Union[_base_pb2.DataSource, _Mapping]] = ..., signed_certificate_timestamp: _Optional[_Iterable[_Union[_base_pb2.DataSource, _Mapping]]] = ...) -> None: ...

class TlsSessionTicketKeys(_message.Message):
    __slots__ = ("keys",)
    KEYS_FIELD_NUMBER: _ClassVar[int]
    keys: _containers.RepeatedCompositeFieldContainer[_base_pb2.DataSource]
    def __init__(self, keys: _Optional[_Iterable[_Union[_base_pb2.DataSource, _Mapping]]] = ...) -> None: ...

class CertificateProviderPluginInstance(_message.Message):
    __slots__ = ("instance_name", "certificate_name")
    INSTANCE_NAME_FIELD_NUMBER: _ClassVar[int]
    CERTIFICATE_NAME_FIELD_NUMBER: _ClassVar[int]
    instance_name: str
    certificate_name: str
    def __init__(self, instance_name: _Optional[str] = ..., certificate_name: _Optional[str] = ...) -> None: ...

class SubjectAltNameMatcher(_message.Message):
    __slots__ = ("san_type", "matcher", "oid")
    class SanType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        SAN_TYPE_UNSPECIFIED: _ClassVar[SubjectAltNameMatcher.SanType]
        EMAIL: _ClassVar[SubjectAltNameMatcher.SanType]
        DNS: _ClassVar[SubjectAltNameMatcher.SanType]
        URI: _ClassVar[SubjectAltNameMatcher.SanType]
        IP_ADDRESS: _ClassVar[SubjectAltNameMatcher.SanType]
        OTHER_NAME: _ClassVar[SubjectAltNameMatcher.SanType]
    SAN_TYPE_UNSPECIFIED: SubjectAltNameMatcher.SanType
    EMAIL: SubjectAltNameMatcher.SanType
    DNS: SubjectAltNameMatcher.SanType
    URI: SubjectAltNameMatcher.SanType
    IP_ADDRESS: SubjectAltNameMatcher.SanType
    OTHER_NAME: SubjectAltNameMatcher.SanType
    SAN_TYPE_FIELD_NUMBER: _ClassVar[int]
    MATCHER_FIELD_NUMBER: _ClassVar[int]
    OID_FIELD_NUMBER: _ClassVar[int]
    san_type: SubjectAltNameMatcher.SanType
    matcher: _string_pb2.StringMatcher
    oid: str
    def __init__(self, san_type: _Optional[_Union[SubjectAltNameMatcher.SanType, str]] = ..., matcher: _Optional[_Union[_string_pb2.StringMatcher, _Mapping]] = ..., oid: _Optional[str] = ...) -> None: ...

class CertificateValidationContext(_message.Message):
    __slots__ = ("trusted_ca", "ca_certificate_provider_instance", "system_root_certs", "watched_directory", "verify_certificate_spki", "verify_certificate_hash", "match_typed_subject_alt_names", "match_subject_alt_names", "require_signed_certificate_timestamp", "crl", "allow_expired_certificate", "trust_chain_verification", "custom_validator_config", "only_verify_leaf_cert_crl", "max_verify_depth")
    class TrustChainVerification(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        VERIFY_TRUST_CHAIN: _ClassVar[CertificateValidationContext.TrustChainVerification]
        ACCEPT_UNTRUSTED: _ClassVar[CertificateValidationContext.TrustChainVerification]
    VERIFY_TRUST_CHAIN: CertificateValidationContext.TrustChainVerification
    ACCEPT_UNTRUSTED: CertificateValidationContext.TrustChainVerification
    class SystemRootCerts(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    TRUSTED_CA_FIELD_NUMBER: _ClassVar[int]
    CA_CERTIFICATE_PROVIDER_INSTANCE_FIELD_NUMBER: _ClassVar[int]
    SYSTEM_ROOT_CERTS_FIELD_NUMBER: _ClassVar[int]
    WATCHED_DIRECTORY_FIELD_NUMBER: _ClassVar[int]
    VERIFY_CERTIFICATE_SPKI_FIELD_NUMBER: _ClassVar[int]
    VERIFY_CERTIFICATE_HASH_FIELD_NUMBER: _ClassVar[int]
    MATCH_TYPED_SUBJECT_ALT_NAMES_FIELD_NUMBER: _ClassVar[int]
    MATCH_SUBJECT_ALT_NAMES_FIELD_NUMBER: _ClassVar[int]
    REQUIRE_SIGNED_CERTIFICATE_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    CRL_FIELD_NUMBER: _ClassVar[int]
    ALLOW_EXPIRED_CERTIFICATE_FIELD_NUMBER: _ClassVar[int]
    TRUST_CHAIN_VERIFICATION_FIELD_NUMBER: _ClassVar[int]
    CUSTOM_VALIDATOR_CONFIG_FIELD_NUMBER: _ClassVar[int]
    ONLY_VERIFY_LEAF_CERT_CRL_FIELD_NUMBER: _ClassVar[int]
    MAX_VERIFY_DEPTH_FIELD_NUMBER: _ClassVar[int]
    trusted_ca: _base_pb2.DataSource
    ca_certificate_provider_instance: CertificateProviderPluginInstance
    system_root_certs: CertificateValidationContext.SystemRootCerts
    watched_directory: _base_pb2.WatchedDirectory
    verify_certificate_spki: _containers.RepeatedScalarFieldContainer[str]
    verify_certificate_hash: _containers.RepeatedScalarFieldContainer[str]
    match_typed_subject_alt_names: _containers.RepeatedCompositeFieldContainer[SubjectAltNameMatcher]
    match_subject_alt_names: _containers.RepeatedCompositeFieldContainer[_string_pb2.StringMatcher]
    require_signed_certificate_timestamp: _wrappers_pb2.BoolValue
    crl: _base_pb2.DataSource
    allow_expired_certificate: bool
    trust_chain_verification: CertificateValidationContext.TrustChainVerification
    custom_validator_config: _extension_pb2.TypedExtensionConfig
    only_verify_leaf_cert_crl: bool
    max_verify_depth: _wrappers_pb2.UInt32Value
    def __init__(self, trusted_ca: _Optional[_Union[_base_pb2.DataSource, _Mapping]] = ..., ca_certificate_provider_instance: _Optional[_Union[CertificateProviderPluginInstance, _Mapping]] = ..., system_root_certs: _Optional[_Union[CertificateValidationContext.SystemRootCerts, _Mapping]] = ..., watched_directory: _Optional[_Union[_base_pb2.WatchedDirectory, _Mapping]] = ..., verify_certificate_spki: _Optional[_Iterable[str]] = ..., verify_certificate_hash: _Optional[_Iterable[str]] = ..., match_typed_subject_alt_names: _Optional[_Iterable[_Union[SubjectAltNameMatcher, _Mapping]]] = ..., match_subject_alt_names: _Optional[_Iterable[_Union[_string_pb2.StringMatcher, _Mapping]]] = ..., require_signed_certificate_timestamp: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., crl: _Optional[_Union[_base_pb2.DataSource, _Mapping]] = ..., allow_expired_certificate: bool = ..., trust_chain_verification: _Optional[_Union[CertificateValidationContext.TrustChainVerification, str]] = ..., custom_validator_config: _Optional[_Union[_extension_pb2.TypedExtensionConfig, _Mapping]] = ..., only_verify_leaf_cert_crl: bool = ..., max_verify_depth: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ...) -> None: ...
