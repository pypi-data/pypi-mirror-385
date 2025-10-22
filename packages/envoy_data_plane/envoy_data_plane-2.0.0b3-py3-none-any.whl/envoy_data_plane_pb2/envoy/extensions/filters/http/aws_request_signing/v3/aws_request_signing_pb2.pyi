import datetime

from envoy.extensions.common.aws.v3 import credential_provider_pb2 as _credential_provider_pb2
from envoy.type.matcher.v3 import string_pb2 as _string_pb2
from google.protobuf import duration_pb2 as _duration_pb2
from udpa.annotations import status_pb2 as _status_pb2
from udpa.annotations import versioning_pb2 as _versioning_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AwsRequestSigning(_message.Message):
    __slots__ = ("service_name", "region", "host_rewrite", "use_unsigned_payload", "match_excluded_headers", "signing_algorithm", "query_string", "credential_provider")
    class SigningAlgorithm(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        AWS_SIGV4: _ClassVar[AwsRequestSigning.SigningAlgorithm]
        AWS_SIGV4A: _ClassVar[AwsRequestSigning.SigningAlgorithm]
    AWS_SIGV4: AwsRequestSigning.SigningAlgorithm
    AWS_SIGV4A: AwsRequestSigning.SigningAlgorithm
    class QueryString(_message.Message):
        __slots__ = ("expiration_time",)
        EXPIRATION_TIME_FIELD_NUMBER: _ClassVar[int]
        expiration_time: _duration_pb2.Duration
        def __init__(self, expiration_time: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ...) -> None: ...
    SERVICE_NAME_FIELD_NUMBER: _ClassVar[int]
    REGION_FIELD_NUMBER: _ClassVar[int]
    HOST_REWRITE_FIELD_NUMBER: _ClassVar[int]
    USE_UNSIGNED_PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    MATCH_EXCLUDED_HEADERS_FIELD_NUMBER: _ClassVar[int]
    SIGNING_ALGORITHM_FIELD_NUMBER: _ClassVar[int]
    QUERY_STRING_FIELD_NUMBER: _ClassVar[int]
    CREDENTIAL_PROVIDER_FIELD_NUMBER: _ClassVar[int]
    service_name: str
    region: str
    host_rewrite: str
    use_unsigned_payload: bool
    match_excluded_headers: _containers.RepeatedCompositeFieldContainer[_string_pb2.StringMatcher]
    signing_algorithm: AwsRequestSigning.SigningAlgorithm
    query_string: AwsRequestSigning.QueryString
    credential_provider: _credential_provider_pb2.AwsCredentialProvider
    def __init__(self, service_name: _Optional[str] = ..., region: _Optional[str] = ..., host_rewrite: _Optional[str] = ..., use_unsigned_payload: bool = ..., match_excluded_headers: _Optional[_Iterable[_Union[_string_pb2.StringMatcher, _Mapping]]] = ..., signing_algorithm: _Optional[_Union[AwsRequestSigning.SigningAlgorithm, str]] = ..., query_string: _Optional[_Union[AwsRequestSigning.QueryString, _Mapping]] = ..., credential_provider: _Optional[_Union[_credential_provider_pb2.AwsCredentialProvider, _Mapping]] = ...) -> None: ...

class AwsRequestSigningPerRoute(_message.Message):
    __slots__ = ("aws_request_signing", "stat_prefix")
    AWS_REQUEST_SIGNING_FIELD_NUMBER: _ClassVar[int]
    STAT_PREFIX_FIELD_NUMBER: _ClassVar[int]
    aws_request_signing: AwsRequestSigning
    stat_prefix: str
    def __init__(self, aws_request_signing: _Optional[_Union[AwsRequestSigning, _Mapping]] = ..., stat_prefix: _Optional[str] = ...) -> None: ...
