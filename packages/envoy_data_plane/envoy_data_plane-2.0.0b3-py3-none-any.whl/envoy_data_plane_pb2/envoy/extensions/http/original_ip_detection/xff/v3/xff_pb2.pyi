from envoy.config.core.v3 import address_pb2 as _address_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from udpa.annotations import status_pb2 as _status_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class XffConfig(_message.Message):
    __slots__ = ("xff_num_trusted_hops", "xff_trusted_cidrs", "skip_xff_append")
    XFF_NUM_TRUSTED_HOPS_FIELD_NUMBER: _ClassVar[int]
    XFF_TRUSTED_CIDRS_FIELD_NUMBER: _ClassVar[int]
    SKIP_XFF_APPEND_FIELD_NUMBER: _ClassVar[int]
    xff_num_trusted_hops: int
    xff_trusted_cidrs: XffTrustedCidrs
    skip_xff_append: _wrappers_pb2.BoolValue
    def __init__(self, xff_num_trusted_hops: _Optional[int] = ..., xff_trusted_cidrs: _Optional[_Union[XffTrustedCidrs, _Mapping]] = ..., skip_xff_append: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ...) -> None: ...

class XffTrustedCidrs(_message.Message):
    __slots__ = ("cidrs",)
    CIDRS_FIELD_NUMBER: _ClassVar[int]
    cidrs: _containers.RepeatedCompositeFieldContainer[_address_pb2.CidrRange]
    def __init__(self, cidrs: _Optional[_Iterable[_Union[_address_pb2.CidrRange, _Mapping]]] = ...) -> None: ...
