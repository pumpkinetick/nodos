from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Optional

from nodos.config import (
    BASE_DEVELOPMENT,
    BASE_HAPPINESS,
    BASE_POP_CAP,
    COM_DEV_BOOST,
    COM_HAPPY_BOOST,
    COM_RES_PROD,
    DEATH_POPULATION_THRESHOLD,
    DEFAULT_DEVELOPMENT,
    DEFAULT_HAPPINESS,
    DEFAULT_POPULATION,
    DEFAULT_REPRODUCTION_COOLDOWN,
    DEFAULT_RESOURCES,
    IND_DEV_BOOST,
    IND_HAPPY_PENALTY,
    IND_RES_PROD,
    POP_CONSUMPTION_RATE,
    RES_POP_CAP_BOOST
)

if TYPE_CHECKING:
    from nodos.simulation import SimulationEngine
    from nodos.world.cities import City

logger = logging.getLogger(__name__)


class CityStatusManager:
    def __init__(self, engine: SimulationEngine):
        self.engine = engine

        self.city_states: dict[int, dict[str, Any]] = dict()

    def initialize_city_states(self):
        self.city_states = {
            cid: self.default_city_state()
            for cid in self.engine.world.cities.keys()
        }

    @staticmethod
    def default_city_state() -> dict[str, Any]:
        return {
            'population': DEFAULT_POPULATION,
            'happiness': DEFAULT_HAPPINESS,
            'resources': DEFAULT_RESOURCES,
            'development': DEFAULT_DEVELOPMENT,
            'reproduction_cooldown': DEFAULT_REPRODUCTION_COOLDOWN
        }

    def get_state(self, city_id: int) -> Optional[dict[str, Any]]:
        return self.city_states.get(city_id)

    def set_state(self,
                  city_id: int,
                  state: dict[str, Any]
                  ):
        self.city_states[city_id] = state

    def remove_state(self, city_id: int):
        self.city_states.pop(city_id, None)

    def apply_metric_updates(self,
                             city: City,
                             state: dict[str, Any]
                             ):
        # 1. Count districts
        counts = {'residential': 0, 'industrial': 0, 'commercial': 0, 'center': 0}
        for zone_type in city.districts.values():
            if zone_type in counts:
                counts[zone_type] += 1

        n_res = counts['residential']
        n_ind = counts['industrial']
        n_com = counts['commercial']

        # 2. Extract current state
        pop = float(state.get('population', DEFAULT_POPULATION))
        res = float(state.get('resources', DEFAULT_RESOURCES))
        cooldown = int(state.get('reproduction_cooldown', 0))

        # 3. Calculate dynamic metrics
        # Capacity and Overcrowding
        pop_max = BASE_POP_CAP + n_res * RES_POP_CAP_BOOST
        overcrowding_penalty = max(0.0, (pop - pop_max) / pop_max) if pop_max > 0 else 1.0

        # Happiness (affects growth)
        happiness = BASE_HAPPINESS + (n_com * COM_HAPPY_BOOST) - (n_ind * IND_HAPPY_PENALTY) - overcrowding_penalty
        happiness = max(-0.5, min(0.5, happiness))

        # Development (affects resource production efficiency)
        development = BASE_DEVELOPMENT + (n_ind * IND_DEV_BOOST) + (n_com * COM_DEV_BOOST)

        # 4. Apply updates
        # Population growth
        new_pop = max(0.0, pop * (1.0 + happiness))

        # Resource production / consumption
        res_prod = (n_ind * IND_RES_PROD) + (n_com * pop * COM_RES_PROD)
        res_cons = pop * POP_CONSUMPTION_RATE
        res_net = (res_prod - res_cons) * (1.0 + development)
        new_res = max(0.0, res + res_net)

        # Update state object
        state['population'] = new_pop
        state['resources'] = new_res
        state['happiness'] = happiness
        state['development'] = development
        if cooldown > 0:
            state['reproduction_cooldown'] = cooldown - 1

        # 5. Death check
        if new_pop <= DEATH_POPULATION_THRESHOLD:
            logger.info('City %s (id=%s) died (population=%.2f)',
                        getattr(city, 'name', ''), city.id_num, new_pop)
            self.engine.remove_city(city.id_num)
            return
