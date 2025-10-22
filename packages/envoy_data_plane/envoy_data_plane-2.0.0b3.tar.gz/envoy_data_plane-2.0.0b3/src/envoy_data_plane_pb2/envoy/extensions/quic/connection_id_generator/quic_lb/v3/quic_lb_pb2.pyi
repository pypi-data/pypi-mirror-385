from envoy.config.core.v3 import base_pb2 as _base_pb2
from envoy.extensions.transport_sockets.tls.v3 import secret_pb2 as _secret_pb2
from xds.annotations.v3 import status_pb2 as _status_pb2
from udpa.annotations import status_pb2 as _status_pb2_1
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Config(_message.Message):
    __slots__ = ("server_id", "server_id_base64_encoded", "expected_server_id_length", "nonce_length_bytes", "encryption_parameters", "unencrypted_mode")
    SERVER_ID_FIELD_NUMBER: _ClassVar[int]
    SERVER_ID_BASE64_ENCODED_FIELD_NUMBER: _ClassVar[int]
    EXPECTED_SERVER_ID_LENGTH_FIELD_NUMBER: _ClassVar[int]
    NONCE_LENGTH_BYTES_FIELD_NUMBER: _ClassVar[int]
    ENCRYPTION_PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    UNENCRYPTED_MODE_FIELD_NUMBER: _ClassVar[int]
    server_id: _base_pb2.DataSource
    server_id_base64_encoded: bool
    expected_server_id_length: int
    nonce_length_bytes: int
    encryption_parameters: _secret_pb2.SdsSecretConfig
    unencrypted_mode: bool
    def __init__(self, server_id: _Optional[_Union[_base_pb2.DataSource, _Mapping]] = ..., server_id_base64_encoded: bool = ..., expected_server_id_length: _Optional[int] = ..., nonce_length_bytes: _Optional[int] = ..., encryption_parameters: _Optional[_Union[_secret_pb2.SdsSecretConfig, _Mapping]] = ..., unencrypted_mode: bool = ...) -> None: ...
