from functools import cached_property

from nodos.core.hex_math import Hex


class HexTile:
    def __init__(self,
                 hex_obj: Hex
                 ):
        self.hex_obj = hex_obj

    def __repr__(self):
        return f'HexTile({self.hex_obj.q}, {self.hex_obj.r})'

class WorldMap:
    def __init__(self,
                 width: int,
                 height: int
                 ):
        self.width = width
        self.height = height

    @cached_property
    def tiles(self) -> dict[Hex, HexTile]:
        tiles = dict()
        for r in range(self.height):
            r_offset = r // 2
            for col in range(self.width):
                q = col - r_offset
                hex_obj = Hex(q=q, r=r)
                tiles[hex_obj] = HexTile(hex_obj=hex_obj)
        return tiles

    def get_tile(self,
                 hex_obj: Hex
                 ) -> HexTile | None:
        return self.tiles.get(hex_obj)
