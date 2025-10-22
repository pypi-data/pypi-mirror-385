from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class LightstepConfig(_message.Message):
    __slots__ = ("collector_cluster", "access_token_file", "propagation_modes")
    class PropagationMode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ENVOY: _ClassVar[LightstepConfig.PropagationMode]
        LIGHTSTEP: _ClassVar[LightstepConfig.PropagationMode]
        B3: _ClassVar[LightstepConfig.PropagationMode]
        TRACE_CONTEXT: _ClassVar[LightstepConfig.PropagationMode]
    ENVOY: LightstepConfig.PropagationMode
    LIGHTSTEP: LightstepConfig.PropagationMode
    B3: LightstepConfig.PropagationMode
    TRACE_CONTEXT: LightstepConfig.PropagationMode
    COLLECTOR_CLUSTER_FIELD_NUMBER: _ClassVar[int]
    ACCESS_TOKEN_FILE_FIELD_NUMBER: _ClassVar[int]
    PROPAGATION_MODES_FIELD_NUMBER: _ClassVar[int]
    collector_cluster: str
    access_token_file: str
    propagation_modes: _containers.RepeatedScalarFieldContainer[LightstepConfig.PropagationMode]
    def __init__(self, collector_cluster: _Optional[str] = ..., access_token_file: _Optional[str] = ..., propagation_modes: _Optional[_Iterable[_Union[LightstepConfig.PropagationMode, str]]] = ...) -> None: ...
