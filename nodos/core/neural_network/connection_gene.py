from __future__ import annotations


class ConnectionGene:
    def __init__(self,
                 in_node: int,
                 out_node: int,
                 weight: float,
                 enabled: bool,
                 innov: int
                 ):
        self.in_node = in_node
        self.out_node = out_node
        self.weight = weight
        self.enabled = enabled
        self.innov = innov

    def copy(self) -> ConnectionGene:
        return ConnectionGene(
            in_node=self.in_node,
            out_node=self.out_node,
            weight=self.weight,
            enabled=self.enabled,
            innov=self.innov
        )
