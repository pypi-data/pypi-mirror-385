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

from typing import List, Union, Tuple
from cztile.tiling_strategy import (
    TilingStrategy3D,
    Region3D,
    Tile3D,
    TileBorder3D,
    TileInput,
)
from cztile.fixed_total_length_strategy_1d import (
    AlmostEqualBorderFixedTotalLengthStrategy1D,
)


class AlmostEqualBorderFixedTotalVolumeStrategy3D(TilingStrategy3D):
    """A 3D tiling strategy that covers a total volume with a minimal number of tiles of constant
    total volume such that:
        a) all interior tiles have at least a minimum border width/height on all sides.
        b) the edge tiles have zero border at the edge and at least the minimum border width
           on their inner sides.
        c) The sizes of all non-zero borders differ at most by one pixel.

    Attributes:
        width: An object containing values related to the width dimension:
            - the fixed total tile length (inc. border) of the tiles to generate
            - the minimum length of each of the interior borders.
        height: An object containing values related to the height dimension:
            - the fixed total tile length (inc. border) of the tiles to generate
            - the minimum length of each of the interior borders.
        depth: An object containing values related to the depth dimension:
            - the fixed total tile length (inc. border) of the tiles to generate
            - the minimum length of each of the interior borders.
    """

    def __init__(
        self,
        width: TileInput,
        height: TileInput,
        depth: TileInput,
    ) -> None:
        """Initializes an AlmostEqualBorderFixedTotalVolumeStrategy3D.

        Args:
            width: An object containing values related to the width dimension:
                - the fixed total tile length (inc. border) of the tiles to generate
                - the minimum length of each of the interior borders.
            height: An object containing values related to the height dimension:
                - the fixed total tile length (inc. border) of the tiles to generate
                - the minimum length of each of the interior borders.
            depth: An object containing values related to the depth dimension:
                - the fixed total tile length (inc. border) of the tiles to generate
                - the minimum length of each of the interior borders.
        """
        self.width = width
        self.height = height
        self.depth = depth

        self.horizontal_tiler = AlmostEqualBorderFixedTotalLengthStrategy1D(
            total_tile_length=width.total_tile_length,
            min_border_length=width.min_border_length,
        )
        self.vertical_tiler = AlmostEqualBorderFixedTotalLengthStrategy1D(
            total_tile_length=height.total_tile_length,
            min_border_length=height.min_border_length,
        )
        self.depth_tiler = AlmostEqualBorderFixedTotalLengthStrategy1D(
            total_tile_length=depth.total_tile_length,
            min_border_length=depth.min_border_length,
        )

    def calculate_3d_tiles(self, region3d: Union[Tuple[int, int, int, int, int, int], Region3D]) -> List[Tile3D]:
        """Tiles the provided 3D region.

        Args:
            region3d: The 3D region to tile.

        Returns:
            A list with the tiles covering the specified 3D region.
        """
        region3d = Region3D(*region3d)
        if region3d.w * region3d.h * region3d.d == 0:
            return []

        horizontal_tiles = self.horizontal_tiler.calculate_tiles(region3d.w)
        vertical_tiles = self.vertical_tiler.calculate_tiles(region3d.h)
        depth_tiles = self.depth_tiler.calculate_tiles(region3d.d)

        result: List[Tile3D] = []
        for horizontal_tile in horizontal_tiles:
            for vertical_tile in vertical_tiles:
                for depth_tile in depth_tiles:
                    tile_center = Region3D(
                        x=region3d.x + horizontal_tile.left_most_tile_pixel,
                        y=region3d.y + vertical_tile.left_most_tile_pixel,
                        z=region3d.z + depth_tile.left_most_tile_pixel,
                        w=horizontal_tile.width,
                        h=vertical_tile.width,
                        d=depth_tile.width,
                    )
                    tile_border = TileBorder3D(
                        left=horizontal_tile.left_border_width,
                        top=vertical_tile.left_border_width,
                        right=horizontal_tile.right_border_width,
                        bottom=vertical_tile.right_border_width,
                        front=depth_tile.left_border_width,
                        back=depth_tile.right_border_width,
                    )
                    result.append(Tile3D(center3d=tile_center, border3d=tile_border))
        return result
