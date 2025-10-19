# pylint: disable=duplicate-code
"""
Scalar autograd engine.

Implements automatic differentiation for scalar values with support for
basic arithmetic operations, activation functions (tanh, ReLU, sigmoid, GELU),
and computational graph visualization.

Adapted from Andrej Karpathy's micrograd:
https://github.com/karpathy/micrograd
https://www.youtube.com/watch?v=VMj-3S1tku0
"""

import math

from graphviz import Digraph

class Value:
    """Scalar value with automatic differentiation support."""

    def __init__(self, data, prev=(), op="", label=""):
        self.data = data
        self.prev = prev
        self.op = op
        self.label = label
        self.grad = 0.0
        self.grad_fn = lambda: None

    def __add__(self, other):
        other = other if isinstance(other, Value) else Value(other)
        output = Value(self.data + other.data, (self, other), '+')

        def grad_fn():
            self.grad += output.grad
            other.grad += output.grad

        output.grad_fn = grad_fn
        return output

    def __mul__(self, other):
        other = other if isinstance(other, Value) else Value(other)
        output = Value(self.data * other.data, (self, other), '*')

        def grad_fn():
            self.grad += other.data * output.grad
            other.grad += self.data * output.grad

        output.grad_fn = grad_fn
        return output

    def __pow__(self, other):
        assert isinstance(other, (int, float)), "Only supports int/float powers"
        output = Value(self.data ** other, (self,), f'**{other}')

        def grad_fn():
            self.grad += (other * self.data**(other - 1)) * output.grad

        output.grad_fn = grad_fn
        return output

    def __neg__(self):
        return self * -1

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
        output = Value(0 if self.data < 0 else self.data, (self,), 'ReLU')

        def grad_fn():
            self.grad += (self.data > 0) * output.grad

        output.grad_fn = grad_fn
        return output

    def sigmoid(self):
        """Apply sigmoid activation function."""
        x = self.data
        s = 1 / (1 + math.exp(-x))
        output = Value(s, (self,), 'Sigmoid')

        def grad_fn():
            self.grad += s * (1 - s) * output.grad

        output.grad_fn = grad_fn
        return output

    def tanh(self):
        """Apply tanh activation function."""
        x = self.data
        t = (math.exp(2*x) - 1) / (math.exp(2*x) + 1)
        output = Value(t, (self,), 'Tanh')

        def grad_fn():
            self.grad += (1 - t**2) * output.grad

        output.grad_fn = grad_fn
        return output

    def gelu(self):
        """Apply GELU activation function."""
        x = self.data
        cdf = 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))
        pdf = math.exp(-x**2 / 2) / math.sqrt(2*math.pi)
        g = x * cdf
        output = Value(g, (self,), 'GELU')

        def grad_fn():
            self.grad += (cdf + x * pdf) * output.grad

        self.grad_fn = grad_fn
        return output

    def __repr__(self):
        return f"Value(data={self.data}, grad={self.grad})"

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

        self.grad = 1.0
        for node in reversed(topo):
            node.grad_fn()

    def draw(self, fmt="ascii"):
        """Generate a graphical representation of the computational graph."""
        graph = Digraph(format=fmt, graph_attr={'rankdir': "LR"})

        def trace(root):
            nodes, edges = set(), set()
            def build(node):
                if node not in nodes:
                    nodes.add(node)
                    for child in node.prev:
                        edges.add((child, node))
                        build(child)
            build(root)
            return nodes, edges

        nodes, edges = trace(self)
        for node in nodes:
            uid = str(id(node))
            graph.node(
                name=uid,
                label="{ %s | data %.4f | grad %.4f }" \
                      % (node.label, node.data, node.grad),
                shape='record'
            )
            if node.op:
                graph.node(name=uid+node.op, label=node.op)
                graph.edge(uid+node.op, uid)

        for start, end in edges:
            start_uid = str(id(start))
            end_uid = str(id(end))
            graph.edge(start_uid, end_uid+end.op)

        return graph
