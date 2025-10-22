import datetime

from envoy.api.v2.core import address_pb2 as _address_pb2
from envoy.api.v2.core import base_pb2 as _base_pb2
from envoy.api.v2.core import socket_option_pb2 as _socket_option_pb2
from google.protobuf import any_pb2 as _any_pb2
from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
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

class TCPAccessLogEntry(_message.Message):
    __slots__ = ("common_properties", "connection_properties")
    COMMON_PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    CONNECTION_PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    common_properties: AccessLogCommon
    connection_properties: ConnectionProperties
    def __init__(self, common_properties: _Optional[_Union[AccessLogCommon, _Mapping]] = ..., connection_properties: _Optional[_Union[ConnectionProperties, _Mapping]] = ...) -> None: ...

class HTTPAccessLogEntry(_message.Message):
    __slots__ = ("common_properties", "protocol_version", "request", "response")
    class HTTPVersion(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PROTOCOL_UNSPECIFIED: _ClassVar[HTTPAccessLogEntry.HTTPVersion]
        HTTP10: _ClassVar[HTTPAccessLogEntry.HTTPVersion]
        HTTP11: _ClassVar[HTTPAccessLogEntry.HTTPVersion]
        HTTP2: _ClassVar[HTTPAccessLogEntry.HTTPVersion]
        HTTP3: _ClassVar[HTTPAccessLogEntry.HTTPVersion]
    PROTOCOL_UNSPECIFIED: HTTPAccessLogEntry.HTTPVersion
    HTTP10: HTTPAccessLogEntry.HTTPVersion
    HTTP11: HTTPAccessLogEntry.HTTPVersion
    HTTP2: HTTPAccessLogEntry.HTTPVersion
    HTTP3: HTTPAccessLogEntry.HTTPVersion
    COMMON_PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    PROTOCOL_VERSION_FIELD_NUMBER: _ClassVar[int]
    REQUEST_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    common_properties: AccessLogCommon
    protocol_version: HTTPAccessLogEntry.HTTPVersion
    request: HTTPRequestProperties
    response: HTTPResponseProperties
    def __init__(self, common_properties: _Optional[_Union[AccessLogCommon, _Mapping]] = ..., protocol_version: _Optional[_Union[HTTPAccessLogEntry.HTTPVersion, str]] = ..., request: _Optional[_Union[HTTPRequestProperties, _Mapping]] = ..., response: _Optional[_Union[HTTPResponseProperties, _Mapping]] = ...) -> None: ...

class ConnectionProperties(_message.Message):
    __slots__ = ("received_bytes", "sent_bytes")
    RECEIVED_BYTES_FIELD_NUMBER: _ClassVar[int]
    SENT_BYTES_FIELD_NUMBER: _ClassVar[int]
    received_bytes: int
    sent_bytes: int
    def __init__(self, received_bytes: _Optional[int] = ..., sent_bytes: _Optional[int] = ...) -> None: ...

class AccessLogCommon(_message.Message):
    __slots__ = ("sample_rate", "downstream_remote_address", "downstream_local_address", "tls_properties", "start_time", "time_to_last_rx_byte", "time_to_first_upstream_tx_byte", "time_to_last_upstream_tx_byte", "time_to_first_upstream_rx_byte", "time_to_last_upstream_rx_byte", "time_to_first_downstream_tx_byte", "time_to_last_downstream_tx_byte", "upstream_remote_address", "upstream_local_address", "upstream_cluster", "response_flags", "metadata", "upstream_transport_failure_reason", "route_name", "downstream_direct_remote_address", "filter_state_objects")
    class FilterStateObjectsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _any_pb2.Any
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...
    SAMPLE_RATE_FIELD_NUMBER: _ClassVar[int]
    DOWNSTREAM_REMOTE_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    DOWNSTREAM_LOCAL_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    TLS_PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    START_TIME_FIELD_NUMBER: _ClassVar[int]
    TIME_TO_LAST_RX_BYTE_FIELD_NUMBER: _ClassVar[int]
    TIME_TO_FIRST_UPSTREAM_TX_BYTE_FIELD_NUMBER: _ClassVar[int]
    TIME_TO_LAST_UPSTREAM_TX_BYTE_FIELD_NUMBER: _ClassVar[int]
    TIME_TO_FIRST_UPSTREAM_RX_BYTE_FIELD_NUMBER: _ClassVar[int]
    TIME_TO_LAST_UPSTREAM_RX_BYTE_FIELD_NUMBER: _ClassVar[int]
    TIME_TO_FIRST_DOWNSTREAM_TX_BYTE_FIELD_NUMBER: _ClassVar[int]
    TIME_TO_LAST_DOWNSTREAM_TX_BYTE_FIELD_NUMBER: _ClassVar[int]
    UPSTREAM_REMOTE_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    UPSTREAM_LOCAL_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    UPSTREAM_CLUSTER_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_FLAGS_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    UPSTREAM_TRANSPORT_FAILURE_REASON_FIELD_NUMBER: _ClassVar[int]
    ROUTE_NAME_FIELD_NUMBER: _ClassVar[int]
    DOWNSTREAM_DIRECT_REMOTE_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    FILTER_STATE_OBJECTS_FIELD_NUMBER: _ClassVar[int]
    sample_rate: float
    downstream_remote_address: _address_pb2.Address
    downstream_local_address: _address_pb2.Address
    tls_properties: TLSProperties
    start_time: _timestamp_pb2.Timestamp
    time_to_last_rx_byte: _duration_pb2.Duration
    time_to_first_upstream_tx_byte: _duration_pb2.Duration
    time_to_last_upstream_tx_byte: _duration_pb2.Duration
    time_to_first_upstream_rx_byte: _duration_pb2.Duration
    time_to_last_upstream_rx_byte: _duration_pb2.Duration
    time_to_first_downstream_tx_byte: _duration_pb2.Duration
    time_to_last_downstream_tx_byte: _duration_pb2.Duration
    upstream_remote_address: _address_pb2.Address
    upstream_local_address: _address_pb2.Address
    upstream_cluster: str
    response_flags: ResponseFlags
    metadata: _base_pb2.Metadata
    upstream_transport_failure_reason: str
    route_name: str
    downstream_direct_remote_address: _address_pb2.Address
    filter_state_objects: _containers.MessageMap[str, _any_pb2.Any]
    def __init__(self, sample_rate: _Optional[float] = ..., downstream_remote_address: _Optional[_Union[_address_pb2.Address, _Mapping]] = ..., downstream_local_address: _Optional[_Union[_address_pb2.Address, _Mapping]] = ..., tls_properties: _Optional[_Union[TLSProperties, _Mapping]] = ..., start_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., time_to_last_rx_byte: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., time_to_first_upstream_tx_byte: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., time_to_last_upstream_tx_byte: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., time_to_first_upstream_rx_byte: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., time_to_last_upstream_rx_byte: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., time_to_first_downstream_tx_byte: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., time_to_last_downstream_tx_byte: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., upstream_remote_address: _Optional[_Union[_address_pb2.Address, _Mapping]] = ..., upstream_local_address: _Optional[_Union[_address_pb2.Address, _Mapping]] = ..., upstream_cluster: _Optional[str] = ..., response_flags: _Optional[_Union[ResponseFlags, _Mapping]] = ..., metadata: _Optional[_Union[_base_pb2.Metadata, _Mapping]] = ..., upstream_transport_failure_reason: _Optional[str] = ..., route_name: _Optional[str] = ..., downstream_direct_remote_address: _Optional[_Union[_address_pb2.Address, _Mapping]] = ..., filter_state_objects: _Optional[_Mapping[str, _any_pb2.Any]] = ...) -> None: ...

class ResponseFlags(_message.Message):
    __slots__ = ("failed_local_healthcheck", "no_healthy_upstream", "upstream_request_timeout", "local_reset", "upstream_remote_reset", "upstream_connection_failure", "upstream_connection_termination", "upstream_overflow", "no_route_found", "delay_injected", "fault_injected", "rate_limited", "unauthorized_details", "rate_limit_service_error", "downstream_connection_termination", "upstream_retry_limit_exceeded", "stream_idle_timeout", "invalid_envoy_request_headers", "downstream_protocol_error")
    class Unauthorized(_message.Message):
        __slots__ = ("reason",)
        class Reason(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            REASON_UNSPECIFIED: _ClassVar[ResponseFlags.Unauthorized.Reason]
            EXTERNAL_SERVICE: _ClassVar[ResponseFlags.Unauthorized.Reason]
        REASON_UNSPECIFIED: ResponseFlags.Unauthorized.Reason
        EXTERNAL_SERVICE: ResponseFlags.Unauthorized.Reason
        REASON_FIELD_NUMBER: _ClassVar[int]
        reason: ResponseFlags.Unauthorized.Reason
        def __init__(self, reason: _Optional[_Union[ResponseFlags.Unauthorized.Reason, str]] = ...) -> None: ...
    FAILED_LOCAL_HEALTHCHECK_FIELD_NUMBER: _ClassVar[int]
    NO_HEALTHY_UPSTREAM_FIELD_NUMBER: _ClassVar[int]
    UPSTREAM_REQUEST_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    LOCAL_RESET_FIELD_NUMBER: _ClassVar[int]
    UPSTREAM_REMOTE_RESET_FIELD_NUMBER: _ClassVar[int]
    UPSTREAM_CONNECTION_FAILURE_FIELD_NUMBER: _ClassVar[int]
    UPSTREAM_CONNECTION_TERMINATION_FIELD_NUMBER: _ClassVar[int]
    UPSTREAM_OVERFLOW_FIELD_NUMBER: _ClassVar[int]
    NO_ROUTE_FOUND_FIELD_NUMBER: _ClassVar[int]
    DELAY_INJECTED_FIELD_NUMBER: _ClassVar[int]
    FAULT_INJECTED_FIELD_NUMBER: _ClassVar[int]
    RATE_LIMITED_FIELD_NUMBER: _ClassVar[int]
    UNAUTHORIZED_DETAILS_FIELD_NUMBER: _ClassVar[int]
    RATE_LIMIT_SERVICE_ERROR_FIELD_NUMBER: _ClassVar[int]
    DOWNSTREAM_CONNECTION_TERMINATION_FIELD_NUMBER: _ClassVar[int]
    UPSTREAM_RETRY_LIMIT_EXCEEDED_FIELD_NUMBER: _ClassVar[int]
    STREAM_IDLE_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    INVALID_ENVOY_REQUEST_HEADERS_FIELD_NUMBER: _ClassVar[int]
    DOWNSTREAM_PROTOCOL_ERROR_FIELD_NUMBER: _ClassVar[int]
    failed_local_healthcheck: bool
    no_healthy_upstream: bool
    upstream_request_timeout: bool
    local_reset: bool
    upstream_remote_reset: bool
    upstream_connection_failure: bool
    upstream_connection_termination: bool
    upstream_overflow: bool
    no_route_found: bool
    delay_injected: bool
    fault_injected: bool
    rate_limited: bool
    unauthorized_details: ResponseFlags.Unauthorized
    rate_limit_service_error: bool
    downstream_connection_termination: bool
    upstream_retry_limit_exceeded: bool
    stream_idle_timeout: bool
    invalid_envoy_request_headers: bool
    downstream_protocol_error: bool
    def __init__(self, failed_local_healthcheck: bool = ..., no_healthy_upstream: bool = ..., upstream_request_timeout: bool = ..., local_reset: bool = ..., upstream_remote_reset: bool = ..., upstream_connection_failure: bool = ..., upstream_connection_termination: bool = ..., upstream_overflow: bool = ..., no_route_found: bool = ..., delay_injected: bool = ..., fault_injected: bool = ..., rate_limited: bool = ..., unauthorized_details: _Optional[_Union[ResponseFlags.Unauthorized, _Mapping]] = ..., rate_limit_service_error: bool = ..., downstream_connection_termination: bool = ..., upstream_retry_limit_exceeded: bool = ..., stream_idle_timeout: bool = ..., invalid_envoy_request_headers: bool = ..., downstream_protocol_error: bool = ...) -> None: ...

class TLSProperties(_message.Message):
    __slots__ = ("tls_version", "tls_cipher_suite", "tls_sni_hostname", "local_certificate_properties", "peer_certificate_properties", "tls_session_id")
    class TLSVersion(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        VERSION_UNSPECIFIED: _ClassVar[TLSProperties.TLSVersion]
        TLSv1: _ClassVar[TLSProperties.TLSVersion]
        TLSv1_1: _ClassVar[TLSProperties.TLSVersion]
        TLSv1_2: _ClassVar[TLSProperties.TLSVersion]
        TLSv1_3: _ClassVar[TLSProperties.TLSVersion]
    VERSION_UNSPECIFIED: TLSProperties.TLSVersion
    TLSv1: TLSProperties.TLSVersion
    TLSv1_1: TLSProperties.TLSVersion
    TLSv1_2: TLSProperties.TLSVersion
    TLSv1_3: TLSProperties.TLSVersion
    class CertificateProperties(_message.Message):
        __slots__ = ("subject_alt_name", "subject")
        class SubjectAltName(_message.Message):
            __slots__ = ("uri", "dns")
            URI_FIELD_NUMBER: _ClassVar[int]
            DNS_FIELD_NUMBER: _ClassVar[int]
            uri: str
            dns: str
            def __init__(self, uri: _Optional[str] = ..., dns: _Optional[str] = ...) -> None: ...
        SUBJECT_ALT_NAME_FIELD_NUMBER: _ClassVar[int]
        SUBJECT_FIELD_NUMBER: _ClassVar[int]
        subject_alt_name: _containers.RepeatedCompositeFieldContainer[TLSProperties.CertificateProperties.SubjectAltName]
        subject: str
        def __init__(self, subject_alt_name: _Optional[_Iterable[_Union[TLSProperties.CertificateProperties.SubjectAltName, _Mapping]]] = ..., subject: _Optional[str] = ...) -> None: ...
    TLS_VERSION_FIELD_NUMBER: _ClassVar[int]
    TLS_CIPHER_SUITE_FIELD_NUMBER: _ClassVar[int]
    TLS_SNI_HOSTNAME_FIELD_NUMBER: _ClassVar[int]
    LOCAL_CERTIFICATE_PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    PEER_CERTIFICATE_PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    TLS_SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    tls_version: TLSProperties.TLSVersion
    tls_cipher_suite: _wrappers_pb2.UInt32Value
    tls_sni_hostname: str
    local_certificate_properties: TLSProperties.CertificateProperties
    peer_certificate_properties: TLSProperties.CertificateProperties
    tls_session_id: str
    def __init__(self, tls_version: _Optional[_Union[TLSProperties.TLSVersion, str]] = ..., tls_cipher_suite: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., tls_sni_hostname: _Optional[str] = ..., local_certificate_properties: _Optional[_Union[TLSProperties.CertificateProperties, _Mapping]] = ..., peer_certificate_properties: _Optional[_Union[TLSProperties.CertificateProperties, _Mapping]] = ..., tls_session_id: _Optional[str] = ...) -> None: ...

class HTTPRequestProperties(_message.Message):
    __slots__ = ("request_method", "scheme", "authority", "port", "path", "user_agent", "referer", "forwarded_for", "request_id", "original_path", "request_headers_bytes", "request_body_bytes", "request_headers")
    class RequestHeadersEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    REQUEST_METHOD_FIELD_NUMBER: _ClassVar[int]
    SCHEME_FIELD_NUMBER: _ClassVar[int]
    AUTHORITY_FIELD_NUMBER: _ClassVar[int]
    PORT_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    USER_AGENT_FIELD_NUMBER: _ClassVar[int]
    REFERER_FIELD_NUMBER: _ClassVar[int]
    FORWARDED_FOR_FIELD_NUMBER: _ClassVar[int]
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    ORIGINAL_PATH_FIELD_NUMBER: _ClassVar[int]
    REQUEST_HEADERS_BYTES_FIELD_NUMBER: _ClassVar[int]
    REQUEST_BODY_BYTES_FIELD_NUMBER: _ClassVar[int]
    REQUEST_HEADERS_FIELD_NUMBER: _ClassVar[int]
    request_method: _base_pb2.RequestMethod
    scheme: str
    authority: str
    port: _wrappers_pb2.UInt32Value
    path: str
    user_agent: str
    referer: str
    forwarded_for: str
    request_id: str
    original_path: str
    request_headers_bytes: int
    request_body_bytes: int
    request_headers: _containers.ScalarMap[str, str]
    def __init__(self, request_method: _Optional[_Union[_base_pb2.RequestMethod, str]] = ..., scheme: _Optional[str] = ..., authority: _Optional[str] = ..., port: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., path: _Optional[str] = ..., user_agent: _Optional[str] = ..., referer: _Optional[str] = ..., forwarded_for: _Optional[str] = ..., request_id: _Optional[str] = ..., original_path: _Optional[str] = ..., request_headers_bytes: _Optional[int] = ..., request_body_bytes: _Optional[int] = ..., request_headers: _Optional[_Mapping[str, str]] = ...) -> None: ...

class HTTPResponseProperties(_message.Message):
    __slots__ = ("response_code", "response_headers_bytes", "response_body_bytes", "response_headers", "response_trailers", "response_code_details")
    class ResponseHeadersEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    class ResponseTrailersEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    RESPONSE_CODE_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_HEADERS_BYTES_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_BODY_BYTES_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_HEADERS_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_TRAILERS_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_CODE_DETAILS_FIELD_NUMBER: _ClassVar[int]
    response_code: _wrappers_pb2.UInt32Value
    response_headers_bytes: int
    response_body_bytes: int
    response_headers: _containers.ScalarMap[str, str]
    response_trailers: _containers.ScalarMap[str, str]
    response_code_details: str
    def __init__(self, response_code: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., response_headers_bytes: _Optional[int] = ..., response_body_bytes: _Optional[int] = ..., response_headers: _Optional[_Mapping[str, str]] = ..., response_trailers: _Optional[_Mapping[str, str]] = ..., response_code_details: _Optional[str] = ...) -> None: ...
