from arcade.shape_list import ShapeElementList, create_line_strip, create_polygon

from nodos.render.layers import RenderLayer

from nodos.config import (
    ZONE_COLORS
)


class TerrainLayer(RenderLayer):
    def __init__(self, layout):
        self.layout = layout
        self.shapes = ShapeElementList()
        self._base_map = {}
        self._overlay_map = {}

    def build(self, world_map):
        self._base_map.clear()
        self._overlay_map.clear()
        self.shapes = ShapeElementList()

        for hex_obj, tile in world_map.tiles.items():
            corners = self.layout.polygon_corners(hex_obj=hex_obj)
            
            # Bake terrain tile logic
            t_border = self._darken_color(color=tile.color, amount=25)
            base_shapes = self._create_hex_shapes(
                corners=corners, fill_color=tile.color, border_color=t_border, line_width=1.0
            )

            overlay_shapes = []
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

    @staticmethod
    def _darken_color(color, amount):
        return max(0, color[0] - amount), max(0, color[1] - amount), max(0, color[2] - amount), 255

    @staticmethod
    def _create_hex_shapes(corners, fill_color, border_color, line_width=1.0):
        poly = create_polygon(point_list=corners, color=fill_color)
        border = create_line_strip(point_list=corners + [corners[0]], color=border_color, line_width=line_width)
        return [poly, border]
