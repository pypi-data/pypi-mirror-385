from envoy.extensions.load_balancing_policies.common.v3 import common_pb2 as _common_pb2
from udpa.annotations import status_pb2 as _status_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Random(_message.Message):
    __slots__ = ("locality_lb_config",)
    LOCALITY_LB_CONFIG_FIELD_NUMBER: _ClassVar[int]
    locality_lb_config: _common_pb2.LocalityLbConfig
    def __init__(self, locality_lb_config: _Optional[_Union[_common_pb2.LocalityLbConfig, _Mapping]] = ...) -> None: ...
