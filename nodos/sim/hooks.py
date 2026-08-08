from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Callable, Optional

if TYPE_CHECKING:
    from nodos.core.hex_math import Hex
    from nodos.render.window import Window
    from nodos.sim.engine import Simulation

logger = logging.getLogger(__name__)


class SimulationWindowHooks:
    def __init__(self,
                 window: Window
                 ):
        self.window = window
        self._city_removed_hook: Optional[Callable[..., None]] = None

    def attach(self,
               simulation: Simulation
               ):
        if self._city_removed_hook is None:
            self._city_removed_hook = self._build_city_removed_hook()

        simulation.register_hook(
            hook_name='city_removed',
            func=self._city_removed_hook
        )

    def detach(self,
               simulation: Simulation
               ):
        if self._city_removed_hook is not None:
            simulation.unregister_hook(
                hook_name='city_removed',
                func=self._city_removed_hook
            )
            self._city_removed_hook = None

    def _build_city_removed_hook(self) -> Callable[..., None]:
        def _on_city_removed(
            sim_obj: Simulation,
            city_id: int,
            removed_hexes: list[Hex],
        ):
            try:
                self.window.queue_city_removal_updates(removed_hexes=removed_hexes)
            except Exception:
                logger.exception('Error in city_removed handler')

        return _on_city_removed
