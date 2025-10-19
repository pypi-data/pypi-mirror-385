"""
Multi-dimensional tensor autograd engine.

Implements automatic differentiation for NumPy-backed tensors with support for
matrix operations (matmul, transpose, sum), broadcasting, activation functions
(tanh, ReLU, sigmoid, GELU), and backpropagation through computational graphs.

Adapted from Andrew Trask's Grokking Deep Learning:
> Chapter 13 - Introducing Automating Optimization
"""

import numpy as np

from scipy.special import erf

class Tensor:
    """Multi-dimensional array with automatic differentiation support."""

    def __init__(self, data, prev=(), op="", label=""):
        self.data = np.array(data, dtype=np.float64)
        self.prev = prev
        self.op = op
        self.label = label
        self.grad = np.zeros_like(self.data)
        self.grad_fn = lambda: None

    def __add__(self, other):
        output = Tensor(self.data + other.data, (self, other), '+')

        def grad_fn():
            self.grad += output.grad
            other.grad += output.grad

        output.grad_fn = grad_fn
        return output

    def __mul__(self, other):
        output = Tensor(self.data * other.data, (self, other), '*')

        def grad_fn():
            self.grad += other.data * output.grad
            other.grad += self.data * output.grad

        output.grad_fn = grad_fn
        return output

    def __pow__(self, other):
        output = Tensor(self.data ** other, (self,), f'**{other}')

        def grad_fn():
            self.grad += (other * self.data**(other - 1)) * output.grad

        output.grad_fn = grad_fn
        return output

    def __neg__(self):
        return self * Tensor(-np.ones_like(self.data))

    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        return self + (-other)

    def __rsub__(self, other):
        return other + (-self)

    def __rmul__(self, other):
        return self * other

    def __truediv__(self, other):
        return self * other**-1

    def __rtruediv__(self, other):
        return other * self**-1

    def relu(self):
        """Apply ReLU activation function."""
        output = Tensor((self.data > 0) * self.data, (self,), 'ReLU')

        def grad_fn():
            self.grad += (self.data > 0) * output.grad

        output.grad_fn = grad_fn
        return output

    def sigmoid(self):
        """Apply sigmoid activation function."""
        x = self.data
        s = 1 / (1 + np.exp(-x))
        output = Tensor(s, (self,), 'Sigmoid')

        def grad_fn():
            self.grad += s * (1 - s) * output.grad

        output.grad_fn = grad_fn
        return output

    def tanh(self):
        """Apply tanh activation function."""
        x = self.data
        t = (np.exp(2*x) - 1) / (np.exp(2*x) + 1)
        output = Tensor(t, (self,), 'Tanh')

        def grad_fn():
            self.grad += (1 - t**2) * output.grad

        output.grad_fn = grad_fn
        return output

    def gelu(self):
        """Apply GELU activation function."""
        x = self.data
        cdf = 0.5 * (1.0 + erf(x / np.sqrt(2.0)))
        pdf = np.exp(-x**2 / 2) / np.sqrt(2*np.pi)
        g = x * cdf
        output = Tensor(g, (self,), 'GELU')

        def grad_fn():
            self.grad += (cdf + x * pdf) * output.grad

        self.grad_fn = grad_fn
        return output

    def expand(self, dim, copies):
        """Expand tensor along specified dimension."""
        trans_cmd = list(range(0, len(self.data.shape)))
        trans_cmd.insert(dim, len(self.data.shape))
        new_data = self.data.repeat(copies)\
                            .reshape(list(self.data.shape) + [copies])\
                            .transpose(trans_cmd)
        output = Tensor(new_data, (self,), 'Expand_' + str(dim))

        def grad_fn():
            self.grad += output.grad.sum(dim)

        output.grad_fn = grad_fn
        return output

    def sum(self, dim):
        """Sum tensor along specified dimension."""
        output = Tensor(self.data.sum(dim), (self,), 'Sum_' + str(dim))

        def grad_fn():
            self.grad += Tensor(output.grad).expand(dim, self.data.shape[dim]).data

        output.grad_fn = grad_fn
        return output

    def transpose(self):
        """Transpose the tensor."""
        output = Tensor(self.data.transpose(), (self,), 'Transpose')

        def grad_fn():
            self.grad += output.grad.transpose()

        output.grad_fn = grad_fn
        return output

    def matmul(self, x):
        """Perform matrix multiplication with another tensor."""
        output = Tensor(self.data.dot(x.data), (self, x), 'MatMul')

        def grad_fn():
            self.grad += output.grad.dot(x.data.transpose())
            x.grad += self.data.transpose().dot(output.grad)

        output.grad_fn = grad_fn
        return output

    def __repr__(self):
        return str(self.data.__repr__())

    def __str__(self):
        return str(self.data.__str__())

    def backward(self):
        """Perform backpropagation to compute gradients."""
        topo = []
        seen = set()

        def topo_sort(root):
            if root not in seen:
                seen.add(root)
                for child in root.prev:
                    topo_sort(child)
                topo.append(root)

        topo_sort(self)

        self.grad = np.ones_like(self.data)
        for node in reversed(topo):
            node.grad_fn()
