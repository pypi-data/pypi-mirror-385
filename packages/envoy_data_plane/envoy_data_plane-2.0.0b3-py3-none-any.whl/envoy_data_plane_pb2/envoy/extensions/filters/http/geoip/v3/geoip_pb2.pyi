from envoy.config.core.v3 import extension_pb2 as _extension_pb2
from xds.annotations.v3 import status_pb2 as _status_pb2
from udpa.annotations import status_pb2 as _status_pb2_1
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Geoip(_message.Message):
    __slots__ = ("xff_config", "provider")
    class XffConfig(_message.Message):
        __slots__ = ("xff_num_trusted_hops",)
        XFF_NUM_TRUSTED_HOPS_FIELD_NUMBER: _ClassVar[int]
        xff_num_trusted_hops: int
        def __init__(self, xff_num_trusted_hops: _Optional[int] = ...) -> None: ...
    XFF_CONFIG_FIELD_NUMBER: _ClassVar[int]
    PROVIDER_FIELD_NUMBER: _ClassVar[int]
    xff_config: Geoip.XffConfig
    provider: _extension_pb2.TypedExtensionConfig
    def __init__(self, xff_config: _Optional[_Union[Geoip.XffConfig, _Mapping]] = ..., provider: _Optional[_Union[_extension_pb2.TypedExtensionConfig, _Mapping]] = ...) -> None: ...
