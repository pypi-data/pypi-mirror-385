from envoy.config.core.v3 import extension_pb2 as _extension_pb2
from envoy.config.core.v3 import grpc_service_pb2 as _grpc_service_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from opentelemetry.proto.common.v1 import common_pb2 as _common_pb2
from xds.type.matcher.v3 import matcher_pb2 as _matcher_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SinkConfig(_message.Message):
    __slots__ = ("grpc_service", "resource_detectors", "report_counters_as_deltas", "report_histograms_as_deltas", "emit_tags_as_attributes", "use_tag_extracted_name", "prefix", "custom_metric_conversions")
    class ConversionAction(_message.Message):
        __slots__ = ("metric_name", "static_metric_labels")
        METRIC_NAME_FIELD_NUMBER: _ClassVar[int]
        STATIC_METRIC_LABELS_FIELD_NUMBER: _ClassVar[int]
        metric_name: str
        static_metric_labels: _containers.RepeatedCompositeFieldContainer[_common_pb2.KeyValue]
        def __init__(self, metric_name: _Optional[str] = ..., static_metric_labels: _Optional[_Iterable[_Union[_common_pb2.KeyValue, _Mapping]]] = ...) -> None: ...
    GRPC_SERVICE_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_DETECTORS_FIELD_NUMBER: _ClassVar[int]
    REPORT_COUNTERS_AS_DELTAS_FIELD_NUMBER: _ClassVar[int]
    REPORT_HISTOGRAMS_AS_DELTAS_FIELD_NUMBER: _ClassVar[int]
    EMIT_TAGS_AS_ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    USE_TAG_EXTRACTED_NAME_FIELD_NUMBER: _ClassVar[int]
    PREFIX_FIELD_NUMBER: _ClassVar[int]
    CUSTOM_METRIC_CONVERSIONS_FIELD_NUMBER: _ClassVar[int]
    grpc_service: _grpc_service_pb2.GrpcService
    resource_detectors: _containers.RepeatedCompositeFieldContainer[_extension_pb2.TypedExtensionConfig]
    report_counters_as_deltas: bool
    report_histograms_as_deltas: bool
    emit_tags_as_attributes: _wrappers_pb2.BoolValue
    use_tag_extracted_name: _wrappers_pb2.BoolValue
    prefix: str
    custom_metric_conversions: _matcher_pb2.Matcher
    def __init__(self, grpc_service: _Optional[_Union[_grpc_service_pb2.GrpcService, _Mapping]] = ..., resource_detectors: _Optional[_Iterable[_Union[_extension_pb2.TypedExtensionConfig, _Mapping]]] = ..., report_counters_as_deltas: bool = ..., report_histograms_as_deltas: bool = ..., emit_tags_as_attributes: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., use_tag_extracted_name: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., prefix: _Optional[str] = ..., custom_metric_conversions: _Optional[_Union[_matcher_pb2.Matcher, _Mapping]] = ...) -> None: ...
