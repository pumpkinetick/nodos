from __future__ import annotations

import random

import numpy as np

from nodos.core.neural_network import ConnectionGene, InnovationTracker, NodeGene

from nodos.config import (
    NEAT_MUTATION_RATE_CONN,
    NEAT_MUTATION_RATE_NODE,
    NEAT_MUTATION_RATE_TOGGLE,
    NEAT_MUTATION_RATE_WEIGHT,
    NEAT_MUTATION_SCALE
)


class Brain:
    def __init__(self,
                 num_inputs: int = 4,
                 num_outputs: int = 13
                 ):
        self.num_inputs = num_inputs
        self.num_outputs = num_outputs

        self.nodes: dict[int, NodeGene] = dict()
        self.connections: list[ConnectionGene] = list()

        self.next_node_id = 0

        # Initialize input nodes
        for _ in range(num_inputs):
            self.nodes[self.next_node_id] = NodeGene(node_id=self.next_node_id, node_type='input')
            self.next_node_id += 1

        # Initialize output nodes
        for _ in range(num_outputs):
            self.nodes[self.next_node_id] = NodeGene(node_id=self.next_node_id, node_type='output')
            self.next_node_id += 1

    def copy(self) -> Brain:
        new_brain = Brain(num_inputs=self.num_inputs, num_outputs=self.num_outputs)
        new_brain.nodes = {n_id: n.copy() for n_id, n in self.nodes.items()}
        new_brain.connections = [c.copy() for c in self.connections]
        new_brain.next_node_id = self.next_node_id
        return new_brain

    def mutate(self):
        # Mutate weights and biases
        for n in self.nodes.values():
            if n.type != 'input' and random.random() < NEAT_MUTATION_RATE_WEIGHT:
                n.bias += random.gauss(mu=0, sigma=NEAT_MUTATION_SCALE)

        for c in self.connections:
            if random.random() < NEAT_MUTATION_RATE_WEIGHT:
                c.weight += random.gauss(mu=0, sigma=NEAT_MUTATION_SCALE)

            # Toggle connection
            if random.random() < NEAT_MUTATION_RATE_TOGGLE:
                c.enabled = not c.enabled

        # Add connection
        if random.random() < NEAT_MUTATION_RATE_CONN:
            self._mutate_add_connection()

        # Add node
        if random.random() < NEAT_MUTATION_RATE_NODE:
            self._mutate_add_node()

    def _mutate_add_connection(self):
        nodes = list(self.nodes.values())
        if not nodes:
            return

        in_node = random.choice(seq=nodes)
        out_node = random.choice(seq=nodes)

        # Basic validity checks
        if out_node.type == 'input':
            return
        if in_node.type == 'output' and out_node.type == 'output':
            return

        if self._forms_cycle(in_node_id=in_node.id, out_node_id=out_node.id):
            return

        # Check if already connected
        for c in self.connections:
            if c.in_node == in_node.id and c.out_node == out_node.id:
                return

        innov = InnovationTracker.get_innovation(in_node=in_node.id, out_node=out_node.id)
        weight = random.gauss(mu=0, sigma=1)
        self.connections.append(ConnectionGene(
            in_node=in_node.id, out_node=out_node.id, weight=weight, enabled=True, innov=innov
        ))

    def _mutate_add_node(self):
        if not self.connections:
            return

        valid_conns = [c for c in self.connections if c.enabled]
        if not valid_conns:
            return

        c = random.choice(valid_conns)
        c.enabled = False

        new_node_id = self.next_node_id
        self.next_node_id += 1
        self.nodes[new_node_id] = NodeGene(node_id=new_node_id, node_type='hidden')
        self.nodes[new_node_id].bias = 0.0

        innov1 = InnovationTracker.get_innovation(in_node=c.in_node, out_node=new_node_id)
        self.connections.append(ConnectionGene(
            in_node=c.in_node, out_node=new_node_id, weight=1.0, enabled=True, innov=innov1
        ))

        innov2 = InnovationTracker.get_innovation(in_node=new_node_id, out_node=c.out_node)
        self.connections.append(ConnectionGene(
            in_node=new_node_id, out_node=c.out_node, weight=c.weight, enabled=True, innov=innov2
        ))

    def _forms_cycle(self,
                     in_node_id: int,
                     out_node_id: int
                     ) -> bool:
        if in_node_id == out_node_id:
            return True

        visited = set()
        stack = [out_node_id]

        while stack:
            current = stack.pop()
            if current == in_node_id:
                return True
            visited.add(current)
            for c in self.connections:
                if c.in_node == current and c.enabled and c.out_node not in visited:
                    stack.append(c.out_node)
        return False

    @classmethod
    def create_prescripted(cls,
                           num_inputs: int = 4,
                           num_outputs: int = 13
                           ) -> Brain:
        brain = cls(num_inputs=num_inputs, num_outputs=num_outputs)

        # Population = 0, Happiness = 1, Resources = 2, Development = 3
        # Reproduce = 12, Build = 0,1,2

        # Start with a simple feedforward architecture mapping resources to reproduction
        reproduce_out = num_inputs + 12
        resources_in = 2
        population_in = 0

        innov1 = InnovationTracker.get_innovation(in_node=resources_in, out_node=reproduce_out)
        brain.connections.append(ConnectionGene(
            in_node=resources_in, out_node=reproduce_out, weight=5.0, enabled=True, innov=innov1
        ))

        innov2 = InnovationTracker.get_innovation(in_node=population_in, out_node=reproduce_out)
        brain.connections.append(ConnectionGene(
            in_node=population_in, out_node=reproduce_out, weight=5.0, enabled=True, innov=innov2
        ))

        brain.nodes[reproduce_out].bias = -4.0

        # Fallback build actions
        brain.nodes[num_inputs + 0].bias = 0.5
        brain.nodes[num_inputs + 1].bias = 0.5
        brain.nodes[num_inputs + 2].bias = 0.5

        return brain

    @staticmethod
    def sigmoid(x: float) -> float:
        # Clip to prevent overflow
        return 1.0 / (1.0 + np.exp(-np.clip(a=x, a_min=-50, a_max=50)))

    def think(self, inputs: np.ndarray) -> np.ndarray:
        node_values = {n_id: 0.0 for n_id in self.nodes.keys()}

        for i, val in enumerate(inputs):
            if i < self.num_inputs:
                node_values[i] = val

        # Evaluate nodes by resolving dependencies (like topological sort but simplified with propagation)
        # Because we prevent cycles, we can iteratively propagate values.
        in_degrees = {n_id: 0 for n_id in self.nodes.keys()}
        adj = {n_id: list() for n_id in self.nodes.keys()}

        for c in self.connections:
            if c.enabled:
                adj[c.in_node].append((c.out_node, c.weight))
                in_degrees[c.out_node] += 1

        queue = [n_id for n_id, deg in in_degrees.items() if deg == 0]

        while queue:
            current = queue.pop(0)
            node = self.nodes[current]

            if node.type != 'input':
                node_values[current] = self.sigmoid(node_values[current] + node.bias)

            for out_node, weight in adj[current]:
                node_values[out_node] += node_values[current] * weight
                in_degrees[out_node] -= 1
                if in_degrees[out_node] == 0:
                    queue.append(out_node)

        # Any node not reached due to disconnected topology or unresolved degrees stays at 0.0
        # For a truly strict feedforward pass, nodes are activated after all inputs are collected.

        outputs = np.zeros(self.num_outputs)
        for i in range(self.num_outputs):
            out_node_id = self.num_inputs + i
            outputs[i] = node_values[out_node_id]

        return outputs
