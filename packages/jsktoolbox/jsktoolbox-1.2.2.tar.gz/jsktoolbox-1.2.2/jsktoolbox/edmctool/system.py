# -*- coding: utf-8 -*-
"""
Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: 2024-10-07

Purpose: EDMC plugins system classes.
"""

import os

from ..basetool.data import BData
from ..systemtool import Env
from ..attribtool import ReadOnlyClass


class _Keys(object, metaclass=ReadOnlyClass):
    """Internal Keys container class."""

    DIR: str = "__dir__"


class Directory(BData):
    """Container class to store the directory path."""

    def is_directory(self, path_string: str) -> bool:
        """Check if the given string is a directory.

        ### Arguments:
        * path_string: str - Path string to verify.

        ### Returns:
        bool - True when path exists and is a directory, False otherwise.
        """
        return os.path.exists(path_string) and os.path.isdir(path_string)

    @property
    def dir(self) -> str:
        """Property that returns directory string.

        ### Returns:
        str - The configured directory path.
        """
        return self._get_data(key=_Keys.DIR, default_value="")  # type: ignore

    @dir.setter
    def dir(self, arg: str) -> None:
        """Setter for directory string.

        ### Arguments:
        * arg: str - Directory path to assign. Must exist and be a valid directory.
        """
        if self.is_directory(arg):
            self._set_data(key=_Keys.DIR, value=arg, set_default_type=str)


class EnvLocal(Env):
    """Environmental class."""

    def __init__(self) -> None:
        """Initialize Env class."""
        super().__init__()

    def check_dir(self, directory: str) -> str:
        """Check if dir exists, return dir or else HOME.

        ### Arguments:
        * directory: str - Directory path to verify.

        ### Returns:
        str - Validated directory path or home directory when invalid.
        """
        if not Directory().is_directory(directory):
            return self.home
        return directory

    @property
    def plugin_dir(self) -> str:
        """Return plugin dir path.

        ### Returns:
        str - The plugin directory path.
        """
        return f"{os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))}"


# #[EOF]#######################################################################
