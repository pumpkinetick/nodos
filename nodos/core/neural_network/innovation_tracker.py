class InnovationTracker:
    _current_innov = 0
    _innovations: dict[tuple[int, int], int] = dict()

    @classmethod
    def get_innovation(cls,
                       in_node: int,
                       out_node: int
                       ) -> int:
        key = (in_node, out_node)
        if key in cls._innovations:
            return cls._innovations[key]
        cls._current_innov += 1
        cls._innovations[key] = cls._current_innov
        return cls._current_innov
