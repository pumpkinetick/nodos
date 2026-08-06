import math
import random

from nodos.core.hex_math import Hex

from nodos.config import (
    CITY_EXPANSION_STEPS,
    HEX_DIRECTIONS,
    INIT_NUM_CITIES,
    ZONE_COLORS
)


class City:
    def __init__(self,
                 id_num: int,
                 center: Hex
                 ):
        self.id_num = id_num
        self.center = center

        self.industrial_angle: float = random.uniform(a=0.0, b=2.0 * math.pi)

        self.districts: dict[Hex, str] = {center: 'center'}


class CityBuilderEngine:
    @classmethod
    def generate_cities(cls,
                        tiles: dict
                        ) -> list[City]:
        buildable_hexes = [h for h, t in tiles.items() if t.is_buildable]

        num_seeds = min(INIT_NUM_CITIES, len(buildable_hexes))
        if num_seeds == 0:
            return list()

        seed_hexes = random.sample(population=buildable_hexes, k=num_seeds)

        cities = list()
        for i, center_hex in enumerate(seed_hexes, start=1):
            city = City(
                id_num=i,
                center=center_hex
            )

            frontier = [center_hex]
            visited = {center_hex}

            tiles[center_hex].city_id = city.id_num
            tiles[center_hex].zone_type = 'center'
            tiles[center_hex].zone_color = ZONE_COLORS['center']

            for distance_step in range(1, CITY_EXPANSION_STEPS + 1):
                next_frontier = list()
                for current_hex in frontier:
                    for dq, dr in HEX_DIRECTIONS:
                        neighbor = Hex(q=current_hex.q + dq, r=current_hex.r + dr)
                        if (
                            neighbor in tiles and
                            tiles[neighbor].is_buildable and
                            neighbor not in visited and
                            tiles[neighbor].city_id is None
                        ):
                            visited.add(neighbor)
                            next_frontier.append(neighbor)

                            zone_type = cls._determine_directional_zone(
                                city=city,
                                hex_obj=neighbor,
                                distance=distance_step
                            )
                            city.districts[neighbor] = zone_type

                            tiles[neighbor].city_id = city.id_num
                            tiles[neighbor].zone_type = zone_type
                            tiles[neighbor].zone_color = ZONE_COLORS[zone_type]

                frontier = next_frontier
            cities.append(city)
        return cities

    @classmethod
    def _determine_directional_zone(cls,
                                    city: City,
                                    hex_obj: Hex,
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
