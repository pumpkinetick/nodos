from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Optional

from nodos.config import (
    DEATH_POPULATION_THRESHOLD,
    DEFAULT_DEVELOPMENT,
    DEFAULT_HAPPINESS,
    DEFAULT_POPULATION,
    DEFAULT_REPRODUCTION_COOLDOWN,
    DEFAULT_RESOURCES
)

if TYPE_CHECKING:
    from nodos.simulation import SimulationEngine
    from nodos.world.cities import City

logger = logging.getLogger(__name__)


class CityStatusManager:
    def __init__(self,
                 engine: SimulationEngine
                 ):
        self.engine = engine

        self._city_states: dict[int, dict[str, Any]] = dict()

    def initialize_city_states(self):
        self._city_states = {
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

    def get_state(self,
                  city_id: int
                  ) -> Optional[dict[str, Any]]:
        return self._city_states.get(city_id)

    def set_state(self,
                  city_id: int,
                  state: dict[str, Any]
                  ):
        self._city_states[city_id] = state

    def remove_state(self,
                     city_id: int
                     ):
        self._city_states.pop(city_id, None)

    def apply_metric_updates(self,
                             city: City,
                             state: dict[str, Any]
                             ):
        pop = float(state.get('population', DEFAULT_POPULATION))
        res = float(state.get('resources', DEFAULT_RESOURCES))
        happiness = float(state.get('happiness', DEFAULT_HAPPINESS))
        development = float(state.get('development', DEFAULT_DEVELOPMENT))

        new_pop = max(0.0, pop * (1.0 + happiness))
        new_res = max(0.0, res * (1.0 + development))

        state['population'] = new_pop
        state['resources'] = new_res

        if new_pop <= DEATH_POPULATION_THRESHOLD:
            logger.info(
                'City %s (id=%s) died (population=%.2f)',
                getattr(city, 'name', ''), city.id_num, new_pop
            )
            self.engine.remove_city(city.id_num)
            return

        self.engine.reproduction.try_reproduce(city=city, state=state)
