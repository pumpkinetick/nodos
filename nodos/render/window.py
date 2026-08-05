import arcade

from nodos.core.hex_math import HexLayout
from nodos.render.camera import CameraController
from nodos.render.drawer import HexBatchDrawer
from nodos.world.map import WorldMap


class Window(arcade.Window):
    def __init__(self,
                 width: int,
                 height: int,
                 title: str
                 ):
        super().__init__(
            width=width,
            height=height,
            title=title,
            resizable=True
        )

        arcade.set_background_color(arcade.color.CHARCOAL)

        self.camera_controller = CameraController()
        self.layout = HexLayout(
            size=32.0,
            origin_x=0.0,
            origin_y=0.0
        )
        self.drawer = HexBatchDrawer(layout=self.layout)

        self.world_map = WorldMap(width=10, height=10)

        self.active_keys = set()

    def on_draw(self):
        self.clear()
        self.camera_controller.use_world()
        self.drawer.draw_world_map(world_map=self.world_map)

    def on_update(self,
                  delta_time: float
                  ):
        self.camera_controller.update(delta_time=delta_time, active_keys=self.active_keys)

    def on_mouse_scroll(self,
                        x: int,
                        y: int,
                        scroll_x: int,
                        scroll_y: int
                        ):
        self.camera_controller.adjust_zoom_target(scroll_y=scroll_y)

    def on_key_press(self,
                     symbol: int,
                     modifiers: int
                     ):
        self.active_keys.add(symbol)

    def on_key_release(self,
                       symbol: int,
                       modifiers: int
                       ):
        self.active_keys.discard(symbol)
