from udpa.annotations import status_pb2 as _status_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar

DESCRIPTOR: _descriptor.FileDescriptor

class DnsLookupFamily(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNSPECIFIED: _ClassVar[DnsLookupFamily]
    AUTO: _ClassVar[DnsLookupFamily]
    V4_ONLY: _ClassVar[DnsLookupFamily]
    V6_ONLY: _ClassVar[DnsLookupFamily]
    V4_PREFERRED: _ClassVar[DnsLookupFamily]
    ALL: _ClassVar[DnsLookupFamily]
UNSPECIFIED: DnsLookupFamily
AUTO: DnsLookupFamily
V4_ONLY: DnsLookupFamily
V6_ONLY: DnsLookupFamily
V4_PREFERRED: DnsLookupFamily
ALL: DnsLookupFamily
