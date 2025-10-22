# CZTile provides a set of tiling strategies
# Copyright 2025 Carl Zeiss Microscopy GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# To obtain a commercial version please contact Carl Zeiss Microscopy GmbH.
"""Contains all tiling strategies supported by cztile"""

from dataclasses import dataclass
from typing import List, NamedTuple, Union, Tuple
from abc import abstractmethod, ABCMeta

Region2D = NamedTuple("Region2D", [("x", int), ("y", int), ("w", int), ("h", int)])

Region3D = NamedTuple("Region3D", [("x", int), ("y", int), ("z", int), ("w", int), ("h", int), ("d", int)])


@dataclass
class TileInput:
    """Input parameters for tiling strategies.

    Attributes:
        total_tile_length: The total length of the tile including borders.
        min_border_length: The minimum required border length.
    """

    total_tile_length: int
    min_border_length: int


@dataclass
class Tile1D:
    """A single 1D tile.

    Attributes:
        left_most_tile_pixel: the left-most pixel belonging to the tile
        width: the width of the tile interior (excluding borders)
        left_border_width: the width of the left border
        right_border_width: the width of the right border
    """

    left_most_tile_pixel: int
    width: int
    left_border_width: int
    right_border_width: int


@dataclass
class TileBorder2D:
    """A 2D border.

    Attributes:
        left: the left border size.
        top: the top border size.
        right: the right border size.
        bottom: the bottom border size.
    """

    left: int
    top: int
    right: int
    bottom: int


@dataclass
class TileBorder3D(TileBorder2D):
    """A 3D border.

    Attributes:
        left: the left border size (inherited from 'TileBorder2D').
        top: the top border size (inherited from 'TileBorder2D').
        right: the right border size (inherited from 'TileBorder2D').
        bottom: the bottom border size (inherited from 'TileBorder2D').
        front: the front border size.
        back: the back border size.
    """

    front: int
    back: int


class Tile2D:
    """A 2D tile.

    Attributes:
        roi: the tile roi
        border: the tile border
    """

    center: Region2D
    border: TileBorder2D
    roi: Region2D

    def __init__(self, center: Union[Tuple[int, int, int, int], Region2D], border: TileBorder2D) -> None:
        """Initializes a 2D tile.

        Args:
            center: the tile center
            border: the tile border
        """
        self.center = Region2D(*center)
        self.border = border
        self.roi = Region2D(
            x=self.center.x - self.border.left,
            y=self.center.y - self.border.top,
            w=self.center.w + self.border.left + self.border.right,
            h=self.center.h + self.border.top + self.border.bottom,
        )

    def __eq__(self, other: object) -> bool:
        """Implementation of the equal operator for a 2D tile."""
        # Taken from https://stackoverflow.com/questions/54801832/mypy-eq-incompatible-with-supertype-object
        # Also refer to https://mypy.readthedocs.io/en/stable/common_issues.html#incompatible-overrides
        if not isinstance(other, Tile2D):
            # If we return NotImplemented, Python will automatically try
            # running other.__eq__(self), in case 'other' knows what to do with Tile2D objects.
            return NotImplemented
        return self.center == other.center and self.border == other.border and self.roi == other.roi


class Tile3D:
    """A 3D tile.

    Attributes:
        roi3d: the tile roi3d
        border3d: the 3D tile border
    """

    center3d: Region3D
    border3d: TileBorder3D
    roi3d: Region3D

    def __init__(
        self,
        center3d: Union[Tuple[int, int, int, int, int, int], Region3D],
        border3d: TileBorder3D,
    ) -> None:
        """Initializes a 3D tile.

        Args:
            center3d: the 3D tile center
            border3d: the 3D tile border
        """
        self.center3d = Region3D(*center3d)
        self.border3d = border3d
        self.roi3d = Region3D(
            x=self.center3d.x - self.border3d.left,
            y=self.center3d.y - self.border3d.top,
            z=self.center3d.z - self.border3d.front,
            w=self.center3d.w + self.border3d.left + self.border3d.right,
            h=self.center3d.h + self.border3d.top + self.border3d.bottom,
            d=self.center3d.d + self.border3d.front + self.border3d.back,
        )

    def __eq__(self, other: object) -> bool:
        """Implementation of the equal operator for a 3D tile."""
        # Taken from https://stackoverflow.com/questions/54801832/mypy-eq-incompatible-with-supertype-object
        # Also refer to https://mypy.readthedocs.io/en/stable/common_issues.html#incompatible-overrides
        if not isinstance(other, Tile3D):
            # If we return NotImplemented, Python will automatically try
            # running other.__eq__(self), in case 'other' knows what to do with Tile3D objects.
            return NotImplemented
        return self.center3d == other.center3d and self.border3d == other.border3d and self.roi3d == other.roi3d


class TilingStrategy2D(metaclass=ABCMeta):
    """Base module for creating a strategy to store the data samples on disk in a defined format"""

    @abstractmethod
    def calculate_2d_tiles(self, region2d: Union[Tuple[int, int, int, int], Region2D]) -> List[Tile2D]:
        """Tiles the provided 2D region.

        Args:
            region2d: The 2D region to tile.

        Returns:
            A list with the tiles covering the specified 2D region.
        """


class TilingStrategy3D(metaclass=ABCMeta):
    """Base module for creating a strategy to store the data samples on disk in a defined format"""

    @abstractmethod
    def calculate_3d_tiles(self, region3d: Union[Tuple[int, int, int, int, int, int], Region3D]) -> List[Tile3D]:
        """Tiles the provided 3D region.

        Args:
            region3d: The 3D region to tile.

        Returns:
            A list with the tiles covering the specified 3D region.
        """
