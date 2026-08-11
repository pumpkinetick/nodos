from __future__ import annotations

import arcade

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from nodos.render import SimulationWindow


class InputHandler:
    def __init__(self, window: SimulationWindow):
        self.window = window

        self.active_keys: set[int] = set()

    def on_key_press(self,
                     symbol: int,
                     modifiers: int
                     ):
        self.active_keys.add(symbol)
        if symbol == arcade.key.Z:
            self.window.view_mode = 'zoning' if self.window.view_mode == 'terrain' else 'terrain'

    def on_key_release(self,
                       symbol: int,
                       modifiers: int
                       ):
        self.active_keys.discard(symbol)

    def on_mouse_motion(self,
                        x: int,
                        y: int,
                        dx: int,
                        dy: int
                        ):
        world_pos = self.window.camera_controller.world_camera.unproject(screen_coordinate=(x, y))
        self.window.hovered_hex = self.window.layout.pixel_to_hex(x=world_pos[0], y=world_pos[1])

    def on_mouse_scroll(self,
                        x: int,
                        y: int,
                        scroll_x: int,
                        scroll_y: int
                        ):
        self.window.camera_controller.adjust_zoom_target(scroll_y=scroll_y)

    def update_camera(self, delta_time: float):
        self.window.camera_controller.update(delta_time=delta_time, active_keys=self.active_keys)
