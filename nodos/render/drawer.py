import arcade

from nodos.core.hex_math import HexLayout
from nodos.world.map import WorldMap


class HexBatchDrawer:
    def __init__(self,
                 layout: HexLayout
                 ):
        self.layout = layout

    def draw_world_map(self,
                       world_map: WorldMap
                       ):
        for hex_obj, tile in world_map.tiles.items():
            corners = self.layout.polygon_corners(hex_obj=hex_obj)

            fill_color = (50, 120, 90)
            border_color = (30, 80, 60)

            arcade.draw_polygon_filled(point_list=corners, color=fill_color)
            arcade.draw_polygon_outline(point_list=corners, color=border_color)
