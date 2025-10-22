from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CpuUtilizationConfig(_message.Message):
    __slots__ = ("mode",)
    class UtilizationComputeStrategy(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        HOST: _ClassVar[CpuUtilizationConfig.UtilizationComputeStrategy]
        CONTAINER: _ClassVar[CpuUtilizationConfig.UtilizationComputeStrategy]
    HOST: CpuUtilizationConfig.UtilizationComputeStrategy
    CONTAINER: CpuUtilizationConfig.UtilizationComputeStrategy
    MODE_FIELD_NUMBER: _ClassVar[int]
    mode: CpuUtilizationConfig.UtilizationComputeStrategy
    def __init__(self, mode: _Optional[_Union[CpuUtilizationConfig.UtilizationComputeStrategy, str]] = ...) -> None: ...
