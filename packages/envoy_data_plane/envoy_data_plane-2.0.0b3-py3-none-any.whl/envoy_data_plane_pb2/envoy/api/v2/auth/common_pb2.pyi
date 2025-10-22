from envoy.api.v2.core import base_pb2 as _base_pb2
from envoy.api.v2.core import socket_option_pb2 as _socket_option_pb2
from envoy.type.matcher import string_pb2 as _string_pb2
from google.protobuf import any_pb2 as _any_pb2
from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from udpa.annotations import migrate_pb2 as _migrate_pb2
from udpa.annotations import sensitive_pb2 as _sensitive_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TlsParameters(_message.Message):
    __slots__ = ("tls_minimum_protocol_version", "tls_maximum_protocol_version", "cipher_suites", "ecdh_curves")
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
    TLS_MINIMUM_PROTOCOL_VERSION_FIELD_NUMBER: _ClassVar[int]
    TLS_MAXIMUM_PROTOCOL_VERSION_FIELD_NUMBER: _ClassVar[int]
    CIPHER_SUITES_FIELD_NUMBER: _ClassVar[int]
    ECDH_CURVES_FIELD_NUMBER: _ClassVar[int]
    tls_minimum_protocol_version: TlsParameters.TlsProtocol
    tls_maximum_protocol_version: TlsParameters.TlsProtocol
    cipher_suites: _containers.RepeatedScalarFieldContainer[str]
    ecdh_curves: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, tls_minimum_protocol_version: _Optional[_Union[TlsParameters.TlsProtocol, str]] = ..., tls_maximum_protocol_version: _Optional[_Union[TlsParameters.TlsProtocol, str]] = ..., cipher_suites: _Optional[_Iterable[str]] = ..., ecdh_curves: _Optional[_Iterable[str]] = ...) -> None: ...

class PrivateKeyProvider(_message.Message):
    __slots__ = ("provider_name", "config", "typed_config")
    PROVIDER_NAME_FIELD_NUMBER: _ClassVar[int]
    CONFIG_FIELD_NUMBER: _ClassVar[int]
    TYPED_CONFIG_FIELD_NUMBER: _ClassVar[int]
    provider_name: str
    config: _struct_pb2.Struct
    typed_config: _any_pb2.Any
    def __init__(self, provider_name: _Optional[str] = ..., config: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., typed_config: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...

class TlsCertificate(_message.Message):
    __slots__ = ("certificate_chain", "private_key", "private_key_provider", "password", "ocsp_staple", "signed_certificate_timestamp")
    CERTIFICATE_CHAIN_FIELD_NUMBER: _ClassVar[int]
    PRIVATE_KEY_FIELD_NUMBER: _ClassVar[int]
    PRIVATE_KEY_PROVIDER_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    OCSP_STAPLE_FIELD_NUMBER: _ClassVar[int]
    SIGNED_CERTIFICATE_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    certificate_chain: _base_pb2.DataSource
    private_key: _base_pb2.DataSource
    private_key_provider: PrivateKeyProvider
    password: _base_pb2.DataSource
    ocsp_staple: _base_pb2.DataSource
    signed_certificate_timestamp: _containers.RepeatedCompositeFieldContainer[_base_pb2.DataSource]
    def __init__(self, certificate_chain: _Optional[_Union[_base_pb2.DataSource, _Mapping]] = ..., private_key: _Optional[_Union[_base_pb2.DataSource, _Mapping]] = ..., private_key_provider: _Optional[_Union[PrivateKeyProvider, _Mapping]] = ..., password: _Optional[_Union[_base_pb2.DataSource, _Mapping]] = ..., ocsp_staple: _Optional[_Union[_base_pb2.DataSource, _Mapping]] = ..., signed_certificate_timestamp: _Optional[_Iterable[_Union[_base_pb2.DataSource, _Mapping]]] = ...) -> None: ...

class TlsSessionTicketKeys(_message.Message):
    __slots__ = ("keys",)
    KEYS_FIELD_NUMBER: _ClassVar[int]
    keys: _containers.RepeatedCompositeFieldContainer[_base_pb2.DataSource]
    def __init__(self, keys: _Optional[_Iterable[_Union[_base_pb2.DataSource, _Mapping]]] = ...) -> None: ...

class CertificateValidationContext(_message.Message):
    __slots__ = ("trusted_ca", "verify_certificate_spki", "verify_certificate_hash", "verify_subject_alt_name", "match_subject_alt_names", "require_ocsp_staple", "require_signed_certificate_timestamp", "crl", "allow_expired_certificate", "trust_chain_verification")
    class TrustChainVerification(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        VERIFY_TRUST_CHAIN: _ClassVar[CertificateValidationContext.TrustChainVerification]
        ACCEPT_UNTRUSTED: _ClassVar[CertificateValidationContext.TrustChainVerification]
    VERIFY_TRUST_CHAIN: CertificateValidationContext.TrustChainVerification
    ACCEPT_UNTRUSTED: CertificateValidationContext.TrustChainVerification
    TRUSTED_CA_FIELD_NUMBER: _ClassVar[int]
    VERIFY_CERTIFICATE_SPKI_FIELD_NUMBER: _ClassVar[int]
    VERIFY_CERTIFICATE_HASH_FIELD_NUMBER: _ClassVar[int]
    VERIFY_SUBJECT_ALT_NAME_FIELD_NUMBER: _ClassVar[int]
    MATCH_SUBJECT_ALT_NAMES_FIELD_NUMBER: _ClassVar[int]
    REQUIRE_OCSP_STAPLE_FIELD_NUMBER: _ClassVar[int]
    REQUIRE_SIGNED_CERTIFICATE_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    CRL_FIELD_NUMBER: _ClassVar[int]
    ALLOW_EXPIRED_CERTIFICATE_FIELD_NUMBER: _ClassVar[int]
    TRUST_CHAIN_VERIFICATION_FIELD_NUMBER: _ClassVar[int]
    trusted_ca: _base_pb2.DataSource
    verify_certificate_spki: _containers.RepeatedScalarFieldContainer[str]
    verify_certificate_hash: _containers.RepeatedScalarFieldContainer[str]
    verify_subject_alt_name: _containers.RepeatedScalarFieldContainer[str]
    match_subject_alt_names: _containers.RepeatedCompositeFieldContainer[_string_pb2.StringMatcher]
    require_ocsp_staple: _wrappers_pb2.BoolValue
    require_signed_certificate_timestamp: _wrappers_pb2.BoolValue
    crl: _base_pb2.DataSource
    allow_expired_certificate: bool
    trust_chain_verification: CertificateValidationContext.TrustChainVerification
    def __init__(self, trusted_ca: _Optional[_Union[_base_pb2.DataSource, _Mapping]] = ..., verify_certificate_spki: _Optional[_Iterable[str]] = ..., verify_certificate_hash: _Optional[_Iterable[str]] = ..., verify_subject_alt_name: _Optional[_Iterable[str]] = ..., match_subject_alt_names: _Optional[_Iterable[_Union[_string_pb2.StringMatcher, _Mapping]]] = ..., require_ocsp_staple: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., require_signed_certificate_timestamp: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., crl: _Optional[_Union[_base_pb2.DataSource, _Mapping]] = ..., allow_expired_certificate: bool = ..., trust_chain_verification: _Optional[_Union[CertificateValidationContext.TrustChainVerification, str]] = ...) -> None: ...
