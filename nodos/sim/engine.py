from __future__ import annotations

import logging
from functools import cached_property
from typing import Any, Callable, Optional

from nodos.world.map import WorldMap
from nodos.world.zones import City

from nodos.config import (
    DEFAULT_GROWTH_RATE,
    DEFAULT_HAPPINESS,
    DEFAULT_POPULATION,
    DEFAULT_RESOURCES
)

logger = logging.getLogger(__name__)


class Simulation:
    def __init__(self,
                 world: Optional[WorldMap] = None,
                 tick_length: float = 1.0
                 ):
        self.world = world or WorldMap()
        self.tick_length = tick_length

        self.current_tick: int = 0
        self.time: float = 0.0

        self.hooks: dict[str, list[Callable[..., Any]]] = {
            'pre_tick': list(),
            'post_tick': list(),
            'city_tick': list()
        }

        logger.info(
            'Simulation initialized: %d cities', len(self.world.cities)
        )

    @cached_property
    def city_states(self) -> dict[int, dict[str, Any]]:
        states = dict()
        for cid, city in self.world.cities.items():
            states[cid] = self._default_city_state()
        return states

    @staticmethod
    def _default_city_state() -> dict[str, Any]:
        return {
            'population': DEFAULT_POPULATION,
            'resources': DEFAULT_RESOURCES,
            'happiness': DEFAULT_HAPPINESS,
            'growth_rate': DEFAULT_GROWTH_RATE
        }

    def register_hook(self,
                      hook_name: str,
                      func: Callable[..., Any]
                      ):
        if hook_name not in self.hooks:
            raise KeyError(f'Unknown hook name: {hook_name}')
        self.hooks[hook_name].append(func)

    def unregister_hook(self,
                        hook_name: str,
                        func: Callable[..., Any]
                        ):
        if hook_name not in self.hooks:
            raise KeyError(f'Unknown hook name: {hook_name}')
        self.hooks[hook_name].remove(func)

    def tick(self):
        logger.debug(
            'Tick %d starting', self.current_tick
        )

        for fn in list(self.hooks['pre_tick']):
            try:
                fn(self)
            except Exception:
                logger.exception(
                    'Error in pre_tick hook %s', fn
                )

        for cid, city in list(self.world.cities.items()):
            state = self.city_states.get(cid)
            if state is None:
                state = self._default_city_state()
                self.city_states[cid] = state

            for fn in list(self.hooks['city_tick']):
                try:
                    fn(self, city, state)
                except Exception:
                    logger.exception(
                        'Error in city_tick hook %s for city %d', fn, cid
                    )

        for fn in list(self.hooks['post_tick']):
            try:
                fn(self)
            except Exception:
                logger.exception(
                    'Error in post_tick hook %s', fn
                )

        self.current_tick += 1
        self.time += float(self.tick_length)

        logger.debug(
            'Tick %d complete (time=%s)', self.current_tick, self.time
        )

    def step(self):
        self.tick()

    def run(self,
            steps: int
            ):
        logger.info(
            'Running simulation for %d steps', steps
        )
        for _ in range(steps):
            self.tick()

    def get_city_state(self,
                       city_id: int
                       ) -> dict[str, Any]:
        return self.city_states.get(city_id)

    def set_city_state(self,
                       city_id: int,
                       state: dict[str, Any]
                       ):
        self.city_states[city_id] = state

    def add_city(self,
                 city: City
                 ):
        self.world.cities[city.id_num] = city
        self.city_states[city.id_num] = self._default_city_state()

    def remove_city(self,
                    city_id: int
                    ):
        self.world.cities.pop(city_id, None)
        self.city_states.pop(city_id, None)
