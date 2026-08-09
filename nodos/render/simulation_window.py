import logging
from typing import Optional

import arcade

from nodos.core.hex_math import HexLayout, HexObject
from nodos.render import *
from nodos.simulation import HookManager
from nodos.simulation import SimulationEngine
from nodos.world.map import WorldMap

logger = logging.getLogger(__name__)


class SimulationWindow(arcade.Window):
    def __init__(self,
                 width: int,
                 height: int,
                 title: str
                 ):
        super().__init__(
            width=width, height=height, title=title, resizable=False
        )
        arcade.set_background_color(arcade.color.CHARCOAL)

        self.layout = HexLayout()
        self.world_map = WorldMap()
        self.sim = SimulationEngine(world=self.world_map)
        self._sim_time_acc = 0.0

        self.camera_controller = CameraController()
        self.drawer = SimulationDrawer(layout=self.layout)
        self.drawer.build_geometry(world_map=self.world_map)

        self.interface_renderer = InterfaceRenderer(window=self)
        self.input_handler = InputHandler(window=self)

        self._needs_rebuild = False
        self._removed_hexes_acc: list[HexObject] = list()

        try:
            self.sim_hooks = HookManager(window=self)
            self.sim_hooks.attach(simulation=self.sim)
        except Exception:
            logger.exception('Failed registering city_removed hook')

        self.view_mode = 'terrain'
        self.hovered_hex: Optional[HexObject] = None

    def queue_city_creation_updates(self):
        self._removed_hexes_acc = list()
        self._needs_rebuild = True

    def queue_city_removal_updates(self, removed_hexes: list[HexObject]):
        if removed_hexes:
            self._removed_hexes_acc.extend(removed_hexes)
            self._needs_rebuild = True

    def on_draw(self):
        self.clear()
        self.camera_controller.use_world()
        self.drawer.draw_layer(view_mode=self.view_mode)
        self.interface_renderer.draw(
            view_mode=self.view_mode,
            current_tick=self.sim.current_tick,
            hovered_hex=self.hovered_hex
        )

    def on_mouse_motion(self,
                        x: int,
                        y: int,
                        dx: int,
                        dy: int
                        ):
        self.input_handler.on_mouse_motion(
            x=x, y=y, dx=dx, dy=dy
        )

    def on_update(self, delta_time: float):
        self._sim_time_acc += delta_time
        try:
            while self._sim_time_acc >= self.sim.tick_length:
                self.sim.tick()
                self._sim_time_acc -= self.sim.tick_length
        except Exception:
            logger.exception('SimulationEngine tick error')

        if self._needs_rebuild:
            self._handle_rebuild()

        self.input_handler.update_camera(delta_time=delta_time)

    def _handle_rebuild(self):
        try:
            if self._removed_hexes_acc:
                self.drawer.remove_tiles(hexes=self._removed_hexes_acc, world_map=self.world_map)
                self.drawer.bake_roads(world_map=self.world_map)
                self._removed_hexes_acc = list()
            else:
                self.drawer.build_geometry(world_map=self.world_map)
        except Exception:
            logger.exception('Error rebuilding geometry')
            self.drawer.build_geometry(world_map=self.world_map)
        finally:
            self._needs_rebuild = False

    def on_mouse_scroll(self,
                        x: int,
                        y: int,
                        scroll_x: int,
                        scroll_y: int
                        ):
        self.input_handler.on_mouse_scroll(
            x=x, y=y, scroll_x=scroll_x, scroll_y=scroll_y
        )

    def on_key_press(self,
                     symbol: int,
                     modifiers: int
                     ):
        self.input_handler.on_key_press(symbol=symbol, modifiers=modifiers)

    def on_key_release(self,
                       symbol: int,
                       modifiers: int
                       ):
        self.input_handler.on_key_release(symbol=symbol, modifiers=modifiers)
