# -*- coding: utf-8 -*-
"""
Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: 2024-10-10

Purpose: Mathematical algorithms for route optimization in Elite Dangerous.
"""

from __future__ import annotations

import math
import time
import random

from inspect import currentframe
from queue import Queue, SimpleQueue
from typing import Optional, List, Tuple, Union, Any, Dict
from types import FrameType, MethodType
from abc import ABC, abstractmethod
from itertools import permutations
from sys import maxsize

from types import FrameType

from .ed_keys import EDKeys

from ..attribtool import ReadOnlyClass
from ..raisetool import Raise
from .base import BLogClient
from .logs import LogClient
from .data import RscanData
from .stars import StarsSystem
from .edsm_keys import EdsmKeys

try:
    import numpy as np  # pyright: ignore[reportMissingImports]
except ModuleNotFoundError:
    np = None  # type: ignore[assignment]

try:
    from scipy.spatial import distance  # pyright: ignore[reportMissingImports]
except ModuleNotFoundError:
    distance = None  # type: ignore[assignment]


class IAlg(ABC):
    """Interface for algorithm class ."""

    @abstractmethod
    def run(self) -> None:
        """Run the work."""

    @abstractmethod
    def debug(self, currentframe: Optional[FrameType], message: str) -> None:
        """Debug formatter for logger."""

    @property
    @abstractmethod
    def get_final(self) -> list:
        """Return final data.

        ### Returns:
        List[StarsSystem] - List of star systems in the final route.
        """

    @property
    @abstractmethod
    def final_distance(self) -> float:
        """Return final distance.

        ### Returns:
        float - The total distance of the final route.
        """


class _Keys(object, metaclass=ReadOnlyClass):
    """Internal Keys container class."""

    E_METHODS: str = "__e_methods__"
    R_DATA: str = "__e_r_data__"


def _filter_reachable_points(
    start: StarsSystem,
    systems: List[StarsSystem],
    euclid_alg: Euclid,
    jump_range: int,
) -> List[StarsSystem]:
    """Return systems reachable from `start` under the jump range constraint."""

    reachable: List[StarsSystem] = []
    frontier: List[StarsSystem] = [start]
    remaining: List[StarsSystem] = [
        system for system in systems if isinstance(system, StarsSystem)
    ]

    while frontier:
        current = frontier.pop(0)
        for candidate in remaining[:]:
            if euclid_alg.distance(current.star_pos, candidate.star_pos) <= jump_range:
                reachable.append(candidate)
                frontier.append(candidate)
                remaining.remove(candidate)

    return reachable


class Euclid(BLogClient):
    """Euclid.

    A class that calculates the length of a vector in Cartesian space.
    """

    def __init__(self, queue: Union[Queue, SimpleQueue], r_data: RscanData) -> None:
        """Create class object.

        ### Arguments:
        * queue: Union[Queue, SimpleQueue] - Queue for communication and logging.
        * r_data: RscanData - Route scan data container.
        """

        methods: List[MethodType] = []

        if np is not None:
            methods.extend(
                [
                    self.__numpy_l2,
                    self.__numpy,
                    self.__einsum,
                ]
            )
        if distance is not None:
            methods.append(self.__scipy)
        methods.extend(
            [
                self.__math,
                self.__core,
            ]
        )

        self._set_data(
            key=_Keys.E_METHODS,
            set_default_type=List,
            value=methods,
        )

        # init log subsystem
        if isinstance(queue, (Queue, SimpleQueue)):
            self.logger = LogClient(queue)
        else:
            raise Raise.error(
                f"Queue or SimpleQueue type expected, '{type(queue)}' received.",
                TypeError,
                self._c_name,
                currentframe(),
            )

        if isinstance(r_data, RscanData):
            self._set_data(
                key=_Keys.R_DATA,
                set_default_type=RscanData,
                value=r_data,
            )
            self.debug(currentframe(), f"{r_data}")
        else:
            raise Raise.error(
                f"RscanData type expected, '{type(r_data)}' received",
                TypeError,
                self._c_name,
                currentframe(),
            )

        self.debug(currentframe(), "Initialize dataset")

    @property
    def __r_data(self) -> RscanData:
        """Return data.

        ### Returns:
        RscanData - The route scan data object.
        """
        return self._get_data(key=_Keys.R_DATA)  # type: ignore

    @property
    def __euclid_methods(self) -> List[MethodType]:
        """Return test list.

        ### Returns:
        List[MethodType] - List of euclidean distance calculation methods.
        """
        return self._get_data(key=_Keys.E_METHODS)  # type: ignore

    def benchmark(self) -> None:
        """Do benchmark test.

        Compare the computational efficiency of functions for real data
        and choose the right priority of their use.
        """
        p_name: str = f"{self.__r_data.plugin_name}"
        c_name: str = f"{self._c_name}"

        if self.logger:
            self.logger.info = f"{p_name}->{c_name}: Warming up math system..."
        data1: List[List[float]] = [
            [641.71875, -536.06250, -6886.37500],
            [10.31250, -160.53125, 74.18750],
            [51.40625, -54.40625, -30.50000],
            [45.59375, -51.90625, -39.46875],
            [22.28125, -43.40625, -36.18750],
            [11.18750, -37.37500, -31.84375],
            [5.90625, -30.50000, -36.37500],
            [11.18750, -37.37500, -31.84375],
            [5.62500, -36.65625, -33.87500],
            [-0.56250, -43.71875, -30.81250],
        ]
        data2: List[List[float]] = [
            [67.50000, -74.90625, -93.68750],
            [134.12500, 15.09375, -63.87500],
            [124.50000, 4.31250, -49.12500],
            [118.93750, -8.53125, -33.46875],
            [105.96875, -20.87500, -22.21875],
            [95.40625, -33.50000, -11.40625],
            [78.34375, -42.96875, -2.21875],
            [66.84375, -60.65625, -3.84375],
            [60.93750, -75.25000, 10.87500],
            [58.28125, -92.09375, 23.71875],
        ]

        # build test
        test = []
        bench_out = {}

        for item in self.__euclid_methods:
            if item(data1[0], data2[0]) is not None:
                test.append(item)

        # start test
        for item in test:
            t_start: float = time.time()
            for idx in range(0, len(data1)):
                item(data1[idx], data2[idx])
            t_stop: float = time.time()
            bench_out[t_stop - t_start] = item

        # optimize list of the methods
        self.__euclid_methods.clear()
        for idx in sorted(bench_out.keys()):
            self.__euclid_methods.append(bench_out[idx])
            self.debug(currentframe(), f"{idx}: {bench_out[idx]}")

        if self.logger:
            self.logger.info = f"{p_name}->{c_name}: done."

    def debug(self, currentframe: Optional[FrameType], message: str = "") -> None:
        """Build debug message."""
        p_name: str = f"{self.__r_data.plugin_name}"
        c_name: str = f"{self._c_name}"
        m_name: str = (
            f"{currentframe.f_code.co_name}" if currentframe is not None else ""
        )
        if message != "":
            message = f": {message}"
        if self.logger:
            self.logger.debug = f"{p_name}->{c_name}.{m_name}{message}"

    def __core(self, point_1: List[float], point_2: List[float]) -> float:
        """Do calculations without math libraries.

        The method iterates over each pair of vector elements,
        performs calculations on it and sums up the intermediate results.
        """
        return sum((i - j) ** 2 for i, j in zip(point_1, point_2)) ** 0.5
        # return math.sqrt(sum((i - j) ** 2 for i, j in zip(point_1, point_2)))

    def __math(self, point_1: List[float], point_2: List[float]) -> Optional[float]:
        """Try to use math lib."""
        try:
            return math.dist(point_1, point_2)
        except Exception as ex:
            self.debug(currentframe(), f"{ex}")
        return None

    def __numpy_l2(self, point_1: List[float], point_2: List[float]) -> Optional[float]:
        """Try to use numpy lib.

        The method uses the fact that the Euclidean distance of two vectors
        is nothing but the L^2 norm of their difference.
        """
        try:
            return np.linalg.norm(np.array(point_1) - np.array(point_2))  # type: ignore
        except Exception as ex:
            self.debug(currentframe(), f"{ex}")
        return None

    def __numpy(self, point_1: List[float], point_2: List[float]) -> Optional[float]:
        """Try to use numpy lib.

        The method is an optimization of the core method using numpy
        and vectorization.
        """
        try:
            return np.sqrt(
                np.sum((np.array(point_1) - np.array(point_2)) ** 2)
            )  # pyright: ignore[reportOptionalMemberAccess]
        except Exception as ex:
            self.debug(currentframe(), f"{ex}")
        return None

    def __einsum(self, point_1: List[float], point_2: List[float]) -> Optional[float]:
        """Try to use numpy lib.

        Einstein summation convention.
        """
        try:
            tmp = np.array(point_1) - np.array(
                point_2
            )  # pyright: ignore[reportOptionalMemberAccess]
            return np.sqrt(
                np.einsum("i,i->", tmp, tmp)
            )  # pyright: ignore[reportOptionalMemberAccess]
        except Exception as ex:
            self.debug(currentframe(), f"{ex}")
        return None

    def __scipy(self, point_1: List[float], point_2: List[float]) -> Optional[float]:
        """Try to use scipy lib.

        The scipy library has a built-in function to calculate
        the Euclidean distance.
        """
        try:
            return distance.euclidean(
                point_1, point_2
            )  # pyright: ignore[reportOptionalMemberAccess]
        except Exception as ex:
            self.debug(currentframe(), f"{ex}")
        return None

    def distance(self, point_1: List[float], point_2: List[float]) -> float:
        """Find the first working algorithm and do the calculations."""
        out: float = None  # type: ignore
        i = 0

        while out is None:
            if i < len(self.__euclid_methods):
                out = self.__euclid_methods[i](point_1, point_2)
            else:
                break
            i += 1

        return out


class AlgAStar(IAlg, BLogClient):
    """A* pathfinding algorithm implementation for route optimization."""

    __plugin_name: str = None  # type: ignore
    __math: Euclid = None  # type: ignore
    __points: List[StarsSystem] = None  # type: ignore
    __active_points: List[StarsSystem] = None  # type: ignore
    __jump_range: int = None  # type: ignore
    __final: List[StarsSystem] = None  # type: ignore
    __start_point: StarsSystem = None  # type: ignore

    def __init__(
        self,
        start: StarsSystem,
        systems: List[StarsSystem],
        jump_range: int,
        log_queue: Optional[Union[Queue, SimpleQueue]],
        euclid_alg: Euclid,
        plugin_name: str,
    ) -> None:
        """Initialize A* pathfinding algorithm.

        Sets up the A* algorithm for finding optimal routes between star systems
        considering jump range constraints and using Euclidean distance calculations.

        ### Arguments:
        * start: StarsSystem - Starting point for pathfinding.
        * systems: List[StarsSystem] - List of available star systems to navigate through.
        * jump_range: int - Maximum jump distance allowed between systems.
        * log_queue: Optional[Union[Queue, SimpleQueue]] - Queue for logging operations.
        * euclid_alg: Euclid - Euclidean distance calculation algorithm instance.
        * plugin_name: str - Name of the plugin using this algorithm.

        ### Raises:
        * TypeError: If log_queue is not Queue or SimpleQueue type.
        * TypeError: If euclid_alg is not Euclid type.
        * TypeError: If jump_range is not int type.
        * TypeError: If start is not StarsSystem type.
        * TypeError: If systems is not list type.
        """
        self.__plugin_name = plugin_name
        # init log subsystem
        if isinstance(log_queue, (Queue, SimpleQueue)):
            self.logger = LogClient(log_queue)
        else:
            raise Raise.error(
                f"Queue or SimpleQueue type expected, '{type(log_queue)}' received.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        # Euclid's algorithm for calculating the length of vectors
        if isinstance(euclid_alg, Euclid):
            self.__math = euclid_alg
        else:
            raise Raise.error(
                f"Euclid type expected, '{type(euclid_alg)}' received",
                TypeError,
                self._c_name,
                currentframe(),
            )
        if isinstance(jump_range, int):
            self.__jump_range = jump_range
        else:
            raise Raise.error(
                f"Int type expected, '{type(jump_range)}' received",
                TypeError,
                self._c_name,
                currentframe(),
            )
        if not isinstance(start, StarsSystem):
            raise Raise.error(
                f"StarsSystem type expected, '{type(start)}' received.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        if not isinstance(systems, List):
            raise Raise.error(
                f"list type expected, '{type(systems)}' received.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        self.debug(currentframe(), "Initialize dataset")

        self.__start_point = start
        self.__points = [
            system for system in systems if isinstance(system, StarsSystem)
        ]
        self.__final = []

    def __get_neighbors(
        self,
        point: StarsSystem,
        candidates: List[StarsSystem],
    ) -> List[StarsSystem]:
        """Return points reachable from `point` within the jump range."""
        neighbors: List[StarsSystem] = []
        for candidate in candidates:
            if (
                self.__math.distance(point.star_pos, candidate.star_pos)
                <= self.__jump_range
            ):
                neighbors.append(candidate)
        return neighbors

    def __reconstruct_path(
        self, came_from: dict, current: StarsSystem
    ) -> List[StarsSystem]:
        """Rekonstruuje ścieżkę od punktu startowego do celu."""
        path: List[StarsSystem] = []
        while current in came_from:
            path.append(current)
            current = came_from[current]
        path.reverse()
        return path

    def debug(self, currentframe: Optional[FrameType], message: str = "") -> None:
        """Build debug message."""
        p_name: str = f"{self.__plugin_name}"
        c_name: str = f"{self._c_name}"
        m_name: str = f"{currentframe.f_code.co_name}" if currentframe else ""
        if message != "":
            message = f": {message}"
        if self.logger:
            self.logger.debug = f"{p_name}->{c_name}.{m_name}{message}"

    def run(self) -> None:
        """Greedy path finder honoring jump range constraints."""
        start_t: float = time.time()
        reachable: List[StarsSystem] = _filter_reachable_points(
            self.__start_point,
            self.__points,
            self.__math,
            self.__jump_range,
        )
        remaining: List[StarsSystem] = reachable[:]
        self.__final = []

        if not remaining:
            self.debug(currentframe(), "No reachable targets")
            return

        current: StarsSystem = self.__start_point

        while remaining:
            neighbors = self.__get_neighbors(current, remaining)
            if not neighbors:
                # brak dalszych punktów w zasięgu – przerywamy poszukiwanie
                self.debug(currentframe(), "No reachable neighbors found")
                break
            next_point = min(
                neighbors,
                key=lambda point: self.__math.distance(
                    current.star_pos, point.star_pos
                ),
            )
            self.__final.append(next_point)
            remaining.remove(next_point)
            current = next_point

        if self.__final:
            dist = self.__math.distance(
                self.__start_point.star_pos, self.__final[0].star_pos
            )
            self.__final[0].data[EdsmKeys.DISTANCE] = dist
            for idx in range(len(self.__final) - 1):
                dist = self.__math.distance(
                    self.__final[idx].star_pos,
                    self.__final[idx + 1].star_pos,
                )
                self.__final[idx + 1].data[EdsmKeys.DISTANCE] = dist

        end_t: float = time.time()
        self.debug(
            currentframe(),
            f"Path constructed in {end_t - start_t:.4f}s, visited {len(self.__final)} nodes",
        )

    @property
    def final_distance(self) -> float:
        """Calculate the total distance of the final route.

        ### Returns:
        float - Total distance in light years, or 0.0 if no route found.
        """
        if not self.__final:
            return 0.0
        dist = self.__math.distance(
            self.__start_point.star_pos, self.__final[0].star_pos
        )
        for item in range(len(self.__final) - 1):
            dist += self.__math.distance(
                self.__final[item].star_pos, self.__final[item + 1].star_pos
            )
        return dist if dist else 0.0

    @property
    def get_final(self) -> List[StarsSystem]:
        """Return final data.

        ### Returns:
        List[StarsSystem] - List of star systems in the final route.
        """
        return [point for point in self.__final if point != self.__start_point]


class AlgTsp(IAlg, BLogClient):
    """Travelling salesman problem."""

    __plugin_name: str = None  # type: ignore
    __math: Euclid = None  # type: ignore
    __points: List[StarsSystem] = None  # type: ignore
    __jump_range: int = None  # type: ignore
    __final: List[StarsSystem] = None  # type: ignore
    __costs: List[List[float]] = None  # type: ignore
    __route: List[int] = None  # type: ignore
    __total_distance: float = 0.0

    def __init__(
        self,
        start: StarsSystem,
        systems: List[StarsSystem],
        jump_range: int,
        log_queue: Optional[Union[Queue, SimpleQueue]],
        euclid_alg: Euclid,
        plugin_name: str,
    ) -> None:
        """Construct instance object.

        ### Arguments:
        * start: StarsSystem - Starting position object.
        * systems: List[StarsSystem] - List of points of interest to visit.
        * jump_range: int - Maximum jump range in light years.
        * log_queue: Optional[Union[Queue, SimpleQueue]] - Queue for LogClient communication.
        * euclid_alg: Euclid - Initialized Euclidean distance calculation object.
        * plugin_name: str - Name of the plugin for debug logging.
        """
        self.__plugin_name = plugin_name
        # init log subsystem
        if isinstance(log_queue, (Queue, SimpleQueue)):
            self.logger = LogClient(log_queue)
        else:
            raise Raise.error(
                f"Queue or SimpleQueue type expected, '{type(log_queue)}' received.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        # Euclid's algorithm for calculating the length of vectors
        if isinstance(euclid_alg, Euclid):
            self.__math = euclid_alg
        else:
            raise Raise.error(
                f"Euclid type expected, '{type(euclid_alg)}' received",
                TypeError,
                self._c_name,
                currentframe(),
            )
        if isinstance(jump_range, int):
            self.__jump_range = jump_range
        else:
            raise Raise.error(
                f"Int type expected, '{type(jump_range)}' received",
                TypeError,
                self._c_name,
                currentframe(),
            )
        if not isinstance(start, StarsSystem):
            raise Raise.error(
                f"StarsSystem type expected, '{type(start)}' received.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        if not isinstance(systems, list):
            raise Raise.error(
                f"list type expected, '{type(systems)}' received.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        self.debug(currentframe(), "Initialize dataset")

        self.__final = []
        self.__points = [start]
        self.__points.extend(
            [system for system in systems if isinstance(system, StarsSystem)]
        )
        self.__costs = []
        self.__route = []
        self.__total_distance = 0.0

    def run(self) -> None:
        """Run algorithm."""
        if not self.__points:
            self.__final = []
            self.__total_distance = 0.0
            return

        start = self.__points[0]
        reachable = _filter_reachable_points(
            start,
            self.__points[1:],
            self.__math,
            self.__jump_range,
        )
        points = [start]
        points.extend(reachable)

        if len(points) == 1:
            self.__final = []
            self.__total_distance = 0.0
            return

        self.__stage_1_costs(points)
        self.__stage_2_solution(points)
        self.__final_update(points)

    def __stage_1_costs(self, points: List[StarsSystem]) -> None:
        """Stage 1: generate a cost table."""
        self.__costs = []
        count: int = len(points)
        for idx in range(count):
            row: List[float] = []
            for idx2 in range(count):
                row.append(
                    self.__math.distance(points[idx].star_pos, points[idx2].star_pos)
                )
            self.__costs.append(row)
        self.debug(currentframe(), f"{self.__costs}")

    def __stage_2_solution(self, points: List[StarsSystem]) -> None:
        """Stage 2: search the solution."""
        out: List[Any] = []
        vertex: List[int] = []
        start: int = 0
        for i in range(len(points)):
            if i != start:
                vertex.append(i)
        # store minimum weight Hamilton Cycle
        min_path: float = float(maxsize)
        next_permutation = permutations(vertex)

        best_first_edge: float = float("inf")

        for i in next_permutation:
            # store current path weight (open tour)
            first_edge: float = self.__costs[start][i[0]]
            current_path_weight: float = first_edge
            for idx in range(len(i) - 1):
                current_path_weight += self.__costs[i[idx]][i[idx + 1]]

            # update minimum
            if current_path_weight < min_path or (
                current_path_weight == min_path and first_edge < best_first_edge
            ):
                out = [current_path_weight, i]
                min_path = current_path_weight
                best_first_edge = first_edge

        # best solution
        if self.logger:
            self.logger.debug = f"DATA: {points}"
        if self.logger:
            self.logger.debug = f"PATH: {out}"
        if out:
            self.__route = [0]
            self.__route.extend(list(out[1]))
        else:
            self.__route = [idx for idx in range(len(points))]

    def __final_update(self, points: List[StarsSystem]) -> None:
        """Build final dataset."""
        self.__final = []
        self.__total_distance = 0.0
        if self.logger:
            self.logger.debug = f"ROUTE: {self.__route}"
        for idx in range(1, len(self.__route)):
            prev_idx = self.__route[idx - 1]
            cur_idx = self.__route[idx]
            system: StarsSystem = points[cur_idx]
            distance_segment = self.__math.distance(
                points[prev_idx].star_pos,
                system.star_pos,
            )
            system.data[EdsmKeys.DISTANCE] = distance_segment
            self.__total_distance += distance_segment
            self.__final.append(system)
        if self.logger:
            self.logger.debug = f"FINAL Distance: {self.__total_distance:.2f} ly"
        if self.logger:
            self.logger.debug = f"INPUT: {self.__points}"
        if self.logger:
            self.logger.debug = f"OUTPUT: {self.__final}"

    def debug(self, currentframe: Optional[FrameType], message: str = "") -> None:
        """Build debug message."""
        p_name: str = f"{self.__plugin_name}"
        c_name: str = f"{self._c_name}"
        m_name: str = f"{currentframe.f_code.co_name}" if currentframe else ""
        if message != "":
            message = f": {message}"
        if self.logger:
            self.logger.debug = f"{p_name}->{c_name}.{m_name}{message}"

    @property
    def final_distance(self) -> float:
        """Calculate the total distance of the final route.

        ### Returns:
        float - Total distance in light years, or 0.0 if no route found.
        """
        return self.__total_distance

    @property
    def get_final(self) -> List[StarsSystem]:
        """Return final data.

        ### Returns:
        List[StarsSystem] - List of star systems in the final route.
        """
        return self.__final


class AlgGeneric(IAlg, BLogClient):
    """Generic optimization algorithm for route planning."""

    __plugin_name: str = None  # type: ignore
    __math: Euclid = None  # type: ignore

    __start_point: StarsSystem = None  # type: ignore
    __points: List[StarsSystem] = None  # type: ignore
    __jump_range: int = 0
    __final: List[StarsSystem] = None  # type: ignore

    def __init__(
        self,
        start: StarsSystem,
        systems: List[StarsSystem],
        jump_range: int,
        log_queue: Optional[Union[Queue, SimpleQueue]],
        euclid_alg: Euclid,
        plugin_name: str,
    ) -> None:
        """Construct instance object.

        ### Arguments:
        * start: StarsSystem - Starting position object.
        * systems: List[StarsSystem] - List of points of interest to visit.
        * jump_range: int - Maximum jump range in light years.
        * log_queue: Optional[Union[Queue, SimpleQueue]] - Queue for LogClient communication.
        * euclid_alg: Euclid - Initialized Euclidean distance calculation object.
        * plugin_name: str - Name of the plugin for debug logging.
        """
        self.__plugin_name = plugin_name
        # init log subsystem
        if isinstance(log_queue, (Queue, SimpleQueue)):
            self.logger = LogClient(log_queue)
        else:
            raise Raise.error(
                f"Queue or SimpleQueue type expected, '{type(log_queue)}' received.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        # Euclid's algorithm for calculating the length of vectors
        if isinstance(euclid_alg, Euclid):
            self.__math = euclid_alg
        else:
            raise Raise.error(
                f"Euclid type expected, '{type(euclid_alg)}' received",
                TypeError,
                self._c_name,
                currentframe(),
            )
        if isinstance(jump_range, int):
            self.__jump_range = jump_range
        else:
            raise Raise.error(
                f"Int type expected, '{type(jump_range)}' received",
                TypeError,
                self._c_name,
                currentframe(),
            )
        if not isinstance(start, StarsSystem):
            raise Raise.error(
                f"StarsSystem type expected, '{type(start)}' received.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        if not isinstance(systems, list):
            raise Raise.error(
                f"list type expected, '{type(systems)}' received.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        self.debug(currentframe(), "Initialize dataset")
        self.__start_point = start
        self.__points = [
            system for system in systems if isinstance(system, StarsSystem)
        ]
        self.__final = []

    def run(self) -> None:
        """Algorytm Genetyczny wyszukujący najkrótszą ścieżkę od punktu start,
        poprzez punkty z listy systems przy założeniach:
         - boki grafu o długości przekraczającej jump_range są wykluczone,
         - algorytm ma przejść przez jak największą liczbę punktów,
         - każdy punkt odwiedzany jest tylko raz,
         - wynikowa lista punktów bez punktu startowego umieszczana jest w self.__final
        """

        start_t: float = time.time()
        current_point: StarsSystem = self.__start_point
        systems: List[StarsSystem] = self.__points[:]
        remaining_systems: List[StarsSystem] = systems  # lista punktów do odwiedzenia

        while remaining_systems:
            # Szukamy najbliższego punktu, który jest w zasięgu jump_range z obecnego punktu
            next_point: Optional[StarsSystem] = None
            min_distance: float = float("inf")

            for system in remaining_systems:
                dist = self.__math.distance(current_point.star_pos, system.star_pos)
                if (
                    dist is not None
                    and dist <= self.__jump_range
                    and dist < min_distance
                ):
                    next_point = system
                    min_distance = dist

            if next_point is None:
                # Nie znaleziono żadnego punktu w zasięgu jump_range
                break

            # Przechodzimy do znalezionego punktu i usuwamy go z listy
            self.__final.append(next_point)
            remaining_systems.remove(next_point)
            current_point = next_point  # Aktualizujemy bieżący punkt

        # update distance
        if self.__final:
            dist: float = self.__math.distance(
                self.__start_point.star_pos, self.__final[0].star_pos
            )
            self.__final[0].data[EdsmKeys.DISTANCE] = dist
            for item in range(len(self.__final) - 1):
                dist = self.__math.distance(
                    self.__final[item].star_pos,
                    self.__final[item + 1].star_pos,
                )
                self.__final[item + 1].data[EdsmKeys.DISTANCE] = dist

        end_t: float = time.time()
        self.debug(currentframe(), f"Evolution took {end_t - start_t} seconds.")

    def debug(self, currentframe: Optional[FrameType], message: str = "") -> None:
        """Build debug message."""
        p_name: str = f"{self.__plugin_name}"
        c_name: str = f"{self._c_name}"
        m_name: str = f"{currentframe.f_code.co_name}" if currentframe else ""
        if message != "":
            message = f": {message}"
        if self.logger:
            self.logger.debug = f"{p_name}->{c_name}.{m_name}{message}"

    @property
    def final_distance(self) -> float:
        """Calculate the total distance of the final route.

        ### Returns:
        float - Total distance in light years, or 0.0 if no route found.
        """
        if not self.__final:
            return 0.0
        dist: float = self.__math.distance(
            self.__start_point.star_pos, self.__final[0].star_pos
        )
        for item in range(len(self.__final) - 1):
            dist += self.__math.distance(
                self.__final[item].star_pos, self.__final[item + 1].star_pos
            )
        return dist if dist else 0.0

    @property
    def get_final(self) -> List[StarsSystem]:
        """Return final data.

        ### Returns:
        List[StarsSystem] - List of star systems in the final route.
        """
        return self.__final


class AlgGenetic(IAlg, BLogClient):
    """Genetic algorithm solving the problem of finding the best path."""

    __plugin_name: str = None  # type: ignore
    __math: Euclid = None  # type: ignore
    __final: List[StarsSystem] = None  # type: ignore

    __points: List[StarsSystem] = None  # type: ignore
    __active_points: List[StarsSystem] = None  # type: ignore
    __start_point: StarsSystem = None  # type: ignore
    __jump_range: int = None  # type: ignore
    __population_size: int = None  # type: ignore
    __generations: int = None  # type: ignore
    __mutation_rate: float = None  # type: ignore
    __crossover_rate: float = None  # type: ignore
    __stagnation_limit: int = None  # type: ignore

    def __init__(
        self,
        start: StarsSystem,
        systems: List[StarsSystem],
        jump_range: int,
        log_queue: Optional[Union[Queue, SimpleQueue]],
        euclid_alg: Euclid,
        plugin_name: str,
    ) -> None:
        """Construct instance object.

        ### Arguments:
        * start: StarsSystem - Starting position object.
        * systems: List[StarsSystem] - List of points of interest to visit.
        * jump_range: int - Maximum jump range in light years.
        * log_queue: Optional[Union[Queue, SimpleQueue]] - Queue for LogClient communication.
        * euclid_alg: Euclid - Initialized Euclidean distance calculation object.
        * plugin_name: str - Name of the plugin for debug logging.
        """

        self.__plugin_name = plugin_name
        # init log subsystem
        if isinstance(log_queue, (Queue, SimpleQueue)):
            self.logger = LogClient(log_queue)
        else:
            raise Raise.error(
                f"Queue or SimpleQueue type expected, '{type(log_queue)}' received.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        # Euclid's algorithm for calculating the length of vectors
        if isinstance(euclid_alg, Euclid):
            self.__math = euclid_alg
        else:
            raise Raise.error(
                f"Euclid type expected, '{type(euclid_alg)}' received",
                TypeError,
                self._c_name,
                currentframe(),
            )
        if isinstance(jump_range, int):
            self.__jump_range = jump_range
        else:
            raise Raise.error(
                f"Int type expected, '{type(jump_range)}' received",
                TypeError,
                self._c_name,
                currentframe(),
            )
        if not isinstance(start, StarsSystem):
            raise Raise.error(
                f"StarsSystem type expected, '{type(start)}' received.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        if not isinstance(systems, list):
            raise Raise.error(
                f"list type expected, '{type(systems)}' received.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        self.debug(currentframe(), "Initialize dataset")

        self.__points = [
            system for system in systems if isinstance(system, StarsSystem)
        ]
        self.__start_point = start
        self.__population_size = len(systems) * 3
        self.__generations = 200
        self.__mutation_rate = 0.01
        self.__crossover_rate = 0.4

    def __generate_individual(self) -> List[StarsSystem]:
        individual: List[StarsSystem] = [self.__start_point]
        source_points = self.__active_points or []
        remaining_points: List[StarsSystem] = source_points[:]
        while remaining_points:
            closest_point: StarsSystem = min(
                remaining_points,
                key=lambda point: self.__math.distance(
                    individual[-1].star_pos, point.star_pos
                ),
            )
            if (
                self.__math.distance(individual[-1].star_pos, closest_point.star_pos)
                > self.__jump_range
            ):
                break
            individual.append(closest_point)
            remaining_points.remove(closest_point)
        return individual

    def __generate_population(self) -> List[List[StarsSystem]]:
        population: List[List[StarsSystem]] = []
        for _ in range(self.__population_size):
            population.append(self.__generate_individual())
        return population

    def __get_fitness(self, individual: List[StarsSystem]) -> float:
        distance: float = 0
        for i in range(len(individual) - 1):
            segment = self.__math.distance(
                individual[i].star_pos, individual[i + 1].star_pos
            )
            if segment > self.__jump_range:
                return 0.0
            distance += segment
        return 1 / distance if distance > 0 else float("inf")

    def __select_parents(
        self, population: List[List[StarsSystem]]
    ) -> Tuple[List[StarsSystem], List[StarsSystem]]:
        parent1: List[StarsSystem]
        parent2: List[StarsSystem]
        parent1, parent2 = random.choices(
            population,
            weights=[self.__get_fitness(individual) for individual in population],
            k=2,
        )
        return parent1, parent2

    def __crossover(
        self, parent1: List[StarsSystem], parent2: List[StarsSystem]
    ) -> List[StarsSystem]:
        if random.random() > self.__crossover_rate:
            return parent1
        crossover_point: int = random.randint(1, len(parent1) - 2)
        child: List[StarsSystem] = parent1[:crossover_point] + [
            point for point in parent2 if point not in parent1[:crossover_point]
        ]
        return child

    def __mutate(self, individual: List[StarsSystem]) -> List[StarsSystem]:
        mutation_point1: int
        mutation_point2: int
        if random.random() > self.__mutation_rate:
            return individual
        mutation_point1, mutation_point2 = random.sample(
            range(1, len(individual) - 1), 2
        )
        individual[mutation_point1], individual[mutation_point2] = (
            individual[mutation_point2],
            individual[mutation_point1],
        )
        return individual

    def __evolve(self) -> List[StarsSystem]:
        population: List[List[StarsSystem]] = self.__generate_population()
        best_individual: List[StarsSystem] = None  # type: ignore
        target_length = len(self.__active_points or []) + 1

        for _ in range(self.__generations):
            fitnesses: List[float] = [
                self.__get_fitness(individual) for individual in population
            ]
            best_individual = population[fitnesses.index(max(fitnesses))]
            if len(best_individual) >= target_length:
                break
            new_population: List[List[StarsSystem]] = [best_individual]
            while len(new_population) < self.__population_size:
                parent1, parent2 = self.__select_parents(population)
                child = self.__crossover(parent1, parent2)
                child = self.__mutate(child)
                new_population.append(child)
            population = new_population
        return best_individual

    def run(self) -> None:
        """Run algorithm."""
        self.__active_points = _filter_reachable_points(
            self.__start_point,
            self.__points,
            self.__math,
            self.__jump_range,
        )
        if not self.__active_points:
            self.__final = []
            return
        points_count = max(len(self.__active_points), 1)
        self.__population_size = max(points_count * 3, 6)
        self.__generations = max(200, points_count * 40)
        self.__stagnation_limit = max(25, points_count * 5)
        self.__final = self.__evolve() or []
        if self.__start_point in self.__final:
            self.__final.remove(self.__start_point)
        # update distance
        d_sum: float = 0.0
        start: StarsSystem = self.__start_point
        for item in self.__final:
            end: StarsSystem = item
            end.data[EdsmKeys.DISTANCE] = self.__math.distance(
                start.star_pos, end.star_pos
            )
            d_sum += end.data[EdsmKeys.DISTANCE]
            start = end
        self.debug(currentframe(), f"FINAL Distance: {d_sum:.2f} ly")

    def debug(self, currentframe: Optional[FrameType], message: str = "") -> None:
        """Build debug message."""
        p_name: str = f"{self.__plugin_name}"
        c_name: str = f"{self._c_name}"
        m_name: str = f"{currentframe.f_code.co_name}" if currentframe else ""
        if message != "":
            message = f": {message}"
        if self.logger:
            self.logger.debug = f"{p_name}->{c_name}.{m_name}{message}"

    @property
    def final_distance(self) -> float:
        """Calculate the total distance of the final route.

        ### Returns:
        float - Total distance in light years, or 0.0 if no route found.
        """
        if not self.__final:
            return 0.0
        dist: float = self.__math.distance(
            self.__start_point.star_pos, self.__final[0].star_pos
        )
        for item in range(len(self.__final) - 1):
            dist += self.__math.distance(
                self.__final[item].star_pos, self.__final[item + 1].star_pos
            )
        return dist if dist else 0.0

    @property
    def get_final(self) -> List[StarsSystem]:
        """Return final data.

        ### Returns:
        List[StarsSystem] - List of star systems in the final route.
        """
        return self.__final


class AlgGenetic2(IAlg, BLogClient):
    """Genetic algorithm implementation (version 2) for route optimization."""

    __plugin_name: str = None  # type: ignore
    __math: Euclid = None  # type: ignore
    __final: List[StarsSystem] = None  # type: ignore

    __points: List[StarsSystem] = None  # type: ignore
    __start_point: StarsSystem = None  # type: ignore
    __jump_range: int = None  # type: ignore
    __population_size: int = None  # type: ignore
    __generations: int = None  # type: ignore
    __mutation_rate: float = None  # type: ignore
    __population: List[List[StarsSystem]] = None  # type: ignore
    __stagnation_limit: int = None  # type: ignore
    __active_points: List[StarsSystem] = None  # type: ignore

    def __init__(
        self,
        start: StarsSystem,
        systems: List[StarsSystem],
        jump_range: int,
        log_queue: Optional[Union[Queue, SimpleQueue]],
        euclid_alg: Euclid,
        plugin_name: str,
    ) -> None:
        """Construct instance object.

        ### Arguments:
        * start: StarsSystem - Starting position object.
        * systems: List[StarsSystem] - List of points of interest to visit.
        * jump_range: int - Maximum jump range in light years.
        * log_queue: Optional[Union[Queue, SimpleQueue]] - Queue for LogClient communication.
        * euclid_alg: Euclid - Initialized Euclidean distance calculation object.
        * plugin_name: str - Name of the plugin for debug logging.
        """
        self.__plugin_name = plugin_name
        # init log subsystem
        if isinstance(log_queue, (Queue, SimpleQueue)):
            self.logger = LogClient(log_queue)
        else:
            raise Raise.error(
                f"Queue or SimpleQueue type expected, '{type(log_queue)}' received.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        # Euclid's algorithm for calculating the length of vectors
        if isinstance(euclid_alg, Euclid):
            self.__math = euclid_alg
        else:
            raise Raise.error(
                f"Euclid type expected, '{type(euclid_alg)}' received",
                TypeError,
                self._c_name,
                currentframe(),
            )
        if isinstance(jump_range, int):
            self.__jump_range = jump_range
        else:
            raise Raise.error(
                f"Int type expected, '{type(jump_range)}' received",
                TypeError,
                self._c_name,
                currentframe(),
            )
        if not isinstance(start, StarsSystem):
            raise Raise.error(
                f"StarsSystem type expected, '{type(start)}' received.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        if not isinstance(systems, list):
            raise Raise.error(
                f"list type expected, '{type(systems)}' received.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        self.debug(currentframe(), "Initialize dataset")

        self.__start_point = start
        self.__points = [
            system for system in systems if isinstance(system, StarsSystem)
        ]

        self.__population = []
        self.__final = []

        self.__population_size = 100
        self.__generations = 500
        self.__mutation_rate = 0.01  # Prawdopodobieństwo mutacji (0.01)
        self.__stagnation_limit = 100

        # 1. Rozmiar populacji (population_size):
        # Małe wartości (10-50): Szybsze obliczenia, ale może prowadzić do szybkiej
        # konwergencji do lokalnych optymalnych rozwiązań, zwłaszcza przy bardziej
        # skomplikowanych problemach.
        # Średnie wartości (50-200): Wystarczające dla większości problemów.
        # Dają równowagę pomiędzy różnorodnością rozwiązań a szybkością konwergencji.
        # Duże wartości (200-1000 i więcej): Większa różnorodność, ale znacznie
        # wolniejsze obliczenia. Może być korzystne w bardzo trudnych problemach,
        # gdzie wiele rozwiązań lokalnych wymaga długiego czasu na znalezienie
        # rozwiązania globalnego.

        # Rekomendacja:
        # Zaczynaj od wartości w zakresie 50-100. Dla mniejszych problemów możesz
        # próbować 20-50, a dla większych problemów (np. setki punktów) warto
        # eksperymentować z wartościami 100-500.

        # 2. Liczba generacji (generations):
        # Małe wartości (10-100): Może być wystarczające w przypadku prostych problemów,
        # ale algorytm może nie zdążyć znaleźć optymalnych rozwiązań.
        # Średnie wartości (100-1000): Często wystarczają do osiągnięcia dobrego kompromisu
        # między czasem obliczeń a jakością rozwiązania.
        # Duże wartości (1000-5000 i więcej): Dają algorytmowi więcej czasu na eksplorację
        # i poprawę rozwiązań, ale mogą znacząco wydłużyć czas działania.

        # Rekomendacja:
        # Warto zaczynać od wartości w zakresie 200-500. Jeśli widzisz, że algorytm osiąga
        # zadowalające rozwiązania wcześnie, możesz zmniejszyć liczbę generacji.
        # W przypadku bardziej złożonych problemów, możesz zwiększyć liczbę generacji do 1000-2000.

        # 3. Współczynnik mutacji (mutation_rate):
        # Bardzo małe wartości (0.001-0.01): Utrzymują stabilność populacji, co jest dobre,
        # gdy mamy dobrze zdefiniowane populacje i mało zaburzeń jest potrzebnych. Mogą
        # jednak prowadzić do zbyt wczesnej konwergencji.
        # Średnie wartości (0.01-0.05): Najczęściej stosowane. Dają odpowiednią równowagę
        # między eksploracją nowych rozwiązań a eksploatacją istniejących. Pomaga utrzymać
        # różnorodność populacji bez zbytniego zakłócania dobrych rozwiązań.
        # Duże wartości (0.05-0.3): Wprowadzają dużo różnorodności, co może pomóc
        # w uniknięciu lokalnych minimów, ale może również sprawić, że dobre rozwiązania zostaną przypadkowo zepsute.

        # Rekomendacja:
        # Zacznij od wartości w przedziale 0.01-0.05. Jeśli zauważysz, że algorytm zbyt
        # szybko osiąga stabilizację (lokalne optimum), rozważ zwiększenie współczynnika
        # mutacji. Jeśli natomiast zbyt wiele dobrych rozwiązań jest niszczonych przez
        # mutacje, zmniejsz ten współczynnik.

    def __initialize_population(self) -> None:
        """Initialize the population with random routes."""
        self.__population = []
        active = self.__active_points or []
        for _ in range(self.__population_size):
            route: List[StarsSystem] = active[:]
            random.shuffle(route)
            self.__population.append(route)

    def __fitness(self, route: List[StarsSystem]) -> float:
        """Calculate the fitness (inverse of the total route distance)."""
        total_distance = 0.0
        current_point: StarsSystem = self.__start_point
        for system in route:
            segment = self.__math.distance(current_point.star_pos, system.star_pos)
            if segment > self.__jump_range:
                return 0.0
            total_distance += segment
            current_point = system
        # Add distance back to the start if needed (optional for closed loop)
        return 1 / total_distance if total_distance > 0 else 0.0

    def __selection(self) -> Tuple[List[StarsSystem], List[StarsSystem]]:
        """Select two parents based on their fitness (roulette wheel selection)."""
        fitness_values: List[float] = [
            self.__fitness(route) for route in self.__population
        ]
        total_fitness: float = sum(fitness_values)
        if total_fitness == 0:
            parent1 = random.choice(self.__population)
            parent2 = random.choice(self.__population)
        else:
            probabilities: List[float] = [f / total_fitness for f in fitness_values]
            parent1 = random.choices(self.__population, weights=probabilities, k=1)[0]
            parent2 = random.choices(self.__population, weights=probabilities, k=1)[0]

        return parent1, parent2

    def __crossover(
        self, parent1: List[StarsSystem], parent2: List[StarsSystem]
    ) -> List[StarsSystem]:
        """Perform Order Crossover (OX) to generate a child route."""
        start_idx: int = random.randint(0, len(parent1) - 1)
        end_idx: int = random.randint(start_idx, len(parent1) - 1)

        child: List[StarsSystem] = [None] * len(parent1)  # type: ignore
        child[start_idx:end_idx] = parent1[start_idx:end_idx]

        current_pos: int = end_idx
        for system in parent2:
            if system not in child:
                if current_pos >= len(parent1):
                    current_pos = 0
                child[current_pos] = system
                current_pos += 1

        return child

    def __mutate(self, route: List[StarsSystem]) -> None:
        """Perform swap mutation with a given probability."""
        if len(route) <= 1:
            return
        if random.random() < self.__mutation_rate:
            idx1: int = random.randint(0, len(route) - 1)
            idx2: int = random.randint(0, len(route) - 1)
            route[idx1], route[idx2] = route[idx2], route[idx1]

    def __evolve(self) -> List[StarsSystem]:
        """Run the evolutionary algorithm over several generations."""
        self.__initialize_population()
        best_route: Optional[List[StarsSystem]] = None
        best_fitness: float = float("-inf")
        stagnant_generations = 0
        target_length = len(self.__active_points or [])

        for _ in range(self.__generations):
            new_population = []
            for _ in range(self.__population_size // 2):  # Generate new population
                parent1, parent2 = self.__selection()
                child1: List[StarsSystem] = self.__crossover(parent1, parent2)
                child2: List[StarsSystem] = self.__crossover(parent2, parent1)
                self.__mutate(child1)
                self.__mutate(child2)
                new_population.extend([child1, child2])

            # Replace old population with new population
            self.__population = new_population
            current_best = max(self.__population, key=self.__fitness)
            current_fitness = self.__fitness(current_best)
            if current_fitness > best_fitness:
                best_fitness = current_fitness
                best_route = current_best
                stagnant_generations = 0
            else:
                stagnant_generations += 1
            if stagnant_generations >= self.__stagnation_limit:
                break
            if len(current_best) >= target_length:
                best_route = current_best
                break

        if best_route is None:
            best_route = max(self.__population, key=self.__fitness)
        return best_route

    def run(self) -> None:
        """Return the best route found after evolution."""
        start_t: float = time.time()
        self.__active_points = _filter_reachable_points(
            self.__start_point,
            self.__points,
            self.__math,
            self.__jump_range,
        )

        if not self.__active_points:
            self.__final = []
            self.__total_distance = 0.0
            return

        points_count = max(len(self.__active_points), 1)
        self.__population_size = max(20, points_count * 4)
        self.__generations = max(100, points_count * 20)
        self.__stagnation_limit = max(25, points_count * 5)
        self.__population = []
        best_route = self.__evolve()

        ordered: List[StarsSystem] = []
        current = self.__start_point
        remaining = best_route[:]
        while remaining:
            next_point = min(
                remaining,
                key=lambda point: self.__math.distance(
                    current.star_pos, point.star_pos
                ),
            )
            if (
                self.__math.distance(current.star_pos, next_point.star_pos)
                > self.__jump_range
            ):
                break
            ordered.append(next_point)
            remaining.remove(next_point)
            current = next_point
        self.__final = ordered

        # update distance
        if self.__final:
            dist: float = self.__math.distance(
                self.__start_point.star_pos, self.__final[0].star_pos
            )
            self.__final[0].data[EdsmKeys.DISTANCE] = dist
            for item in range(len(self.__final) - 1):
                dist = self.__math.distance(
                    self.__final[item].star_pos,
                    self.__final[item + 1].star_pos,
                )
                self.__final[item + 1].data[EdsmKeys.DISTANCE] = dist

        end_t: float = time.time()
        self.debug(currentframe(), f"Evolution took {end_t - start_t} seconds.")

    def debug(self, currentframe: Optional[FrameType], message: str = "") -> None:
        """Build debug message."""
        p_name: str = f"{self.__plugin_name}"
        c_name: str = f"{self._c_name}"
        m_name: str = f"{currentframe.f_code.co_name}" if currentframe else ""
        if message != "":
            message = f": {message}"
        if self.logger:
            self.logger.debug = f"{p_name}->{c_name}.{m_name}{message}"

    @property
    def final_distance(self) -> float:
        """Calculate the total distance of the final route.

        ### Returns:
        float - Total distance in light years, or 0.0 if no route found.
        """
        if not self.__final:
            return 0.0
        dist: float = self.__math.distance(
            self.__start_point.star_pos, self.__final[0].star_pos
        )
        for item in range(len(self.__final) - 1):
            dist += self.__math.distance(
                self.__final[item].star_pos, self.__final[item + 1].star_pos
            )
        return dist if dist else 0.0

    @property
    def get_final(self) -> List[StarsSystem]:
        """Return final data.

        ### Returns:
        List[StarsSystem] - List of star systems in the final route.
        """
        return self.__final


class AlgSimulatedAnnealing(IAlg, BLogClient):
    """Simulated annealing algorithm for finding optimal routes."""

    __plugin_name: str = None  # type: ignore
    __math: Euclid = None  # type: ignore
    __final: List[StarsSystem] = None  # type: ignore

    __points: List[StarsSystem] = None  # type: ignore
    __start_point: StarsSystem = None  # type: ignore
    __jump_range: int = None  # type: ignore
    __initial_temp: float = 0.0
    __cooling_rate: float = 0.0
    __best_distance: float = float("inf")
    __current_solution: List[StarsSystem] = None  # type: ignore

    def __init__(
        self,
        start: StarsSystem,
        systems: List[StarsSystem],
        jump_range: int,
        log_queue: Optional[Union[Queue, SimpleQueue]],
        euclid_alg: Euclid,
        plugin_name: str,
    ) -> None:
        """Construct instance object.

        ### Arguments:
        * start: StarsSystem - Starting position object.
        * systems: List[StarsSystem] - List of points of interest to visit.
        * jump_range: int - Maximum jump range in light years.
        * log_queue: Optional[Union[Queue, SimpleQueue]] - Queue for LogClient communication.
        * euclid_alg: Euclid - Initialized Euclidean distance calculation object.
        * plugin_name: str - Name of the plugin for debug logging.
        """

        self.__plugin_name = plugin_name
        # init log subsystem
        if isinstance(log_queue, (Queue, SimpleQueue)):
            self.logger = LogClient(log_queue)
        else:
            raise Raise.error(
                f"Queue or SimpleQueue type expected, '{type(log_queue)}' received.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        # Euclid's algorithm for calculating the length of vectors
        if isinstance(euclid_alg, Euclid):
            self.__math = euclid_alg
        else:
            raise Raise.error(
                f"Euclid type expected, '{type(euclid_alg)}' received",
                TypeError,
                self._c_name,
                currentframe(),
            )
        if isinstance(jump_range, int):
            self.__jump_range = jump_range
        else:
            raise Raise.error(
                f"Int type expected, '{type(jump_range)}' received",
                TypeError,
                self._c_name,
                currentframe(),
            )
        if not isinstance(start, StarsSystem):
            raise Raise.error(
                f"StarsSystem type expected, '{type(start)}' received.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        if not isinstance(systems, list):
            raise Raise.error(
                f"list type expected, '{type(systems)}' received.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        self.debug(currentframe(), "Initialize dataset")

        self.__start_point = start
        self.__points = [
            system for system in systems if isinstance(system, StarsSystem)
        ]
        self.__jump_range = jump_range
        self.__initial_temp = 1000.0  # 1000
        self.__cooling_rate = 0.003  # 0.003
        # initial_temp: Im wyższa temperatura początkowa, tym większe jest
        # prawdopodobieństwo zaakceptowania gorszych rozwiązań na początku procesu.
        # cooling_rate: Kontroluje tempo chłodzenia. Im mniejsza wartość,
        # tym wolniejsze chłodzenie, co pozwala na dokładniejszą eksplorację
        # przestrzeni rozwiązań, ale wydłuża czas działania algorytmu.

        # Aby zoptymalizować działanie algorytmu SA, możesz dostosować:
        # Temperaturę początkową (initial_temp): większe wartości pozwalają
        # na większą eksplorację na początku.
        # Tempo chłodzenia (cooling_rate): wolniejsze tempo daje większe
        # szanse na znalezienie optymalnych rozwiązań, ale wydłuża czas działania.
        # Liczbę iteracji: algorytm może przerywać działanie, gdy temperatura
        # osiągnie bardzo niską wartość.

    def calculate_total_distance(self, path: List[StarsSystem]) -> float:
        """Calculate the total distance of the path, starting from the start point."""
        total_dist = 0
        current_star: StarsSystem = self.__start_point
        for next_star in path:
            dist: float = self.__math.distance(
                current_star.star_pos, next_star.star_pos
            )
            if dist <= self.__jump_range:  # Only count valid jumps
                total_dist += dist
            else:
                return float("inf")  # Penalize paths that exceed jump_range
            current_star = next_star
        return total_dist

    def accept_solution(
        self, current_distance: float, new_distance: float, temperature: float
    ) -> bool:
        """Decide whether to accept the new solution based on the current temperature."""
        if new_distance < current_distance:
            return True
        # Accept worse solutions with a probability depending on the temperature
        return random.random() < math.exp(
            (current_distance - new_distance) / temperature
        )

    def run(self) -> None:
        """Perform the Simulated Annealing optimization."""
        start_t: float = time.time()
        systems: List[StarsSystem] = _filter_reachable_points(
            self.__start_point,
            self.__points,
            self.__math,
            self.__jump_range,
        )
        self.__current_solution = systems[:]
        self.__final = systems[:]

        if not self.__current_solution:
            self.__best_distance = float("inf")
            return

        random.shuffle(self.__current_solution)
        self.__best_distance = self.calculate_total_distance(self.__current_solution)

        temperature: float = self.__initial_temp
        while temperature > 1:
            # Create a new solution by swapping two random points
            new_solution: List[StarsSystem] = self.__current_solution[:]
            if len(new_solution) >= 2:
                i, j = random.sample(range(len(new_solution)), 2)
                new_solution[i], new_solution[j] = new_solution[j], new_solution[i]

            # Calculate the total distance for the new solution
            current_distance: float = self.calculate_total_distance(
                self.__current_solution
            )
            new_distance: float = self.calculate_total_distance(new_solution)

            # Decide whether to accept the new solution
            if self.accept_solution(current_distance, new_distance, temperature):
                self.__current_solution = new_solution

            # Update the best solution found so far
            if new_distance < self.__best_distance:
                self.__final = new_solution
                self.__best_distance = new_distance

            # Decrease the temperature (cooling)
            temperature *= 1 - self.__cooling_rate

        # update distance
        if self.__final:
            dist: float = self.__math.distance(
                self.__start_point.star_pos, self.__final[0].star_pos
            )
            self.__final[0].data[EdsmKeys.DISTANCE] = dist
            for item in range(len(self.__final) - 1):
                dist = self.__math.distance(
                    self.__final[item].star_pos,
                    self.__final[item + 1].star_pos,
                )
                self.__final[item + 1].data[EdsmKeys.DISTANCE] = dist

        end_t: float = time.time()
        self.debug(currentframe(), f"Evolution took {end_t - start_t} seconds.")

    def debug(self, currentframe: Optional[FrameType], message: str = "") -> None:
        """Build debug message."""
        p_name: str = f"{self.__plugin_name}"
        c_name: str = f"{self._c_name}"
        m_name: str = f"{currentframe.f_code.co_name}" if currentframe else ""
        if message != "":
            message = f": {message}"
        if self.logger:
            self.logger.debug = f"{p_name}->{c_name}.{m_name}{message}"

    @property
    def final_distance(self) -> float:
        """Calculate the total distance of the final route.

        ### Returns:
        float - Total distance in light years, or 0.0 if no route found.
        """
        if not self.__final:
            return 0.0
        dist: float = self.__math.distance(
            self.__start_point.star_pos, self.__final[0].star_pos
        )
        for item in range(len(self.__final) - 1):
            dist += self.__math.distance(
                self.__final[item].star_pos, self.__final[item + 1].star_pos
            )
        return dist if dist else 0.0

    @property
    def get_final(self) -> List[StarsSystem]:
        """Return final data.

        ### Returns:
        List[StarsSystem] - List of star systems in the final route.
        """
        return self.__final


# #[EOF]#######################################################################
