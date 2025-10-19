"""
Author:  Jacek Kotlarski --<szumak@virthost.pl>
Created: 2023-10-29

Purpose: Provide reusable networking utilities including IPv4 and IPv6 helpers.

This module lazily exposes address models, subnet calculators, and supporting data
structures so consumers can import lightweight symbols without paying the cost of
initialising the entire toolkit.
"""

from importlib import import_module
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .ipv4 import Address as Address
    from .ipv4 import DEFAULT_IPV4_HOST_LIMIT as DEFAULT_IPV4_HOST_LIMIT
    from .ipv4 import DEFAULT_IPV4_SUBNET_LIMIT as DEFAULT_IPV4_SUBNET_LIMIT
    from .ipv4 import Netmask as Netmask
    from .ipv4 import Network as Network
    from .ipv4 import SubNetwork as SubNetwork
    from .ipv6 import Address6 as Address6
    from .ipv6 import DEFAULT_IPV6_HOST_LIMIT as DEFAULT_IPV6_HOST_LIMIT
    from .ipv6 import DEFAULT_IPV6_SUBNET_LIMIT as DEFAULT_IPV6_SUBNET_LIMIT
    from .ipv6 import Network6 as Network6
    from .ipv6 import Prefix6 as Prefix6
    from .ipv6 import SubNetwork6 as SubNetwork6
    from .libs.octets import Octet as Octet
    from .libs.words import Word16 as Word16

__all__ = [
    "Address",
    "Address6",
    "DEFAULT_IPV4_HOST_LIMIT",
    "DEFAULT_IPV4_SUBNET_LIMIT",
    "DEFAULT_IPV6_HOST_LIMIT",
    "DEFAULT_IPV6_SUBNET_LIMIT",
    "Netmask",
    "Network",
    "Network6",
    "Octet",
    "Prefix6",
    "SubNetwork",
    "SubNetwork6",
    "Word16",
]

_EXPORT_MAP = {
    "Address": ("ipv4", "Address"),
    "Netmask": ("ipv4", "Netmask"),
    "Network": ("ipv4", "Network"),
    "SubNetwork": ("ipv4", "SubNetwork"),
    "DEFAULT_IPV4_HOST_LIMIT": ("ipv4", "DEFAULT_IPV4_HOST_LIMIT"),
    "DEFAULT_IPV4_SUBNET_LIMIT": ("ipv4", "DEFAULT_IPV4_SUBNET_LIMIT"),
    "Address6": ("ipv6", "Address6"),
    "Prefix6": ("ipv6", "Prefix6"),
    "Network6": ("ipv6", "Network6"),
    "SubNetwork6": ("ipv6", "SubNetwork6"),
    "DEFAULT_IPV6_HOST_LIMIT": ("ipv6", "DEFAULT_IPV6_HOST_LIMIT"),
    "DEFAULT_IPV6_SUBNET_LIMIT": ("ipv6", "DEFAULT_IPV6_SUBNET_LIMIT"),
    "Octet": ("libs.octets", "Octet"),
    "Word16": ("libs.words", "Word16"),
}


def __getattr__(name: str) -> Any:
    """Resolve configured netaddresstool exports on demand.

    ### Arguments:
    * name: str - Requested attribute name.

    ### Returns:
    [Any] - Resolved attribute from the target submodule.

    ### Raises:
    * AttributeError: Raised when the attribute is not registered.
    """
    if name not in _EXPORT_MAP:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
    module_name, attr_name = _EXPORT_MAP[name]
    module = import_module(f"{__name__}.{module_name}")
    value = getattr(module, attr_name)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    """Expose lazy exports to dir()."""
    return sorted(__all__)
