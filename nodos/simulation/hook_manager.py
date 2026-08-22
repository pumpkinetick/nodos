from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Callable, Optional

from nodos.world.cities import City

if TYPE_CHECKING:
    from nodos.core.hex_math import HexObject
    from nodos.render import SimulationWindow
    from nodos.simulation import SimulationEngine

logger = logging.getLogger(__name__)


class HookManager:
    def __init__(self, window: SimulationWindow):
        self.window = window

        self._city_added_hook: Optional[Callable[..., None]] = None
        self._city_removed_hook: Optional[Callable[..., None]] = None

        self._district_added_hook: Optional[Callable[..., None]] = None
        self._district_changed_hook: Optional[Callable[..., None]] = None
        self._district_removed_hook: Optional[Callable[..., None]] = None

    def attach(self, engine: SimulationEngine):
        if self._city_added_hook is None:
            self._city_added_hook = self._build_city_added_hook()
        if self._city_removed_hook is None:
            self._city_removed_hook = self._build_city_removed_hook()

        if self._district_added_hook is None:
            self._district_added_hook = self._build_district_added_hook()
        if self._district_changed_hook is None:
            self._district_changed_hook = self._build_district_changed_hook()
        if self._district_removed_hook is None:
            self._district_removed_hook = self._build_district_removed_hook()

        engine.register_hook(
            hook_name='city_added',
            func=self._city_added_hook
        )
        engine.register_hook(
            hook_name='city_removed',
            func=self._city_removed_hook
        )

        engine.register_hook(
            hook_name='district_added',
            func=self._district_added_hook
        )
        engine.register_hook(
            hook_name='district_changed',
            func=self._district_changed_hook
        )
        engine.register_hook(
            hook_name='district_removed',
            func=self._district_removed_hook
        )

    def detach(self, engine: SimulationEngine):
        if self._city_added_hook is not None:
            engine.unregister_hook(
               hook_name='city_added',
               func=self._city_added_hook
            )
            self._city_added_hook = None
        if self._city_removed_hook is not None:
            engine.unregister_hook(
               hook_name='city_removed',
               func=self._city_removed_hook
            )
            self._city_removed_hook = None

        if self._district_added_hook is not None:
            engine.unregister_hook(
               hook_name='district_added',
               func=self._district_added_hook
            )
            self._district_added_hook = None
        if self._district_changed_hook is not None:
            engine.unregister_hook(
               hook_name='district_changed',
               func=self._district_changed_hook
            )
            self._district_changed_hook = None
        if self._district_removed_hook is not None:
            engine.unregister_hook(
               hook_name='district_removed',
               func=self._district_removed_hook
            )
            self._district_removed_hook = None

    def _build_city_added_hook(self) -> Callable[..., None]:
        def _on_city_added(
            sim_obj: SimulationEngine,
            city: City,
            state: dict[str, Any]
        ):
            try:
               added_hexes = list(getattr(city, 'districts', dict()).keys())
               self.window.queue_city_creation_updates(added_hexes=added_hexes)
            except Exception:
               logger.exception('Error in city_added handler')

        return _on_city_added

    def _build_city_removed_hook(self) -> Callable[..., None]:
        def _on_city_removed(
            sim_obj: SimulationEngine,
            city_id: int,
            removed_hexes: list[HexObject]
        ):
            try:
               self.window.queue_city_removal_updates(removed_hexes=removed_hexes)
            except Exception:
               logger.exception('Error in city_removed handler')

        return _on_city_removed

    def _build_district_added_hook(self) -> Callable[..., None]:
        def _on_district_added(
            sim_obj: SimulationEngine,
            city_id: int,
            hex_obj: HexObject
        ):
            try:
               self.window.queue_city_creation_updates(added_hexes=[hex_obj])
            except Exception:
               logger.exception('Error in district_added handler')

        return _on_district_added

    def _build_district_changed_hook(self) -> Callable[..., None]:
        def _on_district_changed(
            sim_obj: SimulationEngine,
            city_id: int,
            hex_obj: HexObject
        ):
            try:
               self.window.queue_city_creation_updates(added_hexes=[hex_obj])
            except Exception:
               logger.exception('Error in district_changed handler')

        return _on_district_changed

    def _build_district_removed_hook(self) -> Callable[..., None]:
        def _on_district_removed(
            sim_obj: SimulationEngine,
            city_id: int,
            hex_obj: HexObject
        ):
            try:
               self.window.queue_city_removal_updates(removed_hexes=[hex_obj])
            except Exception:
               logger.exception('Error in district_removed handler')

        return _on_district_removed
