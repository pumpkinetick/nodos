from arcade.shape_list import (
    ShapeElementList,
    create_line,
    create_line_strip,
    create_polygon
)

from nodos.core.hex_math import HexLayout, Hex
from nodos.world.map import HexTile, WorldMap

from nodos.config import POINTY_TOP_DIRECTIONS, ZONE_COLORS


class HexBatchDrawer:
    def __init__(self,
                 layout: HexLayout
                 ):
        self.layout = layout

        self.terrain_shapes = ShapeElementList()
        self.zoning_shapes = ShapeElementList()
        self.road_shapes = ShapeElementList()
        self.border_shapes = ShapeElementList()

    def build_geometry(self,
                       world_map: WorldMap
                       ):
        self.terrain_shapes = ShapeElementList()
        self.zoning_shapes = ShapeElementList()
        self.road_shapes = ShapeElementList()
        self.border_shapes = ShapeElementList()

        for hex_obj, tile in world_map.tiles.items():
            corners = self.layout.polygon_corners(hex_obj=hex_obj)

            self._bake_zoning_tile(
                corners=corners,
                tile=tile
            )
            self._bake_terrain_tile(
                corners=corners,
                tile=tile,
                world_map=world_map
            )

        self._bake_roads(world_map=world_map)

    def draw_layer(self,
                   view_mode: str
                   ):
        if view_mode == 'terrain':
            self.terrain_shapes.draw()
            self.border_shapes.draw()
        elif view_mode == 'zoning':
            self.zoning_shapes.draw()

        self.road_shapes.draw()

    @staticmethod
    def _darken_color(color: tuple[int, int, int, int],
                      amount: int
                      ) -> tuple[int, int, int, int]:
        return (
            max(0, color[0] - amount),
            max(0, color[1] - amount),
            max(0, color[2] - amount),
            255
        )

    @staticmethod
    def _append_hex_shape(target_list: ShapeElementList,
                          corners: list[tuple[float, float]],
                          fill_color: tuple[int, int, int, int],
                          border_color: tuple[int, int, int, int],
                          line_width: float = 1.0
                          ):
        target_list.append(create_polygon(
            point_list=corners,
            color=fill_color
        ))
        target_list.append(create_line_strip(
            point_list=corners + [corners[0]],
            color=border_color,
            line_width=line_width
        ))

    def _bake_zoning_tile(self,
                          corners: list[tuple[float, float]],
                          tile: HexTile
                          ):
        if tile.zone_color:
            z_border = self._darken_color(color=tile.zone_color, amount=50)
            self._append_hex_shape(
                target_list=self.zoning_shapes,
                corners=corners,
                fill_color=tile.zone_color,
                border_color=z_border,
                line_width=1.0
            )
        else:
            dimmed_fill = (
                tile.color[0] // 2,
                tile.color[1] // 2,
                tile.color[2] // 2,
                255
            )
            dimmed_border = self._darken_color(color=dimmed_fill, amount=15)
            self._append_hex_shape(
                target_list=self.zoning_shapes,
                corners=corners,
                fill_color=dimmed_fill,
                border_color=dimmed_border,
                line_width=1.0
            )

    def _bake_terrain_tile(self,
                           corners: list[tuple[float, float]],
                           tile: HexTile,
                           world_map: WorldMap
                           ):
        if tile.city_id is not None:
            city = world_map.cities[tile.city_id]

            c_fill = (
                ZONE_COLORS['center']
                if tile.zone_type == 'center'
                else city.color
            )

            self.terrain_shapes.append(create_polygon(
                point_list=corners,
                color=c_fill
            ))

            self._bake_tile_borders(
                hex_obj=tile.hex_obj,
                corners=corners,
                tile=tile,
                world_map=world_map
            )
        else:
            t_border = self._darken_color(color=tile.color, amount=25)
            self._append_hex_shape(
                target_list=self.terrain_shapes,
                corners=corners,
                fill_color=tile.color,
                border_color=t_border,
                line_width=1.0
            )

    def _bake_tile_borders(self,
                           hex_obj: Hex,
                           corners: list[tuple[float, float]],
                           tile: HexTile,
                           world_map: WorldMap
                           ):
        city = world_map.cities[tile.city_id]

        for i, (dq, dr) in enumerate(POINTY_TOP_DIRECTIONS):
            neighbor = world_map.get_tile(hex_obj=Hex(
                q=hex_obj.q + dq, r=hex_obj.r + dr
            ))

            if neighbor is None or neighbor.city_id != tile.city_id:
                p1 = corners[i]
                p2 = corners[(i + 1) % 6]

                border_color = self._darken_color(color=city.color, amount=60)
                self.border_shapes.append(
                    create_line(
                        start_x=p1[0],
                        start_y=p1[1],
                        end_x=p2[0],
                        end_y=p2[1],
                        color=border_color,
                        line_width=3.0
                    )
                )

    def _bake_roads(self,
                    world_map: WorldMap
                    ):
        for h1, h2 in world_map.infra_graph.road_edges:
            p1_x, p1_y = self.layout.hex_to_pixel(hex_obj=h1)
            p2_x, p2_y = self.layout.hex_to_pixel(hex_obj=h2)
            self.road_shapes.append(
                create_line(
                    start_x=p1_x,
                    start_y=p1_y,
                    end_x=p2_x,
                    end_y=p2_y,
                    color=(60, 40, 30, 255),
                    line_width=2.5
                )
            )
