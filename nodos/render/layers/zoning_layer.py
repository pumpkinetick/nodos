from typing import Optional

from arcade.shape_list import Shape, ShapeElementList

from nodos.core.hex_math import HexLayout, HexObject
from nodos.render.layers import RenderLayer
from nodos.render.utilities import create_hex_shapes, darken_color
from nodos.world.map import HexTile, WorldMap


class ZoningLayer(RenderLayer):
    def __init__(self, layout: HexLayout):
        self.layout = layout

        self.shapes: ShapeElementList = ShapeElementList()
        self._tile_map: dict[HexObject, list[Shape]] = dict()

    def build(self, world_map: WorldMap):
        self.shapes = ShapeElementList()
        self._tile_map.clear()

        for hex_obj, tile in world_map.tiles.items():
            corners = self.layout.polygon_corners(hex_obj=hex_obj)
            z_shapes = self._bake_zoning_tile(corners=corners, tile=tile)

            if z_shapes:
                self._tile_map[hex_obj] = z_shapes
                for s in z_shapes:
                    self.shapes.append(s)

    def update_tile(self,
                    hex_obj: HexObject,
                    tile: HexTile
                    ):
        self.update_tiles(hexes=[hex_obj], world_map=None, tile_override=tile)

    def update_tiles(self,
                     hexes: list[HexObject],
                     world_map: Optional[WorldMap],
                     tile_override: Optional[HexTile] = None
                     ):
        for h in hexes:
            tile = tile_override or world_map.get_tile(hex_obj=h)
            if tile:
                corners = self.layout.polygon_corners(hex_obj=h)
                self._tile_map[h] = self._bake_zoning_tile(corners=corners, tile=tile)
            else:
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
    def _bake_zoning_tile(corners: list[tuple[float, float]], tile: HexTile):
        if tile.zone_color:
            z_border = darken_color(color=tile.zone_color, amount=50)
            return create_hex_shapes(
                corners=corners, fill_color=tile.zone_color, border_color=z_border, line_width=1.0
            )
        else:
            dimmed_fill = (tile.color[0] // 2, tile.color[1] // 2, tile.color[2] // 2, 255)
            dimmed_border = darken_color(color=dimmed_fill, amount=15)
            return create_hex_shapes(
                corners=corners, fill_color=dimmed_fill, border_color=dimmed_border, line_width=1.0
            )
