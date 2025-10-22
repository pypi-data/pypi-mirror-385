from envoy.extensions.geoip_providers.common.v3 import common_pb2 as _common_pb2
from xds.annotations.v3 import status_pb2 as _status_pb2
from udpa.annotations import status_pb2 as _status_pb2_1
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MaxMindConfig(_message.Message):
    __slots__ = ("city_db_path", "asn_db_path", "anon_db_path", "isp_db_path", "common_provider_config")
    CITY_DB_PATH_FIELD_NUMBER: _ClassVar[int]
    ASN_DB_PATH_FIELD_NUMBER: _ClassVar[int]
    ANON_DB_PATH_FIELD_NUMBER: _ClassVar[int]
    ISP_DB_PATH_FIELD_NUMBER: _ClassVar[int]
    COMMON_PROVIDER_CONFIG_FIELD_NUMBER: _ClassVar[int]
    city_db_path: str
    asn_db_path: str
    anon_db_path: str
    isp_db_path: str
    common_provider_config: _common_pb2.CommonGeoipProviderConfig
    def __init__(self, city_db_path: _Optional[str] = ..., asn_db_path: _Optional[str] = ..., anon_db_path: _Optional[str] = ..., isp_db_path: _Optional[str] = ..., common_provider_config: _Optional[_Union[_common_pb2.CommonGeoipProviderConfig, _Mapping]] = ...) -> None: ...
