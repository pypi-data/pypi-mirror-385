# -*- coding: UTF-8 -*-
"""
Author:  Jacek Kotlarski --<szumak@virthost.pl>
Created: 08.12.2023

Purpose: Query class as helper for build query elements dict.
"""

from copy import copy
from typing import Dict, Optional

from .....basetool.data import BData
from .....attribtool import ReadOnlyClass


class RBQuery(BData):
    """RBQuery class helper."""

    class Keys(object, metaclass=ReadOnlyClass):
        """Immutable keys for RBQuery internal storage."""

        SEARCH = "_search_query_"

    def __init__(self) -> None:
        """Constructor."""
        self._set_data(
            key=RBQuery.Keys.SEARCH,
            set_default_type=Dict,
            value={},
        )

    def add_attrib(self, attrib: str, value: Optional[str] = None) -> None:
        """Build query

        ### Arguments:
        * attrib -- name of the attribute being searched for

        ### Keyword Arguments:
        * value -- optional value of the attribute being searched for
          (default: {None})
        """
        self._get_data(key=RBQuery.Keys.SEARCH)[attrib] = value  # type: ignore

    @property
    def query(self) -> Dict:
        """Returns query dict.

        ### Returns:
        Dict - Copy of the search query dictionary.
        """
        return copy(self._get_data(key=RBQuery.Keys.SEARCH))  # type: ignore


# #[EOF]#######################################################################
