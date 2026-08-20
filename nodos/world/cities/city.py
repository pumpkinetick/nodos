import colorsys
import math
import random
from typing import Optional

import numpy as np

from nodos.core.hex_math import HexObject

from nodos.config import (
    NAME_PREFIXES,
    NAME_SUFFIXES
)


class City:
    def __init__(self,
                 id_num: int,
                 center: HexObject,
                 parent_color: Optional[tuple[int, int, int, int]] = None
                 ):
        from nodos.core.brain import Brain

        self.id_num = id_num
        self.center = center

        self.brain = Brain(layer_sizes=[4, 8, 13])

        self.name = f'{random.choice(NAME_PREFIXES)}{random.choice(NAME_SUFFIXES)}'

        if parent_color:
            self.color = City._get_new_color(parent_color=parent_color)
        else:
            self.color = (
                random.randint(a=50, b=220),
                random.randint(a=50, b=220),
                random.randint(a=50, b=220),
                180
            )

        self.industrial_angle = random.uniform(a=0.0, b=2.0 * math.pi)

        self.districts: dict[HexObject, str] = {center: 'center'}

    @staticmethod
    def _get_new_color(parent_color: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
        r, g, b = [x / 255.0 for x in parent_color[:3]]
        hsv_array = np.array(colorsys.rgb_to_hsv(r=r, g=g, b=b))

        delta_signs = np.random.randint(low=0, high=2, size=3)*2-1
        diffs = delta_signs * np.random.uniform(low=0.0, high=0.05, size=3)

        h, s, v = tuple(hsv_array + diffs)
        new_r, new_g, new_b = colorsys.hsv_to_rgb(h=h, s=s, v=v)

        return (
            int(new_r * 255),
            int(new_g * 255),
            int(new_b * 255),
            parent_color[3]
        )
