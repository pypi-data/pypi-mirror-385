import datetime

from envoy.config.cluster.v3 import circuit_breaker_pb2 as _circuit_breaker_pb2
from envoy.config.cluster.v3 import filter_pb2 as _filter_pb2
from envoy.config.cluster.v3 import outlier_detection_pb2 as _outlier_detection_pb2
from envoy.config.core.v3 import address_pb2 as _address_pb2
from envoy.config.core.v3 import base_pb2 as _base_pb2
from envoy.config.core.v3 import config_source_pb2 as _config_source_pb2
from envoy.config.core.v3 import extension_pb2 as _extension_pb2
from envoy.config.core.v3 import health_check_pb2 as _health_check_pb2
from envoy.config.core.v3 import protocol_pb2 as _protocol_pb2
from envoy.config.core.v3 import resolver_pb2 as _resolver_pb2
from envoy.config.endpoint.v3 import endpoint_pb2 as _endpoint_pb2
from envoy.type.metadata.v3 import metadata_pb2 as _metadata_pb2
from envoy.type.v3 import percent_pb2 as _percent_pb2
from google.protobuf import any_pb2 as _any_pb2
from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from xds.core.v3 import collection_entry_pb2 as _collection_entry_pb2
from envoy.annotations import deprecation_pb2 as _deprecation_pb2
from udpa.annotations import migrate_pb2 as _migrate_pb2
from udpa.annotations import security_pb2 as _security_pb2
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

class ClusterCollection(_message.Message):
    __slots__ = ("entries",)
    ENTRIES_FIELD_NUMBER: _ClassVar[int]
    entries: _collection_entry_pb2.CollectionEntry
    def __init__(self, entries: _Optional[_Union[_collection_entry_pb2.CollectionEntry, _Mapping]] = ...) -> None: ...

class Cluster(_message.Message):
    __slots__ = ("transport_socket_matches", "name", "alt_stat_name", "type", "cluster_type", "eds_cluster_config", "connect_timeout", "per_connection_buffer_limit_bytes", "lb_policy", "load_assignment", "health_checks", "max_requests_per_connection", "circuit_breakers", "upstream_http_protocol_options", "common_http_protocol_options", "http_protocol_options", "http2_protocol_options", "typed_extension_protocol_options", "dns_refresh_rate", "dns_jitter", "dns_failure_refresh_rate", "respect_dns_ttl", "dns_lookup_family", "dns_resolvers", "use_tcp_for_dns_lookups", "dns_resolution_config", "typed_dns_resolver_config", "wait_for_warm_on_init", "outlier_detection", "cleanup_interval", "upstream_bind_config", "lb_subset_config", "ring_hash_lb_config", "maglev_lb_config", "original_dst_lb_config", "least_request_lb_config", "round_robin_lb_config", "common_lb_config", "transport_socket", "metadata", "protocol_selection", "upstream_connection_options", "close_connections_on_host_health_failure", "ignore_health_on_host_removal", "filters", "load_balancing_policy", "lrs_server", "lrs_report_endpoint_metrics", "track_timeout_budgets", "upstream_config", "track_cluster_stats", "preconnect_policy", "connection_pool_per_downstream_connection")
    class DiscoveryType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        STATIC: _ClassVar[Cluster.DiscoveryType]
        STRICT_DNS: _ClassVar[Cluster.DiscoveryType]
        LOGICAL_DNS: _ClassVar[Cluster.DiscoveryType]
        EDS: _ClassVar[Cluster.DiscoveryType]
        ORIGINAL_DST: _ClassVar[Cluster.DiscoveryType]
    STATIC: Cluster.DiscoveryType
    STRICT_DNS: Cluster.DiscoveryType
    LOGICAL_DNS: Cluster.DiscoveryType
    EDS: Cluster.DiscoveryType
    ORIGINAL_DST: Cluster.DiscoveryType
    class LbPolicy(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ROUND_ROBIN: _ClassVar[Cluster.LbPolicy]
        LEAST_REQUEST: _ClassVar[Cluster.LbPolicy]
        RING_HASH: _ClassVar[Cluster.LbPolicy]
        RANDOM: _ClassVar[Cluster.LbPolicy]
        MAGLEV: _ClassVar[Cluster.LbPolicy]
        CLUSTER_PROVIDED: _ClassVar[Cluster.LbPolicy]
        LOAD_BALANCING_POLICY_CONFIG: _ClassVar[Cluster.LbPolicy]
    ROUND_ROBIN: Cluster.LbPolicy
    LEAST_REQUEST: Cluster.LbPolicy
    RING_HASH: Cluster.LbPolicy
    RANDOM: Cluster.LbPolicy
    MAGLEV: Cluster.LbPolicy
    CLUSTER_PROVIDED: Cluster.LbPolicy
    LOAD_BALANCING_POLICY_CONFIG: Cluster.LbPolicy
    class DnsLookupFamily(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        AUTO: _ClassVar[Cluster.DnsLookupFamily]
        V4_ONLY: _ClassVar[Cluster.DnsLookupFamily]
        V6_ONLY: _ClassVar[Cluster.DnsLookupFamily]
        V4_PREFERRED: _ClassVar[Cluster.DnsLookupFamily]
        ALL: _ClassVar[Cluster.DnsLookupFamily]
    AUTO: Cluster.DnsLookupFamily
    V4_ONLY: Cluster.DnsLookupFamily
    V6_ONLY: Cluster.DnsLookupFamily
    V4_PREFERRED: Cluster.DnsLookupFamily
    ALL: Cluster.DnsLookupFamily
    class ClusterProtocolSelection(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        USE_CONFIGURED_PROTOCOL: _ClassVar[Cluster.ClusterProtocolSelection]
        USE_DOWNSTREAM_PROTOCOL: _ClassVar[Cluster.ClusterProtocolSelection]
    USE_CONFIGURED_PROTOCOL: Cluster.ClusterProtocolSelection
    USE_DOWNSTREAM_PROTOCOL: Cluster.ClusterProtocolSelection
    class TransportSocketMatch(_message.Message):
        __slots__ = ("name", "match", "transport_socket")
        NAME_FIELD_NUMBER: _ClassVar[int]
        MATCH_FIELD_NUMBER: _ClassVar[int]
        TRANSPORT_SOCKET_FIELD_NUMBER: _ClassVar[int]
        name: str
        match: _struct_pb2.Struct
        transport_socket: _base_pb2.TransportSocket
        def __init__(self, name: _Optional[str] = ..., match: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., transport_socket: _Optional[_Union[_base_pb2.TransportSocket, _Mapping]] = ...) -> None: ...
    class CustomClusterType(_message.Message):
        __slots__ = ("name", "typed_config")
        NAME_FIELD_NUMBER: _ClassVar[int]
        TYPED_CONFIG_FIELD_NUMBER: _ClassVar[int]
        name: str
        typed_config: _any_pb2.Any
        def __init__(self, name: _Optional[str] = ..., typed_config: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...
    class EdsClusterConfig(_message.Message):
        __slots__ = ("eds_config", "service_name")
        EDS_CONFIG_FIELD_NUMBER: _ClassVar[int]
        SERVICE_NAME_FIELD_NUMBER: _ClassVar[int]
        eds_config: _config_source_pb2.ConfigSource
        service_name: str
        def __init__(self, eds_config: _Optional[_Union[_config_source_pb2.ConfigSource, _Mapping]] = ..., service_name: _Optional[str] = ...) -> None: ...
    class LbSubsetConfig(_message.Message):
        __slots__ = ("fallback_policy", "default_subset", "subset_selectors", "locality_weight_aware", "scale_locality_weight", "panic_mode_any", "list_as_any", "metadata_fallback_policy")
        class LbSubsetFallbackPolicy(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            NO_FALLBACK: _ClassVar[Cluster.LbSubsetConfig.LbSubsetFallbackPolicy]
            ANY_ENDPOINT: _ClassVar[Cluster.LbSubsetConfig.LbSubsetFallbackPolicy]
            DEFAULT_SUBSET: _ClassVar[Cluster.LbSubsetConfig.LbSubsetFallbackPolicy]
        NO_FALLBACK: Cluster.LbSubsetConfig.LbSubsetFallbackPolicy
        ANY_ENDPOINT: Cluster.LbSubsetConfig.LbSubsetFallbackPolicy
        DEFAULT_SUBSET: Cluster.LbSubsetConfig.LbSubsetFallbackPolicy
        class LbSubsetMetadataFallbackPolicy(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            METADATA_NO_FALLBACK: _ClassVar[Cluster.LbSubsetConfig.LbSubsetMetadataFallbackPolicy]
            FALLBACK_LIST: _ClassVar[Cluster.LbSubsetConfig.LbSubsetMetadataFallbackPolicy]
        METADATA_NO_FALLBACK: Cluster.LbSubsetConfig.LbSubsetMetadataFallbackPolicy
        FALLBACK_LIST: Cluster.LbSubsetConfig.LbSubsetMetadataFallbackPolicy
        class LbSubsetSelector(_message.Message):
            __slots__ = ("keys", "single_host_per_subset", "fallback_policy", "fallback_keys_subset")
            class LbSubsetSelectorFallbackPolicy(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
                __slots__ = ()
                NOT_DEFINED: _ClassVar[Cluster.LbSubsetConfig.LbSubsetSelector.LbSubsetSelectorFallbackPolicy]
                NO_FALLBACK: _ClassVar[Cluster.LbSubsetConfig.LbSubsetSelector.LbSubsetSelectorFallbackPolicy]
                ANY_ENDPOINT: _ClassVar[Cluster.LbSubsetConfig.LbSubsetSelector.LbSubsetSelectorFallbackPolicy]
                DEFAULT_SUBSET: _ClassVar[Cluster.LbSubsetConfig.LbSubsetSelector.LbSubsetSelectorFallbackPolicy]
                KEYS_SUBSET: _ClassVar[Cluster.LbSubsetConfig.LbSubsetSelector.LbSubsetSelectorFallbackPolicy]
            NOT_DEFINED: Cluster.LbSubsetConfig.LbSubsetSelector.LbSubsetSelectorFallbackPolicy
            NO_FALLBACK: Cluster.LbSubsetConfig.LbSubsetSelector.LbSubsetSelectorFallbackPolicy
            ANY_ENDPOINT: Cluster.LbSubsetConfig.LbSubsetSelector.LbSubsetSelectorFallbackPolicy
            DEFAULT_SUBSET: Cluster.LbSubsetConfig.LbSubsetSelector.LbSubsetSelectorFallbackPolicy
            KEYS_SUBSET: Cluster.LbSubsetConfig.LbSubsetSelector.LbSubsetSelectorFallbackPolicy
            KEYS_FIELD_NUMBER: _ClassVar[int]
            SINGLE_HOST_PER_SUBSET_FIELD_NUMBER: _ClassVar[int]
            FALLBACK_POLICY_FIELD_NUMBER: _ClassVar[int]
            FALLBACK_KEYS_SUBSET_FIELD_NUMBER: _ClassVar[int]
            keys: _containers.RepeatedScalarFieldContainer[str]
            single_host_per_subset: bool
            fallback_policy: Cluster.LbSubsetConfig.LbSubsetSelector.LbSubsetSelectorFallbackPolicy
            fallback_keys_subset: _containers.RepeatedScalarFieldContainer[str]
            def __init__(self, keys: _Optional[_Iterable[str]] = ..., single_host_per_subset: bool = ..., fallback_policy: _Optional[_Union[Cluster.LbSubsetConfig.LbSubsetSelector.LbSubsetSelectorFallbackPolicy, str]] = ..., fallback_keys_subset: _Optional[_Iterable[str]] = ...) -> None: ...
        FALLBACK_POLICY_FIELD_NUMBER: _ClassVar[int]
        DEFAULT_SUBSET_FIELD_NUMBER: _ClassVar[int]
        SUBSET_SELECTORS_FIELD_NUMBER: _ClassVar[int]
        LOCALITY_WEIGHT_AWARE_FIELD_NUMBER: _ClassVar[int]
        SCALE_LOCALITY_WEIGHT_FIELD_NUMBER: _ClassVar[int]
        PANIC_MODE_ANY_FIELD_NUMBER: _ClassVar[int]
        LIST_AS_ANY_FIELD_NUMBER: _ClassVar[int]
        METADATA_FALLBACK_POLICY_FIELD_NUMBER: _ClassVar[int]
        fallback_policy: Cluster.LbSubsetConfig.LbSubsetFallbackPolicy
        default_subset: _struct_pb2.Struct
        subset_selectors: _containers.RepeatedCompositeFieldContainer[Cluster.LbSubsetConfig.LbSubsetSelector]
        locality_weight_aware: bool
        scale_locality_weight: bool
        panic_mode_any: bool
        list_as_any: bool
        metadata_fallback_policy: Cluster.LbSubsetConfig.LbSubsetMetadataFallbackPolicy
        def __init__(self, fallback_policy: _Optional[_Union[Cluster.LbSubsetConfig.LbSubsetFallbackPolicy, str]] = ..., default_subset: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., subset_selectors: _Optional[_Iterable[_Union[Cluster.LbSubsetConfig.LbSubsetSelector, _Mapping]]] = ..., locality_weight_aware: bool = ..., scale_locality_weight: bool = ..., panic_mode_any: bool = ..., list_as_any: bool = ..., metadata_fallback_policy: _Optional[_Union[Cluster.LbSubsetConfig.LbSubsetMetadataFallbackPolicy, str]] = ...) -> None: ...
    class SlowStartConfig(_message.Message):
        __slots__ = ("slow_start_window", "aggression", "min_weight_percent")
        SLOW_START_WINDOW_FIELD_NUMBER: _ClassVar[int]
        AGGRESSION_FIELD_NUMBER: _ClassVar[int]
        MIN_WEIGHT_PERCENT_FIELD_NUMBER: _ClassVar[int]
        slow_start_window: _duration_pb2.Duration
        aggression: _base_pb2.RuntimeDouble
        min_weight_percent: _percent_pb2.Percent
        def __init__(self, slow_start_window: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., aggression: _Optional[_Union[_base_pb2.RuntimeDouble, _Mapping]] = ..., min_weight_percent: _Optional[_Union[_percent_pb2.Percent, _Mapping]] = ...) -> None: ...
    class RoundRobinLbConfig(_message.Message):
        __slots__ = ("slow_start_config",)
        SLOW_START_CONFIG_FIELD_NUMBER: _ClassVar[int]
        slow_start_config: Cluster.SlowStartConfig
        def __init__(self, slow_start_config: _Optional[_Union[Cluster.SlowStartConfig, _Mapping]] = ...) -> None: ...
    class LeastRequestLbConfig(_message.Message):
        __slots__ = ("choice_count", "active_request_bias", "slow_start_config")
        CHOICE_COUNT_FIELD_NUMBER: _ClassVar[int]
        ACTIVE_REQUEST_BIAS_FIELD_NUMBER: _ClassVar[int]
        SLOW_START_CONFIG_FIELD_NUMBER: _ClassVar[int]
        choice_count: _wrappers_pb2.UInt32Value
        active_request_bias: _base_pb2.RuntimeDouble
        slow_start_config: Cluster.SlowStartConfig
        def __init__(self, choice_count: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., active_request_bias: _Optional[_Union[_base_pb2.RuntimeDouble, _Mapping]] = ..., slow_start_config: _Optional[_Union[Cluster.SlowStartConfig, _Mapping]] = ...) -> None: ...
    class RingHashLbConfig(_message.Message):
        __slots__ = ("minimum_ring_size", "hash_function", "maximum_ring_size")
        class HashFunction(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            XX_HASH: _ClassVar[Cluster.RingHashLbConfig.HashFunction]
            MURMUR_HASH_2: _ClassVar[Cluster.RingHashLbConfig.HashFunction]
        XX_HASH: Cluster.RingHashLbConfig.HashFunction
        MURMUR_HASH_2: Cluster.RingHashLbConfig.HashFunction
        MINIMUM_RING_SIZE_FIELD_NUMBER: _ClassVar[int]
        HASH_FUNCTION_FIELD_NUMBER: _ClassVar[int]
        MAXIMUM_RING_SIZE_FIELD_NUMBER: _ClassVar[int]
        minimum_ring_size: _wrappers_pb2.UInt64Value
        hash_function: Cluster.RingHashLbConfig.HashFunction
        maximum_ring_size: _wrappers_pb2.UInt64Value
        def __init__(self, minimum_ring_size: _Optional[_Union[_wrappers_pb2.UInt64Value, _Mapping]] = ..., hash_function: _Optional[_Union[Cluster.RingHashLbConfig.HashFunction, str]] = ..., maximum_ring_size: _Optional[_Union[_wrappers_pb2.UInt64Value, _Mapping]] = ...) -> None: ...
    class MaglevLbConfig(_message.Message):
        __slots__ = ("table_size",)
        TABLE_SIZE_FIELD_NUMBER: _ClassVar[int]
        table_size: _wrappers_pb2.UInt64Value
        def __init__(self, table_size: _Optional[_Union[_wrappers_pb2.UInt64Value, _Mapping]] = ...) -> None: ...
    class OriginalDstLbConfig(_message.Message):
        __slots__ = ("use_http_header", "http_header_name", "upstream_port_override", "metadata_key")
        USE_HTTP_HEADER_FIELD_NUMBER: _ClassVar[int]
        HTTP_HEADER_NAME_FIELD_NUMBER: _ClassVar[int]
        UPSTREAM_PORT_OVERRIDE_FIELD_NUMBER: _ClassVar[int]
        METADATA_KEY_FIELD_NUMBER: _ClassVar[int]
        use_http_header: bool
        http_header_name: str
        upstream_port_override: _wrappers_pb2.UInt32Value
        metadata_key: _metadata_pb2.MetadataKey
        def __init__(self, use_http_header: bool = ..., http_header_name: _Optional[str] = ..., upstream_port_override: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., metadata_key: _Optional[_Union[_metadata_pb2.MetadataKey, _Mapping]] = ...) -> None: ...
    class CommonLbConfig(_message.Message):
        __slots__ = ("healthy_panic_threshold", "zone_aware_lb_config", "locality_weighted_lb_config", "update_merge_window", "ignore_new_hosts_until_first_hc", "close_connections_on_host_set_change", "consistent_hashing_lb_config", "override_host_status")
        class ZoneAwareLbConfig(_message.Message):
            __slots__ = ("routing_enabled", "min_cluster_size", "fail_traffic_on_panic")
            ROUTING_ENABLED_FIELD_NUMBER: _ClassVar[int]
            MIN_CLUSTER_SIZE_FIELD_NUMBER: _ClassVar[int]
            FAIL_TRAFFIC_ON_PANIC_FIELD_NUMBER: _ClassVar[int]
            routing_enabled: _percent_pb2.Percent
            min_cluster_size: _wrappers_pb2.UInt64Value
            fail_traffic_on_panic: bool
            def __init__(self, routing_enabled: _Optional[_Union[_percent_pb2.Percent, _Mapping]] = ..., min_cluster_size: _Optional[_Union[_wrappers_pb2.UInt64Value, _Mapping]] = ..., fail_traffic_on_panic: bool = ...) -> None: ...
        class LocalityWeightedLbConfig(_message.Message):
            __slots__ = ()
            def __init__(self) -> None: ...
        class ConsistentHashingLbConfig(_message.Message):
            __slots__ = ("use_hostname_for_hashing", "hash_balance_factor")
            USE_HOSTNAME_FOR_HASHING_FIELD_NUMBER: _ClassVar[int]
            HASH_BALANCE_FACTOR_FIELD_NUMBER: _ClassVar[int]
            use_hostname_for_hashing: bool
            hash_balance_factor: _wrappers_pb2.UInt32Value
            def __init__(self, use_hostname_for_hashing: bool = ..., hash_balance_factor: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ...) -> None: ...
        HEALTHY_PANIC_THRESHOLD_FIELD_NUMBER: _ClassVar[int]
        ZONE_AWARE_LB_CONFIG_FIELD_NUMBER: _ClassVar[int]
        LOCALITY_WEIGHTED_LB_CONFIG_FIELD_NUMBER: _ClassVar[int]
        UPDATE_MERGE_WINDOW_FIELD_NUMBER: _ClassVar[int]
        IGNORE_NEW_HOSTS_UNTIL_FIRST_HC_FIELD_NUMBER: _ClassVar[int]
        CLOSE_CONNECTIONS_ON_HOST_SET_CHANGE_FIELD_NUMBER: _ClassVar[int]
        CONSISTENT_HASHING_LB_CONFIG_FIELD_NUMBER: _ClassVar[int]
        OVERRIDE_HOST_STATUS_FIELD_NUMBER: _ClassVar[int]
        healthy_panic_threshold: _percent_pb2.Percent
        zone_aware_lb_config: Cluster.CommonLbConfig.ZoneAwareLbConfig
        locality_weighted_lb_config: Cluster.CommonLbConfig.LocalityWeightedLbConfig
        update_merge_window: _duration_pb2.Duration
        ignore_new_hosts_until_first_hc: bool
        close_connections_on_host_set_change: bool
        consistent_hashing_lb_config: Cluster.CommonLbConfig.ConsistentHashingLbConfig
        override_host_status: _health_check_pb2.HealthStatusSet
        def __init__(self, healthy_panic_threshold: _Optional[_Union[_percent_pb2.Percent, _Mapping]] = ..., zone_aware_lb_config: _Optional[_Union[Cluster.CommonLbConfig.ZoneAwareLbConfig, _Mapping]] = ..., locality_weighted_lb_config: _Optional[_Union[Cluster.CommonLbConfig.LocalityWeightedLbConfig, _Mapping]] = ..., update_merge_window: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., ignore_new_hosts_until_first_hc: bool = ..., close_connections_on_host_set_change: bool = ..., consistent_hashing_lb_config: _Optional[_Union[Cluster.CommonLbConfig.ConsistentHashingLbConfig, _Mapping]] = ..., override_host_status: _Optional[_Union[_health_check_pb2.HealthStatusSet, _Mapping]] = ...) -> None: ...
    class RefreshRate(_message.Message):
        __slots__ = ("base_interval", "max_interval")
        BASE_INTERVAL_FIELD_NUMBER: _ClassVar[int]
        MAX_INTERVAL_FIELD_NUMBER: _ClassVar[int]
        base_interval: _duration_pb2.Duration
        max_interval: _duration_pb2.Duration
        def __init__(self, base_interval: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., max_interval: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ...) -> None: ...
    class PreconnectPolicy(_message.Message):
        __slots__ = ("per_upstream_preconnect_ratio", "predictive_preconnect_ratio")
        PER_UPSTREAM_PRECONNECT_RATIO_FIELD_NUMBER: _ClassVar[int]
        PREDICTIVE_PRECONNECT_RATIO_FIELD_NUMBER: _ClassVar[int]
        per_upstream_preconnect_ratio: _wrappers_pb2.DoubleValue
        predictive_preconnect_ratio: _wrappers_pb2.DoubleValue
        def __init__(self, per_upstream_preconnect_ratio: _Optional[_Union[_wrappers_pb2.DoubleValue, _Mapping]] = ..., predictive_preconnect_ratio: _Optional[_Union[_wrappers_pb2.DoubleValue, _Mapping]] = ...) -> None: ...
    class TypedExtensionProtocolOptionsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _any_pb2.Any
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...
    TRANSPORT_SOCKET_MATCHES_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ALT_STAT_NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    CLUSTER_TYPE_FIELD_NUMBER: _ClassVar[int]
    EDS_CLUSTER_CONFIG_FIELD_NUMBER: _ClassVar[int]
    CONNECT_TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    PER_CONNECTION_BUFFER_LIMIT_BYTES_FIELD_NUMBER: _ClassVar[int]
    LB_POLICY_FIELD_NUMBER: _ClassVar[int]
    LOAD_ASSIGNMENT_FIELD_NUMBER: _ClassVar[int]
    HEALTH_CHECKS_FIELD_NUMBER: _ClassVar[int]
    MAX_REQUESTS_PER_CONNECTION_FIELD_NUMBER: _ClassVar[int]
    CIRCUIT_BREAKERS_FIELD_NUMBER: _ClassVar[int]
    UPSTREAM_HTTP_PROTOCOL_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    COMMON_HTTP_PROTOCOL_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    HTTP_PROTOCOL_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    HTTP2_PROTOCOL_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    TYPED_EXTENSION_PROTOCOL_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    DNS_REFRESH_RATE_FIELD_NUMBER: _ClassVar[int]
    DNS_JITTER_FIELD_NUMBER: _ClassVar[int]
    DNS_FAILURE_REFRESH_RATE_FIELD_NUMBER: _ClassVar[int]
    RESPECT_DNS_TTL_FIELD_NUMBER: _ClassVar[int]
    DNS_LOOKUP_FAMILY_FIELD_NUMBER: _ClassVar[int]
    DNS_RESOLVERS_FIELD_NUMBER: _ClassVar[int]
    USE_TCP_FOR_DNS_LOOKUPS_FIELD_NUMBER: _ClassVar[int]
    DNS_RESOLUTION_CONFIG_FIELD_NUMBER: _ClassVar[int]
    TYPED_DNS_RESOLVER_CONFIG_FIELD_NUMBER: _ClassVar[int]
    WAIT_FOR_WARM_ON_INIT_FIELD_NUMBER: _ClassVar[int]
    OUTLIER_DETECTION_FIELD_NUMBER: _ClassVar[int]
    CLEANUP_INTERVAL_FIELD_NUMBER: _ClassVar[int]
    UPSTREAM_BIND_CONFIG_FIELD_NUMBER: _ClassVar[int]
    LB_SUBSET_CONFIG_FIELD_NUMBER: _ClassVar[int]
    RING_HASH_LB_CONFIG_FIELD_NUMBER: _ClassVar[int]
    MAGLEV_LB_CONFIG_FIELD_NUMBER: _ClassVar[int]
    ORIGINAL_DST_LB_CONFIG_FIELD_NUMBER: _ClassVar[int]
    LEAST_REQUEST_LB_CONFIG_FIELD_NUMBER: _ClassVar[int]
    ROUND_ROBIN_LB_CONFIG_FIELD_NUMBER: _ClassVar[int]
    COMMON_LB_CONFIG_FIELD_NUMBER: _ClassVar[int]
    TRANSPORT_SOCKET_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    PROTOCOL_SELECTION_FIELD_NUMBER: _ClassVar[int]
    UPSTREAM_CONNECTION_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    CLOSE_CONNECTIONS_ON_HOST_HEALTH_FAILURE_FIELD_NUMBER: _ClassVar[int]
    IGNORE_HEALTH_ON_HOST_REMOVAL_FIELD_NUMBER: _ClassVar[int]
    FILTERS_FIELD_NUMBER: _ClassVar[int]
    LOAD_BALANCING_POLICY_FIELD_NUMBER: _ClassVar[int]
    LRS_SERVER_FIELD_NUMBER: _ClassVar[int]
    LRS_REPORT_ENDPOINT_METRICS_FIELD_NUMBER: _ClassVar[int]
    TRACK_TIMEOUT_BUDGETS_FIELD_NUMBER: _ClassVar[int]
    UPSTREAM_CONFIG_FIELD_NUMBER: _ClassVar[int]
    TRACK_CLUSTER_STATS_FIELD_NUMBER: _ClassVar[int]
    PRECONNECT_POLICY_FIELD_NUMBER: _ClassVar[int]
    CONNECTION_POOL_PER_DOWNSTREAM_CONNECTION_FIELD_NUMBER: _ClassVar[int]
    transport_socket_matches: _containers.RepeatedCompositeFieldContainer[Cluster.TransportSocketMatch]
    name: str
    alt_stat_name: str
    type: Cluster.DiscoveryType
    cluster_type: Cluster.CustomClusterType
    eds_cluster_config: Cluster.EdsClusterConfig
    connect_timeout: _duration_pb2.Duration
    per_connection_buffer_limit_bytes: _wrappers_pb2.UInt32Value
    lb_policy: Cluster.LbPolicy
    load_assignment: _endpoint_pb2.ClusterLoadAssignment
    health_checks: _containers.RepeatedCompositeFieldContainer[_health_check_pb2.HealthCheck]
    max_requests_per_connection: _wrappers_pb2.UInt32Value
    circuit_breakers: _circuit_breaker_pb2.CircuitBreakers
    upstream_http_protocol_options: _protocol_pb2.UpstreamHttpProtocolOptions
    common_http_protocol_options: _protocol_pb2.HttpProtocolOptions
    http_protocol_options: _protocol_pb2.Http1ProtocolOptions
    http2_protocol_options: _protocol_pb2.Http2ProtocolOptions
    typed_extension_protocol_options: _containers.MessageMap[str, _any_pb2.Any]
    dns_refresh_rate: _duration_pb2.Duration
    dns_jitter: _duration_pb2.Duration
    dns_failure_refresh_rate: Cluster.RefreshRate
    respect_dns_ttl: bool
    dns_lookup_family: Cluster.DnsLookupFamily
    dns_resolvers: _containers.RepeatedCompositeFieldContainer[_address_pb2.Address]
    use_tcp_for_dns_lookups: bool
    dns_resolution_config: _resolver_pb2.DnsResolutionConfig
    typed_dns_resolver_config: _extension_pb2.TypedExtensionConfig
    wait_for_warm_on_init: _wrappers_pb2.BoolValue
    outlier_detection: _outlier_detection_pb2.OutlierDetection
    cleanup_interval: _duration_pb2.Duration
    upstream_bind_config: _address_pb2.BindConfig
    lb_subset_config: Cluster.LbSubsetConfig
    ring_hash_lb_config: Cluster.RingHashLbConfig
    maglev_lb_config: Cluster.MaglevLbConfig
    original_dst_lb_config: Cluster.OriginalDstLbConfig
    least_request_lb_config: Cluster.LeastRequestLbConfig
    round_robin_lb_config: Cluster.RoundRobinLbConfig
    common_lb_config: Cluster.CommonLbConfig
    transport_socket: _base_pb2.TransportSocket
    metadata: _base_pb2.Metadata
    protocol_selection: Cluster.ClusterProtocolSelection
    upstream_connection_options: UpstreamConnectionOptions
    close_connections_on_host_health_failure: bool
    ignore_health_on_host_removal: bool
    filters: _containers.RepeatedCompositeFieldContainer[_filter_pb2.Filter]
    load_balancing_policy: LoadBalancingPolicy
    lrs_server: _config_source_pb2.ConfigSource
    lrs_report_endpoint_metrics: _containers.RepeatedScalarFieldContainer[str]
    track_timeout_budgets: bool
    upstream_config: _extension_pb2.TypedExtensionConfig
    track_cluster_stats: TrackClusterStats
    preconnect_policy: Cluster.PreconnectPolicy
    connection_pool_per_downstream_connection: bool
    def __init__(self, transport_socket_matches: _Optional[_Iterable[_Union[Cluster.TransportSocketMatch, _Mapping]]] = ..., name: _Optional[str] = ..., alt_stat_name: _Optional[str] = ..., type: _Optional[_Union[Cluster.DiscoveryType, str]] = ..., cluster_type: _Optional[_Union[Cluster.CustomClusterType, _Mapping]] = ..., eds_cluster_config: _Optional[_Union[Cluster.EdsClusterConfig, _Mapping]] = ..., connect_timeout: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., per_connection_buffer_limit_bytes: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., lb_policy: _Optional[_Union[Cluster.LbPolicy, str]] = ..., load_assignment: _Optional[_Union[_endpoint_pb2.ClusterLoadAssignment, _Mapping]] = ..., health_checks: _Optional[_Iterable[_Union[_health_check_pb2.HealthCheck, _Mapping]]] = ..., max_requests_per_connection: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ..., circuit_breakers: _Optional[_Union[_circuit_breaker_pb2.CircuitBreakers, _Mapping]] = ..., upstream_http_protocol_options: _Optional[_Union[_protocol_pb2.UpstreamHttpProtocolOptions, _Mapping]] = ..., common_http_protocol_options: _Optional[_Union[_protocol_pb2.HttpProtocolOptions, _Mapping]] = ..., http_protocol_options: _Optional[_Union[_protocol_pb2.Http1ProtocolOptions, _Mapping]] = ..., http2_protocol_options: _Optional[_Union[_protocol_pb2.Http2ProtocolOptions, _Mapping]] = ..., typed_extension_protocol_options: _Optional[_Mapping[str, _any_pb2.Any]] = ..., dns_refresh_rate: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., dns_jitter: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., dns_failure_refresh_rate: _Optional[_Union[Cluster.RefreshRate, _Mapping]] = ..., respect_dns_ttl: bool = ..., dns_lookup_family: _Optional[_Union[Cluster.DnsLookupFamily, str]] = ..., dns_resolvers: _Optional[_Iterable[_Union[_address_pb2.Address, _Mapping]]] = ..., use_tcp_for_dns_lookups: bool = ..., dns_resolution_config: _Optional[_Union[_resolver_pb2.DnsResolutionConfig, _Mapping]] = ..., typed_dns_resolver_config: _Optional[_Union[_extension_pb2.TypedExtensionConfig, _Mapping]] = ..., wait_for_warm_on_init: _Optional[_Union[_wrappers_pb2.BoolValue, _Mapping]] = ..., outlier_detection: _Optional[_Union[_outlier_detection_pb2.OutlierDetection, _Mapping]] = ..., cleanup_interval: _Optional[_Union[datetime.timedelta, _duration_pb2.Duration, _Mapping]] = ..., upstream_bind_config: _Optional[_Union[_address_pb2.BindConfig, _Mapping]] = ..., lb_subset_config: _Optional[_Union[Cluster.LbSubsetConfig, _Mapping]] = ..., ring_hash_lb_config: _Optional[_Union[Cluster.RingHashLbConfig, _Mapping]] = ..., maglev_lb_config: _Optional[_Union[Cluster.MaglevLbConfig, _Mapping]] = ..., original_dst_lb_config: _Optional[_Union[Cluster.OriginalDstLbConfig, _Mapping]] = ..., least_request_lb_config: _Optional[_Union[Cluster.LeastRequestLbConfig, _Mapping]] = ..., round_robin_lb_config: _Optional[_Union[Cluster.RoundRobinLbConfig, _Mapping]] = ..., common_lb_config: _Optional[_Union[Cluster.CommonLbConfig, _Mapping]] = ..., transport_socket: _Optional[_Union[_base_pb2.TransportSocket, _Mapping]] = ..., metadata: _Optional[_Union[_base_pb2.Metadata, _Mapping]] = ..., protocol_selection: _Optional[_Union[Cluster.ClusterProtocolSelection, str]] = ..., upstream_connection_options: _Optional[_Union[UpstreamConnectionOptions, _Mapping]] = ..., close_connections_on_host_health_failure: bool = ..., ignore_health_on_host_removal: bool = ..., filters: _Optional[_Iterable[_Union[_filter_pb2.Filter, _Mapping]]] = ..., load_balancing_policy: _Optional[_Union[LoadBalancingPolicy, _Mapping]] = ..., lrs_server: _Optional[_Union[_config_source_pb2.ConfigSource, _Mapping]] = ..., lrs_report_endpoint_metrics: _Optional[_Iterable[str]] = ..., track_timeout_budgets: bool = ..., upstream_config: _Optional[_Union[_extension_pb2.TypedExtensionConfig, _Mapping]] = ..., track_cluster_stats: _Optional[_Union[TrackClusterStats, _Mapping]] = ..., preconnect_policy: _Optional[_Union[Cluster.PreconnectPolicy, _Mapping]] = ..., connection_pool_per_downstream_connection: bool = ...) -> None: ...

class LoadBalancingPolicy(_message.Message):
    __slots__ = ("policies",)
    class Policy(_message.Message):
        __slots__ = ("typed_extension_config",)
        TYPED_EXTENSION_CONFIG_FIELD_NUMBER: _ClassVar[int]
        typed_extension_config: _extension_pb2.TypedExtensionConfig
        def __init__(self, typed_extension_config: _Optional[_Union[_extension_pb2.TypedExtensionConfig, _Mapping]] = ...) -> None: ...
    POLICIES_FIELD_NUMBER: _ClassVar[int]
    policies: _containers.RepeatedCompositeFieldContainer[LoadBalancingPolicy.Policy]
    def __init__(self, policies: _Optional[_Iterable[_Union[LoadBalancingPolicy.Policy, _Mapping]]] = ...) -> None: ...

class UpstreamConnectionOptions(_message.Message):
    __slots__ = ("tcp_keepalive", "set_local_interface_name_on_upstream_connections", "happy_eyeballs_config")
    class FirstAddressFamilyVersion(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DEFAULT: _ClassVar[UpstreamConnectionOptions.FirstAddressFamilyVersion]
        V4: _ClassVar[UpstreamConnectionOptions.FirstAddressFamilyVersion]
        V6: _ClassVar[UpstreamConnectionOptions.FirstAddressFamilyVersion]
    DEFAULT: UpstreamConnectionOptions.FirstAddressFamilyVersion
    V4: UpstreamConnectionOptions.FirstAddressFamilyVersion
    V6: UpstreamConnectionOptions.FirstAddressFamilyVersion
    class HappyEyeballsConfig(_message.Message):
        __slots__ = ("first_address_family_version", "first_address_family_count")
        FIRST_ADDRESS_FAMILY_VERSION_FIELD_NUMBER: _ClassVar[int]
        FIRST_ADDRESS_FAMILY_COUNT_FIELD_NUMBER: _ClassVar[int]
        first_address_family_version: UpstreamConnectionOptions.FirstAddressFamilyVersion
        first_address_family_count: _wrappers_pb2.UInt32Value
        def __init__(self, first_address_family_version: _Optional[_Union[UpstreamConnectionOptions.FirstAddressFamilyVersion, str]] = ..., first_address_family_count: _Optional[_Union[_wrappers_pb2.UInt32Value, _Mapping]] = ...) -> None: ...
    TCP_KEEPALIVE_FIELD_NUMBER: _ClassVar[int]
    SET_LOCAL_INTERFACE_NAME_ON_UPSTREAM_CONNECTIONS_FIELD_NUMBER: _ClassVar[int]
    HAPPY_EYEBALLS_CONFIG_FIELD_NUMBER: _ClassVar[int]
    tcp_keepalive: _address_pb2.TcpKeepalive
    set_local_interface_name_on_upstream_connections: bool
    happy_eyeballs_config: UpstreamConnectionOptions.HappyEyeballsConfig
    def __init__(self, tcp_keepalive: _Optional[_Union[_address_pb2.TcpKeepalive, _Mapping]] = ..., set_local_interface_name_on_upstream_connections: bool = ..., happy_eyeballs_config: _Optional[_Union[UpstreamConnectionOptions.HappyEyeballsConfig, _Mapping]] = ...) -> None: ...

class TrackClusterStats(_message.Message):
    __slots__ = ("timeout_budgets", "request_response_sizes", "per_endpoint_stats")
    TIMEOUT_BUDGETS_FIELD_NUMBER: _ClassVar[int]
    REQUEST_RESPONSE_SIZES_FIELD_NUMBER: _ClassVar[int]
    PER_ENDPOINT_STATS_FIELD_NUMBER: _ClassVar[int]
    timeout_budgets: bool
    request_response_sizes: bool
    per_endpoint_stats: bool
    def __init__(self, timeout_budgets: bool = ..., request_response_sizes: bool = ..., per_endpoint_stats: bool = ...) -> None: ...
