import arcade

from nodos.core.hex_math import HexLayout
from nodos.world.map import WorldMap


class HexBatchDrawer:
    def __init__(self,
                 layout: HexLayout
                 ):
        self.layout = layout

        self.shape_list = arcade.shape_list.ShapeElementList()

    def build_geometry(self,
                       world_map: WorldMap
                       ):
        self.shape_list = arcade.shape_list.ShapeElementList()

        for hex_obj, tile in world_map.tiles.items():
            corners = self.layout.polygon_corners(hex_obj=hex_obj)

            fill_color = tile.color
            border_color = (max(0, fill_color[0] - 20),
                            max(0, fill_color[1] - 20),
                            max(0, fill_color[2] - 20),
                            255)

            fill_shape = arcade.shape_list.create_polygon(
                point_list=corners, color=fill_color
            )
            self.shape_list.append(fill_shape)

            closed_corners = corners + [corners[0]]
            outline_shape = arcade.shape_list.create_line_strip(
                point_list=closed_corners, color=border_color
            )
            self.shape_list.append(outline_shape)

    def draw_world_map(self):
        self.shape_list.draw()
