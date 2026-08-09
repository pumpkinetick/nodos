from arcade.shape_list import ShapeElementList, create_line_strip, create_polygon

from nodos.render.layers import RenderLayer


class ZoningLayer(RenderLayer):
    def __init__(self, layout):
        self.layout = layout
        self.shapes = ShapeElementList()
        self._tile_map = {}

    def build(self, world_map):
        self._tile_map.clear()
        self.shapes = ShapeElementList()

        for hex_obj, tile in world_map.tiles.items():
            corners = self.layout.polygon_corners(hex_obj=hex_obj)
            z_shapes = self._bake_zoning_tile(corners=corners, tile=tile)
            
            if z_shapes:
                self._tile_map[hex_obj] = z_shapes
                for s in z_shapes:
                    self.shapes.append(s)

    def update_tile(self, hex_obj, tile):
        corners = self.layout.polygon_corners(hex_obj=hex_obj)
        self._tile_map[hex_obj] = self._bake_zoning_tile(corners=corners, tile=tile)
        
        self.shapes = ShapeElementList()
        for shapes in self._tile_map.values():
            for s in shapes:
                self.shapes.append(s)

    def draw(self):
        self.shapes.draw()

    def _bake_zoning_tile(self, corners, tile):
        if tile.zone_color:
            z_border = self._darken_color(color=tile.zone_color, amount=50)
            return self._create_hex_shapes(
                corners=corners, fill_color=tile.zone_color, border_color=z_border, line_width=1.0
            )
        else:
            dimmed_fill = (tile.color[0] // 2, tile.color[1] // 2, tile.color[2] // 2, 255)
            dimmed_border = self._darken_color(color=dimmed_fill, amount=15)
            return self._create_hex_shapes(
                corners=corners, fill_color=dimmed_fill, border_color=dimmed_border, line_width=1.0
            )

    @staticmethod
    def _darken_color(color, amount):
        return max(0, color[0] - amount), max(0, color[1] - amount), max(0, color[2] - amount), 255

    @staticmethod
    def _create_hex_shapes(corners, fill_color, border_color, line_width=1.0):
        poly = create_polygon(point_list=corners, color=fill_color)
        border = create_line_strip(point_list=corners + [corners[0]], color=border_color, line_width=line_width)
        return [poly, border]
