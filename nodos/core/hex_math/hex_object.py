from __future__ import annotations


class HexObject:
    def __init__(self,
                 q: int,
                 r: int
                 ):
        self.q = q
        self.r = r
        self.s: int = -q - r

    def __eq__(self,
               other: object
               ) -> bool:
        if not isinstance(other, HexObject):
            return False
        return self.q == other.q and self.r == other.r

    def __hash__(self) -> int:
        return hash((self.q, self.r))

    def __repr__(self) -> str:
        return f'HexObject(q={self.q}, r={self.r})'

    def distance_to(self,
                    other: HexObject
                    ) -> int:
        return (abs(self.q - other.q) + abs(self.r - other.r) + abs(self.s - other.s)) // 2
