# -*- coding: utf-8 -*-
"""
Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: 2024-10-10

Purpose: Data container classes.
"""

from typing import Union, Optional

from ..attribtool import ReadOnlyClass
from ..basetool.data import BData
from .stars import StarsSystem


class _Keys(object, metaclass=ReadOnlyClass):
    """Internal Keys container class."""

    CMDR: str = "__cmdr__"
    JUMP_RANGE: str = "__jump_range__"
    JUMP_SYSTEM: str = "__jump_system__"
    PLUGIN_NAME: str = "__plugin_name__"
    SHUTDOWN: str = "__shutdown__"
    STARS_SYSTEM: str = "__stars_system__"
    VERSION: str = "__version__"


class RscanData(BData):
    """Data container for username and current system."""

    def __init__(self) -> None:
        """Initialize dataset."""
        self._set_data(
            key=_Keys.CMDR,
            set_default_type=Optional[str],
            value=None,
        )
        self._set_data(
            key=_Keys.PLUGIN_NAME,
            set_default_type=Optional[str],
            value=None,
        )
        self._set_data(
            key=_Keys.VERSION,
            set_default_type=Optional[str],
            value=None,
        )
        self._set_data(
            key=_Keys.JUMP_RANGE,
            set_default_type=float,
            value=1.0,
        )
        self._set_data(
            key=_Keys.JUMP_SYSTEM, set_default_type=StarsSystem, value=StarsSystem()
        )
        self._set_data(
            key=_Keys.STARS_SYSTEM,
            set_default_type=StarsSystem,
            value=StarsSystem(),
        )
        self._set_data(
            key=_Keys.SHUTDOWN,
            set_default_type=bool,
            value=False,
        )

    def __repr__(self) -> str:
        """Return class dump."""
        return (
            f"{self._c_name}(cmdr='{self.cmdr}', "
            f"plugin_name='{self.plugin_name}', "
            f"version='{self.version}', "
            f"jump_range={self.jump_range}, "
            f"{self.stars_system})"
        )

    @property
    def jump_system(self) -> StarsSystem:
        """Return the jump destination StarsSystem object.

        ### Returns:
        StarsSystem - The jump target system instance.
        """
        return self._get_data(key=_Keys.JUMP_SYSTEM)  # type: ignore

    @jump_system.setter
    def jump_system(self, value: Optional[StarsSystem]) -> None:
        """Assign the jump destination system.

        ### Arguments:
        * value: Optional[StarsSystem] - Jump target system or None to reset.
        """
        if value is None:
            self._set_data(key=_Keys.JUMP_SYSTEM, value=StarsSystem())
            return
        self._set_data(
            key=_Keys.JUMP_SYSTEM,
            value=value,
        )

    @property
    def stars_system(self) -> StarsSystem:
        """Return the current StarsSystem object.

        ### Returns:
        StarsSystem - The current system instance.
        """
        return self._get_data(key=_Keys.STARS_SYSTEM)  # type: ignore

    @stars_system.setter
    def stars_system(self, value: Optional[StarsSystem]) -> None:
        """Assign the current stars system.

        ### Arguments:
        * value: Optional[StarsSystem] - Current system or None to reset.
        """
        if value is None:
            self._set_data(key=_Keys.STARS_SYSTEM, value=StarsSystem())
            return
        self._set_data(
            key=_Keys.STARS_SYSTEM,
            value=value,
        )

    @property
    def jump_range(self) -> float:
        """Return the ship's maximum jump range.

        ### Returns:
        float - Jump range value in light years.
        """
        return self._get_data(key=_Keys.JUMP_RANGE)  # type: ignore

    @jump_range.setter
    def jump_range(self, value: Union[str, int, float]) -> None:
        """Assign the ship's jump range.

        ### Arguments:
        * value: Union[str, int, float] - Jump range to set (convertible to float).
        """
        if value is not None and isinstance(value, (str, int, float)):
            try:
                self._set_data(
                    key=_Keys.JUMP_RANGE,
                    value=float(value),
                )
            except Exception:
                pass

    @property
    def plugin_name(self) -> str:
        """Return the plugin name.

        ### Returns:
        str - Name of the EDMC plugin.
        """
        return self._get_data(key=_Keys.PLUGIN_NAME)  # type: ignore

    @plugin_name.setter
    def plugin_name(self, value: Optional[str]) -> None:
        """Assign the plugin name.

        ### Arguments:
        * value: Optional[str] - Plugin name string.
        """
        if value is not None and isinstance(value, str):
            self._set_data(key=_Keys.PLUGIN_NAME, value=value)

    @property
    def version(self) -> str:
        """Return the plugin version.

        ### Returns:
        str - Version string of the plugin.
        """
        return self._get_data(
            key=_Keys.VERSION,
        )  # type: ignore

    @version.setter
    def version(self, value: Optional[str]) -> None:
        """Assign the plugin version.

        ### Arguments:
        * value: Optional[str] - Version string.
        """
        if value is not None and isinstance(value, str):
            self._set_data(
                key=_Keys.VERSION,
                value=value,
            )

    @property
    def cmdr(self) -> str:
        """Return the commander name.

        ### Returns:
        str - Current commander name.
        """
        return self._get_data(
            key=_Keys.CMDR,
        )  # type: ignore

    @cmdr.setter
    def cmdr(self, value: Optional[str]) -> None:
        """Assign the commander name.

        ### Arguments:
        * value: Optional[str] - Commander name string.
        """
        if value is not None and value != self.cmdr:
            self._set_data(key=_Keys.CMDR, value=value)

    @property
    def shutting_down(self) -> bool:
        """Return the shutting down flag status.

        ### Returns:
        bool - True if the plugin is shutting down.
        """
        return self._get_data(
            key=_Keys.SHUTDOWN,
        )  # type: ignore

    @shutting_down.setter
    def shutting_down(self, value: bool) -> None:
        """Assign the shutting down flag.

        ### Arguments:
        * value: bool - Shutdown flag status.
        """
        self._set_data(
            key=_Keys.SHUTDOWN,
            value=value,
        )


# #[EOF]#######################################################################
