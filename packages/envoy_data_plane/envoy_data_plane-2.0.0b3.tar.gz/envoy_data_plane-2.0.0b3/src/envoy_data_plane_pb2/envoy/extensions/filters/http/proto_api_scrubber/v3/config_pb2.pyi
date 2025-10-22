from envoy.config.core.v3 import base_pb2 as _base_pb2
from xds.annotations.v3 import status_pb2 as _status_pb2
from xds.type.matcher.v3 import matcher_pb2 as _matcher_pb2
from udpa.annotations import status_pb2 as _status_pb2_1
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ProtoApiScrubberConfig(_message.Message):
    __slots__ = ("descriptor_set", "restrictions", "filtering_mode")
    class FilteringMode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        OVERRIDE: _ClassVar[ProtoApiScrubberConfig.FilteringMode]
    OVERRIDE: ProtoApiScrubberConfig.FilteringMode
    DESCRIPTOR_SET_FIELD_NUMBER: _ClassVar[int]
    RESTRICTIONS_FIELD_NUMBER: _ClassVar[int]
    FILTERING_MODE_FIELD_NUMBER: _ClassVar[int]
    descriptor_set: DescriptorSet
    restrictions: Restrictions
    filtering_mode: ProtoApiScrubberConfig.FilteringMode
    def __init__(self, descriptor_set: _Optional[_Union[DescriptorSet, _Mapping]] = ..., restrictions: _Optional[_Union[Restrictions, _Mapping]] = ..., filtering_mode: _Optional[_Union[ProtoApiScrubberConfig.FilteringMode, str]] = ...) -> None: ...

class DescriptorSet(_message.Message):
    __slots__ = ("data_source",)
    DATA_SOURCE_FIELD_NUMBER: _ClassVar[int]
    data_source: _base_pb2.DataSource
    def __init__(self, data_source: _Optional[_Union[_base_pb2.DataSource, _Mapping]] = ...) -> None: ...

class Restrictions(_message.Message):
    __slots__ = ("method_restrictions",)
    class MethodRestrictionsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: MethodRestrictions
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[MethodRestrictions, _Mapping]] = ...) -> None: ...
    METHOD_RESTRICTIONS_FIELD_NUMBER: _ClassVar[int]
    method_restrictions: _containers.MessageMap[str, MethodRestrictions]
    def __init__(self, method_restrictions: _Optional[_Mapping[str, MethodRestrictions]] = ...) -> None: ...

class MethodRestrictions(_message.Message):
    __slots__ = ("request_field_restrictions", "response_field_restrictions")
    class RequestFieldRestrictionsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: RestrictionConfig
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[RestrictionConfig, _Mapping]] = ...) -> None: ...
    class ResponseFieldRestrictionsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: RestrictionConfig
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[RestrictionConfig, _Mapping]] = ...) -> None: ...
    REQUEST_FIELD_RESTRICTIONS_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_FIELD_RESTRICTIONS_FIELD_NUMBER: _ClassVar[int]
    request_field_restrictions: _containers.MessageMap[str, RestrictionConfig]
    response_field_restrictions: _containers.MessageMap[str, RestrictionConfig]
    def __init__(self, request_field_restrictions: _Optional[_Mapping[str, RestrictionConfig]] = ..., response_field_restrictions: _Optional[_Mapping[str, RestrictionConfig]] = ...) -> None: ...

class RestrictionConfig(_message.Message):
    __slots__ = ("matcher",)
    MATCHER_FIELD_NUMBER: _ClassVar[int]
    matcher: _matcher_pb2.Matcher
    def __init__(self, matcher: _Optional[_Union[_matcher_pb2.Matcher, _Mapping]] = ...) -> None: ...
