import logging
from typing import Optional

import arcade
from arcade.shape_list import ShapeElementList

from nodos.core.hex_math import HexLayout, HexObject
from nodos.render import CameraController
from nodos.render import SimulationDrawer
from nodos.sim import HookManager
from nodos.sim import Simulation
from nodos.world.map import WorldMap

logger = logging.getLogger(__name__)


class SimulationWindow(arcade.Window):
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

        self.layout: HexLayout = HexLayout()
        self.world_map: WorldMap = WorldMap()

        self.sim: Simulation = Simulation(world=self.world_map)
        self._sim_time_acc: float = 0.0

        self.camera_controller: CameraController = CameraController()

        self.gui_camera: arcade.Camera2D = arcade.Camera2D()

        self.drawer: SimulationDrawer = SimulationDrawer(layout=self.layout)
        self.drawer.build_geometry(world_map=self.world_map)

        self._needs_rebuild: bool = False
        self._removed_hexes_acc: list[HexObject] = list()

        try:
            self.sim_hooks = HookManager(window=self)
            self.sim_hooks.attach(simulation=self.sim)
        except Exception:
            logger.exception('Failed registering city_removed hook')

        self.active_keys: set = set()
        self.view_mode: str = 'terrain'

        self.hovered_hex: Optional[HexObject] = None

        self.mode_text_obj = arcade.Text(
            text='',
            x=20, y=height - 30,
            color=arcade.color.WHITE,
            font_size=14, bold=True
        )

        self.hud_left_text_objs = [
            arcade.Text(
                text='',
                x=30, y=30 + i * 20,
                color=arcade.color.WHITE,
                font_size=12
            )
            for i in range(3)
        ]
        self.hud_right_text_objs = [
            arcade.Text(
                text='',
                x=30, y=30 + i * 20,
                color=arcade.color.WHITE,
                font_size=12
            )
            for i in range(4)
        ]

    def queue_city_creation_updates(self):
        self._removed_hexes_acc = list()
        self._needs_rebuild = True

    def queue_city_removal_updates(self,
                                   removed_hexes: list[HexObject]
                                   ):
        if removed_hexes:
            self._removed_hexes_acc.extend(removed_hexes)
            self._needs_rebuild = True

    def on_draw(self):
        self.clear()

        self.camera_controller.use_world()
        self.drawer.draw_layer(view_mode=self.view_mode)

        self.gui_camera.use()

        base = (
            "View: TERRAIN (Press 'Z' to toggle)"
            if self.view_mode == 'terrain'
            else "View: ZONING (Press 'Z' to toggle)"
        )
        tick_info = f' | Tick: {self.sim.current_tick}' if hasattr(self, 'sim') else ''
        self.mode_text_obj.text = base + tick_info
        self.mode_text_obj.draw()

        if self.hovered_hex:
            tile = self.world_map.get_tile(hex_obj=self.hovered_hex)
            if tile:
                left_lines = [f'Biome: {tile.biome.title()}']
                right_lines: list[str] = list()

                if tile.city_id is not None and tile.city_id in self.world_map.cities:
                    city = self.world_map.cities[tile.city_id]
                    left_lines.append(f'City: {city.name}')
                    left_lines.append(f'District: {tile.zone_type.title()}')

                    state = None
                    if hasattr(self, 'sim'):
                        try:
                            state = self.sim.get_city_state(city.id_num)
                        except Exception:
                            state = None

                    if state:
                        pop = float(state.get('population', 0.0))
                        res = float(state.get('resources', 0.0))
                        happiness = float(state.get('happiness', 0.0))
                        development = float(state.get('development', 0.0))
                        right_lines = [
                            f'Population: {pop:.0f}',
                            f'Resources: {res:.0f}',
                            f'Happiness: {happiness:+.2f}',
                            f'Development: {development:+.2f}'
                        ]
                else:
                    left_lines.append('No city')

                world_x, world_y = self.layout.hex_to_pixel(hex_obj=self.hovered_hex)
                screen_pos = self.camera_controller.world_camera.project((world_x, world_y))

                line_height = 18
                padding = 10
                col_spacing = 10
                left_col_width = 150
                right_col_width = 150
                box_width = left_col_width + col_spacing + right_col_width
                box_height = max(len(left_lines), len(right_lines)) * line_height + padding * 2
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

                for i, line in enumerate(left_lines):
                    text_obj = self.hud_left_text_objs[i]

                    text_obj.text = line
                    text_obj.x = box_x - box_width / 2 + padding
                    text_obj.y = box_y + box_height - padding - (i + 1) * line_height
                    text_obj.anchor_y = 'bottom'
                    text_obj.draw()

                for i, line in enumerate(right_lines):
                    text_obj = self.hud_right_text_objs[i]

                    text_obj.text = line
                    text_obj.x = box_x - box_width / 2 + padding + left_col_width + col_spacing
                    text_obj.y = box_y + box_height - padding - (i + 1) * line_height
                    text_obj.anchor_y = 'bottom'
                    text_obj.draw()

    def on_mouse_motion(self,
                        x: int,
                        y: int,
                        dx: int,
                        dy: int
                        ):
        world_pos = self.camera_controller.world_camera.unproject(screen_coordinate=(x, y))
        self.hovered_hex = self.layout.pixel_to_hex(x=world_pos[0], y=world_pos[1])

    def on_update(self,
                  delta_time: float
                  ):
        self._sim_time_acc += delta_time
        try:
            while self._sim_time_acc >= self.sim.tick_length:
                self.sim.tick()
                self._sim_time_acc -= self.sim.tick_length
        except Exception:
            logger.exception('Simulation tick error')

        if getattr(self, '_needs_rebuild', False):
            try:
                if getattr(self, '_removed_hexes_acc', None):
                    try:
                        self.drawer.remove_tiles(
                            hexes=self._removed_hexes_acc,
                            world_map=self.world_map
                        )
                    except Exception:
                        self.drawer.build_geometry(world_map=self.world_map)

                    try:
                        self.drawer.road_shapes = ShapeElementList()
                        self.drawer.bake_roads(world_map=self.world_map)
                    except Exception:
                        self.drawer.build_geometry(world_map=self.world_map)

                    self._removed_hexes_acc = list()
                else:
                    self.drawer.build_geometry(world_map=self.world_map)
            except Exception:
                logger.exception('Error rebuilding geometry')
            finally:
                self._needs_rebuild = False

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
