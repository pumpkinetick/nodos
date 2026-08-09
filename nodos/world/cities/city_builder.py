import logging
import math
from typing import Optional

from nodos.core.hex_math import HexObject
from nodos.world.cities import City

from nodos.config import (
    CITY_EXPANSION_STEPS,
    HEX_DIRECTIONS,
    ZONE_COLORS
)

logger = logging.getLogger(__name__)


class CityBuilder:
    @staticmethod
    def create_single_cell_city_inplace(tiles: dict,
                                        city_id: int,
                                        center_hex: HexObject
                                        ) -> Optional[City]:
        tile = tiles.get(center_hex)
        if tile is None or not tile.is_buildable or tile.city_id is not None:
            return None

        city = City(id_num=city_id, center=center_hex)
        city.districts = {center_hex: 'center'}

        tile.city_id = city_id
        tile.zone_type = 'center'
        tile.zone_color = ZONE_COLORS['center']

        return city

    @staticmethod
    def create_expanded_city_inplace(tiles: dict,
                                     city_id: int,
                                     center_hex: HexObject
                                     ) -> Optional[City]:
        tile = tiles.get(center_hex)
        if tile is None or not tile.is_buildable or tile.city_id is not None:
            return None

        city = City(id_num=city_id, center=center_hex)

        frontier: list[HexObject] = [center_hex]
        visited: set[HexObject] = {center_hex}

        tile.city_id = city_id
        tile.zone_type = 'center'
        tile.zone_color = ZONE_COLORS['center']

        for distance_step in range(1, CITY_EXPANSION_STEPS + 1):
            next_frontier = list()
            for current_hex in frontier:
                for dq, dr in HEX_DIRECTIONS:
                    neighbor = HexObject(q=current_hex.q + dq, r=current_hex.r + dr)
                    neighbor_tile = tiles.get(neighbor)
                    if (
                        neighbor_tile is not None and
                        neighbor_tile.is_buildable and
                        neighbor not in visited and
                        neighbor_tile.city_id is None
                    ):
                        visited.add(neighbor)
                        next_frontier.append(neighbor)

                        zone_type = CityBuilder._determine_directional_zone(
                            city=city,
                            hex_obj=neighbor,
                            distance=distance_step
                        )
                        city.districts[neighbor] = zone_type

                        neighbor_tile.city_id = city_id
                        neighbor_tile.zone_type = zone_type
                        neighbor_tile.zone_color = ZONE_COLORS[zone_type]

            frontier = next_frontier

        return city

    @staticmethod
    def _determine_directional_zone(city: City,
                                    hex_obj: HexObject,
                                    distance: int
                                    ) -> str:
        if distance == 1:
            return 'commercial'

        dq = hex_obj.q - city.center.q
        dr = hex_obj.r - city.center.r

        dx = dq + dr / 2.0
        dy = dr * (math.sqrt(3.0) / 2.0)

        length = math.hypot(dx, dy)
        norm_x = dx / length
        norm_y = dy / length

        target_x = math.cos(city.industrial_angle)
        target_y = math.sin(city.industrial_angle)

        dot_product = norm_x * target_x + norm_y * target_y

        if dot_product > 0.5:
            return 'industrial'
        elif dot_product >= 0.0:
            return 'commercial'
        else:
            return 'residential'
