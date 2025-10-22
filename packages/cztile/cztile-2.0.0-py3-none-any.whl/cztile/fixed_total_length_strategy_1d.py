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
"""Provides tiling primitives for the DNN tiling strategy.

This is a python implementation of the algorithm described in README.
"""
import sys
from math import ceil, floor
from typing import List
from cztile.tiling_strategy import Tile1D


class AlmostEqualBorderFixedTotalLengthStrategy1D:
    """Tiles an integer interval beginning at 0 with tiles having a fixed total length and with zero outer borders.

    Attributes:
        total_tile_length: The fixed total length of the tiles to generate.
        min_border_length: The minimum length of each of the interior borders.
    """

    def __init__(self, total_tile_length: int, min_border_length: int) -> None:
        """Initializes an AlmostEqualBorderFixedTotalLengthStrategy1D.

        Args:
            total_tile_length: The fixed total length of the tiles to generate.
            min_border_length: The minimum length of each of the interior borders.

        Raises:
            TypeError: For invalid type of total tile or min border length.
            ValueError: For invalid value of total tile or min border length.
        """
        # Check if values are integers
        if not isinstance(total_tile_length, int):
            raise TypeError("Total tile length must be an integer.")
        if not isinstance(min_border_length, int):
            raise TypeError("Minimum border length must be an integer.")

        if total_tile_length <= 0:
            raise ValueError("Total tile length must be greater than zero.")
        if min_border_length < 0:
            raise ValueError("Minimum border length cannot be negative.")
        if min_border_length > sys.maxsize / 2:
            raise ValueError(f"Minimum border length is too large. It needs to be smaller than {sys.maxsize / 2}.")

        self.total_tile_length = total_tile_length
        self.min_border_length = min_border_length
        if 2 * min_border_length >= total_tile_length:
            raise ValueError("Minimum border length must be less than half the tile length.")

    def calculate_tiles(self, image_width: int) -> List[Tile1D]:
        """Calculates tiling of the specified image width.

        Args:
            image_width: The width of the image.

        Returns:
            A list of tiles covering the specified image_width.

        Raises:
            AssertionError: Border misconfigurations.
        """
        if image_width < self.total_tile_length:
            border_width = self.total_tile_length - image_width
            left_border = border_width // 2
            right_border = border_width - left_border
            return [Tile1D(0, image_width, left_border, right_border)]

        if image_width == self.total_tile_length:
            return [Tile1D(0, self.total_tile_length, 0, 0)]

        max_width_of_edge_tiles: int = self.total_tile_length - self.min_border_length
        max_width_of_interior_tiles: int = self.total_tile_length - 2 * self.min_border_length
        interior: int = max(0, image_width - 2 * max_width_of_edge_tiles)

        number_of_tiles: int = ceil(interior * 1.0 / max_width_of_interior_tiles) + 2
        number_of_non_zero_borders: int = 2 * number_of_tiles - 2

        excess_border: float = (
            2.0 * max_width_of_edge_tiles + (number_of_tiles - 2) * max_width_of_interior_tiles - image_width
        )

        fractional_excess_border: float = excess_border / number_of_non_zero_borders
        fractional_border_width: float = fractional_excess_border + self.min_border_length

        cumulative_border: List[int] = [0] * (number_of_non_zero_borders + 1)
        for j in range(0, number_of_non_zero_borders + 1):
            cbj: float = j * fractional_border_width
            cumulative_border[j] = floor(cbj)

        tile_boundaries: List[int] = [0] * (number_of_tiles + 1)
        tile_boundaries[0] = 0
        tile_boundaries[number_of_tiles] = image_width
        for i in range(1, number_of_tiles):
            tile_boundaries[i] = i * self.total_tile_length - cumulative_border[2 * i - 1]

        result: List[Tile1D] = []
        for k in range(0, number_of_tiles):
            left_most_tile_pixel = tile_boundaries[k]
            width = tile_boundaries[k + 1] - tile_boundaries[k]
            total_border = self.total_tile_length - width

            if k == 0:
                left_border = 0
            elif k == number_of_tiles - 1:
                left_border = total_border
            else:
                left_border_index = 2 * k
                left_border = cumulative_border[left_border_index] - cumulative_border[left_border_index - 1]

                # Some assertions. These can be removed without harm.
                right_border1 = total_border - left_border
                right_border2 = cumulative_border[left_border_index + 1] - cumulative_border[left_border_index]
                if right_border1 != right_border2:
                    raise AssertionError("right_border1 != right_border2")
                if right_border1 < self.min_border_length:
                    raise AssertionError("right border < self.min_border_width")
                if left_border < self.min_border_length:
                    raise AssertionError("left border < self.min_border_width")

            right_border = total_border - left_border

            if left_border + width + right_border != self.total_tile_length:
                raise AssertionError("LB + W + RB != Total Width")

            result.append(Tile1D(left_most_tile_pixel, width, left_border, right_border))

        return result
