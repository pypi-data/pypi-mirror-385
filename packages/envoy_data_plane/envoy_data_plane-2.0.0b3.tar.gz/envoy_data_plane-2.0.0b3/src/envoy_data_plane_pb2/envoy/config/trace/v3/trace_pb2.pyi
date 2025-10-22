from envoy.config.trace.v3 import datadog_pb2 as _datadog_pb2
from envoy.config.trace.v3 import dynamic_ot_pb2 as _dynamic_ot_pb2
from envoy.config.trace.v3 import http_tracer_pb2 as _http_tracer_pb2
from envoy.config.trace.v3 import lightstep_pb2 as _lightstep_pb2
from envoy.config.trace.v3 import opentelemetry_pb2 as _opentelemetry_pb2
from envoy.config.trace.v3 import service_pb2 as _service_pb2
from envoy.config.trace.v3 import zipkin_pb2 as _zipkin_pb2
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar
from envoy.config.trace.v3.datadog_pb2 import DatadogRemoteConfig as DatadogRemoteConfig
from envoy.config.trace.v3.datadog_pb2 import DatadogConfig as DatadogConfig
from envoy.config.trace.v3.dynamic_ot_pb2 import DynamicOtConfig as DynamicOtConfig
from envoy.config.trace.v3.http_tracer_pb2 import Tracing as Tracing
from envoy.config.trace.v3.lightstep_pb2 import LightstepConfig as LightstepConfig
from envoy.config.trace.v3.opentelemetry_pb2 import OpenTelemetryConfig as OpenTelemetryConfig
from envoy.config.trace.v3.service_pb2 import TraceServiceConfig as TraceServiceConfig
from envoy.config.trace.v3.zipkin_pb2 import ZipkinConfig as ZipkinConfig

DESCRIPTOR: _descriptor.FileDescriptor
