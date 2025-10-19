"""
Neural network layer implementations.

Provides foundational building blocks for constructing neural networks:
- Layer: Base class for all layers
- Linear: Fully connected layer with weights and biases
- Sequential: Container for chaining multiple layers together
"""

import numpy as np

from tardigrad.tensor import Tensor

class Layer:  # pylint: disable=too-few-public-methods
    """Base class for neural network layers."""

    def __init__(self):
        self.params = []

    def get_params(self):
        """Return list of layer parameters."""
        return self.params


class Linear(Layer):
    """Fully connected linear layer."""

    def __init__(self, n_inputs, n_outputs):
        super().__init__()
        self.weights = Tensor(np.random.rand(n_inputs, n_outputs))
        self.biases = Tensor(np.zeros(n_outputs))
        self.params.append(self.weights)
        self.params.append(self.biases)

    def forward(self, inputs):
        """Forward pass through the linear layer."""
        return inputs.matmul(self.weights) + self.biases.expand(0, len(inputs.data))


class Sequential(Layer):
    """Container for sequentially applying multiple layers."""

    def __init__(self, layers):
        super().__init__()
        self.layers = layers

    def add(self, layer):
        """Add a layer to the sequence."""
        self.layers.append(layer)

    def forward(self, inputs):
        """Forward pass through all layers in sequence."""
        outputs = inputs
        for layer in self.layers:
            outputs = layer.forward(inputs)
            inputs = outputs
        return outputs

    def get_params(self):
        """Return all parameters from all layers."""
        params = []
        for layer in self.layers:
            params += layer.get_params()
        return params
