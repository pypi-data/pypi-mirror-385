"""
Service Discovery Module for ISA Model Core

Provides service discovery capabilities using Consul for dynamic service resolution.
"""

from .consul_discovery import (
    ConsulServiceDiscovery,
    get_consul_discovery,
    discover_service,
    resolve_url
)

__all__ = [
    "ConsulServiceDiscovery",
    "get_consul_discovery", 
    "discover_service",
    "resolve_url"
]