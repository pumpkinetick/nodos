from typing import Optional

from nodos.core.hex_math import Hex


class HexTile:
    def __init__(self,
                 hex_obj: Hex
                 ):
        self.hex_obj = hex_obj

        self.elevation: float = 0.0
        self.biome: str = 'water'
        self.color: tuple[int, int, int, int] = (0, 0, 0, 255)
        self.is_buildable: bool = False

        self.city_id: Optional[int] = None
        self.zone_type: Optional[str] = None
        self.zone_color: Optional[tuple[int, int, int, int]] = None

    def __repr__(self):
        return f'HexTile({self.hex_obj.q}, {self.hex_obj.r})'
