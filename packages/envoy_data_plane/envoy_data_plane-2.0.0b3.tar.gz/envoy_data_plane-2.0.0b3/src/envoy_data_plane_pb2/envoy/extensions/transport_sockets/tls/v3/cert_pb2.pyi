from envoy.extensions.transport_sockets.tls.v3 import common_pb2 as _common_pb2
from envoy.extensions.transport_sockets.tls.v3 import secret_pb2 as _secret_pb2
from envoy.extensions.transport_sockets.tls.v3 import tls_pb2 as _tls_pb2
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar
from envoy.extensions.transport_sockets.tls.v3.common_pb2 import TlsParameters as TlsParameters
from envoy.extensions.transport_sockets.tls.v3.common_pb2 import PrivateKeyProvider as PrivateKeyProvider
from envoy.extensions.transport_sockets.tls.v3.common_pb2 import TlsCertificate as TlsCertificate
from envoy.extensions.transport_sockets.tls.v3.common_pb2 import TlsSessionTicketKeys as TlsSessionTicketKeys
from envoy.extensions.transport_sockets.tls.v3.common_pb2 import CertificateProviderPluginInstance as CertificateProviderPluginInstance
from envoy.extensions.transport_sockets.tls.v3.common_pb2 import SubjectAltNameMatcher as SubjectAltNameMatcher
from envoy.extensions.transport_sockets.tls.v3.common_pb2 import CertificateValidationContext as CertificateValidationContext
from envoy.extensions.transport_sockets.tls.v3.secret_pb2 import GenericSecret as GenericSecret
from envoy.extensions.transport_sockets.tls.v3.secret_pb2 import SdsSecretConfig as SdsSecretConfig
from envoy.extensions.transport_sockets.tls.v3.secret_pb2 import Secret as Secret
from envoy.extensions.transport_sockets.tls.v3.tls_pb2 import UpstreamTlsContext as UpstreamTlsContext
from envoy.extensions.transport_sockets.tls.v3.tls_pb2 import DownstreamTlsContext as DownstreamTlsContext
from envoy.extensions.transport_sockets.tls.v3.tls_pb2 import TlsKeyLog as TlsKeyLog
from envoy.extensions.transport_sockets.tls.v3.tls_pb2 import CommonTlsContext as CommonTlsContext

DESCRIPTOR: _descriptor.FileDescriptor
