import numpy as np
from ngio import PixelSize

from ome_zarr_converters_tools._tile import Point, Tile, Vector
from ome_zarr_converters_tools._tiled_image import PlatePathBuilder, TiledImage


class DummyLoader:
    def __init__(self, shape):
        self.shape = shape

    def load(self):
        return np.zeros(self.shape, dtype="uint8")

    @property
    def dtype(self):
        return "uint8"


def generate_grid_tiles(
    overlap,
    tile_shape,
    pixel_size_xy=0.1,
    grid_size_x=2,
    grid_size_y=2,
    invert_x=False,
    invert_y=False,
    swap_xy=False,
    z_offset: int | float = 0,
    t_offset: int = 0,
) -> list[Tile]:
    length_y = tile_shape[3] * pixel_size_xy
    length_x = tile_shape[4] * pixel_size_xy

    if swap_xy:
        length_x, length_y = length_y, length_x

    tiles = []
    for i in range(grid_size_x):
        for j in range(grid_size_y):
            x = i * overlap * length_x
            y = j * overlap * length_y

            if invert_x:
                x = -x

            if invert_y:
                y = -y

            if swap_xy:
                x, y = y, x

            tile = Tile(
                top_l=Point(x=x, y=y, z=z_offset, t=t_offset),
                diag=Vector(x=length_x, y=length_y, z=1, t=1, c=1),
                pixel_size=PixelSize(x=pixel_size_xy, y=pixel_size_xy, z=1),
                data_loader=DummyLoader(tile_shape),
            )
            tiles.append(tile)

    return tiles


def generate_tiled_image(
    plate_name: str,
    tiled_image_name: str,
    row: str,
    column: int,
    acquisition_id: int,
    z_offset: int | float = 0,
    t_offset: int = 0,
) -> TiledImage:
    path_builder = PlatePathBuilder(
        plate_name=plate_name,
        row=row,
        column=column,
        acquisition_id=acquisition_id,
    )
    tiled_image = TiledImage(
        name=tiled_image_name,
        path_builder=path_builder,
        channel_names=["channel1"],
        wavelength_ids=["wavelength1"],
        attributes={"cell_line": "cell_line_1"},
    )

    tiles = generate_grid_tiles(
        overlap=0.9, tile_shape=(1, 1, 1, 11, 10), z_offset=z_offset, t_offset=t_offset
    )
    for tile in tiles:
        tiled_image.add_tile(tile)
    return tiled_image


def generate_tiled_images(
    plate_name: str,
    rows: list[str],
    columns: list[int],
    acquisition_ids: list[int],
) -> list[TiledImage]:
    tiled_images = []
    for row, column, acquisition_id in zip(rows, columns, acquisition_ids, strict=True):
        tiled_image = generate_tiled_image(
            plate_name=plate_name,
            tiled_image_name="tiled_image",
            row=row,
            column=column,
            acquisition_id=acquisition_id,
        )
        tiled_images.append(tiled_image)
    return tiled_images
