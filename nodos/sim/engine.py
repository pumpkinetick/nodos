from __future__ import annotations

import logging
from functools import cached_property
from typing import Any, Callable, Optional

from nodos.core.hex_math import Hex
from nodos.sim.reproduction import ReproductionSystem
from nodos.world.map import WorldMap
from nodos.world.zones import City

from nodos.config import (
    DEATH_POPULATION_THRESHOLD,
    DEFAULT_DEVELOPMENT,
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
            'city_tick': list(),
            'city_added': list(),
            'city_removed': list()
        }

        self.reproduction = ReproductionSystem(simulation=self)

        logger.info(
            'Simulation initialized: %d cities', len(self.world.cities)
        )

    @cached_property
    def city_states(self) -> dict[int, dict[str, Any]]:
        states: dict[int, dict[str, Any]] = dict()
        for cid, city in self.world.cities.items():
            states[cid] = self.default_city_state()
        return states

    @staticmethod
    def default_city_state() -> dict[str, Any]:
        return {
            'population': DEFAULT_POPULATION,
            'happiness': DEFAULT_HAPPINESS,
            'resources': DEFAULT_RESOURCES,
            'development': DEFAULT_DEVELOPMENT,
            'reproduction_cooldown': 0
        }

    def register_hook(self,
                      hook_name: str,
                      func: Callable[..., Any]
                      ):
        if hook_name not in self.hooks:
            raise KeyError(f'Unknown hook name: {hook_name}')
        self.hooks[hook_name].append(func)

    def _notify_city_added(self,
                           city: City,
                           state: dict[str, Any]
                           ):
        for fn in list(self.hooks.get('city_added', list())):
            try:
                fn(self, city, state)
            except Exception:
                logger.exception('Error in city_added hook %s', fn)

    def unregister_hook(self,
                        hook_name: str,
                        func: Callable[..., Any]
                        ):
        if hook_name not in self.hooks:
            raise KeyError(f'Unknown hook name: {hook_name}')
        self.hooks[hook_name].remove(func)

    def _apply_metric_updates(self,
                              city: City,
                              state: dict[str, Any]
                              ):
        pop = float(state.get(
            'population', DEFAULT_POPULATION
        ))
        res = float(state.get(
            'resources', DEFAULT_RESOURCES
        ))

        happiness = float(state.get(
            'happiness', DEFAULT_HAPPINESS
        ))
        development = float(state.get(
            'development', DEFAULT_DEVELOPMENT
        ))

        new_pop = max(0.0, pop * (1.0 + happiness))
        new_res = max(0.0, res * (1.0 + development))

        state['population'] = new_pop
        state['resources'] = new_res

        if new_pop <= DEATH_POPULATION_THRESHOLD:
            logger.info(
                'City %s (id=%s) died (population=%.2f)',
                getattr(city, 'name', ''), city.id_num, new_pop
            )
            self.remove_city(city.id_num)
            return

        self.reproduction.try_reproduce(city=city, state=state)

    def tick(self):
        logger.debug(
            'Tick %d starting', self.current_tick
        )

        for fn in list(self.hooks['pre_tick']):
            try:
                fn(self)
            except Exception:
                logger.exception('Error in pre_tick hook %s', fn)

        for cid, city in list(self.world.cities.items()):
            state = self.city_states.get(cid)
            if state is None:
                state = self.default_city_state()
                self.city_states[cid] = state

            for fn in list(self.hooks['city_tick']):
                try:
                    fn(self, city, state)
                except Exception:
                    logger.exception('Error in city_tick hook %s for city %d', fn, cid)

            try:
                self._apply_metric_updates(city, state)
            except Exception:
                logger.exception('Error applying metric updates for city %s', cid)

        for fn in list(self.hooks['post_tick']):
            try:
                fn(self)
            except Exception:
                logger.exception('Error in post_tick hook %s', fn)

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
                 city: City,
                 state: Optional[dict[str, Any]] = None
                 ):
        city_state = state if state is not None else self.default_city_state()
        self.world.cities[city.id_num] = city
        self.city_states[city.id_num] = city_state
        self._notify_city_added(city=city, state=city_state)

    def remove_city(self,
                    city_id: int
                    ):
        city = self.world.cities.get(city_id)

        removed_hexes: list[Hex] = list()
        try:
            if city is not None and hasattr(city, 'districts'):
                for hex_obj in list(city.districts.keys()):
                    tile = self.world.tiles.get(hex_obj)
                    if tile and tile.city_id == city_id:
                        tile.city_id = None
                        tile.zone_type = None
                        tile.zone_color = None
                        removed_hexes.append(hex_obj)
            else:
                for hex_obj, tile in self.world.tiles.items():
                    if getattr(tile, 'city_id', None) == city_id:
                        tile.city_id = None
                        tile.zone_type = None
                        tile.zone_color = None
                        removed_hexes.append(hex_obj)
        except Exception:
            logger.exception('Error clearing tiles for removed city %s', city_id)

        self.world.cities.pop(city_id, None)
        self.city_states.pop(city_id, None)

        try:
            if city is not None and hasattr(city, 'center'):
                self.world.infra_graph.remove_city_connections(center=city.center)
        except Exception:
            logger.exception('Error removing infrastructure edges for city %s', city_id)

        for fn in list(self.hooks.get('city_removed', list())):
            try:
                fn(self, city_id, removed_hexes)
            except Exception:
                logger.exception('Error in city_removed hook %s', fn)
