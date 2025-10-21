# Copyright 2023 Canonical
# See LICENSE file for licensing details.

r"""## Overview.

This module provides a set of utilities for generating Nginx configurations and managing Nginx workloads.
Used by the coordinator to load-balance and group the workers.

- `NginxLocationModifier`: An enum representing valid Nginx `location` block modifiers (e.g., `=`, `~`, `^~`).
Should be used to populate an `NginxLocationConfig` object.

- `NginxLocationConfig`: A class that defines a single Nginx `location` block, including path matching, modifier, custom headers, .etc.

- `NginxUpstream`: A class that describes an Nginx `upstream` block — specifying an upstream `name`, `port`, and `worker_role` used to resolve backend endpoints.

- `NginxConfig`: A class that builds a full Nginx configuration to be used by the coordinator to load-balance traffic across the workers.

- `Nginx`: A helper class for managing the Nginx container workload (e.g., pebble service lifecycle, config reloads).

- `NginxPrometheusExporter`: A helper class for managing the Nginx Prometheus exporter container workload (e.g., pebble service lifecycle, config reloads).

- `is_ipv6_enabled()`: A utility function to check whether IPv6 is enabled on the container's network interfaces.

## Usage
### Nginx Config Generation

To generate an Nginx configuration for a charm, instantiate the `NginxConfig` class with the required inputs:

1. `server_name`: The name of the server (e.g. charm fqdn), which is used to identify the server in Nginx configurations.
2. `upstream_configs`: List of `NginxUpstream` used to generate Nginx `upstream` blocks.
3. `server_ports_to_locations`: Mapping from server ports to a list of `NginxLocationConfig`.

#### Use `NginxConfig` in the context of the shared `Coordinator` object

A coordinator charm may instantiate the `NginxConfig` in its constructor as follows:
    from coordinated_workers.nginx import NginxConfig, NginxUpstream, NginxLocationConfig
    ...

    class CoordinatorCharm(CharmBase):
        ...
        def __init__(self, *args):
            super().__init__(*args)
            ...
            self.coordinator = Coordinator(
                ...
                nginx_config=NginxConfig(
                    server_name=self.hostname,
                    upstream_configs=self._nginx_upstreams(),
                    server_ports_to_locations=self._server_ports_to_locations(),
                )
            )
        ...
        @property
        def hostname(self) -> str:
            return socket.getfqdn()

        @property
        def _nginx_locations(self) -> List[NginxLocationConfig]:
            return [
                NginxLocationConfig(path="/loki/api/v1/rules", backend="backend",modifier="="),
                NginxLocationConfig(path="/prometheus", backend="backend",modifier="="),
                NginxLocationConfig(path="/api/v1/rules", backend="backend", backend_url="/loki/api/v1/rules",modifier="~"),
            ]

        def _nginx_upstreams(self) -> List[NginxUpstream]:
            # WORKER_ROLES is a list of worker roles that we want to route traffic to
            for upstream in WORKER_ROLES:
                # WORKER_PORT is the port the worker services are running on
                upstreams.append(NginxUpstream(upstream, WORKER_PORT, upstream))
                return upstreams

        def _server_ports_to_locations(self) -> Dict[int, List[NginxLocationConfig]]:
            # NGINX_PORT is the port an nginx server is running on
            # Note that: you can define multiple server blocks, each running on a different port
            return {NGINX_PORT: self._nginx_locations}

Passing the populated `NginxConfig` to the shared `Coordinator` will:
1. generate the full Nginx configuration
2. write the config to a file inside the `nginx` container
3. start the `nginx` pebble service to run with that config file

#### Use `NginxConfig` as a standalone

Any charm can instantiate `NginxConfig` to generate its own Nginx configuration as follows:
    from coordinated_workers.nginx import NginxConfig, NginxUpstream, NginxLocationConfig
    ...

    class AnyCharm(CharmBase):
        ...
        def __init__(self, *args):
            super().__init__(*args)
            ...
            self._container = self.unit.get_container("nginx")
            self._nginx = NginxConfig(
                server_name=self.hostname,
                upstream_configs=self._nginx_upstreams(),
                server_ports_to_locations=self._server_ports_to_locations(),
            )
            ...
            self._reconcile()


        ...
        @property
        def hostname(self) -> str:
            return socket.getfqdn()

        @property
        def _nginx_locations(self) -> List[NginxLocationConfig]:
            return [
                NginxLocationConfig(path="/api/v1", backend="upstream1",modifier="~"),
                NginxLocationConfig(path="/status", backend="upstream2",modifier="="),
            ]

        @property
        def _upstream_addresses(self) -> Dict[str, Set[str]]:
            # a mapping from an upstream "role" to the set of addresses that belong to this upstream
            return {
                "upstream1": {"address1", "address2"},
                "upstream2": {"address3", "address4"},
            }

        @property
        def _tls_available(self) -> bool:
            # return if the Nginx config should have TLS enabled
            pass

        def _reconcile(self):
            if self._container.can_connect():
                new_config: str = self._nginx.get_config(self._upstream_addresses, self._tls_available)
                should_restart: bool = self._has_config_changed(new_config)
                self._container.push(self.config_path, new_config, make_dirs=True)
                self._container.add_layer("nginx", self.layer, combine=True)
                self._container.autostart()

                if should_restart:
                    logger.info("new nginx config: restarting the service")
                    self.reload()

        def _nginx_upstreams(self) -> List[NginxUpstream]:
            # UPSTREAMS is a list of backend services that we want to route traffic to
            for upstream in UPSTREAMS:
                # UPSTREAMS_PORT is the port the backend services are running on
                upstreams.append(NginxUpstream(upstream, UPSTREAMS_PORT, upstream))
                return upstreams

        def _server_ports_to_locations(self) -> Dict[int, List[NginxLocationConfig]]:
            # NGINX_PORT is the port an nginx server is running on
            # Note that: you can define multiple server blocks, each running on a different port
            return {NGINX_PORT: self._nginx_locations}

"""

import logging
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Literal, Optional, Set, TypedDict, cast

import crossplane  # type: ignore
from opentelemetry import trace
from ops import CharmBase, pebble

from coordinated_workers.models import TLSConfig

logger = logging.getLogger(__name__)

# TODO: should we add these to _NginxMapping and make them configurable / accessible?
NGINX_DIR = "/etc/nginx"
NGINX_CONFIG = f"{NGINX_DIR}/nginx.conf"
KEY_PATH = f"{NGINX_DIR}/certs/server.key"
CERT_PATH = f"{NGINX_DIR}/certs/server.cert"
CA_CERT_PATH = "/usr/local/share/ca-certificates/ca.crt"

_NginxMapping = TypedDict(
    "_NginxMapping", {"nginx_port": int, "nginx_exporter_port": int}, total=True
)
NginxMappingOverrides = TypedDict(
    "NginxMappingOverrides", {"nginx_port": int, "nginx_exporter_port": int}, total=False
)
DEFAULT_OPTIONS: _NginxMapping = {
    "nginx_port": 8080,
    "nginx_exporter_port": 9113,
}
RESOLV_CONF_PATH = "/etc/resolv.conf"

_tracer = trace.get_tracer("nginx.tracer")


# Define valid Nginx `location` block modifiers.
# cfr. https://www.digitalocean.com/community/tutorials/nginx-location-directive#nginx-location-directive-syntax
NginxLocationModifier = Literal[
    "",  # prefix match
    "=",  # exact match
    "~",  # case-sensitive regex match
    "~*",  # case-insensitive regex match
    "^~",  # prefix match that disables further regex matching
]


@dataclass
class NginxLocationConfig:
    """Represents a `location` block in an Nginx configuration.

    For example, NginxLocationConfig('/', 'foo', backend_url="/api/v1" headers={'a': 'b'}, modifier=EXACT, is_grpc=True, use_tls=True)
    would result in:
        location = / {
            set $backend grpcs://foo/api/v1;
            grpc_pass $backend;
            proxy_connect_timeout 5s;
            proxy_set_header a b;
        }

    To support serving static files `backend` should be omitted. For example, NginxLocationConfig('/', extra_directives={"try_files": ["$uri", "/index.html"], "autoindex": ["on"],})
    would result in:
        location / {
            try_files $uri /index.html;
            autoindex on;
        }
    """

    path: str
    """The location path (e.g., '/', '/api') to match incoming requests."""
    backend: Optional[str] = None
    """The name of the upstream service to route requests to (e.g., defined in an `upstream` block)."""
    backend_url: str = ""
    """An optional URL path to append when forwarding to the upstream (e.g., '/v1')."""
    headers: Dict[str, str] = field(default_factory=lambda: cast(Dict[str, str], {}))
    """Custom headers to include in the proxied request."""
    modifier: NginxLocationModifier = ""
    """The Nginx location modifier."""
    is_grpc: bool = False
    """Whether to use gRPC proxying (i.e. `grpc_pass` instead of `proxy_pass`)."""
    upstream_tls: Optional[bool] = None
    """Whether to connect to the upstream over TLS (e.g., https:// or grpcs://)
    If None, it will inherit the TLS setting from the server block that the location is part of.
    """
    rewrite: Optional[List[str]] = None
    """Custom rewrite, used i.e. to drop the subpath from the proxied request if needed.
    Example: ['^/auth(/.*)$', '$1', 'break'] to drop `/auth` from the request.
    """
    extra_directives: Dict[str, List[str]] = field(
        default_factory=lambda: cast(Dict[str, List[str]], {})
    )
    """Dictionary of arbitrary location configuration keys and values.
    Example: {"proxy_ssl_verify": ["off"]}
    """


@dataclass
class NginxUpstream:
    """Represents metadata needed to construct an Nginx `upstream` block."""

    name: str
    """Name of the upstream block."""
    port: int
    """Port number that all backend servers in this upstream listen on.

    Our coordinators assume that all servers under an upstream share the same port.
    """
    worker_role: str
    """The worker role that corresponds to this upstream.

    This role will be used to look up workers (backend server) addresses for this upstream.

    TODO: This class is now used outside of the context of pure coordinated-workers.
    This arg hence must be renamed to have a more generic name for eg. `address_lookup_key`.
    See: https://github.com/canonical/cos-coordinated-workers/issues/105
    """
    ignore_worker_role: bool = False
    """If True, overrides `worker_role` and routes to all available backend servers.

    Use this when the upstream should be generic and include any available backend.

    TODO: This class is now used outside of the context of pure coordinated-workers.
    This arg hence must be renamed to have a more generic name for eg. `ignore_address_lookup`.
    See: https://github.com/canonical/cos-coordinated-workers/issues/105
    """


@dataclass
class NginxMapConfig:
    """Represents a `map` block of the Nginx config.

    Example:
    NginxMapConfig(
        source_variable="$http_upgrade",
        target_variable="$connection_upgrade",
        value_mappings={
            "default": ["upgrade"],
            "": ["close"],
        },
    )
    will result in the following `map` block:

    map $http_upgrade $connection_upgrade {
        default upgrade;
        '' close;
    }
    """

    source_variable: str
    """Name of the variable to map from."""
    target_variable: str
    """Name of the variable to be created."""
    value_mappings: Dict[str, List[str]]
    """Mapping of source values to target values."""


@dataclass
class NginxTracingConfig:
    """Configuration for OTel tracing in Nginx."""

    endpoint: str
    service_name: str
    resource_attributes: Dict[str, str] = field(default_factory=lambda: {})


class NginxConfig:
    """Responsible for building the Nginx configuration used by the coordinators."""

    _worker_processes = "5"
    _pid = "/tmp/nginx.pid"
    _worker_rlimit_nofile = "8192"
    _worker_connections = "4096"
    _proxy_read_timeout = "300"
    _supported_tls_versions = ["TLSv1", "TLSv1.1", "TLSv1.2", "TLSv1.3"]
    _ssl_ciphers = ["HIGH:!aNULL:!MD5"]
    _proxy_connect_timeout = "5s"
    otel_module_path = "/etc/nginx/modules/ngx_otel_module.so"
    _http_x_scope_orgid_map_config = NginxMapConfig(
        source_variable="$http_x_scope_orgid",
        target_variable="$ensured_x_scope_orgid",
        value_mappings={
            "default": ["$http_x_scope_orgid"],
            "": ["anonymous"],
        },
    )
    _logging_by_status_map_config = NginxMapConfig(
        source_variable="$status",
        target_variable="$loggable",
        value_mappings={
            "~^[23]": ["0"],
            "default": ["1"],
        },
    )

    def __init__(
        self,
        server_name: str,
        upstream_configs: List[NginxUpstream],
        server_ports_to_locations: Dict[int, List[NginxLocationConfig]],
        map_configs: Optional[List[NginxMapConfig]] = None,
        enable_health_check: bool = False,
        enable_status_page: bool = False,
    ):
        """Constructor for an Nginx config generator object.

        Args:
            server_name: The name of the server (e.g. coordinator fqdn), which is used to identify the server in Nginx configurations.
            upstream_configs: List of Nginx upstream metadata configurations used to generate Nginx `upstream` blocks.
            server_ports_to_locations: Mapping from server ports to a list of Nginx location configurations.
            map_configs: List of extra `map` directives to be put under the `http` directive.
            enable_health_check: If True, adds a `/` location that returns a basic 200 OK response.
            enable_status_page: If True, adds a `/status` location that enables `stub_status` for basic Nginx metrics.

        Example:
            .. code-block:: python
            NginxConfig(
                server_name = "tempo-coordinator-0.tempo-coordinator-endpoints.model.svc.cluster.local",
                upstreams = [
                    NginxUpstream(name="zipkin", port=9411, worker_role="distributor"),
                ],
                server_ports_to_locations = {
                    9411: [
                        NginxLocationConfig(
                            path="/",
                            backend="zipkin"
                        )
                    ]
                },
                map_configs=[
                    NginxMapConfig(
                        source_variable="$http_upgrade",
                        target_variable="$connection_upgrade",
                        value_mappings={
                            "default": ["upgrade"],
                            "": ["close"],
                        },
                    )
                ],
            )
        """
        self.server_name = server_name
        self.upstream_configs = upstream_configs
        self.server_ports_to_locations = server_ports_to_locations
        self.map_configs = map_configs or []
        self.enable_health_check = enable_health_check
        self.enable_status_page = enable_status_page
        self._dns_IP_address = self._get_dns_ip_address()
        self._ipv6_enabled = is_ipv6_enabled()

    def get_config(
        self,
        upstreams_to_addresses: Dict[str, Set[str]],
        listen_tls: bool,
        root_path: Optional[str] = None,
        tracing_config: Optional[NginxTracingConfig] = None,
    ) -> str:
        """Render the Nginx configuration as a string.

        Args:
            upstreams_to_addresses: A dictionary mapping each upstream name to a set of addresses associated with that upstream.
            listen_tls: Whether Nginx should listen for incoming traffic over TLS.
            root_path: If provided, it is used as a location where static files will be served.
            tracing_config: Enables tracing in Nginx and exports traces to the specified endpoint if provided.
                Note: Tracing is only available if the Nginx binary has been built with the ngx_otel_module.
        """
        full_config = self._prepare_config(
            upstreams_to_addresses, listen_tls, root_path, tracing_config
        )
        return crossplane.build(full_config)  # type: ignore

    def _prepare_config(
        self,
        upstreams_to_addresses: Dict[str, Set[str]],
        listen_tls: bool,
        root_path: Optional[str] = None,
        tracing_config: Optional[NginxTracingConfig] = None,
    ) -> List[Dict[str, Any]]:
        upstreams = self._upstreams(upstreams_to_addresses)
        # extract the upstream name
        backends = [upstream["args"][0] for upstream in upstreams]
        # build the complete configuration
        full_config = [
            *(
                [{"directive": "load_module", "args": [self.otel_module_path]}]
                if tracing_config
                else []
            ),
            {"directive": "worker_processes", "args": [self._worker_processes]},
            {"directive": "error_log", "args": ["/dev/stderr", "error"]},
            {"directive": "pid", "args": [self._pid]},
            {"directive": "worker_rlimit_nofile", "args": [self._worker_rlimit_nofile]},
            {
                "directive": "events",
                "args": [],
                "block": [{"directive": "worker_connections", "args": [self._worker_connections]}],
            },
            {
                "directive": "http",
                "args": [],
                "block": [
                    *self._tracing_block(tracing_config),
                    # upstreams (load balancing)
                    *upstreams,
                    # temp paths
                    {
                        "directive": "client_body_temp_path",
                        "args": ["/tmp/client_temp"],
                    },
                    {"directive": "proxy_temp_path", "args": ["/tmp/proxy_temp_path"]},
                    {"directive": "fastcgi_temp_path", "args": ["/tmp/fastcgi_temp"]},
                    {"directive": "uwsgi_temp_path", "args": ["/tmp/uwsgi_temp"]},
                    {"directive": "scgi_temp_path", "args": ["/tmp/scgi_temp"]},
                    # include mime types so nginx can map file extensions correctly.
                    # Without this, files may fall back to "application/octet-stream",
                    # and when Nginx serves static files, browsers may download them
                    # instead of rendering (e.g., JS, CSS, SVG).
                    {"directive": "include", "args": ["/etc/nginx/mime.types"]},
                    # logging
                    {"directive": "default_type", "args": ["application/octet-stream"]},
                    {
                        "directive": "log_format",
                        "args": [
                            "main",
                            '$remote_addr - $remote_user [$time_local]  $status "$request" $body_bytes_sent "$http_referer" "$http_user_agent" "$http_x_forwarded_for"',
                        ],
                    },
                    *[self._build_map(variable) for variable in self.map_configs],
                    self._build_map(self._logging_by_status_map_config),
                    {"directive": "access_log", "args": ["/dev/stderr"]},
                    {"directive": "sendfile", "args": ["on"]},
                    {"directive": "tcp_nopush", "args": ["on"]},
                    *self._resolver(),
                    # TODO: add custom http block for the user to config?
                    self._build_map(self._http_x_scope_orgid_map_config),
                    {"directive": "proxy_read_timeout", "args": [self._proxy_read_timeout]},
                    # server block
                    *self._build_servers_config(backends, listen_tls, root_path),
                ],
            },
        ]
        return full_config

    @staticmethod
    def _build_map(variable: NginxMapConfig) -> Dict[str, Any]:
        return {
            "directive": "map",
            "args": [variable.source_variable, variable.target_variable],
            "block": [
                {"directive": directive, "args": args}
                for directive, args in variable.value_mappings.items()
            ],
        }

    def _resolver(
        self,
        custom_resolver: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        # pass a custom resolver, such as kube-dns.kube-system.svc.cluster.local.
        if custom_resolver:
            return [{"directive": "resolver", "args": [custom_resolver]}]

        # by default, fetch the DNS resolver address from /etc/resolv.conf
        return [
            {
                "directive": "resolver",
                "args": [self._dns_IP_address],
            }
        ]

    @staticmethod
    def _get_dns_ip_address() -> str:
        """Obtain DNS ip address from /etc/resolv.conf."""
        resolv = Path(RESOLV_CONF_PATH).read_text()
        for line in resolv.splitlines():
            if line.startswith("nameserver"):
                # assume there's only one
                return line.split()[1].strip()
        raise RuntimeError("cannot find nameserver in /etc/resolv.conf")

    def _upstreams(self, upstreams_to_addresses: Dict[str, Set[str]]) -> List[Any]:
        nginx_upstreams: List[Any] = []

        for upstream_config in self.upstream_configs:
            if upstream_config.ignore_worker_role:
                # include all available addresses
                addresses: Optional[Set[str]] = set()
                for address_set in upstreams_to_addresses.values():
                    addresses.update(address_set)
            else:
                addresses = upstreams_to_addresses.get(upstream_config.worker_role)

            # don't add an upstream block if there are no addresses
            if addresses:
                upstream_config_name = upstream_config.name
                nginx_upstreams.append(
                    {
                        "directive": "upstream",
                        "args": [upstream_config_name],
                        "block": [
                            # enable dynamic DNS resolution for upstream servers.
                            # since K8s pods IPs are dynamic, we need this config to allow
                            # nginx to re-resolve the DNS name without requiring a config reload.
                            # cfr. https://www.f5.com/company/blog/nginx/dns-service-discovery-nginx-plus#:~:text=second%20method
                            {
                                "directive": "zone",
                                "args": [f"{upstream_config_name}_zone", "64k"],
                            },
                            *[
                                {
                                    "directive": "server",
                                    "args": [f"{addr}:{upstream_config.port}", "resolve"],
                                }
                                for addr in addresses
                            ],
                        ],
                    }
                )

        return nginx_upstreams

    def _build_servers_config(
        self, backends: List[str], listen_tls: bool = False, root_path: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        servers: List[Dict[str, Any]] = []
        for port, locations in self.server_ports_to_locations.items():
            server_config = self._build_server_config(
                port,
                locations,
                backends,
                listen_tls,
                root_path,
            )
            if server_config:
                servers.append(server_config)
        return servers

    def _build_server_config(
        self,
        port: int,
        locations: List[NginxLocationConfig],
        backends: List[str],
        listen_tls: bool = False,
        root_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        auth_enabled = False
        is_grpc = any(loc.is_grpc for loc in locations)
        nginx_locations = self._locations(locations, is_grpc, backends, listen_tls)
        server_config = {}
        if len(nginx_locations) > 0:
            server_config = {
                "directive": "server",
                "args": [],
                "block": [
                    *self._listen(port, ssl=listen_tls, http2=is_grpc),
                    *self._root_path(root_path),
                    *self._basic_auth(auth_enabled),
                    {
                        "directive": "proxy_set_header",
                        "args": ["X-Scope-OrgID", "$ensured_x_scope_orgid"],
                    },
                    {"directive": "server_name", "args": [self.server_name]},
                    *(
                        [
                            {"directive": "ssl_certificate", "args": [CERT_PATH]},
                            {"directive": "ssl_certificate_key", "args": [KEY_PATH]},
                            {
                                "directive": "ssl_protocols",
                                "args": self._supported_tls_versions,
                            },
                            {
                                "directive": "ssl_ciphers",
                                "args": self._ssl_ciphers,
                            },
                        ]
                        if listen_tls
                        else []
                    ),
                    *nginx_locations,
                ],
            }

        return server_config

    def _locations(
        self,
        locations: List[NginxLocationConfig],
        grpc: bool,
        backends: List[str],
        listen_tls: bool,
    ) -> List[Dict[str, Any]]:
        nginx_locations: List[Dict[str, Any]] = []

        if self.enable_health_check:
            nginx_locations.append(
                {
                    "directive": "location",
                    "args": ["=", "/"],
                    "block": [
                        {
                            "directive": "return",
                            "args": ["200", "'OK'"],
                        },
                        {
                            "directive": "auth_basic",
                            "args": ["off"],
                        },
                    ],
                },
            )
        if self.enable_status_page:
            nginx_locations.append(
                {
                    "directive": "location",
                    "args": ["=", "/status"],
                    "block": [
                        {
                            "directive": "stub_status",
                            "args": [],
                        },
                    ],
                },
            )

        for location in locations:
            # Handle locations without backend, i.e. serving static files
            if not location.backend:
                nginx_locations.append(
                    {
                        "directive": "location",
                        "args": (
                            [location.path]
                            if location.modifier == ""
                            else [location.modifier, location.path]
                        ),
                        "block": [
                            *self._rewrite_block(location.rewrite),
                            # add headers if any
                            *self._headers_block(location.headers),
                            # add extra config directives if any
                            *self._extra_directives_block(location.extra_directives),
                        ],
                    }
                )
            # Handle locations with corresponding backends
            # don't add a location block if the upstream backend doesn't exist in the config
            if location.backend in backends:
                # if upstream_tls is explicitly set for this location, use that; otherwise, use the server's listen_tls setting.
                tls = location.upstream_tls if location.upstream_tls is not None else listen_tls
                s = "s" if tls else ""
                protocol = f"grpc{s}" if grpc else f"http{s}"
                nginx_locations.append(
                    {
                        "directive": "location",
                        "args": (
                            [location.path]
                            if location.modifier == ""
                            else [location.modifier, location.path]
                        ),
                        "block": [
                            {
                                "directive": "set",
                                "args": [
                                    "$backend",
                                    f"{protocol}://{location.backend}{location.backend_url}",
                                ],
                            },
                            *self._rewrite_block(location.rewrite),
                            {
                                "directive": "grpc_pass" if grpc else "proxy_pass",
                                "args": ["$backend"],
                            },
                            # if a server is down, no need to wait for a long time to pass on the request to the next available server
                            {
                                "directive": "proxy_connect_timeout",
                                "args": [self._proxy_connect_timeout],
                            },
                            # add headers if any
                            *self._headers_block(location.headers),
                            # add extra config directives if any
                            *self._extra_directives_block(location.extra_directives),
                        ],
                    }
                )

        return nginx_locations

    @staticmethod
    def _extra_directives_block(
        extra_directives: Optional[Dict[str, List[str]]],
    ) -> List[Optional[Dict[str, Any]]]:
        if extra_directives:
            return [{"directive": key, "args": val} for key, val in extra_directives.items()]
        return []

    @staticmethod
    def _headers_block(headers: Optional[Dict[str, str]]) -> List[Optional[Dict[str, Any]]]:
        if headers:
            return [
                {"directive": "proxy_set_header", "args": [key, val]}
                for key, val in headers.items()
            ]
        return []

    @staticmethod
    def _rewrite_block(rewrite: Optional[List[str]]) -> List[Optional[Dict[str, Any]]]:
        if rewrite:
            return [{"directive": "rewrite", "args": rewrite}]
        return []

    def _root_path(self, root_path: Optional[str] = None) -> List[Optional[Dict[str, Any]]]:
        if root_path:
            return [{"directive": "root", "args": [root_path]}]
        return []

    def _basic_auth(self, enabled: bool) -> List[Optional[Dict[str, Any]]]:
        if enabled:
            return [
                {"directive": "auth_basic", "args": ['"workload"']},
                {
                    "directive": "auth_basic_user_file",
                    "args": ["/etc/nginx/secrets/.htpasswd"],
                },
            ]
        return []

    def _listen(self, port: int, ssl: bool, http2: bool) -> List[Dict[str, Any]]:
        directives: List[Dict[str, Any]] = []
        directives.append({"directive": "listen", "args": self._listen_args(port, False, ssl)})
        if self._ipv6_enabled:
            directives.append(
                {
                    "directive": "listen",
                    "args": self._listen_args(port, True, ssl),
                }
            )
        if http2:
            directives.append({"directive": "http2", "args": ["on"]})
        return directives

    def _listen_args(self, port: int, ipv6: bool, ssl: bool) -> List[str]:
        args: List[str] = []
        if ipv6:
            args.append(f"[::]:{port}")
        else:
            args.append(f"{port}")
        if ssl:
            args.append("ssl")
        return args

    def _tracing_block(self, tracing_config: Optional[NginxTracingConfig]) -> List[Dict[str, Any]]:
        return (
            [
                {"directive": "otel_trace", "args": ["on"]},
                # propagate the trace context headers
                {"directive": "otel_trace_context", "args": ["propagate"]},
                {
                    "directive": "otel_exporter",
                    "args": [],
                    "block": [{"directive": "endpoint", "args": [tracing_config.endpoint]}],
                },
                {"directive": "otel_service_name", "args": [tracing_config.service_name]},
                *(
                    [
                        {"directive": "otel_resource_attr", "args": [attr_key, attr_val]}
                        for attr_key, attr_val in tracing_config.resource_attributes.items()
                    ]
                ),
            ]
            if tracing_config
            else []
        )


class Nginx:
    """Helper class to manage the nginx workload."""

    config_path = NGINX_CONFIG
    options: _NginxMapping = DEFAULT_OPTIONS

    def __init__(
        self,
        charm: CharmBase,
        options: Optional[NginxMappingOverrides] = None,
        container_name: str = "nginx",
        liveness_check_endpoint_getter: Optional[Callable[[bool], str]] = None,
    ):
        self._charm = charm
        self._container_name = container_name
        self._container = self._charm.unit.get_container(container_name)
        self.options.update(options or {})
        self._liveness_check_endpoint_getter = liveness_check_endpoint_getter
        self._liveness_check_name = f"{self._container_name}-up"

    @property
    def are_certificates_on_disk(self) -> bool:
        """Return True if the certificates files are on disk."""
        return (
            self._container.can_connect()
            and self._container.exists(CERT_PATH)
            and self._container.exists(KEY_PATH)
            and self._container.exists(CA_CERT_PATH)
        )

    def _configure_tls(self, private_key: str, server_cert: str, ca_cert: str) -> None:
        """Save the certificates file to disk and run update-ca-certificates."""
        with _tracer.start_as_current_span("write ca cert"):
            # push CA cert to charm container
            Path(CA_CERT_PATH).parent.mkdir(parents=True, exist_ok=True)
            Path(CA_CERT_PATH).write_text(ca_cert)

        if self._container.can_connect():
            # Read the current content of the files (if they exist)
            current_server_cert = (
                self._container.pull(CERT_PATH).read() if self._container.exists(CERT_PATH) else ""
            )
            current_private_key = (
                self._container.pull(KEY_PATH).read() if self._container.exists(KEY_PATH) else ""
            )
            current_ca_cert = (
                self._container.pull(CA_CERT_PATH).read()
                if self._container.exists(CA_CERT_PATH)
                else ""
            )

            if (
                current_server_cert == server_cert
                and current_private_key == private_key
                and current_ca_cert == ca_cert
            ):
                # No update needed
                return
            self._container.push(KEY_PATH, private_key, make_dirs=True)
            self._container.push(CERT_PATH, server_cert, make_dirs=True)
            self._container.push(CA_CERT_PATH, ca_cert, make_dirs=True)
            logger.debug("running update-ca-certificates")
            self._container.exec(["update-ca-certificates", "--fresh"]).wait()

    def _delete_certificates(self) -> None:
        """Delete the certificate files from disk and run update-ca-certificates."""
        with _tracer.start_as_current_span("delete ca cert"):
            if Path(CA_CERT_PATH).exists():
                Path(CA_CERT_PATH).unlink(missing_ok=True)

        if self._container.can_connect():
            for path in (CERT_PATH, KEY_PATH, CA_CERT_PATH):
                if self._container.exists(path):
                    self._container.remove_path(path, recursive=True)
            logger.debug("running update-ca-certificates")
            self._container.exec(["update-ca-certificates", "--fresh"]).wait()

    def _has_config_changed(self, new_config: str) -> bool:
        """Return True if the passed config differs from the one on disk."""
        if not self._container.can_connect():
            logger.debug("Could not connect to Nginx container")
            return False

        try:
            current_config = self._container.pull(self.config_path).read()
        except (pebble.ProtocolError, pebble.PathError) as e:
            logger.warning(
                "Could not check the current nginx configuration due to "
                "a failure in retrieving the file: %s",
                e,
            )
            return False

        return current_config != new_config

    def reconcile(
        self,
        nginx_config: str,
        tls_config: Optional[TLSConfig] = None,
    ):
        """Configure pebble layer and restart if necessary."""
        if self._container.can_connect():
            self._reconcile_tls_config(tls_config)
            self._reconcile_nginx_config(nginx_config)

    def _reconcile_tls_config(self, tls_config: Optional[TLSConfig] = None):
        if tls_config:
            self._configure_tls(
                server_cert=tls_config.server_cert,
                ca_cert=tls_config.ca_cert,
                private_key=tls_config.private_key,
            )
        else:
            self._delete_certificates()

    def _reconcile_nginx_config(self, nginx_config: str):
        should_restart = self._has_config_changed(nginx_config)
        self._container.push(self.config_path, nginx_config, make_dirs=True)  # type: ignore
        self._container.add_layer("nginx", self.layer, combine=True)
        try:
            self._container.autostart()
        except pebble.ChangeError:
            # check if we're trying to load an external nginx module, but it doesn't exist in the nginx image
            if "ngx_otel_module" in nginx_config and not self._container.exists(
                NginxConfig.otel_module_path
            ):
                logger.exception(
                    "Failed to enable tracing for nginx. The nginx image is missing the ngx_otel_module."
                )
            # otherwise, it's an unexpected error and we should raise it as is
            raise
        if should_restart:
            logger.info("new nginx config: restarting the service")
            # Reload the nginx config without restarting the service
            self._container.exec(["nginx", "-s", "reload"]).wait()

    @property
    def layer(self) -> pebble.Layer:
        """Return the Pebble layer for Nginx."""
        return pebble.Layer(
            {
                "summary": "nginx layer",
                "description": "pebble config layer for Nginx",
                "services": {self._container_name: self._service_dict},
                "checks": {self._liveness_check_name: self._check_dict}
                if self._liveness_check_endpoint_getter
                else {},
            }
        )

    @property
    def _service_dict(self) -> pebble.ServiceDict:
        service_dict: pebble.ServiceDict = {
            "override": "replace",
            "summary": "nginx",
            "command": "nginx -g 'daemon off;'",
            "startup": "enabled",
        }
        if self._liveness_check_endpoint_getter:
            # we've observed that nginx sometimes doesn't get reloaded after a config change.
            # Probably a race condition if we change the config too quickly, while the workers are
            # already reloading because of a previous config change.
            # To counteract this, we rely on the pebble health check: if this check fails,
            # pebble will automatically restart the nginx service.
            service_dict["on-check-failure"] = {self._liveness_check_name: "restart"}
        return service_dict

    @property
    def _check_dict(self) -> pebble.CheckDict:
        if not self._liveness_check_endpoint_getter:
            return {}

        return {
            "override": "replace",
            "startup": "enabled",
            "threshold": 3,
            "http": {"url": self._liveness_check_endpoint_getter(self.are_certificates_on_disk)},
        }


class NginxPrometheusExporter:
    """Helper class to manage the nginx prometheus exporter workload."""

    options: _NginxMapping = DEFAULT_OPTIONS

    def __init__(self, charm: CharmBase, options: Optional[NginxMappingOverrides] = None) -> None:
        self._charm = charm
        self._container = self._charm.unit.get_container("nginx-prometheus-exporter")
        self.options.update(options or {})

    def reconcile(self):
        """Configure pebble layer and restart if necessary."""
        if self._container.can_connect():
            self._container.add_layer("nginx-prometheus-exporter", self.layer, combine=True)
            self._container.autostart()

    @property
    def are_certificates_on_disk(self) -> bool:
        """Return True if the certificates files are on disk."""
        return (
            self._container.can_connect()
            and self._container.exists(CERT_PATH)
            and self._container.exists(KEY_PATH)
            and self._container.exists(CA_CERT_PATH)
        )

    @property
    def port(self) -> int:
        """Return the port where the nginx prometheus exporter is listening to present the metrics.

        This is the port at which an external application would scrape /metrics.
        """
        return self.options["nginx_exporter_port"]

    @property
    def layer(self) -> pebble.Layer:
        """Return the Pebble layer for Nginx Prometheus exporter."""
        scheme = "https" if self.are_certificates_on_disk else "http"  # type: ignore
        return pebble.Layer(
            {
                "summary": "nginx prometheus exporter layer",
                "description": "pebble config layer for Nginx Prometheus exporter",
                "services": {
                    "nginx-prometheus-exporter": {
                        "override": "replace",
                        "summary": "nginx prometheus exporter",
                        "command": f"nginx-prometheus-exporter --no-nginx.ssl-verify --web.listen-address=:{self.port}  --nginx.scrape-uri={scheme}://127.0.0.1:{self.options['nginx_port']}/status",
                        "startup": "enabled",
                    }
                },
            }
        )


def is_ipv6_enabled() -> bool:
    """Check if IPv6 is enabled on the container's network interfaces."""
    try:
        output = subprocess.run(
            ["ip", "-6", "address", "show"], check=True, capture_output=True, text=True
        )
    except subprocess.CalledProcessError:
        # if running the command failed for any reason, assume ipv6 is not enabled.
        return False
    return bool(output.stdout)
