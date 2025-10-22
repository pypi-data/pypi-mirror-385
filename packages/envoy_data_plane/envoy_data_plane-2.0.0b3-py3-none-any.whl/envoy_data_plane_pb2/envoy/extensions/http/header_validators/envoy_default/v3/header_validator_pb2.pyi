from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class HeaderValidatorConfig(_message.Message):
    __slots__ = ("http1_protocol_options", "uri_path_normalization_options", "restrict_http_methods", "headers_with_underscores_action", "strip_fragment_from_path")
    class HeadersWithUnderscoresAction(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ALLOW: _ClassVar[HeaderValidatorConfig.HeadersWithUnderscoresAction]
        REJECT_REQUEST: _ClassVar[HeaderValidatorConfig.HeadersWithUnderscoresAction]
        DROP_HEADER: _ClassVar[HeaderValidatorConfig.HeadersWithUnderscoresAction]
    ALLOW: HeaderValidatorConfig.HeadersWithUnderscoresAction
    REJECT_REQUEST: HeaderValidatorConfig.HeadersWithUnderscoresAction
    DROP_HEADER: HeaderValidatorConfig.HeadersWithUnderscoresAction
    class UriPathNormalizationOptions(_message.Message):
        __slots__ = ("skip_path_normalization", "skip_merging_slashes", "path_with_escaped_slashes_action")
        class PathWithEscapedSlashesAction(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            IMPLEMENTATION_SPECIFIC_DEFAULT: _ClassVar[HeaderValidatorConfig.UriPathNormalizationOptions.PathWithEscapedSlashesAction]
            KEEP_UNCHANGED: _ClassVar[HeaderValidatorConfig.UriPathNormalizationOptions.PathWithEscapedSlashesAction]
            REJECT_REQUEST: _ClassVar[HeaderValidatorConfig.UriPathNormalizationOptions.PathWithEscapedSlashesAction]
            UNESCAPE_AND_REDIRECT: _ClassVar[HeaderValidatorConfig.UriPathNormalizationOptions.PathWithEscapedSlashesAction]
            UNESCAPE_AND_FORWARD: _ClassVar[HeaderValidatorConfig.UriPathNormalizationOptions.PathWithEscapedSlashesAction]
        IMPLEMENTATION_SPECIFIC_DEFAULT: HeaderValidatorConfig.UriPathNormalizationOptions.PathWithEscapedSlashesAction
        KEEP_UNCHANGED: HeaderValidatorConfig.UriPathNormalizationOptions.PathWithEscapedSlashesAction
        REJECT_REQUEST: HeaderValidatorConfig.UriPathNormalizationOptions.PathWithEscapedSlashesAction
        UNESCAPE_AND_REDIRECT: HeaderValidatorConfig.UriPathNormalizationOptions.PathWithEscapedSlashesAction
        UNESCAPE_AND_FORWARD: HeaderValidatorConfig.UriPathNormalizationOptions.PathWithEscapedSlashesAction
        SKIP_PATH_NORMALIZATION_FIELD_NUMBER: _ClassVar[int]
        SKIP_MERGING_SLASHES_FIELD_NUMBER: _ClassVar[int]
        PATH_WITH_ESCAPED_SLASHES_ACTION_FIELD_NUMBER: _ClassVar[int]
        skip_path_normalization: bool
        skip_merging_slashes: bool
        path_with_escaped_slashes_action: HeaderValidatorConfig.UriPathNormalizationOptions.PathWithEscapedSlashesAction
        def __init__(self, skip_path_normalization: bool = ..., skip_merging_slashes: bool = ..., path_with_escaped_slashes_action: _Optional[_Union[HeaderValidatorConfig.UriPathNormalizationOptions.PathWithEscapedSlashesAction, str]] = ...) -> None: ...
    class Http1ProtocolOptions(_message.Message):
        __slots__ = ("allow_chunked_length",)
        ALLOW_CHUNKED_LENGTH_FIELD_NUMBER: _ClassVar[int]
        allow_chunked_length: bool
        def __init__(self, allow_chunked_length: bool = ...) -> None: ...
    HTTP1_PROTOCOL_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    URI_PATH_NORMALIZATION_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    RESTRICT_HTTP_METHODS_FIELD_NUMBER: _ClassVar[int]
    HEADERS_WITH_UNDERSCORES_ACTION_FIELD_NUMBER: _ClassVar[int]
    STRIP_FRAGMENT_FROM_PATH_FIELD_NUMBER: _ClassVar[int]
    http1_protocol_options: HeaderValidatorConfig.Http1ProtocolOptions
    uri_path_normalization_options: HeaderValidatorConfig.UriPathNormalizationOptions
    restrict_http_methods: bool
    headers_with_underscores_action: HeaderValidatorConfig.HeadersWithUnderscoresAction
    strip_fragment_from_path: bool
    def __init__(self, http1_protocol_options: _Optional[_Union[HeaderValidatorConfig.Http1ProtocolOptions, _Mapping]] = ..., uri_path_normalization_options: _Optional[_Union[HeaderValidatorConfig.UriPathNormalizationOptions, _Mapping]] = ..., restrict_http_methods: bool = ..., headers_with_underscores_action: _Optional[_Union[HeaderValidatorConfig.HeadersWithUnderscoresAction, str]] = ..., strip_fragment_from_path: bool = ...) -> None: ...
