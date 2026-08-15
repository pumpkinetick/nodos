from __future__ import annotations

import logging
import random
from typing import TYPE_CHECKING, Any, Optional, Union

from nodos.core.hex_math import HexObject
from nodos.world.cities import CityBuilder

from nodos.config import (
    DEFAULT_DEVELOPMENT,
    DEFAULT_HAPPINESS,
    DEFAULT_POPULATION,
    DEFAULT_REPRODUCTION_COOLDOWN,
    DEFAULT_RESOURCES,
    MAX_CHILD_CITY_DISTANCE,
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
                 engine: SimulationEngine
                 ):
        self.engine = engine

    def try_reproduce(self,
                      city: City,
                      state: dict[str, Any]
                      ) -> bool:
        cooldown = int(state.get('reproduction_cooldown', 0))
        if cooldown > 0:
            logger.debug('City %s is on reproduction cooldown (%d ticks left)',
                         city.id_num, cooldown)
            return False

        pop = float(state.get('population', DEFAULT_POPULATION))
        res = float(state.get('resources', DEFAULT_RESOURCES))
        if pop < REPRODUCTION_THRESHOLD or res < REPRODUCTION_RESOURCE_COST:
            logger.debug('City %s has insufficient population (%.2f < %.2f) or resources (%.2f < %.2f) to reproduce',
                         city.id_num, pop, REPRODUCTION_THRESHOLD, res, REPRODUCTION_RESOURCE_COST)
            return False

        offspring_center = self._find_reproduction_hex(city=city)
        if offspring_center is None:
            logger.debug('Could not find a suitable location for offspring of city %s',
                         city.id_num)
            return False

        child_transfer_pop = pop * 0.1
        child_transfer_res = res * 0.1

        child_state = self.engine.default_city_state()
        child_state['population'] = child_transfer_pop
        child_state['happiness'] = DEFAULT_HAPPINESS
        child_state['resources'] = child_transfer_res
        child_state['development'] = DEFAULT_DEVELOPMENT

        child_city = CityBuilder.create_expanded_city_inplace(
            tiles=self.engine.world.tiles,
            city_id=self._next_city_id(),
            center_hex=offspring_center,
            parent_color=city.color
        )

        if child_city is None:
            return False

        self.engine.add_city(city=child_city, state=child_state)

        self.engine.world.road_network.connect_cities(
            city_a_center=city.center,
            city_b_center=child_city.center,
            tiles=self.engine.world.tiles
        )

        state['population'] = max(0.0, pop - child_transfer_pop)
        state['resources'] = max(0.0, res - child_transfer_res)
        state['reproduction_cooldown'] = DEFAULT_REPRODUCTION_COOLDOWN

        logger.info('City %s (id=%s) reproduced into %s (id=%s)',
                    getattr(city, 'name', ''), city.id_num,
                    getattr(child_city, 'name', ''), child_city.id_num)
        return True

    def _find_reproduction_hex(self,
                               city: City,
                               target_distance: int = MIN_CHILD_CITY_DISTANCE,
                               candidates: Optional[list[HexObject]] = None
                               ) -> Union[HexObject, None]:
        if target_distance > MAX_CHILD_CITY_DISTANCE:
            return None

        if candidates is None:
            potential_hexes = [
                h for h, t in self.engine.world.tiles.items()
                if t.is_buildable and getattr(t, 'city_id', None) is None
            ]

            other_cities = [c for c in self.engine.world.cities.values() if c != city]
            candidates = [
                h for h in potential_hexes
                if all(h.distance_to(other=c.center) >= target_distance for c in other_cities)
            ]

        candidates = [h for h in candidates if h.distance_to(other=city.center) >= target_distance]

        if not candidates:
            return None

        exact_matches = [h for h in candidates if h.distance_to(other=city.center) == target_distance]

        if exact_matches:
            return random.choice(seq=exact_matches)

        return self._find_reproduction_hex(
            city=city,
            target_distance=target_distance + 1,
            candidates=candidates
        )

    def _next_city_id(self) -> int:
        existing_ids = [cid for cid in self.engine.world.cities.keys() if isinstance(cid, int)]
        return max(existing_ids, default=0) + 1
