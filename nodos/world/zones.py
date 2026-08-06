import random

from nodos.core.hex_math import Hex

from nodos.config import (
    CITY_EXPANSION_STEPS,
    HEX_DIRECTIONS,
    NUM_CITIES,
    ZONE_COLORS,
    ZONE_TYPES,
)


class City:
    def __init__(self,
                 id_num: int,
                 center: Hex
                 ):
        self.id_num = id_num
        self.center = center

        self.districts: dict[Hex, str] = {center: 'center'}


class CityBuilderEngine:
    @staticmethod
    def generate_cities(tiles: dict
                        ) -> list[City]:
        buildable_hexes = [h for h, t in tiles.items() if t.is_buildable]

        num_seeds = min(NUM_CITIES, len(buildable_hexes))
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

            for _ in range(CITY_EXPANSION_STEPS):
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

                            zone_type = random.choice(seq=ZONE_TYPES)
                            city.districts[neighbor] = zone_type

                            tiles[neighbor].city_id = city.id_num
                            tiles[neighbor].zone_type = zone_type
                            tiles[neighbor].zone_color = ZONE_COLORS[zone_type]

                frontier = next_frontier
            cities.append(city)
        return cities
