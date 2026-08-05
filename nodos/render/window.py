from typing import Optional
import arcade

from nodos.core.hex_math import Hex, HexLayout
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
            resizable=False
        )

        arcade.set_background_color(arcade.color.CHARCOAL)

        self.layout = HexLayout()
        self.world_map = WorldMap()
        self.camera_controller = CameraController()

        self.gui_camera = arcade.Camera2D()

        self.drawer = HexBatchDrawer(layout=self.layout)
        self.drawer.build_geometry(world_map=self.world_map)

        self.active_keys = set()
        self.view_mode = 'terrain'

        self.hovered_hex: Optional[Hex] = None

        self.mode_text_obj = arcade.Text(
            text='',
            x=20, y=height - 30,
            color=arcade.color.WHITE,
            font_size=14, bold=True
        )

        self.hud_text_objs = [
            arcade.Text(
                text='',
                x=30, y=30 + i * 20,
                color=arcade.color.WHITE,
                font_size=12
            )
            for i in range(3)
        ]

    def on_draw(self):
        self.clear()

        self.camera_controller.use_world()
        self.drawer.draw_layer(view_mode=self.view_mode)

        self.gui_camera.use()

        self.mode_text_obj.text = (
            "View: TERRAIN (Press 'Z' to toggle)"
            if self.view_mode == 'terrain'
            else "View: ZONING (Press 'Z' to toggle)"
        )
        self.mode_text_obj.draw()

        if self.hovered_hex:
            tile = self.world_map.get_tile(hex_obj=self.hovered_hex)
            if tile:
                info_lines = [
                    f'Biome: {tile.biome.title()}'
                ]
                if tile.city_id is not None:
                    city = self.world_map.cities[tile.city_id]
                    info_lines.append(f'City: {city.name}')
                    info_lines.append(f'District: {tile.zone_type.title()}')

                world_x, world_y = self.layout.hex_to_pixel(hex_obj=self.hovered_hex)
                screen_pos = self.camera_controller.world_camera.project((world_x, world_y))

                line_height = 18
                padding = 10
                box_width = 180
                box_height =  len(info_lines) * line_height + padding * 2
                box_x = screen_pos[0]
                box_y = screen_pos[1] + 25.0

                arcade.draw_rect_filled(
                    rect=arcade.rect.XYWH(
                        x=box_x,
                        y=box_y,
                        width=box_width,
                        height=box_height,
                        anchor=arcade.rect.AnchorPoint.BOTTOM_CENTER
                    ),
                    color=(0, 0, 0, 190)
                )

                for i, line in enumerate(info_lines):
                    text_obj = self.hud_text_objs[i]

                    text_obj.text = line
                    text_obj.x = box_x - box_width / 2 + padding
                    text_obj.y = box_y + box_height - padding - (i + 1) * line_height
                    text_obj.anchor_y = 'bottom'
                    text_obj.draw()

    def on_mouse_motion(self,
                        x: int,
                        y: int,
                        dx: int,
                        dy: int
                        ):
        world_pos = self.camera_controller.world_camera.unproject((x, y))
        self.hovered_hex = self.layout.pixel_to_hex(x=world_pos[0], y=world_pos[1])

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

        if symbol == arcade.key.Z:
            self.view_mode = 'zoning' if self.view_mode == 'terrain' else 'terrain'

    def on_key_release(self,
                       symbol: int,
                       modifiers: int
                       ):
        self.active_keys.discard(symbol)
