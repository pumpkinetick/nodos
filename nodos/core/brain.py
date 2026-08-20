import numpy as np


class Brain:
    def __init__(self, layer_sizes: list[int]):
        self.layer_sizes = layer_sizes

        self.weights: list[np.ndarray] = list()
        self.biases: list[np.ndarray] = list()

        # Initialize weights and biases for each layer transition
        for i in range(len(layer_sizes) - 1):
            self.weights.append(np.random.randn(layer_sizes[i], layer_sizes[i+1]))
            self.biases.append(np.zeros(layer_sizes[i+1]))

    @staticmethod
    def sigmoid(x: float) -> float:
        # Clip to prevent overflow
        return 1 / (1 + np.exp(-np.clip(x, -50, 50)))

    def think(self, inputs: np.ndarray) -> np.ndarray:
        activation = inputs
        for w, b in zip(self.weights, self.biases):
            activation = self.sigmoid(np.dot(activation, w) + b)
        return activation
