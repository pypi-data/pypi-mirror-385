import datetime

from google.protobuf import timestamp_pb2 as _timestamp_pb2
from udpa.annotations import status_pb2 as _status_pb2
from udpa.annotations import versioning_pb2 as _versioning_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Certificates(_message.Message):
    __slots__ = ("certificates",)
    CERTIFICATES_FIELD_NUMBER: _ClassVar[int]
    certificates: _containers.RepeatedCompositeFieldContainer[Certificate]
    def __init__(self, certificates: _Optional[_Iterable[_Union[Certificate, _Mapping]]] = ...) -> None: ...

class Certificate(_message.Message):
    __slots__ = ("ca_cert", "cert_chain")
    CA_CERT_FIELD_NUMBER: _ClassVar[int]
    CERT_CHAIN_FIELD_NUMBER: _ClassVar[int]
    ca_cert: _containers.RepeatedCompositeFieldContainer[CertificateDetails]
    cert_chain: _containers.RepeatedCompositeFieldContainer[CertificateDetails]
    def __init__(self, ca_cert: _Optional[_Iterable[_Union[CertificateDetails, _Mapping]]] = ..., cert_chain: _Optional[_Iterable[_Union[CertificateDetails, _Mapping]]] = ...) -> None: ...

class CertificateDetails(_message.Message):
    __slots__ = ("path", "serial_number", "subject_alt_names", "days_until_expiration", "valid_from", "expiration_time", "ocsp_details")
    class OcspDetails(_message.Message):
        __slots__ = ("valid_from", "expiration")
        VALID_FROM_FIELD_NUMBER: _ClassVar[int]
        EXPIRATION_FIELD_NUMBER: _ClassVar[int]
        valid_from: _timestamp_pb2.Timestamp
        expiration: _timestamp_pb2.Timestamp
        def __init__(self, valid_from: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., expiration: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
    PATH_FIELD_NUMBER: _ClassVar[int]
    SERIAL_NUMBER_FIELD_NUMBER: _ClassVar[int]
    SUBJECT_ALT_NAMES_FIELD_NUMBER: _ClassVar[int]
    DAYS_UNTIL_EXPIRATION_FIELD_NUMBER: _ClassVar[int]
    VALID_FROM_FIELD_NUMBER: _ClassVar[int]
    EXPIRATION_TIME_FIELD_NUMBER: _ClassVar[int]
    OCSP_DETAILS_FIELD_NUMBER: _ClassVar[int]
    path: str
    serial_number: str
    subject_alt_names: _containers.RepeatedCompositeFieldContainer[SubjectAlternateName]
    days_until_expiration: int
    valid_from: _timestamp_pb2.Timestamp
    expiration_time: _timestamp_pb2.Timestamp
    ocsp_details: CertificateDetails.OcspDetails
    def __init__(self, path: _Optional[str] = ..., serial_number: _Optional[str] = ..., subject_alt_names: _Optional[_Iterable[_Union[SubjectAlternateName, _Mapping]]] = ..., days_until_expiration: _Optional[int] = ..., valid_from: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., expiration_time: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., ocsp_details: _Optional[_Union[CertificateDetails.OcspDetails, _Mapping]] = ...) -> None: ...

class SubjectAlternateName(_message.Message):
    __slots__ = ("dns", "uri", "ip_address")
    DNS_FIELD_NUMBER: _ClassVar[int]
    URI_FIELD_NUMBER: _ClassVar[int]
    IP_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    dns: str
    uri: str
    ip_address: str
    def __init__(self, dns: _Optional[str] = ..., uri: _Optional[str] = ..., ip_address: _Optional[str] = ...) -> None: ...
