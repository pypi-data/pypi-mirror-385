from envoy.config.core.v3 import base_pb2 as _base_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SPIFFECertValidatorConfig(_message.Message):
    __slots__ = ("trust_domains", "trust_bundles")
    class TrustDomain(_message.Message):
        __slots__ = ("name", "trust_bundle")
        NAME_FIELD_NUMBER: _ClassVar[int]
        TRUST_BUNDLE_FIELD_NUMBER: _ClassVar[int]
        name: str
        trust_bundle: _base_pb2.DataSource
        def __init__(self, name: _Optional[str] = ..., trust_bundle: _Optional[_Union[_base_pb2.DataSource, _Mapping]] = ...) -> None: ...
    TRUST_DOMAINS_FIELD_NUMBER: _ClassVar[int]
    TRUST_BUNDLES_FIELD_NUMBER: _ClassVar[int]
    trust_domains: _containers.RepeatedCompositeFieldContainer[SPIFFECertValidatorConfig.TrustDomain]
    trust_bundles: _base_pb2.DataSource
    def __init__(self, trust_domains: _Optional[_Iterable[_Union[SPIFFECertValidatorConfig.TrustDomain, _Mapping]]] = ..., trust_bundles: _Optional[_Union[_base_pb2.DataSource, _Mapping]] = ...) -> None: ...
