from arcade.shape_list import ShapeElementList, create_line

from nodos.render.layers import RenderLayer


class RoadLayer(RenderLayer):
    def __init__(self, layout):
        self.layout = layout
        self.shapes = ShapeElementList()

    def build(self, world_map):
        self.shapes = ShapeElementList()
        for h1, h2 in world_map.road_network.road_edges:
            p1_x, p1_y = self.layout.hex_to_pixel(hex_obj=h1)
            p2_x, p2_y = self.layout.hex_to_pixel(hex_obj=h2)
            self.shapes.append(
                create_line(
                    start_x=p1_x, start_y=p1_y, end_x=p2_x, end_y=p2_y,
                    color=(60, 40, 30, 255), line_width=3
                )
            )

    def draw(self):
        self.shapes.draw()
