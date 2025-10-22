from envoy.extensions.transport_sockets.tls.v3 import tls_pb2 as _tls_pb2
from udpa.annotations import status_pb2 as _status_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TlsCredentials(_message.Message):
    __slots__ = ("root_certificate_provider", "identity_certificate_provider")
    ROOT_CERTIFICATE_PROVIDER_FIELD_NUMBER: _ClassVar[int]
    IDENTITY_CERTIFICATE_PROVIDER_FIELD_NUMBER: _ClassVar[int]
    root_certificate_provider: _tls_pb2.CommonTlsContext.CertificateProviderInstance
    identity_certificate_provider: _tls_pb2.CommonTlsContext.CertificateProviderInstance
    def __init__(self, root_certificate_provider: _Optional[_Union[_tls_pb2.CommonTlsContext.CertificateProviderInstance, _Mapping]] = ..., identity_certificate_provider: _Optional[_Union[_tls_pb2.CommonTlsContext.CertificateProviderInstance, _Mapping]] = ...) -> None: ...
