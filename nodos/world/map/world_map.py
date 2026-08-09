from functools import cached_property
from typing import TYPE_CHECKING

from nodos.core import RoadNetwork
from nodos.core.hex_math import HexObject
from nodos.world.cities import CityBuilderEngine
from nodos.world.map import HexTile
from nodos.world.map import TerrainGenerator

from nodos.config import (
    MAP_HEIGHT,
    MAP_WIDTH
)

if TYPE_CHECKING:
    from nodos.world.cities import City


class WorldMap:
    def __init__(self,
                 width: int = MAP_WIDTH,
                 height: int = MAP_HEIGHT
                 ):
        self.width = width
        self.height = height

        self.terrain_gen: TerrainGenerator = TerrainGenerator()
        self.city_engine: CityBuilderEngine = CityBuilderEngine()
        self.road_network: RoadNetwork = RoadNetwork()

        cities_list = self.city_engine.generate_cities(tiles=self.tiles)
        self.cities: dict[int, City] = {c.id_num: c for c in cities_list}

        self.road_network.build_regional_network(tiles=self.tiles, cities=cities_list)

    @cached_property
    def tiles(self) -> dict[HexObject, HexTile]:
        tiles: dict[HexObject, HexTile] = dict()
        for r in range(self.height):
            r_offset = r // 2
            for col in range(self.width):
                q = col - r_offset
                hex_obj = HexObject(q=q, r=r)
                tile = HexTile(hex_obj=hex_obj)

                tile.elevation = self.terrain_gen.get_elevation(q=q, r=r)
                tile.biome, tile.color, tile.is_buildable = self.terrain_gen.get_biome_data(
                    elevation=tile.elevation
                )

                tiles[hex_obj] = tile
        return tiles

    def get_tile(self,
                 hex_obj: HexObject
                 ) -> HexTile | None:
        return self.tiles.get(hex_obj)
