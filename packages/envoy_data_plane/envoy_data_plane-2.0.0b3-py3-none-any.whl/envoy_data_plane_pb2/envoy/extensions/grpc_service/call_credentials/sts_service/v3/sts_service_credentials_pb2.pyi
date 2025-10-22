from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class StsServiceCredentials(_message.Message):
    __slots__ = ("token_exchange_service_uri", "resource", "audience", "scope", "requested_token_type", "subject_token_path", "subject_token_type", "actor_token_path", "actor_token_type")
    TOKEN_EXCHANGE_SERVICE_URI_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_FIELD_NUMBER: _ClassVar[int]
    AUDIENCE_FIELD_NUMBER: _ClassVar[int]
    SCOPE_FIELD_NUMBER: _ClassVar[int]
    REQUESTED_TOKEN_TYPE_FIELD_NUMBER: _ClassVar[int]
    SUBJECT_TOKEN_PATH_FIELD_NUMBER: _ClassVar[int]
    SUBJECT_TOKEN_TYPE_FIELD_NUMBER: _ClassVar[int]
    ACTOR_TOKEN_PATH_FIELD_NUMBER: _ClassVar[int]
    ACTOR_TOKEN_TYPE_FIELD_NUMBER: _ClassVar[int]
    token_exchange_service_uri: str
    resource: str
    audience: str
    scope: str
    requested_token_type: str
    subject_token_path: str
    subject_token_type: str
    actor_token_path: str
    actor_token_type: str
    def __init__(self, token_exchange_service_uri: _Optional[str] = ..., resource: _Optional[str] = ..., audience: _Optional[str] = ..., scope: _Optional[str] = ..., requested_token_type: _Optional[str] = ..., subject_token_path: _Optional[str] = ..., subject_token_type: _Optional[str] = ..., actor_token_path: _Optional[str] = ..., actor_token_type: _Optional[str] = ...) -> None: ...
