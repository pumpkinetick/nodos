from arcade.shape_list import ShapeElementList, create_polygon, create_line_strip

from nodos.core.hex_math import HexLayout
from nodos.world.map import WorldMap


class HexBatchDrawer:
    def __init__(self,
                 layout: HexLayout
                 ):
        self.layout = layout

        self.terrain_shapes = ShapeElementList()
        self.district_shapes = ShapeElementList()

    def build_geometry(self,
                       world_map: WorldMap
                       ):
        self.terrain_shapes = ShapeElementList()
        self.district_shapes = ShapeElementList()

        for hex_obj, tile in world_map.tiles.items():
            corners = self.layout.polygon_corners(hex_obj=hex_obj)

            t_fill = tile.color
            t_border = (max(0, t_fill[0] - 20),
                        max(0, t_fill[1] - 20),
                        max(0, t_fill[2] - 20),
                        255)

            self.terrain_shapes.append(create_polygon(
                point_list=corners, color=t_fill
            ))
            self.terrain_shapes.append(create_line_strip(
                point_list=corners + [corners[0]], color=t_border
            ))

            if tile.zone_color:
                d_fill = tile.zone_color
                d_border = (max(0, d_fill[0] - 30),
                            max(0, d_fill[1] - 30),
                            max(0, d_fill[2] - 30),
                            255)
            else:
                d_fill = (t_fill[0] // 2, t_fill[1] // 2, t_fill[2] // 2, 255)
                d_border = d_fill

            self.district_shapes.append(create_polygon(
                point_list=corners, color=d_fill
            ))
            self.district_shapes.append(create_line_strip(
                point_list=corners + [corners[0]], color=d_border
            ))

    def draw_layer(self,
                   view_mode: str
                   ):
        if view_mode == 'terrain':
            self.terrain_shapes.draw()
        elif view_mode == 'districts':
            self.district_shapes.draw()
