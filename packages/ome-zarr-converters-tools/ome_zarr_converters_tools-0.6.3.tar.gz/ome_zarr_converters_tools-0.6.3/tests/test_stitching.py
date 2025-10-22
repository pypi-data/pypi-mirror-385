import copy

import pytest
from utils import generate_grid_tiles

from ome_zarr_converters_tools._stitching import standard_stitching_pipe


@pytest.mark.parametrize("overalap", [0.1, 0.5, 0.9])
def test_standard_grid_stitching(overalap):
    tiles = generate_grid_tiles(overlap=overalap, tile_shape=(1, 1, 1, 11, 10))
    origins = [copy.deepcopy(tile.origin) for tile in tiles]
    tiles_no_overlap = generate_grid_tiles(overlap=1, tile_shape=(1, 1, 1, 11, 10))

    tiles_grid = standard_stitching_pipe(tiles, mode="auto")
    for tile in tiles_grid:
        assert tile in tiles_no_overlap
        assert tile.origin in origins

    tiles_grid = standard_stitching_pipe(tiles, mode="grid")
    for tile in tiles_grid:
        assert tile in tiles_no_overlap
        assert tile.origin in origins

    tiles_free = standard_stitching_pipe(tiles, mode="free")
    for tile in tiles_free:
        assert tile in tiles_no_overlap
        assert tile.origin in origins


def test_grid_stitching_with_missing_top_left():
    tiles = generate_grid_tiles(overlap=0.1, tile_shape=(1, 1, 1, 11, 10))
    tiles = tiles[1:]  # remove the first tile
    origins = [copy.deepcopy(tile.origin) for tile in tiles]
    tiles_no_overlap = generate_grid_tiles(overlap=1, tile_shape=(1, 1, 1, 11, 10))
    tiles_no_overlap = tiles_no_overlap[1:]  # remove the first tile

    tiles_grid = standard_stitching_pipe(tiles, mode="grid")
    for tile in tiles_grid:
        assert tile in tiles_no_overlap
        assert tile.origin in origins


@pytest.mark.parametrize(
    "invert_x, invert_y, swap_xy",
    [
        (True, False, False),
        (False, True, False),
        (False, False, True),
    ],
)
def test_xy_manipulations(invert_x, invert_y, swap_xy):
    tiles = generate_grid_tiles(
        overlap=0.9,
        tile_shape=(1, 1, 1, 11, 10),
        invert_x=invert_x,
        invert_y=invert_y,
        swap_xy=swap_xy,
    )

    tiles_no_overlap = generate_grid_tiles(overlap=1, tile_shape=(1, 1, 1, 11, 10))

    tiles_grid = standard_stitching_pipe(
        tiles, mode="grid", invert_x=invert_x, invert_y=invert_y, swap_xy=swap_xy
    )
    for tile in tiles_grid:
        assert tile in tiles_no_overlap
