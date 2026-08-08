from __future__ import annotations

import logging
import random
from typing import TYPE_CHECKING, Any

from nodos.core.hex_math import Hex

from nodos.config import (
    DEFAULT_DEVELOPMENT,
    DEFAULT_HAPPINESS,
    DEFAULT_POPULATION,
    DEFAULT_REPRODUCTION_COOLDOWN,
    DEFAULT_RESOURCES,
    HEX_DIRECTIONS,
    REPRODUCTION_RESOURCE_COST,
    REPRODUCTION_THRESHOLD,
    ZONE_COLORS
)

if TYPE_CHECKING:
    from nodos.sim.engine import Simulation
    from nodos.world.zones import City

logger = logging.getLogger(__name__)


class ReproductionSystem:
    def __init__(self,
                 simulation: Simulation
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

        child_transfer_pop = min(pop * 0.1, pop) # to config
        child_transfer_res = min(res * 0.1, res) # to config

        child_state = self.simulation.default_city_state()
        child_state['population'] = child_transfer_pop
        child_state['happiness'] = DEFAULT_HAPPINESS
        child_state['resources'] = child_transfer_res
        child_state['development'] = DEFAULT_DEVELOPMENT

        child_city = self._create_child_city(center_hex=offspring_center)
        self.simulation.add_city(city=child_city, state=child_state)

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

    def _create_child_city(self,
                           center_hex: Hex
                           ) -> City:
        child_city = self._make_city(center_hex=center_hex)
        self._claim_city_tiles(city=child_city, center_hex=center_hex)
        return child_city

    def _make_city(self,
                   center_hex: Hex
                   ) -> City:
        return City(id_num=self._next_city_id(), center=center_hex)

    def _find_reproduction_hex(self,
                               city: City
                               ) -> Hex | None:
        if not hasattr(city, 'districts'):
            return None

        candidate_hexes: list[Hex] = list()
        for hex_obj in list(city.districts.keys()):
            for dq, dr in HEX_DIRECTIONS:
                candidate = Hex(q=hex_obj.q + dq, r=hex_obj.r + dr)
                tile = self.simulation.world.tiles.get(candidate)
                if tile and tile.is_buildable and getattr(tile, 'city_id', None) is None:
                    candidate_hexes.append(candidate)

        if not candidate_hexes:
            return None

        return random.choice(candidate_hexes)

    def _claim_city_tiles(self,
                          city: City,
                          center_hex: Hex
                          ):
        tile = self.simulation.world.tiles.get(center_hex)
        if tile is None:
            return

        tile.city_id = city.id_num
        tile.zone_type = 'center'
        tile.zone_color = ZONE_COLORS['center']
        city.districts = {center_hex: 'center'}

    def _next_city_id(self) -> int:
        existing_ids = [cid for cid in self.simulation.world.cities.keys() if isinstance(cid, int)]
        return max(existing_ids, default=0) + 1
