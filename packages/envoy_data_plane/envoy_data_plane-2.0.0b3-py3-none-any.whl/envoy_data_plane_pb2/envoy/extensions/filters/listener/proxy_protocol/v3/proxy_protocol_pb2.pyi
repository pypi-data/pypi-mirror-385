from envoy.config.core.v3 import proxy_protocol_pb2 as _proxy_protocol_pb2
from udpa.annotations import status_pb2 as _status_pb2
from udpa.annotations import versioning_pb2 as _versioning_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ProxyProtocol(_message.Message):
    __slots__ = ("rules", "allow_requests_without_proxy_protocol", "pass_through_tlvs", "disallowed_versions", "stat_prefix")
    class KeyValuePair(_message.Message):
        __slots__ = ("metadata_namespace", "key")
        METADATA_NAMESPACE_FIELD_NUMBER: _ClassVar[int]
        KEY_FIELD_NUMBER: _ClassVar[int]
        metadata_namespace: str
        key: str
        def __init__(self, metadata_namespace: _Optional[str] = ..., key: _Optional[str] = ...) -> None: ...
    class Rule(_message.Message):
        __slots__ = ("tlv_type", "on_tlv_present")
        TLV_TYPE_FIELD_NUMBER: _ClassVar[int]
        ON_TLV_PRESENT_FIELD_NUMBER: _ClassVar[int]
        tlv_type: int
        on_tlv_present: ProxyProtocol.KeyValuePair
        def __init__(self, tlv_type: _Optional[int] = ..., on_tlv_present: _Optional[_Union[ProxyProtocol.KeyValuePair, _Mapping]] = ...) -> None: ...
    RULES_FIELD_NUMBER: _ClassVar[int]
    ALLOW_REQUESTS_WITHOUT_PROXY_PROTOCOL_FIELD_NUMBER: _ClassVar[int]
    PASS_THROUGH_TLVS_FIELD_NUMBER: _ClassVar[int]
    DISALLOWED_VERSIONS_FIELD_NUMBER: _ClassVar[int]
    STAT_PREFIX_FIELD_NUMBER: _ClassVar[int]
    rules: _containers.RepeatedCompositeFieldContainer[ProxyProtocol.Rule]
    allow_requests_without_proxy_protocol: bool
    pass_through_tlvs: _proxy_protocol_pb2.ProxyProtocolPassThroughTLVs
    disallowed_versions: _containers.RepeatedScalarFieldContainer[_proxy_protocol_pb2.ProxyProtocolConfig.Version]
    stat_prefix: str
    def __init__(self, rules: _Optional[_Iterable[_Union[ProxyProtocol.Rule, _Mapping]]] = ..., allow_requests_without_proxy_protocol: bool = ..., pass_through_tlvs: _Optional[_Union[_proxy_protocol_pb2.ProxyProtocolPassThroughTLVs, _Mapping]] = ..., disallowed_versions: _Optional[_Iterable[_Union[_proxy_protocol_pb2.ProxyProtocolConfig.Version, str]]] = ..., stat_prefix: _Optional[str] = ...) -> None: ...
