from functools import cached_property

from nodos.core.hex_math import Hex
from nodos.world.terrain import TerrainGenerator

from nodos.config import MAP_WIDTH, MAP_HEIGHT


class HexTile:
    def __init__(self,
                 hex_obj: Hex
                 ):
        self.hex_obj = hex_obj

        self.elevation: float = 0.0
        self.biome: str = 'water'
        self.color: tuple[int, int, int, int] = (0, 0, 0, 255)
        self.is_buildable: bool = False

    def __repr__(self):
        return f'HexTile({self.hex_obj.q}, {self.hex_obj.r})'

class WorldMap:
    def __init__(self,
                 width: int = MAP_WIDTH,
                 height: int = MAP_HEIGHT
                 ):
        self.width = width
        self.height = height

        self.terrain_gen = TerrainGenerator()

    @cached_property
    def tiles(self) -> dict[Hex, HexTile]:
        tiles = dict()
        for r in range(self.height):
            r_offset = r // 2
            for col in range(self.width):
                q = col - r_offset
                hex_obj = Hex(q=q, r=r)
                tile = HexTile(hex_obj=hex_obj)

                tile.elevation = self.terrain_gen.get_elevation(q=q, r=r)
                tile.biome, tile.color, tile.is_buildable = self.terrain_gen.get_biome_data(
                    elevation=tile.elevation
                )

                tiles[hex_obj] = tile
        return tiles

    def get_tile(self,
                 hex_obj: Hex
                 ) -> HexTile | None:
        return self.tiles.get(hex_obj)
