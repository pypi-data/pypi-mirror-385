from envoy.config.common.matcher.v3 import matcher_pb2 as _matcher_pb2
from envoy.config.core.v3 import extension_pb2 as _extension_pb2
from xds.type.matcher.v3 import matcher_pb2 as _matcher_pb2_1
from envoy.annotations import deprecation_pb2 as _deprecation_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ExtensionWithMatcher(_message.Message):
    __slots__ = ("matcher", "xds_matcher", "extension_config")
    MATCHER_FIELD_NUMBER: _ClassVar[int]
    XDS_MATCHER_FIELD_NUMBER: _ClassVar[int]
    EXTENSION_CONFIG_FIELD_NUMBER: _ClassVar[int]
    matcher: _matcher_pb2.Matcher
    xds_matcher: _matcher_pb2_1.Matcher
    extension_config: _extension_pb2.TypedExtensionConfig
    def __init__(self, matcher: _Optional[_Union[_matcher_pb2.Matcher, _Mapping]] = ..., xds_matcher: _Optional[_Union[_matcher_pb2_1.Matcher, _Mapping]] = ..., extension_config: _Optional[_Union[_extension_pb2.TypedExtensionConfig, _Mapping]] = ...) -> None: ...

class ExtensionWithMatcherPerRoute(_message.Message):
    __slots__ = ("xds_matcher",)
    XDS_MATCHER_FIELD_NUMBER: _ClassVar[int]
    xds_matcher: _matcher_pb2_1.Matcher
    def __init__(self, xds_matcher: _Optional[_Union[_matcher_pb2_1.Matcher, _Mapping]] = ...) -> None: ...
