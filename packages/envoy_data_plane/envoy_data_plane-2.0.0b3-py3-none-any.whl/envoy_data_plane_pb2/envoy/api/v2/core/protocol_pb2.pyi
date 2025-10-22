import datetime

from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from udpa.annotations import migrate_pb2 as _migrate_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TcpProtocolOptions(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class UpstreamHttpProtocolOptions(_message.Message):
    __slots__ = ("auto_sni", "auto_san_validation")
    AUTO_SNI_FIELD_NUMBER: _ClassVar[int]
    AUTO_SAN_VALIDATION_FIELD_NUMBER: _ClassVar[int]
    auto_sni: bool
    auto_san_validation: bool
    def __init__(self, auto_sni: bool = ..., auto_san_validation: bool = ...) -> None: ...

class HttpProtocolOptions(_message.Message):
    __slots__ = ("idle_timeout", "max_connection_duration", "max_headers_count", "max_stream_duration", "headers_with_underscores_action")
    class HeadersWithUnderscoresAction(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ALLOW: _ClassVar[HttpProtocolOptions.HeadersWithUnderscoresAction]
        REJECT_REQUEST: _ClassVar[HttpProtocolOptions.HeadersWithUnderscoresAction]
        DROP_HEADER: _ClassVar[HttpProtocolOptions.HeadersWithUnderscoresAction]
    ALLOW: HttpProtocolOptions.HeadersWithUnderscoresAction
    REJECT_REQUEST: HttpProtocolOptions.HeadersWithUnderscoresAction
    DROP_HEADER: HttpProtocolOptions.HeadersWithUnderscoresAction
    IDLE_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    MAX_CONNECTION_DURATION_FIELD_NUMBER: _ClassVar[int]
    MAX_HEADERS_COUNT_FIELD_NUMBER: _ClassVar[int]
    MAX_STREAM_DURATION_FIELD_NUMBER: _ClassVar[int]
    HEADERS_WITH_UNDERSCORES_ACTION_FIELD_NUMBER: _ClassVar[int]
    idle_timeout: _duration_pb2.Duration
    max_connection_duration: _duration_pb2.Duration
    max_headers_count: _wrappers_pb2.UInt32Value
    max_stream_duration: _duration_pb2.Duration
    headers_with_underscores_action: HttpProtocolOptions.HeadersWithUnderscoresAction
    def __init__(self, idle_timeout: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., max_connection_duration: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., max_headers_count: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., max_stream_duration: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., headers_with_underscores_action: _Optional[_Union[HttpProtocolOptions.HeadersWithUnderscoresAction, str]] = ...) -> None: ...

class Http1ProtocolOptions(_message.Message):
    __slots__ = ("allow_absolute_url", "accept_http_10", "default_host_for_http_10", "header_key_format", "enable_trailers")
    class HeaderKeyFormat(_message.Message):
        __slots__ = ("proper_case_words",)
        class ProperCaseWords(_message.Message):
            __slots__ = ()
            def __init__(self) -> None: ...
        PROPER_CASE_WORDS_FIELD_NUMBER: _ClassVar[int]
        proper_case_words: Http1ProtocolOptions.HeaderKeyFormat.ProperCaseWords
        def __init__(self, proper_case_words: _Optional[_Union[Http1ProtocolOptions.HeaderKeyFormat.ProperCaseWords, _Mapping]] = ...) -> None: ...
    ALLOW_ABSOLUTE_URL_FIELD_NUMBER: _ClassVar[int]
    ACCEPT_HTTP_10_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_HOST_FOR_HTTP_10_FIELD_NUMBER: _ClassVar[int]
    HEADER_KEY_FORMAT_FIELD_NUMBER: _ClassVar[int]
    ENABLE_TRAILERS_FIELD_NUMBER: _ClassVar[int]
    allow_absolute_url: _wrappers_pb2.BoolValue
    accept_http_10: bool
    default_host_for_http_10: str
    header_key_format: Http1ProtocolOptions.HeaderKeyFormat
    enable_trailers: bool
    def __init__(self, allow_absolute_url: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., accept_http_10: bool = ..., default_host_for_http_10: _Optional[str] = ..., header_key_format: _Optional[_Union[Http1ProtocolOptions.HeaderKeyFormat, _Mapping]] = ..., enable_trailers: bool = ...) -> None: ...

class Http2ProtocolOptions(_message.Message):
    __slots__ = ("hpack_table_size", "max_concurrent_streams", "initial_stream_window_size", "initial_connection_window_size", "allow_connect", "allow_metadata", "max_outbound_frames", "max_outbound_control_frames", "max_consecutive_inbound_frames_with_empty_payload", "max_inbound_priority_frames_per_stream", "max_inbound_window_update_frames_per_data_frame_sent", "stream_error_on_invalid_http_messaging", "custom_settings_parameters")
    class SettingsParameter(_message.Message):
        __slots__ = ("identifier", "value")
        IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        identifier: _wrappers_pb2.UInt32Value
        value: _wrappers_pb2.UInt32Value
        def __init__(self, identifier: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., value: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ...) -> None: ...
    HPACK_TABLE_SIZE_FIELD_NUMBER: _ClassVar[int]
    MAX_CONCURRENT_STREAMS_FIELD_NUMBER: _ClassVar[int]
    INITIAL_STREAM_WINDOW_SIZE_FIELD_NUMBER: _ClassVar[int]
    INITIAL_CONNECTION_WINDOW_SIZE_FIELD_NUMBER: _ClassVar[int]
    ALLOW_CONNECT_FIELD_NUMBER: _ClassVar[int]
    ALLOW_METADATA_FIELD_NUMBER: _ClassVar[int]
    MAX_OUTBOUND_FRAMES_FIELD_NUMBER: _ClassVar[int]
    MAX_OUTBOUND_CONTROL_FRAMES_FIELD_NUMBER: _ClassVar[int]
    MAX_CONSECUTIVE_INBOUND_FRAMES_WITH_EMPTY_PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    MAX_INBOUND_PRIORITY_FRAMES_PER_STREAM_FIELD_NUMBER: _ClassVar[int]
    MAX_INBOUND_WINDOW_UPDATE_FRAMES_PER_DATA_FRAME_SENT_FIELD_NUMBER: _ClassVar[int]
    STREAM_ERROR_ON_INVALID_HTTP_MESSAGING_FIELD_NUMBER: _ClassVar[int]
    CUSTOM_SETTINGS_PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    hpack_table_size: _wrappers_pb2.UInt32Value
    max_concurrent_streams: _wrappers_pb2.UInt32Value
    initial_stream_window_size: _wrappers_pb2.UInt32Value
    initial_connection_window_size: _wrappers_pb2.UInt32Value
    allow_connect: bool
    allow_metadata: bool
    max_outbound_frames: _wrappers_pb2.UInt32Value
    max_outbound_control_frames: _wrappers_pb2.UInt32Value
    max_consecutive_inbound_frames_with_empty_payload: _wrappers_pb2.UInt32Value
    max_inbound_priority_frames_per_stream: _wrappers_pb2.UInt32Value
    max_inbound_window_update_frames_per_data_frame_sent: _wrappers_pb2.UInt32Value
    stream_error_on_invalid_http_messaging: bool
    custom_settings_parameters: _containers.RepeatedCompositeFieldContainer[Http2ProtocolOptions.SettingsParameter]
    def __init__(self, hpack_table_size: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., max_concurrent_streams: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., initial_stream_window_size: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., initial_connection_window_size: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., allow_connect: bool = ..., allow_metadata: bool = ..., max_outbound_frames: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., max_outbound_control_frames: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., max_consecutive_inbound_frames_with_empty_payload: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., max_inbound_priority_frames_per_stream: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., max_inbound_window_update_frames_per_data_frame_sent: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., stream_error_on_invalid_http_messaging: bool = ..., custom_settings_parameters: _Optional[_Iterable[_Union[Http2ProtocolOptions.SettingsParameter, _Mapping]]] = ...) -> None: ...

class GrpcProtocolOptions(_message.Message):
    __slots__ = ("http2_protocol_options",)
    HTTP2_PROTOCOL_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    http2_protocol_options: Http2ProtocolOptions
    def __init__(self, http2_protocol_options: _Optional[_Union[Http2ProtocolOptions, _Mapping]] = ...) -> None: ...
