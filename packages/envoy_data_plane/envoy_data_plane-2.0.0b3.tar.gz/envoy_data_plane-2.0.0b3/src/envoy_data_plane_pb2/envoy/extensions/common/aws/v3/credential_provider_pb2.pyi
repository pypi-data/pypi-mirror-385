import datetime

from envoy.config.core.v3 import base_pb2 as _base_pb2
from google.protobuf import duration_pb2 as _duration_pb2
from udpa.annotations import sensitive_pb2 as _sensitive_pb2
from udpa.annotations import status_pb2 as _status_pb2
from validate import validate_pb2 as _validate_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AwsCredentialProvider(_message.Message):
    __slots__ = ("assume_role_with_web_identity_provider", "inline_credential", "credentials_file_provider", "custom_credential_provider_chain", "iam_roles_anywhere_credential_provider", "config_credential_provider", "container_credential_provider", "environment_credential_provider", "instance_profile_credential_provider", "assume_role_credential_provider")
    ASSUME_ROLE_WITH_WEB_IDENTITY_PROVIDER_FIELD_NUMBER: _ClassVar[int]
    INLINE_CREDENTIAL_FIELD_NUMBER: _ClassVar[int]
    CREDENTIALS_FILE_PROVIDER_FIELD_NUMBER: _ClassVar[int]
    CUSTOM_CREDENTIAL_PROVIDER_CHAIN_FIELD_NUMBER: _ClassVar[int]
    IAM_ROLES_ANYWHERE_CREDENTIAL_PROVIDER_FIELD_NUMBER: _ClassVar[int]
    CONFIG_CREDENTIAL_PROVIDER_FIELD_NUMBER: _ClassVar[int]
    CONTAINER_CREDENTIAL_PROVIDER_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_CREDENTIAL_PROVIDER_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_PROFILE_CREDENTIAL_PROVIDER_FIELD_NUMBER: _ClassVar[int]
    ASSUME_ROLE_CREDENTIAL_PROVIDER_FIELD_NUMBER: _ClassVar[int]
    assume_role_with_web_identity_provider: AssumeRoleWithWebIdentityCredentialProvider
    inline_credential: InlineCredentialProvider
    credentials_file_provider: CredentialsFileCredentialProvider
    custom_credential_provider_chain: bool
    iam_roles_anywhere_credential_provider: IAMRolesAnywhereCredentialProvider
    config_credential_provider: ConfigCredentialProvider
    container_credential_provider: ContainerCredentialProvider
    environment_credential_provider: EnvironmentCredentialProvider
    instance_profile_credential_provider: InstanceProfileCredentialProvider
    assume_role_credential_provider: AssumeRoleCredentialProvider
    def __init__(self, assume_role_with_web_identity_provider: _Optional[_Union[AssumeRoleWithWebIdentityCredentialProvider, _Mapping]] = ..., inline_credential: _Optional[_Union[InlineCredentialProvider, _Mapping]] = ..., credentials_file_provider: _Optional[_Union[CredentialsFileCredentialProvider, _Mapping]] = ..., custom_credential_provider_chain: bool = ..., iam_roles_anywhere_credential_provider: _Optional[_Union[IAMRolesAnywhereCredentialProvider, _Mapping]] = ..., config_credential_provider: _Optional[_Union[ConfigCredentialProvider, _Mapping]] = ..., container_credential_provider: _Optional[_Union[ContainerCredentialProvider, _Mapping]] = ..., environment_credential_provider: _Optional[_Union[EnvironmentCredentialProvider, _Mapping]] = ..., instance_profile_credential_provider: _Optional[_Union[InstanceProfileCredentialProvider, _Mapping]] = ..., assume_role_credential_provider: _Optional[_Union[AssumeRoleCredentialProvider, _Mapping]] = ...) -> None: ...

class InlineCredentialProvider(_message.Message):
    __slots__ = ("access_key_id", "secret_access_key", "session_token")
    ACCESS_KEY_ID_FIELD_NUMBER: _ClassVar[int]
    SECRET_ACCESS_KEY_FIELD_NUMBER: _ClassVar[int]
    SESSION_TOKEN_FIELD_NUMBER: _ClassVar[int]
    access_key_id: str
    secret_access_key: str
    session_token: str
    def __init__(self, access_key_id: _Optional[str] = ..., secret_access_key: _Optional[str] = ..., session_token: _Optional[str] = ...) -> None: ...

class AssumeRoleWithWebIdentityCredentialProvider(_message.Message):
    __slots__ = ("web_identity_token_data_source", "role_arn", "role_session_name")
    WEB_IDENTITY_TOKEN_DATA_SOURCE_FIELD_NUMBER: _ClassVar[int]
    ROLE_ARN_FIELD_NUMBER: _ClassVar[int]
    ROLE_SESSION_NAME_FIELD_NUMBER: _ClassVar[int]
    web_identity_token_data_source: _base_pb2.DataSource
    role_arn: str
    role_session_name: str
    def __init__(self, web_identity_token_data_source: _Optional[_Union[_base_pb2.DataSource, _Mapping]] = ..., role_arn: _Optional[str] = ..., role_session_name: _Optional[str] = ...) -> None: ...

class CredentialsFileCredentialProvider(_message.Message):
    __slots__ = ("credentials_data_source", "profile")
    CREDENTIALS_DATA_SOURCE_FIELD_NUMBER: _ClassVar[int]
    PROFILE_FIELD_NUMBER: _ClassVar[int]
    credentials_data_source: _base_pb2.DataSource
    profile: str
    def __init__(self, credentials_data_source: _Optional[_Union[_base_pb2.DataSource, _Mapping]] = ..., profile: _Optional[str] = ...) -> None: ...

class IAMRolesAnywhereCredentialProvider(_message.Message):
    __slots__ = ("role_arn", "certificate", "certificate_chain", "private_key", "trust_anchor_arn", "profile_arn", "role_session_name", "session_duration")
    ROLE_ARN_FIELD_NUMBER: _ClassVar[int]
    CERTIFICATE_FIELD_NUMBER: _ClassVar[int]
    CERTIFICATE_CHAIN_FIELD_NUMBER: _ClassVar[int]
    PRIVATE_KEY_FIELD_NUMBER: _ClassVar[int]
    TRUST_ANCHOR_ARN_FIELD_NUMBER: _ClassVar[int]
    PROFILE_ARN_FIELD_NUMBER: _ClassVar[int]
    ROLE_SESSION_NAME_FIELD_NUMBER: _ClassVar[int]
    SESSION_DURATION_FIELD_NUMBER: _ClassVar[int]
    role_arn: str
    certificate: _base_pb2.DataSource
    certificate_chain: _base_pb2.DataSource
    private_key: _base_pb2.DataSource
    trust_anchor_arn: str
    profile_arn: str
    role_session_name: str
    session_duration: _duration_pb2.Duration
    def __init__(self, role_arn: _Optional[str] = ..., certificate: _Optional[_Union[_base_pb2.DataSource, _Mapping]] = ..., certificate_chain: _Optional[_Union[_base_pb2.DataSource, _Mapping]] = ..., private_key: _Optional[_Union[_base_pb2.DataSource, _Mapping]] = ..., trust_anchor_arn: _Optional[str] = ..., profile_arn: _Optional[str] = ..., role_session_name: _Optional[str] = ..., session_duration: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ...) -> None: ...

class ConfigCredentialProvider(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ContainerCredentialProvider(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class EnvironmentCredentialProvider(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class InstanceProfileCredentialProvider(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class AssumeRoleCredentialProvider(_message.Message):
    __slots__ = ("role_arn", "role_session_name", "external_id", "session_duration", "credential_provider")
    ROLE_ARN_FIELD_NUMBER: _ClassVar[int]
    ROLE_SESSION_NAME_FIELD_NUMBER: _ClassVar[int]
    EXTERNAL_ID_FIELD_NUMBER: _ClassVar[int]
    SESSION_DURATION_FIELD_NUMBER: _ClassVar[int]
    CREDENTIAL_PROVIDER_FIELD_NUMBER: _ClassVar[int]
    role_arn: str
    role_session_name: str
    external_id: str
    session_duration: _duration_pb2.Duration
    credential_provider: AwsCredentialProvider
    def __init__(self, role_arn: _Optional[str] = ..., role_session_name: _Optional[str] = ..., external_id: _Optional[str] = ..., session_duration: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., credential_provider: _Optional[_Union[AwsCredentialProvider, _Mapping]] = ...) -> None: ...
