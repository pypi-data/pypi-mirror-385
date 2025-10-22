from envoy.annotations import deprecation_pb2 as _deprecation_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CommonGeoipProviderConfig(_message.Message):
    __slots__ = ("geo_headers_to_add",)
    class GeolocationHeadersToAdd(_message.Message):
        __slots__ = ("country", "city", "region", "asn", "is_anon", "anon", "anon_vpn", "anon_hosting", "anon_tor", "anon_proxy", "isp", "apple_private_relay")
        COUNTRY_FIELD_NUMBER: _ClassVar[int]
        CITY_FIELD_NUMBER: _ClassVar[int]
        REGION_FIELD_NUMBER: _ClassVar[int]
        ASN_FIELD_NUMBER: _ClassVar[int]
        IS_ANON_FIELD_NUMBER: _ClassVar[int]
        ANON_FIELD_NUMBER: _ClassVar[int]
        ANON_VPN_FIELD_NUMBER: _ClassVar[int]
        ANON_HOSTING_FIELD_NUMBER: _ClassVar[int]
        ANON_TOR_FIELD_NUMBER: _ClassVar[int]
        ANON_PROXY_FIELD_NUMBER: _ClassVar[int]
        ISP_FIELD_NUMBER: _ClassVar[int]
        APPLE_PRIVATE_RELAY_FIELD_NUMBER: _ClassVar[int]
        country: str
        city: str
        region: str
        asn: str
        is_anon: str
        anon: str
        anon_vpn: str
        anon_hosting: str
        anon_tor: str
        anon_proxy: str
        isp: str
        apple_private_relay: str
        def __init__(self, country: _Optional[str] = ..., city: _Optional[str] = ..., region: _Optional[str] = ..., asn: _Optional[str] = ..., is_anon: _Optional[str] = ..., anon: _Optional[str] = ..., anon_vpn: _Optional[str] = ..., anon_hosting: _Optional[str] = ..., anon_tor: _Optional[str] = ..., anon_proxy: _Optional[str] = ..., isp: _Optional[str] = ..., apple_private_relay: _Optional[str] = ...) -> None: ...
    GEO_HEADERS_TO_ADD_FIELD_NUMBER: _ClassVar[int]
    geo_headers_to_add: CommonGeoipProviderConfig.GeolocationHeadersToAdd
    def __init__(self, geo_headers_to_add: _Optional[_Union[CommonGeoipProviderConfig.GeolocationHeadersToAdd, _Mapping]] = ...) -> None: ...
