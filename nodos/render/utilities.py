from arcade.shape_list import Shape, create_line_strip, create_polygon


def darken_color(color,
                 amount: int
                 ) -> tuple[int, int, int, int]:
    return max(0, color[0] - amount), max(0, color[1] - amount), max(0, color[2] - amount), 255


def create_hex_shapes(corners: list[tuple[float, float]],
                      fill_color: tuple[int, int, int, int],
                      border_color: tuple[int, int, int, int],
                      line_width: float = 1.0
                      ) -> list[Shape]:
    poly = create_polygon(point_list=corners, color=fill_color)
    border = create_line_strip(
        point_list=corners + [corners[0]], color=border_color, line_width=line_width
    )
    return [poly, border]
