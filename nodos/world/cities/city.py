import math
import random
from typing import Optional

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
        self.id_num = id_num
        self.center = center

        self.name = f'{random.choice(NAME_PREFIXES)}{random.choice(NAME_SUFFIXES)}'

        if parent_color:
            delta = 20
            self.color = (
                max(50, min(220, parent_color[0] + random.randint(-delta, delta))),
                max(50, min(220, parent_color[1] + random.randint(-delta, delta))),
                max(50, min(220, parent_color[2] + random.randint(-delta, delta))),
                parent_color[3]
            )
        else:
            self.color = (
                random.randint(a=50, b=220),
                random.randint(a=50, b=220),
                random.randint(a=50, b=220),
                180
            )

        self.industrial_angle = random.uniform(a=0.0, b=2.0 * math.pi)

        self.districts: dict[HexObject, str] = {center: 'center'}
