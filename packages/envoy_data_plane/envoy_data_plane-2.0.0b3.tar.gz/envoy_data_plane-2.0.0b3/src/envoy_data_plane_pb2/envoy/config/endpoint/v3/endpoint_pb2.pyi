import datetime

from envoy.config.endpoint.v3 import endpoint_components_pb2 as _endpoint_components_pb2
from envoy.type.v3 import percent_pb2 as _percent_pb2
from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from udpa.annotations import status_pb2 as _status_pb2
from udpa.annotations import versioning_pb2 as _versioning_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ClusterLoadAssignment(_message.Message):
    __slots__ = ("cluster_name", "endpoints", "named_endpoints", "policy")
    class Policy(_message.Message):
        __slots__ = ("drop_overloads", "overprovisioning_factor", "endpoint_stale_after", "weighted_priority_health")
        class DropOverload(_message.Message):
            __slots__ = ("category", "drop_percentage")
            CATEGORY_FIELD_NUMBER: _ClassVar[int]
            DROP_PERCENTAGE_FIELD_NUMBER: _ClassVar[int]
            category: str
            drop_percentage: _percent_pb2.FractionalPercent
            def __init__(self, category: _Optional[str] = ..., drop_percentage: _Optional[_Union[_percent_pb2.FractionalPercent, _Mapping]] = ...) -> None: ...
        DROP_OVERLOADS_FIELD_NUMBER: _ClassVar[int]
        OVERPROVISIONING_FACTOR_FIELD_NUMBER: _ClassVar[int]
        ENDPOINT_STALE_AFTER_FIELD_NUMBER: _ClassVar[int]
        WEIGHTED_PRIORITY_HEALTH_FIELD_NUMBER: _ClassVar[int]
        drop_overloads: _containers.RepeatedCompositeFieldContainer[ClusterLoadAssignment.Policy.DropOverload]
        overprovisioning_factor: _wrappers_pb2.UInt32Value
        endpoint_stale_after: _duration_pb2.Duration
        weighted_priority_health: bool
        def __init__(self, drop_overloads: _Optional[_Iterable[_Union[ClusterLoadAssignment.Policy.DropOverload, _Mapping]]] = ..., overprovisioning_factor: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., endpoint_stale_after: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., weighted_priority_health: bool = ...) -> None: ...
    class NamedEndpointsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _endpoint_components_pb2.Endpoint
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_endpoint_components_pb2.Endpoint, _Mapping]] = ...) -> None: ...
    CLUSTER_NAME_FIELD_NUMBER: _ClassVar[int]
    ENDPOINTS_FIELD_NUMBER: _ClassVar[int]
    NAMED_ENDPOINTS_FIELD_NUMBER: _ClassVar[int]
    POLICY_FIELD_NUMBER: _ClassVar[int]
    cluster_name: str
    endpoints: _containers.RepeatedCompositeFieldContainer[_endpoint_components_pb2.LocalityLbEndpoints]
    named_endpoints: _containers.MessageMap[str, _endpoint_components_pb2.Endpoint]
    policy: ClusterLoadAssignment.Policy
    def __init__(self, cluster_name: _Optional[str] = ..., endpoints: _Optional[_Iterable[_Union[_endpoint_components_pb2.LocalityLbEndpoints, _Mapping]]] = ..., named_endpoints: _Optional[_Mapping[str, _endpoint_components_pb2.Endpoint]] = ..., policy: _Optional[_Union[ClusterLoadAssignment.Policy, _Mapping]] = ...) -> None: ...
