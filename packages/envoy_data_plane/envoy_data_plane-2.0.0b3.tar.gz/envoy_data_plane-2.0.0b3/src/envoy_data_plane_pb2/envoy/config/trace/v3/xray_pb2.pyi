from envoy.config.core.v3 import address_pb2 as _address_pb2
from envoy.config.core.v3 import base_pb2 as _base_pb2
from google.protobuf import struct_pb2 as _struct_pb2
from udpa.annotations import migrate_pb2 as _migrate_pb2
from udpa.annotations import status_pb2 as _status_pb2
from udpa.annotations import versioning_pb2 as _versioning_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class XRayConfig(_message.Message):
    __slots__ = ("daemon_endpoint", "segment_name", "sampling_rule_manifest", "segment_fields")
    class SegmentFields(_message.Message):
        __slots__ = ("origin", "aws")
        ORIGIN_FIELD_NUMBER: _ClassVar[int]
        AWS_FIELD_NUMBER: _ClassVar[int]
        origin: str
        aws: _struct_pb2.Struct
        def __init__(self, origin: _Optional[str] = ..., aws: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...
    DAEMON_ENDPOINT_FIELD_NUMBER: _ClassVar[int]
    SEGMENT_NAME_FIELD_NUMBER: _ClassVar[int]
    SAMPLING_RULE_MANIFEST_FIELD_NUMBER: _ClassVar[int]
    SEGMENT_FIELDS_FIELD_NUMBER: _ClassVar[int]
    daemon_endpoint: _address_pb2.SocketAddress
    segment_name: str
    sampling_rule_manifest: _base_pb2.DataSource
    segment_fields: XRayConfig.SegmentFields
    def __init__(self, daemon_endpoint: _Optional[_Union[_address_pb2.SocketAddress, _Mapping]] = ..., segment_name: _Optional[str] = ..., sampling_rule_manifest: _Optional[_Union[_base_pb2.DataSource, _Mapping]] = ..., segment_fields: _Optional[_Union[XRayConfig.SegmentFields, _Mapping]] = ...) -> None: ...
