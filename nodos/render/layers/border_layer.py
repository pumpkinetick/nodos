from arcade.shape_list import Shape, ShapeElementList, create_line

from nodos.core.hex_math import HexLayout, HexObject
from nodos.render.layers import RenderLayer
from nodos.render.utilities import darken_color
from nodos.world.map import HexTile, WorldMap

from nodos.config import (
    POINTY_TOP_DIRECTIONS
)


class BorderLayer(RenderLayer):
    def __init__(self, layout: HexLayout):
        self.layout = layout

        self.shapes: ShapeElementList = ShapeElementList()
        self._tile_map: dict[HexObject, list[Shape]] = dict()

    def build(self, world_map: WorldMap):
        self.shapes = ShapeElementList()
        self._tile_map.clear()

        for hex_obj, tile in world_map.tiles.items():
            if tile.city_id is not None:
                corners = self.layout.polygon_corners(hex_obj=hex_obj)
                b_shapes = self._bake_tile_borders(
                    hex_obj=hex_obj, corners=corners, tile=tile, world_map=world_map
                )
                if b_shapes:
                    self._tile_map[hex_obj] = b_shapes
                    for s in b_shapes:
                        self.shapes.append(s)

    def update_tiles(self,
                     hexes: list[HexObject],
                     world_map: WorldMap
                     ):
        for h in hexes:
            tile = world_map.get_tile(hex_obj=h)
            if tile and tile.city_id is not None:
                corners = self.layout.polygon_corners(hex_obj=h)
                b_shapes = self._bake_tile_borders(
                    hex_obj=h, corners=corners, tile=tile, world_map=world_map
                )
                if b_shapes:
                    self._tile_map[h] = b_shapes
                else:
                    self._tile_map.pop(h, None)
            else:
                self._tile_map.pop(h, None)

        self._rebuild_list()

    def remove_tiles(self, hexes: list[HexObject]):
        for h in hexes:
            self._tile_map.pop(h, None)

        self._rebuild_list()

    def _rebuild_list(self):
        self.shapes = ShapeElementList()
        for shapes in self._tile_map.values():
            for s in shapes:
                self.shapes.append(s)

    def draw(self):
        self.shapes.draw()

    @staticmethod
    def _bake_tile_borders(hex_obj: HexObject,
                           corners: list[tuple[float, float]],
                           tile: HexTile,
                           world_map: WorldMap
                           ) -> list[Shape]:
        city = world_map.cities[tile.city_id]

        border_list: list = list()
        for i, (dq, dr) in enumerate(POINTY_TOP_DIRECTIONS):
            neighbor = world_map.get_tile(
                hex_obj=HexObject(q=hex_obj.q + dq, r=hex_obj.r + dr)
            )
            if neighbor is None or neighbor.city_id != tile.city_id:
                p1 = corners[i]
                p2 = corners[(i + 1) % 6]
                border_color = darken_color(color=city.color, amount=60)
                border_list.append(create_line(
                    start_x=p1[0], start_y=p1[1], end_x=p2[0], end_y=p2[1], color=border_color, line_width=5.0
                ))

        return border_list
