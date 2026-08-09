import logging
from typing import Any, Callable, Optional

from nodos.core.hex_math import HexObject
from nodos.simulation import CityStatusManager, ReproductionSystem, SimulationClock
from nodos.world.cities import City
from nodos.world.map import WorldMap

logger = logging.getLogger(__name__)


class SimulationEngine:
    def __init__(self,
                 world: Optional[WorldMap] = None,
                 tick_length: float = 1.0
                 ):
        self.world = world or WorldMap()

        self.clock = SimulationClock(tick_length=tick_length)
        self.status_manager = CityStatusManager(engine=self)
        self.status_manager.initialize_city_states()

        self.hooks: dict[str, list[Callable[..., Any]]] = {
            'pre_tick': list(),
            'post_tick': list(),
            'city_tick': list(),
            'city_added': list(),
            'city_removed': list()
        }

        self.reproduction = ReproductionSystem(simulation=self)

        logger.info(
            'SimulationEngine initialized: %d cities', len(self.world.cities)
        )

    @property
    def current_tick(self) -> int:
        return self.clock.current_tick

    @property
    def time(self) -> float:
        return self.clock.time

    @property
    def tick_length(self) -> float:
        return self.clock.tick_length

    @property
    def city_states(self) -> dict[int, dict[str, Any]]:
        return self.status_manager.city_states

    @staticmethod
    def default_city_state() -> dict[str, Any]:
        return CityStatusManager.default_city_state()

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

    def _notify_city_added(self,
                           city: City,
                           state: dict[str, Any]
                           ):
        for fn in list(self.hooks.get('city_added', list())):
            try:
                fn(self, city, state)
            except Exception:
                logger.exception('Error in city_added hook %s', fn)

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
            state = self.status_manager.get_state(cid)
            if state is None:
                state = self.status_manager.default_city_state()
                self.status_manager.set_state(cid, state)

            for fn in list(self.hooks['city_tick']):
                try:
                    fn(self, city, state)
                except Exception:
                    logger.exception('Error in city_tick hook %s for city %d', fn, cid)

            try:
                self.status_manager.apply_metric_updates(city, state)
            except Exception:
                logger.exception('Error applying metric updates for city %s', cid)

        for fn in list(self.hooks['post_tick']):
            try:
                fn(self)
            except Exception:
                logger.exception('Error in post_tick hook %s', fn)

        self.clock.tick()

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
        return self.status_manager.get_state(city_id)

    def set_city_state(self,
                       city_id: int,
                       state: dict[str, Any]
                       ):
        self.status_manager.set_state(city_id, state)

    def add_city(self,
                 city: City,
                 state: Optional[dict[str, Any]] = None
                 ):
        city_state = state if state is not None else self.default_city_state()
        self.world.cities[city.id_num] = city
        self.status_manager.set_state(city.id_num, city_state)
        self._notify_city_added(city=city, state=city_state)

    def remove_city(self,
                    city_id: int
                    ):
        city = self.world.cities.get(city_id)

        removed_hexes: list[HexObject] = list()
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
        self.status_manager.remove_state(city_id)

        try:
            if city is not None and hasattr(city, 'center'):
                self.world.road_network.remove_city_connections(center=city.center)
        except Exception:
            logger.exception('Error removing infrastructure edges for city %s', city_id)

        for fn in list(self.hooks.get('city_removed', list())):
            try:
                fn(self, city_id, removed_hexes)
            except Exception:
                logger.exception('Error in city_removed hook %s', fn)
