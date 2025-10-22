from udpa.annotations import migrate_pb2 as _migrate_pb2
from envoy.api.v2.auth import common_pb2 as _common_pb2
from envoy.api.v2.auth import secret_pb2 as _secret_pb2
from envoy.api.v2.auth import tls_pb2 as _tls_pb2
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar
from envoy.api.v2.auth.common_pb2 import TlsParameters as TlsParameters
from envoy.api.v2.auth.common_pb2 import PrivateKeyProvider as PrivateKeyProvider
from envoy.api.v2.auth.common_pb2 import TlsCertificate as TlsCertificate
from envoy.api.v2.auth.common_pb2 import TlsSessionTicketKeys as TlsSessionTicketKeys
from envoy.api.v2.auth.common_pb2 import CertificateValidationContext as CertificateValidationContext
from envoy.api.v2.auth.secret_pb2 import GenericSecret as GenericSecret
from envoy.api.v2.auth.secret_pb2 import SdsSecretConfig as SdsSecretConfig
from envoy.api.v2.auth.secret_pb2 import Secret as Secret
from envoy.api.v2.auth.tls_pb2 import UpstreamTlsContext as UpstreamTlsContext
from envoy.api.v2.auth.tls_pb2 import DownstreamTlsContext as DownstreamTlsContext
from envoy.api.v2.auth.tls_pb2 import CommonTlsContext as CommonTlsContext

DESCRIPTOR: _descriptor.FileDescriptor
