# -*- coding: UTF-8 -*-
"""
Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: 14.09.2023

Purpose: Classes for IPv6

https://www.ibm.com/docs/en/ts3500-tape-library?topic=formats-subnet-masks-ipv4-prefixes-ipv6
"""

import socket

from copy import deepcopy
from inspect import currentframe
import warnings
from typing import Iterator, Optional, TypeVar, Union, List

from ..attribtool import NoDynamicAttributes
from ..raisetool import Raise
from .libs.words import Word16
from ..libs.interfaces.comparators import IComparators
from ..basetool.classes import BClasses

TAddress6 = TypeVar("TAddress6", bound="Address6")
DEFAULT_IPV6_HOST_LIMIT: int = 65536
DEFAULT_IPV6_SUBNET_LIMIT: int = 4096


class Address6(IComparators, BClasses, NoDynamicAttributes):
    """Address6 class for representing IPv6 addresses.

    Constructor arguments:
    addr: Union[str, int, List[Word16]] -- IPv6 address representation as string, integer or list of eight Word16

    Public property:
    words: List[Word16] -- Return list of eight Word16

    Public setter:
    words: Union[str, int, List] -- Set IPv6 address from string, integer or list of Word16.
    """

    __var_int: int = 0

    def __init__(
        self, addr: Union[str, int, Union[List[int], List[str], List[Word16]]]
    ) -> None:
        """Constructor.

        ### Arguments:
        * addr: Union[str, int, Union[List[int], List[str], List[Word16]]] - IPv6 address in various formats (string, integer, or list of 16-bit words).
        """
        self.words = addr

    def __eq__(self, arg: Union[TAddress6, object]) -> bool:
        """Equal."""
        if not isinstance(arg, Address6):
            raise Raise.error(
                f"Expected argument of Address6 type, received: {type(arg)}.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        return int(self) == int(arg)

    def __ge__(self, arg: Union[TAddress6, object]) -> bool:
        """Greater or equal."""
        if not isinstance(arg, Address6):
            raise Raise.error(
                f"Expected argument of Address6 type, received: {type(arg)}.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        return int(self) >= int(arg)

    def __gt__(self, arg: Union[TAddress6, object]) -> bool:
        """Greater."""
        if not isinstance(arg, Address6):
            raise Raise.error(
                f"Expected argument of Address6 type, received: {type(arg)}.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        return int(self) > int(arg)

    def __le__(self, arg: Union[TAddress6, object]) -> bool:
        """Less or equal."""
        if not isinstance(arg, Address6):
            raise Raise.error(
                f"Expected argument of Address6 type, received: {type(arg)}.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        return int(self) <= int(arg)

    def __lt__(self, arg: Union[TAddress6, object]) -> bool:
        """Less."""
        if not isinstance(arg, Address6):
            raise Raise.error(
                f"Expected argument of Address6 type, received: {type(arg)}.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        return int(self) < int(arg)

    def __ne__(self, arg: Union[TAddress6, object]) -> bool:
        """Negative."""
        if not isinstance(arg, Address6):
            raise Raise.error(
                f"Expected argument of Address6 type, received: {type(arg)}.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        return int(self) != int(arg)

    @staticmethod
    def __check_groups(group_list: List[str]) -> List[str]:
        for i in range(0, len(group_list)):
            group_list[i] = group_list[i].zfill(4)
        return group_list

    @staticmethod
    def __expand_ipv6(ipv6_address: str) -> str:
        # Sprawdzenie czy adres jest już w pełnej reprezentacji
        if "::" not in ipv6_address:
            return ipv6_address

        # Podziel adres na dwie części, przed '::' i po '::'
        parts: list[str] = ipv6_address.split("::", 1)
        head: List[str] = Address6.__check_groups(parts[0].split(":"))
        tail: List[str] = Address6.__check_groups(parts[1].split(":"))

        # Oblicz ile zer należy dodać, aby osiągnąć 8 części
        missing_zeros: int = 8 - (len(head) + len(tail))
        zero_part = "0000"

        # Połącz części przed '::' i po '::', wstawiając brakujące zera
        expanded_parts: str = ":".join(head + [zero_part] * missing_zeros + tail)

        return expanded_parts

    @staticmethod
    def __is_valid_ipv6(ipv6_addr: str) -> bool:
        """Check if ipv6_addr is valid."""
        try:
            # Używamy socket.inet_pton, aby sprawdzić poprawność adresu IPv6
            socket.inet_pton(socket.AF_INET6, ipv6_addr)
            return True
        except (socket.error, ValueError):
            return False

    @staticmethod
    def __int_to_ip(ipint: int) -> str:
        """Convert ip int representation to ipv6 str."""
        # W przypadku adresu IPv6 zawsze przekształcamy go na 16 bajtów (128 bitów)
        binary_ip: bytes = ipint.to_bytes(16, byteorder="big")
        ipv6_address: str = socket.inet_ntop(socket.AF_INET6, binary_ip)

        return ipv6_address

    @staticmethod
    def __ip_to_int(ipstr: str) -> int:
        """Convert ipv6 str representation to ip int."""
        # Używamy socket.inet_pton, aby przekształcić adres IPv6 w postać binarną
        packed_ip: bytes = socket.inet_pton(socket.AF_INET6, ipstr)
        # Następnie przekształcamy binarny adres IPv6 na liczbę całkowitą (integer)
        int_ip: int = int.from_bytes(packed_ip, byteorder="big")

        return int_ip

    def __set_words_from_list(
        self, value: Union[List[int], List[str], List[Word16]]
    ) -> None:
        """Set address from list."""
        if len(value) != 8:
            raise Raise.error(
                f"Expected list of eight elements.",
                ValueError,
                self._c_name,
                currentframe(),
            )
        tmp: str = (
            f"{str(Word16(value[0]))}:"
            f"{str(Word16(value[1]))}:"
            f"{str(Word16(value[2]))}:"
            f"{str(Word16(value[3]))}:"
            f"{str(Word16(value[4]))}:"
            f"{str(Word16(value[5]))}:"
            f"{str(Word16(value[6]))}:"
            f"{str(Word16(value[7]))}"
        )
        self.__set_words_from_str(tmp)

    def __set_words_from_int(self, value: int) -> None:
        # if value >= 0 and value <= 340282366920938463463374607431768211455:
        if value in range(0, 340282366920938463463374607431768211456):
            self.__var_int = value
        else:
            raise Raise.error(
                f"IP-int out of range (0-340282366920938463463374607431768211455), received: {value}",
                ValueError,
                self._c_name,
                currentframe(),
            )

    def __set_words_from_str(self, value: str) -> None:
        if Address6.__is_valid_ipv6(value):
            self.__var_int = Address6.__ip_to_int(value)
        else:
            raise Raise.error(
                f"IPv6 address is invalid: {value}",
                ValueError,
                self._c_name,
                currentframe(),
            )

    def __int__(self) -> int:
        """Return ipv6 representation as integer."""
        return self.__var_int

    def __str__(self) -> str:
        """Return string representation of address."""
        return Address6.__int_to_ip(self.__var_int)

    def __repr__(self) -> str:
        """Return representation of object."""
        return f"{self._c_name}('{str(self)}')"

    @property
    def words(self) -> List[Word16]:
        """Return words list of eight Word16.

        ### Returns:
        List[Word16] - List of eight Word16 objects representing each 16-bit segment.
        """
        tmp: list[str] = Address6.__expand_ipv6(str(self)).split(":")
        return [
            Word16(tmp[0]),
            Word16(tmp[1]),
            Word16(tmp[2]),
            Word16(tmp[3]),
            Word16(tmp[4]),
            Word16(tmp[5]),
            Word16(tmp[6]),
            Word16(tmp[7]),
        ]

    @words.setter
    def words(
        self, value: Union[str, int, Union[List[int], List[str], List[Word16]]]
    ) -> None:
        """Set IPv6 address from string, integer or list of Word16.

        ### Arguments:
        * value: Union[str, int, Union[List[int], List[str], List[Word16]]] - IPv6 address representation.
        """
        if isinstance(value, List):
            self.__set_words_from_list(value)
        elif isinstance(value, int):
            self.__set_words_from_int(value)
        elif isinstance(value, str):
            self.__set_words_from_str(value)
        else:
            raise Raise.error(
                f"Expected String or Integer or List type, received: {type(value)}.",
                TypeError,
                self._c_name,
                currentframe(),
            )


# prefix
# https://www.heficed.com/subnet-mask-cheat-sheet/

TPrefix6 = TypeVar("TPrefix6", bound="Prefix6")


class Prefix6(IComparators, BClasses, NoDynamicAttributes):
    """Prefix6 class for IPv6 addresses.

    Constructor argument:
    prefix: Union[str, int] -- Set prefix from string or integer.

    Public property:
    prefix: str -- Return prefix as string.

    Public setter:
    prefix: Union[str, int] -- Set prefix from string or integer.
    """

    __prefix_int: int = 0

    def __init__(self, prefix: Union[str, int]) -> None:
        """Constructor.

        ### Arguments:
        * prefix: Union[str, int] - IPv6 prefix length (0-128) as string or integer.
        """
        self.prefix = prefix

    def __eq__(self, arg: Union[TPrefix6, object]) -> bool:
        """Equal."""
        if not isinstance(arg, Prefix6):
            raise Raise.error(
                f"Expected argument of Prefix6 type, received: {type(arg)}.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        return int(self) == int(arg)

    def __ge__(self, arg: Union[TPrefix6, object]) -> bool:
        """Greater or equal."""
        if not isinstance(arg, Prefix6):
            raise Raise.error(
                f"Expected argument of Prefix6 type, received: {type(arg)}.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        return int(self) >= int(arg)

    def __gt__(self, arg: Union[TPrefix6, object]) -> bool:
        """Greater."""
        if not isinstance(arg, Prefix6):
            raise Raise.error(
                f"Expected argument of Prefix6 type, received: {type(arg)}.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        return int(self) > int(arg)

    def __le__(self, arg: Union[TPrefix6, object]) -> bool:
        """Less or equal."""
        if not isinstance(arg, Prefix6):
            raise Raise.error(
                f"Expected argument of Prefix6 type, received: {type(arg)}.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        return int(self) <= int(arg)

    def __lt__(self, arg: Union[TPrefix6, object]) -> bool:
        """Less."""
        if not isinstance(arg, Prefix6):
            raise Raise.error(
                f"Expected argument of Prefix6 type, received: {type(arg)}.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        return int(self) < int(arg)

    def __ne__(self, arg: Union[TPrefix6, object]) -> bool:
        """Negative."""
        if not isinstance(arg, Prefix6):
            raise Raise.error(
                f"Expected argument of Prefix6 type, received: {type(arg)}.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        return int(self) != int(arg)

    def __str__(self) -> str:
        """Return prefix as string.

        ### Returns:
        str - The prefix value as string.
        """
        return str(self.__prefix_int)

    def __int__(self) -> int:
        """Return prefix as integer."""
        return self.__prefix_int

    def __repr__(self) -> str:
        """Return Prefix6 representation string."""
        return f"{self._c_name}({int(self)})"

    def __range_validator(self, value: int) -> bool:
        """Proper range validator."""
        if value not in range(0, 129):
            raise Raise.error(
                f"Prefix out of range (0-128), received: {value}",
                ValueError,
                self._c_name,
                currentframe(),
            )
        return True

    @staticmethod
    def __is_integer(value: str) -> bool:
        try:
            int(value)
            return True
        except:
            return False

    @property
    def prefix(self) -> str:
        """Return prefix as string.

        ### Returns:
        str - The prefix value as string.
        """
        return str(self)

    @prefix.setter
    def prefix(self, value: Union[str, int]) -> None:
        """Set prefix from string or integer.

        ### Arguments:
        * value: Union[str, int] - Prefix value as integer (0-128) or string representation.
        """
        if isinstance(value, int) and self.__range_validator(value):
            self.__prefix_int = value
        elif isinstance(value, str):
            if Prefix6.__is_integer(value) and self.__range_validator(int(value)):
                self.__prefix_int = int(value)
            else:
                raise Raise.error(
                    f"Expected proper integer string, '{value}' received.",
                    ValueError,
                    self._c_name,
                    currentframe(),
                )
        else:
            raise Raise.error(
                f"Expected String or Integer type, received: '{type(value)}'.",
                TypeError,
                self._c_name,
                currentframe(),
            )


# Network
class Network6(BClasses, NoDynamicAttributes):
    """Network6 IPv6 class.

    Constructor argument:
    addr: Union[str, List] -- Set IPv6 network address from string or two element list of address [Address6,str,int,list] and prefix [Prefix6, str, int].

    Public property:
    address: Address6 -- Return IPv6 address set in the constructor.
    count: int -- Return count hosts addresses in network range.
    hosts(limit: Optional[int] = DEFAULT_IPV6_HOST_LIMIT): List[Address6] -- Deprecated helper returning host list with an optional safety limit.
    iter_hosts(limit: Optional[int] = DEFAULT_IPV6_HOST_LIMIT) -> Iterator[Address6] -- Lazy host iterator respecting optional limits.
    network: Address6 -- Return network address.
    prefix: Prefix6 -- Return prefix.
    max: Address6 -- Return max address of host in network range.
    min: Address6 -- Return min address of host in network range.
    """

    __address: Address6 = None  # type: ignore
    __prefix: Prefix6 = None  # type: ignore

    def __init__(self, addr: Union[str, List]) -> None:
        """Constructor.

        ### Arguments:
        * addr: Union[str, List] - IPv6 network address in CIDR notation (string) or list format.
        """
        if isinstance(addr, str):
            self.__network_from_str(addr)
        elif isinstance(addr, List):
            self.__network_from_list(addr)
        else:
            raise Raise.error(
                f"Expected IP network string or list type, received: '{type(addr)}'.",
                ValueError,
                self._c_name,
                currentframe(),
            )

    def __str__(self) -> str:
        """Return string representation of network address."""
        return f"{self.network}/{int(self.prefix)}"

    def __repr__(self) -> str:
        """Return  string representation of class object."""
        return f"{self._c_name}('{str(self)}')"

    def __network_from_str(self, addr: str) -> None:
        """Build configuration from string."""
        if addr.find("/") > 0:
            tmp: list[str] = addr.split("/")
            self.__address = Address6(tmp[0])
            self.__prefix = Prefix6(tmp[1])
        else:
            raise Raise.error(
                f"Expected network address in 'ipv6/prefix' format string, received: '{addr}'.",
                ValueError,
                self._c_name,
                currentframe(),
            )

    def __network_from_list(self, addr: List) -> None:
        """Build configuration from list."""
        if len(addr) != 2:
            raise Raise.error(
                "A list of two elements was expected: ['ipv6','prefix']",
                ValueError,
                self._c_name,
                currentframe(),
            )
        if isinstance(addr[0], Address6):
            self.__address = deepcopy(addr[0])
        else:
            self.__address = Address6(addr[0])
        if isinstance(addr[1], Prefix6):
            self.__prefix = deepcopy(addr[1])
        else:
            self.__prefix = Prefix6(addr[1])

    @property
    def address(self) -> Address6:
        """Return IPv6 address.

        ### Returns:
        Address6 - The IPv6 address object.
        """
        return self.__address

    @property
    def count(self) -> int:
        """Return number of hosts in subnet.

        ### Returns:
        int - Number of addresses in the subnet.
        """
        return 2 ** (128 - int(self.prefix))

    def hosts(self, limit: Optional[int] = DEFAULT_IPV6_HOST_LIMIT) -> List[Address6]:
        """Return list of hosts addresses. (Deprecated)

        ### Arguments:
        * limit: Optional[int] - Maximum number of hosts allowed to materialise. Defaults to DEFAULT_IPV6_HOST_LIMIT.

        ### Returns:
        [List[Address6]] - Host addresses contained within the subnet.

        ### Raises:
        * ValueError: Propagated from `iter_hosts()` when the host count exceeds the configured limit.
        """
        warnings.warn(
            "Network6.hosts() is deprecated; use Network6.iter_hosts() for lazy iteration.",
            DeprecationWarning,
            stacklevel=2,
        )
        return list(self.iter_hosts(limit=limit))

    def iter_hosts(
        self, limit: Optional[int] = DEFAULT_IPV6_HOST_LIMIT
    ) -> Iterator[Address6]:
        """Yield IPv6 host addresses lazily.

        ### Arguments:
        * limit: Optional[int] - Maximum number of hosts allowed before raising. Defaults to DEFAULT_IPV6_HOST_LIMIT.

        ### Returns:
        Iterator[Address6] - Generator producing host addresses in ascending order.

        ### Raises:
        * ValueError: Raised when the host count exceeds the configured limit.
        """
        effective_limit = limit
        host_count = self.count
        if effective_limit is not None and host_count > effective_limit:
            raise Raise.error(
                (
                    f"Network6 host count ({host_count}) exceeds limit "
                    f"({effective_limit}). Use iter_hosts(limit=None) for explicit override."
                ),
                ValueError,
                self._c_name,
                currentframe(),
            )
        start = int(self.min)
        for i in range(0, host_count):
            yield Address6(start + i)

    @property
    def max(self) -> Address6:
        """Return last IPv6 address from subnet.

        ### Returns:
        Address6 - The last address in the subnet.
        """
        return Address6(int(self.network) + self.count - 1)

    @property
    def min(self) -> Address6:
        """Return first IPv6 address from subnet.

        ### Returns:
        Address6 - The first address in the subnet.
        """
        ip = int(self.address)
        mask: int = (1 << 128 - int(self.prefix)) - 1
        net: int = ip & ~mask
        subnet_address = []
        for _ in range(8):
            subnet_address.insert(0, format(net & 0xFFFF, "x"))
            net >>= 16
        return Address6(":".join(subnet_address))

    @property
    def network(self) -> Address6:
        """Return network address.

        ### Returns:
        Address6 - The network address.
        """
        return self.min

    @property
    def prefix(self) -> Prefix6:
        """Return IPv6 network prefix.

        ### Returns:
        Prefix6 - The network prefix object.
        """
        return self.__prefix


# SubNetwork
class SubNetwork6(BClasses, NoDynamicAttributes):
    """SubNetwork6 calculator class.

    Constructor argument:
    network: Network6 -- The address of the network where the subnet is being searched for.
    prefix: Prefix6 -- Subnet prefix.

    Public property:
    subnets(limit: Optional[int] = DEFAULT_IPV6_SUBNET_LIMIT): List[Network6] -- Deprecated helper returning subnet list with an optional safety limit.
    iter_subnets(limit: Optional[int] = DEFAULT_IPV6_SUBNET_LIMIT) -> Iterator[Network6] -- Lazy subnet iterator.
    """

    __network: Network6 = None  # type: ignore
    __prefix: Prefix6 = None  # type: ignore

    def __init__(self, network: Network6, prefix: Prefix6) -> None:
        """Constructor.

        ### Arguments:
        * network: Network6 - IPv6 network address object.
        * prefix: Prefix6 - Prefix object defining the subnet size.
        """
        if isinstance(network, Network6) and isinstance(prefix, Prefix6):
            if int(network.prefix) <= int(prefix):
                self.__network = network
                self.__prefix = prefix
            else:
                raise Raise.error(
                    (
                        "The network prefix must be greater then or equal to the subnet prefix you are looking for."
                        f"Received: {int(network.prefix)} and {int(prefix)}"
                    ),
                    ValueError,
                    self._c_name,
                    currentframe(),
                )
        else:
            raise Raise.error(
                f"Argument of (Network6, Prefix6) expected, ({type(network)},{type(prefix)}) received.",
                TypeError,
                self._c_name,
                currentframe(),
            )

    def subnets(
        self, limit: Optional[int] = DEFAULT_IPV6_SUBNET_LIMIT
    ) -> List[Network6]:
        """Return subnets list. (Deprecated)

        ### Arguments:
        * limit: Optional[int] - Maximum number of subnetworks allowed before raising. Defaults to DEFAULT_IPV6_SUBNET_LIMIT.

        ### Returns:
        [List[Network6]] - Generated IPv6 subnetworks.

        ### Raises:
        * ValueError: Propagated from `iter_subnets()` when the subnet count exceeds the configured limit.
        """
        warnings.warn(
            "SubNetwork6.subnets() is deprecated; use SubNetwork6.iter_subnets() for lazy iteration.",
            DeprecationWarning,
            stacklevel=2,
        )
        return list(self.iter_subnets(limit=limit))

    def iter_subnets(
        self, limit: Optional[int] = DEFAULT_IPV6_SUBNET_LIMIT
    ) -> Iterator[Network6]:
        """Yield IPv6 subnetworks lazily.

        ### Arguments:
        * limit: Optional[int] - Maximum number of subnetworks allowed before raising. Defaults to DEFAULT_IPV6_SUBNET_LIMIT.

        ### Returns:
        Iterator[Network6] - Generator producing IPv6 subnetworks in ascending order.

        ### Raises:
        * ValueError: Raised when the subnet count exceeds the configured limit.
        """
        effective_limit = limit
        produced = 0
        net_start = int(self.__network.min)
        net_end = int(self.__network.max)
        start: int = net_start
        while True:
            if effective_limit is not None and produced >= effective_limit:
                raise Raise.error(
                    (
                        f"Subnet count exceeds limit ({effective_limit}). "
                        "Use iter_subnets(limit=None) for explicit override."
                    ),
                    ValueError,
                    self._c_name,
                    currentframe(),
                )
            subnet = Network6([Address6(start), self.__prefix])
            yield subnet
            produced += 1
            if int(subnet.max) >= net_end:
                break
            start = int(subnet.max) + 1


# #[EOF]#######################################################################
