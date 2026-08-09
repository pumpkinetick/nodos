from arcade.shape_list import Shape, ShapeElementList, create_polygon

from nodos.core.hex_math import HexLayout, HexObject
from nodos.render.layers import RenderLayer
from nodos.render.utilities import create_hex_shapes, darken_color
from nodos.world.map import WorldMap

from nodos.config import (
    ZONE_COLORS
)


class TerrainLayer(RenderLayer):
    def __init__(self, layout: HexLayout):
        self.layout = layout

        self.shapes: ShapeElementList = ShapeElementList()
        self._base_map: dict[HexObject, list[Shape]] = dict()
        self._overlay_map: dict[HexObject, list[Shape]] = dict()

    def build(self, world_map: WorldMap):
        self.shapes = ShapeElementList()
        self._base_map.clear()
        self._overlay_map.clear()

        for hex_obj, tile in world_map.tiles.items():
            corners = self.layout.polygon_corners(hex_obj=hex_obj)

            t_border = darken_color(color=tile.color, amount=25)
            base_shapes = create_hex_shapes(
                corners=corners, fill_color=tile.color, border_color=t_border, line_width=1.0
            )

            overlay_shapes: list[Shape] = list()
            if tile.city_id is not None:
                city = world_map.cities[tile.city_id]
                c_fill = (ZONE_COLORS['center'] if tile.zone_type == 'center' else city.color)
                overlay_shapes.append(create_polygon(point_list=corners, color=c_fill))

            if base_shapes:
                self._base_map[hex_obj] = base_shapes
                for s in base_shapes:
                    self.shapes.append(s)

            if overlay_shapes:
                self._overlay_map[hex_obj] = overlay_shapes
                for s in overlay_shapes:
                    self.shapes.append(s)

    def remove_tiles(self, hexes):
        for h in hexes:
            self._overlay_map.pop(h, None)
        self.shapes = ShapeElementList()

        for shapes in self._base_map.values():
            for s in shapes:
                self.shapes.append(s)
        for shapes in self._overlay_map.values():
            for s in shapes:
                self.shapes.append(s)

    def draw(self):
        self.shapes.draw()
