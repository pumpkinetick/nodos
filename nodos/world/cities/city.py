import math
import random

from nodos.core.hex_math import Hex

from nodos.config import (
    NAME_PREFIXES,
    NAME_SUFFIXES
)


class City:
    def __init__(self,
                 id_num: int,
                 center: Hex
                 ):
        self.id_num = id_num
        self.center = center

        self.name: str = f'{random.choice(NAME_PREFIXES)}{random.choice(NAME_SUFFIXES)}'

        self.color: tuple[int, int, int, int] = (
            random.randint(a=50, b=220),
            random.randint(a=50, b=220),
            random.randint(a=50, b=220),
            180
        )

        self.industrial_angle: float = random.uniform(a=0.0, b=2.0 * math.pi)
        self.districts: dict[Hex, str] = {center: 'center'}
