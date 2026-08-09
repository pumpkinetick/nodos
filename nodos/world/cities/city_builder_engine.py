import random
from typing import Optional

from nodos.core.hex_math import HexObject

from nodos.config import (
    CITY_EXPANSION_STEPS,
    INIT_NUM_CITIES,
    MIN_CITY_DISTANCE
)


class CityBuilderEngine:
    @classmethod
    def generate_cities(cls,
                        tiles: dict
                        ) -> list:
        from nodos.world.cities import CityInitializer

        buildable_hexes = [h for h, t in tiles.items() if t.is_buildable]

        num_seeds = min(INIT_NUM_CITIES, len(buildable_hexes))
        if num_seeds == 0:
            return list()

        seed_hexes = cls._select_spread_seeds(
            buildable_hexes=buildable_hexes,
            min_distance=MIN_CITY_DISTANCE
        )

        cities: list = list()
        for i, center_hex in enumerate(seed_hexes, start=1):
            city = CityInitializer.create_expanded_city_inplace(
                tiles=tiles,
                city_id=i,
                center_hex=center_hex
            )
            if city is not None:
                cities.append(city)

        return cities

    @classmethod
    def _select_spread_seeds(cls,
                             buildable_hexes: list[HexObject],
                             min_distance: int,
                             candidates: Optional[list[HexObject]] = None
                             ) -> list[HexObject]:
        if candidates is None:
            candidates = buildable_hexes.copy()
            random.shuffle(candidates)

        selected_seeds: list[HexObject] = list()
        for candidate in candidates:
            if len(selected_seeds) >= INIT_NUM_CITIES:
                break

            is_valid_location: bool = True
            for seed in selected_seeds:
                if candidate.distance_to(other=seed) < min_distance:
                    is_valid_location = False
                    break

            if is_valid_location:
                selected_seeds.append(candidate)

        if len(selected_seeds) < INIT_NUM_CITIES and min_distance > CITY_EXPANSION_STEPS:
            return cls._select_spread_seeds(
                buildable_hexes=buildable_hexes,
                min_distance=min_distance - 1,
                candidates=candidates
            )

        return selected_seeds
