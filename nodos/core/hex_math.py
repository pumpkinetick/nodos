import math
from functools import cached_property

from nodos.config import HEX_SIZE, ORIGIN_X, ORIGIN_Y


class Hex:
    def __init__(self,
                 q: int,
                 r: int
                 ):
        self.q = q
        self.r = r

    @cached_property
    def s(self) -> int:
        return -self.q - self.r

    def __eq__(self,
               other: object
               ) -> bool:
        if not isinstance(other, Hex):
            return False
        return self.q == other.q and self.r == other.r

    def __hash__(self) -> int:
        return hash((self.q, self.r))

    def __repr__(self) -> str:
        return f'Hex(q={self.q}, r={self.r})'

    def distance_to(self,
                    other: 'Hex'
                    ) -> int:
        return (abs(self.q - other.q) + abs(self.r - other.r) + abs(self.s - other.s)) // 2


class HexLayout:
    def __init__(self,
                 size: float = HEX_SIZE,
                 origin_x: float = ORIGIN_X,
                 origin_y: float = ORIGIN_Y
                 ):
        self.size = size
        self.origin_x = origin_x
        self.origin_y = origin_y

        self._pixel_cache: dict[Hex, tuple[float, float]] = dict()
        self._corner_cache: dict[Hex, list[tuple[float, float]]] = dict()

    def hex_to_pixel(self,
                     hex_obj: Hex
                     ) -> tuple[float, float]:
        p = self._pixel_cache.get(hex_obj)
        if p is not None:
            return p

        x = self.size * (math.sqrt(3) * hex_obj.q + math.sqrt(3) / 2.0 * hex_obj.r) + self.origin_x
        y = self.size * (3.0 / 2.0 * hex_obj.r) + self.origin_y
        self._pixel_cache[hex_obj] = (x, y)
        return x, y

    def polygon_corners(self,
                        hex_obj: Hex
                        ) -> list[tuple[float, float]]:
        corners = self._corner_cache.get(hex_obj)
        if corners is not None:
            return corners

        center_x, center_y = self.hex_to_pixel(hex_obj=hex_obj)
        corners = list()
        for i in range(6):
            angle_rad = math.pi / 180.0 * (60 * i + 30)
            x = center_x + self.size * math.cos(angle_rad)
            y = center_y + self.size * math.sin(angle_rad)
            corners.append((x, y))
        self._corner_cache[hex_obj] = corners
        return corners

    def clear_cache(self):
        self._pixel_cache.clear()
        self._corner_cache.clear()

    def pixel_to_hex(self,
                     x: float,
                     y: float
                     ) -> Hex:
        norm_x = (x - self.origin_x) / self.size
        norm_y = (y - self.origin_y) / self.size

        q = math.sqrt(3) / 3.0 * norm_x - 1.0 / 3.0 * norm_y
        r = 2.0 / 3.0 * norm_y
        s = -q - r

        return self._cube_round(q=q, r=r, s=s)

    @staticmethod
    def _cube_round(q: float,
                    r: float,
                    s: float
                    ) -> Hex:
        rounded_q = round(q)
        rounded_r = round(r)
        rounded_s = round(s)

        q_diff = abs(rounded_q - q)
        r_diff = abs(rounded_r - r)
        s_diff = abs(rounded_s - s)

        if q_diff > max(r_diff, s_diff):
            rounded_q = -rounded_r - rounded_s
        elif r_diff > s_diff:
            rounded_r = -rounded_q - rounded_s

        return Hex(q=rounded_q, r=rounded_r)
