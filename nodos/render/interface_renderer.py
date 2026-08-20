from __future__ import annotations

import arcade

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from nodos.render import SimulationWindow
    from nodos.core.hex_math import HexObject
    from nodos.world.cities import City


class InterfaceRenderer:
    def __init__(self, window: SimulationWindow):
        self.window = window

        self.gui_camera = arcade.Camera2D()

        self.mode_text_obj = arcade.Text(
            text='',
            x=20, y=window.height - 30,
            color=arcade.color.WHITE,
            font_size=14, bold=True
        )

        self.hud_left_text_objs = [
            arcade.Text(text='', x=30, y=30 + i * 20, color=arcade.color.WHITE, font_size=12)
            for i in range(3)
        ]
        self.hud_right_text_objs = [
            arcade.Text(text='', x=30, y=30 + i * 20, color=arcade.color.WHITE, font_size=12)
            for i in range(4)
        ]

    def draw(self,
             view_mode: str,
             current_tick: int,
             hovered_hex: Optional[HexObject]
             ):
        self.gui_camera.use()

        base = (
            "View: TERRAIN (Press 'Z' to toggle)" if view_mode == 'terrain'
            else "View: ZONING (Press 'Z' to toggle)"
        )
        self.mode_text_obj.text = f"{base} | Tick: {current_tick}"
        self.mode_text_obj.draw()

        if hovered_hex:
            self._draw_tooltip(hex_obj=hovered_hex)

            tile = self.window.world_map.get_tile(hex_obj=hovered_hex)
            if tile and tile.city_id is not None and tile.city_id in self.window.world_map.cities:
                city = self.window.world_map.cities[tile.city_id]
                self._draw_brain_graph(city=city)

    @staticmethod
    def _draw_brain_graph(city: City):
        # Position fixed in bottom-left
        start_x = 80
        start_y = 60
        layer_spacing = 150
        node_spacing = 20
        margin_size = 20

        box_width = (len(city.brain.layer_sizes)-1) * layer_spacing + margin_size * 2
        box_height = (max(city.brain.layer_sizes)-1) * node_spacing + margin_size * 2

        # Background box
        arcade.draw_rect_filled(
            rect=arcade.rect.XYWH(
                x=start_x + box_width / 2, y=start_y + box_height / 2,
                width=box_width, height=box_height
            ),
            color=(0, 0, 0, 150)
        )

        # Nodes and connections
        node_positions: list[list[tuple[int, int]]] = list()
        for i, layer_size in enumerate(city.brain.layer_sizes):
            x = start_x + margin_size + i * layer_spacing
            layer_nodes = list()
            for j in range(layer_size):
                y = start_y + margin_size + j * node_spacing
                layer_nodes.append((x, y))
                arcade.draw_circle_filled(
                    center_x=x, center_y=y, radius=5, color=arcade.color.WHITE
                )
            node_positions.append(layer_nodes)

        # Draw connections
        for i in range(len(node_positions) - 1):
            for start_node in node_positions[i]:
                for end_node in node_positions[i+1]:
                    arcade.draw_line(
                        start_x=start_node[0], start_y=start_node[1],
                        end_x=end_node[0], end_y=end_node[1],
                        color=(255, 255, 255, 50), line_width=1
                    )

    def _draw_tooltip(self, hex_obj: HexObject):
        tile = self.window.world_map.get_tile(hex_obj=hex_obj)
        if not tile:
            return

        left_lines = [f'Biome: {tile.biome.title()}']
        right_lines: list[str] = list()

        if tile.city_id is not None and tile.city_id in self.window.world_map.cities:
            city = self.window.world_map.cities[tile.city_id]
            left_lines.append(f'City: {city.name}')
            left_lines.append(f'District: {tile.zone_type.title()}')

            state = self.window.engine.get_city_state(city.id_num)
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

        world_x, world_y = self.window.layout.hex_to_pixel(hex_obj=hex_obj)
        screen_pos = self.window.camera_controller.world_camera.project((world_x, world_y))

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
                x=box_x, y=box_y, width=box_width, height=box_height,
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
