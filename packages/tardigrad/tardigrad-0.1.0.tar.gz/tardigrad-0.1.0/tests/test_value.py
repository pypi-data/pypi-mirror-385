# pylint: disable=too-many-public-methods
"""
Test suite for Value class operations and gradients
"""

import math

import pytest

from tardigrad.value import Value

class TestValueOperations:
    """Test forward pass operations for Value"""

    def test_addition(self):
        """Test basic value addition."""
        a = Value(2.0)
        b = Value(3.0)
        c = a + b
        assert c.data == 5.0

    def test_addition_with_scalar(self):
        """Test value addition with scalar."""
        a = Value(2.0)
        c = a + 3
        assert c.data == 5.0

    def test_radd(self):
        """Test reverse addition (scalar + value)."""
        a = Value(2.0)
        c = 3 + a
        assert c.data == 5.0

    def test_multiplication(self):
        """Test basic value multiplication."""
        a = Value(2.0)
        b = Value(3.0)
        c = a * b
        assert c.data == 6.0

    def test_multiplication_with_scalar(self):
        """Test value multiplication with scalar."""
        a = Value(2.0)
        c = a * 3
        assert c.data == 6.0

    def test_rmul(self):
        """Test reverse multiplication (scalar * value)."""
        a = Value(2.0)
        c = 3 * a
        assert c.data == 6.0

    def test_power(self):
        """Test value power operation with integer exponent."""
        a = Value(2.0)
        c = a ** 3
        assert c.data == 8.0

    def test_power_float(self):
        """Test value power operation with float exponent."""
        a = Value(4.0)
        c = a ** 0.5
        assert abs(c.data - 2.0) < 1e-6

    def test_negation(self):
        """Test value negation operation."""
        a = Value(2.0)
        c = -a
        assert c.data == -2.0

    def test_subtraction(self):
        """Test basic value subtraction."""
        a = Value(5.0)
        b = Value(3.0)
        c = a - b
        assert c.data == 2.0

    def test_subtraction_with_scalar(self):
        """Test value subtraction with scalar."""
        a = Value(5.0)
        c = a - 3
        assert c.data == 2.0

    def test_rsub(self):
        """Test reverse subtraction (scalar - value)."""
        a = Value(3.0)
        c = 5 - a
        assert c.data == 2.0

    def test_division(self):
        """Test basic value division."""
        a = Value(6.0)
        b = Value(3.0)
        c = a / b
        assert abs(c.data - 2.0) < 1e-6

    def test_division_with_scalar(self):
        """Test value division with scalar."""
        a = Value(6.0)
        c = a / 3
        assert abs(c.data - 2.0) < 1e-6

    def test_rdiv(self):
        """Test reverse division (scalar / value)."""
        a = Value(3.0)
        c = 6 / a
        assert abs(c.data - 2.0) < 1e-6

    def test_relu_positive(self):
        """Test ReLU activation with positive value."""
        a = Value(2.0)
        c = a.relu()
        assert c.data == 2.0

    def test_relu_negative(self):
        """Test ReLU activation with negative value."""
        a = Value(-2.0)
        c = a.relu()
        assert c.data == 0.0

    def test_relu_zero(self):
        """Test ReLU activation with zero value."""
        a = Value(0.0)
        c = a.relu()
        assert c.data == 0.0

    def test_sigmoid(self):
        """Test sigmoid activation function."""
        a = Value(0.0)
        c = a.sigmoid()
        expected = 1 / (1 + math.exp(0))
        assert abs(c.data - expected) < 1e-6

    def test_tanh(self):
        """Test hyperbolic tangent activation function at zero."""
        a = Value(0.0)
        c = a.tanh()
        assert abs(c.data - 0.0) < 1e-6

    def test_tanh_positive(self):
        """Test hyperbolic tangent activation with positive value."""
        a = Value(1.0)
        c = a.tanh()
        expected = (math.exp(2.0) - 1) / (math.exp(2.0) + 1)
        assert abs(c.data - expected) < 1e-6

    def test_gelu(self):
        """Test GELU activation function."""
        a = Value(0.0)
        c = a.gelu()
        assert abs(c.data - 0.0) < 1e-6

    def test_complex_expression(self):
        """Test complex mathematical expression with multiple operations."""
        a = Value(2.0)
        b = Value(3.0)
        c = Value(-1.0)
        d = a * b + c
        assert d.data == 5.0


class TestValueGradients:
    """Test backward pass (gradients) for Value"""

    def test_addition_gradient(self):
        """Test gradient computation for value addition."""
        a = Value(2.0)
        b = Value(3.0)
        c = a + b
        c.backward()
        assert a.grad == 1.0
        assert b.grad == 1.0

    def test_multiplication_gradient(self):
        """Test gradient computation for value multiplication."""
        a = Value(2.0)
        b = Value(3.0)
        c = a * b
        c.backward()
        assert a.grad == 3.0
        assert b.grad == 2.0

    def test_power_gradient(self):
        """Test gradient computation for value power operation."""
        a = Value(2.0)
        c = a ** 3
        c.backward()
        # d/da (a^3) = 3*a^2 = 3*4 = 12
        assert abs(a.grad - 12.0) < 1e-6

    def test_negation_gradient(self):
        """Test gradient computation for value negation."""
        a = Value(2.0)
        c = -a
        c.backward()
        assert a.grad == -1.0

    def test_subtraction_gradient(self):
        """Test gradient computation for value subtraction."""
        a = Value(5.0)
        b = Value(3.0)
        c = a - b
        c.backward()
        assert a.grad == 1.0
        assert b.grad == -1.0

    def test_division_gradient(self):
        """Test gradient computation for value division."""
        a = Value(6.0)
        b = Value(3.0)
        c = a / b
        c.backward()
        # dc/da = 1/b = 1/3
        assert abs(a.grad - 1.0/3.0) < 1e-6
        # dc/db = -a/b^2 = -6/9 = -2/3
        assert abs(b.grad - (-2.0/3.0)) < 1e-6

    def test_relu_gradient_positive(self):
        """Test ReLU gradient with positive value."""
        a = Value(2.0)
        c = a.relu()
        c.backward()
        assert a.grad == 1.0

    def test_relu_gradient_negative(self):
        """Test ReLU gradient with negative value."""
        a = Value(-2.0)
        c = a.relu()
        c.backward()
        assert a.grad == 0.0

    def test_relu_gradient_zero(self):
        """Test ReLU gradient with zero value."""
        a = Value(0.0)
        c = a.relu()
        c.backward()
        assert a.grad == 0.0

    def test_sigmoid_gradient(self):
        """Test sigmoid gradient computation."""
        a = Value(0.0)
        c = a.sigmoid()
        c.backward()
        # sigmoid'(0) = sigmoid(0) * (1 - sigmoid(0)) = 0.5 * 0.5 = 0.25
        s = 1 / (1 + math.exp(0))
        expected_grad = s * (1 - s)
        assert abs(a.grad - expected_grad) < 1e-6

    def test_tanh_gradient(self):
        """Test tanh gradient computation at zero."""
        a = Value(0.0)
        c = a.tanh()
        c.backward()
        # tanh'(0) = 1 - tanh(0)^2 = 1 - 0 = 1
        assert abs(a.grad - 1.0) < 1e-6

    def test_tanh_gradient_nonzero(self):
        """Test tanh gradient computation at non-zero value."""
        a = Value(1.0)
        c = a.tanh()
        c.backward()
        t = (math.exp(2.0) - 1) / (math.exp(2.0) + 1)
        expected_grad = 1 - t**2
        assert abs(a.grad - expected_grad) < 1e-6

    def test_gelu_gradient(self):
        """Test GELU gradient computation at zero."""
        a = Value(0.0)
        c = a.gelu()
        c.backward()
        # gelu'(0) = cdf(0) + 0 * pdf(0) = 0.5
        assert abs(a.grad - 0.5) < 1e-6

    def test_chain_rule(self):
        """Test gradient computation using chain rule."""
        a = Value(2.0)
        b = Value(3.0)
        c = a * b  # c = 6
        d = c + a  # d = 8
        d.backward()
        # dd/da = dd/dc * dc/da + dd/da = 1 * 3 + 1 = 4
        assert abs(a.grad - 4.0) < 1e-6
        # dd/db = dd/dc * dc/db = 1 * 2 = 2
        assert abs(b.grad - 2.0) < 1e-6

    def test_multi_use_gradient(self):
        """Test gradient accumulation when value is used multiple times."""
        a = Value(2.0)
        b = a + a  # b = 4
        b.backward()
        # db/da = 1 + 1 = 2 (a is used twice)
        assert abs(a.grad - 2.0) < 1e-6

    def test_complex_gradient(self):
        """Test gradient computation in complex computational graph."""
        x = Value(-4.0)
        z = 2 * x + 2 + x
        q = z.relu() + z * x
        h = (z * z).relu()
        y = h + q + q * x
        y.backward()
        # This tests a complex computational graph
        # Just verify backward runs without error and grad is computed
        assert x.grad != 0.0

    def test_neuron_gradient(self):
        """Test gradient computation in simple neuron simulation."""
        # Simulate a simple neuron: y = (w*x + b).tanh()
        x = Value(1.0)
        w = Value(0.5)
        b = Value(0.3)
        y = (w * x + b).tanh()
        y.backward()

        # All gradients should be non-zero
        assert x.grad != 0.0
        assert w.grad != 0.0
        assert b.grad != 0.0

    def test_gradient_accumulation(self):
        """Test proper gradient accumulation across multiple paths."""
        a = Value(2.0)
        b = Value(3.0)

        # Use a in multiple operations
        c = a + b
        d = a * b
        e = c + d
        e.backward()

        # a.grad should be sum of gradients from both paths
        # de/da = de/dc * dc/da + de/dd * dd/da = 1*1 + 1*3 = 4
        assert abs(a.grad - 4.0) < 1e-6


class TestValueEdgeCases:
    """Test edge cases for Value"""

    def test_zero_multiplication(self):
        """Test multiplication with zero values."""
        a = Value(0.0)
        b = Value(5.0)
        c = a * b
        c.backward()
        assert a.grad == 5.0
        assert b.grad == 0.0

    def test_power_zero(self):
        """Test power operation with zero exponent."""
        a = Value(5.0)
        c = a ** 0
        assert c.data == 1.0
        c.backward()
        assert a.grad == 0.0

    def test_power_one(self):
        """Test power operation with exponent of one."""
        a = Value(5.0)
        c = a ** 1
        assert c.data == 5.0
        c.backward()
        assert a.grad == 1.0

    def test_large_values(self):
        """Test operations with large numerical values."""
        a = Value(1000.0)
        b = Value(2000.0)
        c = a + b
        assert c.data == 3000.0

    def test_small_values(self):
        """Test operations with very small numerical values."""
        a = Value(1e-10)
        b = Value(2e-10)
        c = a + b
        assert abs(c.data - 3e-10) < 1e-15

    def test_negative_power(self):
        """Test power operation with negative exponent."""
        a = Value(2.0)
        c = a ** -1
        assert abs(c.data - 0.5) < 1e-6


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
