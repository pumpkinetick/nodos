from __future__ import annotations

import random


class NodeGene:
    def __init__(self,
                 node_id: int,
                 node_type: str
                 ):
        self.id = node_id
        self.type = node_type  # 'input', 'hidden', 'output'

        self.bias = random.gauss(mu=0, sigma=1) if node_type != 'input' else 0.0

    def copy(self) -> NodeGene:
        new_node = NodeGene(node_id=self.id, node_type=self.type)
        new_node.bias = self.bias
        return new_node
