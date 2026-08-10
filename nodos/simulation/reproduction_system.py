from __future__ import annotations

import logging
import random
from typing import TYPE_CHECKING, Any, Union

from nodos.core.hex_math import HexObject
from nodos.world.cities import CityBuilder

from nodos.config import (
    CITY_EXPANSION_STEPS,
    DEFAULT_DEVELOPMENT,
    DEFAULT_HAPPINESS,
    DEFAULT_POPULATION,
    DEFAULT_REPRODUCTION_COOLDOWN,
    DEFAULT_RESOURCES,
    MIN_CHILD_CITY_DISTANCE,
    REPRODUCTION_RESOURCE_COST,
    REPRODUCTION_THRESHOLD
)

if TYPE_CHECKING:
    from nodos.simulation import SimulationEngine
    from nodos.world.cities import City

logger = logging.getLogger(__name__)


class ReproductionSystem:
    def __init__(self,
                 simulation: SimulationEngine
                 ):
        self.simulation = simulation

    def try_reproduce(self,
                      city: City,
                      state: dict[str, Any]
                      ):
        cooldown = int(state.get('reproduction_cooldown', 0))
        if cooldown > 0:
            state['reproduction_cooldown'] = cooldown - 1
            return

        pop = float(state.get('population', DEFAULT_POPULATION))
        res = float(state.get('resources', DEFAULT_RESOURCES))
        if pop < REPRODUCTION_THRESHOLD or res < REPRODUCTION_RESOURCE_COST:
            return

        offspring_center = self._find_reproduction_hex(city=city)
        if offspring_center is None:
            return

        child_transfer_pop = min(pop * 0.1, pop)
        child_transfer_res = min(res * 0.1, res)

        child_state = self.simulation.default_city_state()
        child_state['population'] = child_transfer_pop
        child_state['happiness'] = DEFAULT_HAPPINESS
        child_state['resources'] = child_transfer_res
        child_state['development'] = DEFAULT_DEVELOPMENT

        child_city = CityBuilder.create_expanded_city_inplace(
            tiles=self.simulation.world.tiles,
            city_id=self._next_city_id(),
            center_hex=offspring_center,
            parent_color=city.color
        )

        if child_city is None:
            return

        self.simulation.add_city(city=child_city, state=child_state)

        self.simulation.world.road_network.connect_cities(
            city_a_center=city.center,
            city_b_center=child_city.center,
            tiles=self.simulation.world.tiles
        )

        state['population'] = max(0.0, pop - child_transfer_pop)
        state['resources'] = max(0.0, res - child_transfer_res)
        state['reproduction_cooldown'] = DEFAULT_REPRODUCTION_COOLDOWN

        logger.info(
            'City %s (id=%s) reproduced into %s (id=%s)',
            getattr(city, 'name', ''),
            city.id_num,
            getattr(child_city, 'name', ''),
            child_city.id_num
        )

    def _find_reproduction_hex(self,
                               city: City,
                               min_distance: int = MIN_CHILD_CITY_DISTANCE
                               ) -> Union[HexObject, None]:
        potential_hexes = [
            h for h, t in self.simulation.world.tiles.items()
            if t.is_buildable and getattr(t, 'city_id', None) is None
        ]

        valid_candidates: list[HexObject] = list()
        for candidate in potential_hexes:
            if candidate.distance_to(other=city.center) < min_distance:
                continue

            is_valid: bool = True
            for other_city in self.simulation.world.cities.values():
                if other_city == city:
                    continue
                if candidate.distance_to(other=other_city.center) < min_distance:
                    is_valid = False
                    break

            if is_valid:
                valid_candidates.append(candidate)

        if valid_candidates:
            return random.choice(seq=valid_candidates)

        if min_distance > CITY_EXPANSION_STEPS:
            return self._find_reproduction_hex(city=city, min_distance=min_distance - 1)

        return None

    def _next_city_id(self) -> int:
        existing_ids = [cid for cid in self.simulation.world.cities.keys() if isinstance(cid, int)]
        return max(existing_ids, default=0) + 1
