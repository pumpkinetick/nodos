from arcade.shape_list import Shape, ShapeElementList, create_polygon

from nodos.core.hex_math import HexLayout, HexObject
from nodos.render.layers import RenderLayer
from nodos.render.utilities import create_hex_shapes, darken_color
from nodos.world.map import HexTile, WorldMap

from nodos.config import (
    ZONE_COLORS
)


class TerrainLayer(RenderLayer):
    def __init__(self, layout: HexLayout):
        self.layout = layout

        self.base_shapes = ShapeElementList()
        self.overlay_shapes = ShapeElementList()

        self._base_map: dict[HexObject, list[Shape]] = dict()
        self._overlay_map: dict[HexObject, list[Shape]] = dict()

    def build(self, world_map: WorldMap):
        self.base_shapes = ShapeElementList()
        self.overlay_shapes = ShapeElementList()
        self._base_map.clear()
        self._overlay_map.clear()

        for hex_obj, tile in world_map.tiles.items():
            corners = self.layout.polygon_corners(hex_obj=hex_obj)

            t_border = darken_color(color=tile.color, amount=25)
            base_shapes = create_hex_shapes(
                corners=corners, fill_color=tile.color, border_color=t_border, line_width=1.0
            )

            if base_shapes:
                self._base_map[hex_obj] = base_shapes
                for s in base_shapes:
                    self.base_shapes.append(s)

            self._update_tile_overlay(hex_obj=hex_obj, tile=tile, world_map=world_map)

        self._rebuild_overlay_list()

    def _update_tile_overlay(self,
                             hex_obj: HexObject,
                             tile: HexTile,
                             world_map: WorldMap
                             ):
        overlay_shapes: list[Shape] = list()
        if tile.city_id is not None:
            city = world_map.cities[tile.city_id]
            c_fill = (ZONE_COLORS['center'] if tile.zone_type == 'center' else city.color)
            overlay_shapes.append(create_polygon(
                point_list=self.layout.polygon_corners(hex_obj=hex_obj), color=c_fill
            ))

        if overlay_shapes:
            self._overlay_map[hex_obj] = overlay_shapes
        else:
            self._overlay_map.pop(hex_obj, None)

    def _rebuild_overlay_list(self):
        self.overlay_shapes = ShapeElementList()
        for shapes in self._overlay_map.values():
            for s in shapes:
                self.overlay_shapes.append(s)

    def update_tiles(self,
                     hexes: list[HexObject],
                     world_map: WorldMap
                     ):
        for h in hexes:
            tile = world_map.get_tile(hex_obj=h)
            if tile:
                self._update_tile_overlay(hex_obj=h, tile=tile, world_map=world_map)

        self._rebuild_overlay_list()

    def remove_tiles(self, hexes: list[HexObject]):
        for h in hexes:
            self._overlay_map.pop(h, None)

        self._rebuild_overlay_list()

    def draw(self):
        self.base_shapes.draw()
        self.overlay_shapes.draw()
