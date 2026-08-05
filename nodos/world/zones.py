import random

from nodos.core.hex_math import Hex

from nodos.config import DISTRICT_COUNT, ZONE_TYPES, ZONE_COLORS


class District:
    def __init__(self,
                 id_num: int,
                 center: Hex,
                 zone_type: str
                 ):
        self.id_num = id_num
        self.center = center
        self.zone_type = zone_type

        self.color = ZONE_COLORS[zone_type]
        self.hexes: list[Hex] = list()

class ZonePartitionEngine:
    @staticmethod
    def generate_districts(tiles: dict) -> list[District]:
        buildable_hexes = [h for h, t in tiles.items() if t.is_buildable]

        num_seeds = min(DISTRICT_COUNT, len(buildable_hexes))
        if num_seeds == 0:
            return list()

        seed_hexes = random.sample(buildable_hexes, k=num_seeds)

        districts = list()
        for i, center_hex in enumerate(seed_hexes, start=1):
            zone_type = random.choice(ZONE_TYPES)
            districts.append(District(
                id_num=i,
                center=center_hex,
                zone_type=zone_type
            ))

        for hex_obj in buildable_hexes:
            closest_district = min(districts, key=lambda d: hex_obj.distance_to(d.center))
            closest_district.hexes.append(hex_obj)

            tiles[hex_obj].district_id = closest_district.id_num
            tiles[hex_obj].district_color = closest_district.color

        return districts
