from envoy.extensions.filters.network.redis_proxy.v3 import redis_proxy_pb2 as _redis_proxy_pb2
from udpa.annotations import status_pb2 as _status_pb2
from udpa.annotations import versioning_pb2 as _versioning_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Redis(_message.Message):
    __slots__ = ("key", "aws_iam")
    KEY_FIELD_NUMBER: _ClassVar[int]
    AWS_IAM_FIELD_NUMBER: _ClassVar[int]
    key: str
    aws_iam: _redis_proxy_pb2.AwsIam
    def __init__(self, key: _Optional[str] = ..., aws_iam: _Optional[_Union[_redis_proxy_pb2.AwsIam, _Mapping]] = ...) -> None: ...
