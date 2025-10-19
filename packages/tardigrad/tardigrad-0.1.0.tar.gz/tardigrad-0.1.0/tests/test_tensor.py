# pylint: disable=too-many-public-methods
"""
Test suite for Tensor class operations and gradients
"""

import numpy as np
import pytest

from tardigrad.tensor import Tensor


class TestTensorOperations:
    """Test forward pass operations for Tensor"""

    def test_initialization(self):
        """Test tensor initialization with 1D array."""
        t = Tensor([1.0, 2.0, 3.0])
        assert np.allclose(t.data, np.array([1.0, 2.0, 3.0]))
        assert np.allclose(t.grad, np.zeros(3))

    def test_initialization_2d(self):
        """Test tensor initialization with 2D array."""
        t = Tensor([[1.0, 2.0], [3.0, 4.0]])
        assert t.data.shape == (2, 2)
        assert np.allclose(t.data, np.array([[1.0, 2.0], [3.0, 4.0]]))

    def test_addition(self):
        """Test element-wise tensor addition."""
        a = Tensor([1.0, 2.0, 3.0])
        b = Tensor([4.0, 5.0, 6.0])
        c = a + b
        assert np.allclose(c.data, np.array([5.0, 7.0, 9.0]))

    def test_addition_2d(self):
        """Test element-wise tensor addition with 2D arrays."""
        a = Tensor([[1.0, 2.0], [3.0, 4.0]])
        b = Tensor([[5.0, 6.0], [7.0, 8.0]])
        c = a + b
        assert np.allclose(c.data, np.array([[6.0, 8.0], [10.0, 12.0]]))

    def test_multiplication(self):
        """Test element-wise tensor multiplication."""
        a = Tensor([1.0, 2.0, 3.0])
        b = Tensor([4.0, 5.0, 6.0])
        c = a * b
        assert np.allclose(c.data, np.array([4.0, 10.0, 18.0]))

    def test_multiplication_2d(self):
        """Test element-wise tensor multiplication with 2D arrays."""
        a = Tensor([[1.0, 2.0], [3.0, 4.0]])
        b = Tensor([[2.0, 2.0], [2.0, 2.0]])
        c = a * b
        assert np.allclose(c.data, np.array([[2.0, 4.0], [6.0, 8.0]]))

    def test_power(self):
        """Test tensor power operation with integer exponent."""
        a = Tensor([1.0, 2.0, 3.0])
        c = a ** 2
        assert np.allclose(c.data, np.array([1.0, 4.0, 9.0]))

    def test_power_float(self):
        """Test tensor power operation with float exponent."""
        a = Tensor([1.0, 4.0, 9.0])
        c = a ** 0.5
        assert np.allclose(c.data, np.array([1.0, 2.0, 3.0]))

    def test_negation(self):
        """Test tensor negation operation."""
        a = Tensor([1.0, 2.0, 3.0])
        c = -a
        assert np.allclose(c.data, np.array([-1.0, -2.0, -3.0]))

    def test_subtraction(self):
        """Test element-wise tensor subtraction."""
        a = Tensor([5.0, 7.0, 9.0])
        b = Tensor([1.0, 2.0, 3.0])
        c = a - b
        assert np.allclose(c.data, np.array([4.0, 5.0, 6.0]))

    def test_division(self):
        """Test element-wise tensor division."""
        a = Tensor([6.0, 8.0, 10.0])
        b = Tensor([2.0, 4.0, 5.0])
        c = a / b
        assert np.allclose(c.data, np.array([3.0, 2.0, 2.0]))

    def test_relu_positive(self):
        """Test ReLU activation with positive values."""
        a = Tensor([1.0, 2.0, 3.0])
        c = a.relu()
        assert np.allclose(c.data, np.array([1.0, 2.0, 3.0]))

    def test_relu_negative(self):
        """Test ReLU activation with negative values."""
        a = Tensor([-1.0, -2.0, -3.0])
        c = a.relu()
        assert np.allclose(c.data, np.array([0.0, 0.0, 0.0]))

    def test_relu_mixed(self):
        """Test ReLU activation with mixed positive, negative, and zero values."""
        a = Tensor([-1.0, 0.0, 1.0])
        c = a.relu()
        assert np.allclose(c.data, np.array([0.0, 0.0, 1.0]))

    def test_sigmoid(self):
        """Test sigmoid activation function."""
        a = Tensor([0.0, 1.0, -1.0])
        c = a.sigmoid()
        expected = 1 / (1 + np.exp(-a.data))
        assert np.allclose(c.data, expected)

    def test_tanh(self):
        """Test hyperbolic tangent activation function."""
        a = Tensor([0.0, 1.0, -1.0])
        c = a.tanh()
        expected = (np.exp(2*a.data) - 1) / (np.exp(2*a.data) + 1)
        assert np.allclose(c.data, expected)

    def test_gelu(self):
        """Test GELU activation function."""
        a = Tensor([0.0, 1.0, -1.0])
        c = a.gelu()
        # GELU should be approximately 0 at 0, positive for positive, negative for negative
        assert c.data[0] < 0.1  # Near zero
        assert c.data[1] > 0.0  # Positive
        assert c.data[2] < 0.0  # Negative

    def test_expand(self):
        """Test tensor expansion along specified axis."""
        a = Tensor([[1.0, 2.0], [3.0, 4.0]])
        b = a.expand(0, 3)
        assert b.data.shape == (3, 2, 2)
        # Each copy should be the same as the original
        for i in range(3):
            assert np.allclose(b.data[i], a.data)

    def test_sum(self):
        """Test tensor summation along axis 0."""
        a = Tensor([[1.0, 2.0], [3.0, 4.0]])
        b = a.sum(0)
        assert np.allclose(b.data, np.array([4.0, 6.0]))

    def test_sum_axis1(self):
        """Test tensor summation along axis 1."""
        a = Tensor([[1.0, 2.0], [3.0, 4.0]])
        b = a.sum(1)
        assert np.allclose(b.data, np.array([3.0, 7.0]))

    def test_transpose(self):
        """Test tensor transpose operation."""
        a = Tensor([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
        b = a.transpose()
        expected = np.array([[1.0, 4.0], [2.0, 5.0], [3.0, 6.0]])
        assert np.allclose(b.data, expected)

    def test_matmul(self):
        """Test tensor matrix multiplication."""
        a = Tensor([[1.0, 2.0], [3.0, 4.0]])
        b = Tensor([[5.0, 6.0], [7.0, 8.0]])
        c = a.matmul(b)
        expected = np.array([[19.0, 22.0], [43.0, 50.0]])
        assert np.allclose(c.data, expected)

    def test_matmul_vector(self):
        """Test matrix multiplication with vector (column matrix)."""
        a = Tensor([[1.0, 2.0], [3.0, 4.0]])
        b = Tensor([1.0, 2.0])
        c = a.matmul(b)
        expected = np.array([[5.0], [11.0]])
        assert np.allclose(c.data, expected)


class TestTensorGradients:
    """Test backward pass (gradients) for Tensor"""

    def test_addition_gradient(self):
        """Test gradient computation for tensor addition."""
        a = Tensor([1.0, 2.0, 3.0])
        b = Tensor([4.0, 5.0, 6.0])
        c = a + b
        c.backward()
        assert np.allclose(a.grad, np.ones(3))
        assert np.allclose(b.grad, np.ones(3))

    def test_multiplication_gradient(self):
        """Test gradient computation for tensor multiplication."""
        a = Tensor([2.0, 3.0])
        b = Tensor([4.0, 5.0])
        c = a * b
        c.backward()
        assert np.allclose(a.grad, b.data)
        assert np.allclose(b.grad, a.data)

    def test_power_gradient(self):
        """Test gradient computation for tensor power operation."""
        a = Tensor([2.0, 3.0])
        c = a ** 2
        c.backward()
        # d/da (a^2) = 2*a
        assert np.allclose(a.grad, 2 * a.data)

    def test_power_gradient_cube(self):
        """Test gradient computation for tensor cube operation."""
        a = Tensor([2.0, 3.0])
        c = a ** 3
        c.backward()
        # d/da (a^3) = 3*a^2
        assert np.allclose(a.grad, 3 * a.data**2)

    def test_negation_gradient(self):
        """Test gradient computation for tensor negation."""
        a = Tensor([1.0, 2.0, 3.0])
        c = -a
        c.backward()
        assert np.allclose(a.grad, -np.ones(3))

    def test_subtraction_gradient(self):
        """Test gradient computation for tensor subtraction."""
        a = Tensor([5.0, 7.0])
        b = Tensor([1.0, 2.0])
        c = a - b
        c.backward()
        assert np.allclose(a.grad, np.ones(2))
        assert np.allclose(b.grad, -np.ones(2))

    def test_division_gradient(self):
        """Test gradient computation for tensor division."""
        a = Tensor([6.0, 8.0])
        b = Tensor([2.0, 4.0])
        c = a / b
        c.backward()
        # dc/da = 1/b
        assert np.allclose(a.grad, 1.0 / b.data)
        # dc/db = -a/b^2
        assert np.allclose(b.grad, -a.data / (b.data**2))

    def test_relu_gradient_positive(self):
        """Test ReLU gradient computation with positive values."""
        a = Tensor([1.0, 2.0, 3.0])
        c = a.relu()
        c.backward()
        assert np.allclose(a.grad, np.ones(3))

    def test_relu_gradient_negative(self):
        """Test ReLU gradient computation with negative values."""
        a = Tensor([-1.0, -2.0, -3.0])
        c = a.relu()
        c.backward()
        assert np.allclose(a.grad, np.zeros(3))

    def test_relu_gradient_mixed(self):
        """Test ReLU gradient computation with mixed values."""
        a = Tensor([-1.0, 0.0, 1.0])
        c = a.relu()
        c.backward()
        assert np.allclose(a.grad, np.array([0.0, 0.0, 1.0]))

    def test_sigmoid_gradient(self):
        """Test sigmoid gradient computation."""
        a = Tensor([0.0])
        c = a.sigmoid()
        c.backward()
        s = 1 / (1 + np.exp(0))
        expected_grad = s * (1 - s)
        assert np.allclose(a.grad, expected_grad)

    def test_tanh_gradient(self):
        """Test tanh gradient computation at zero."""
        a = Tensor([0.0])
        c = a.tanh()
        c.backward()
        # tanh'(0) = 1 - tanh(0)^2 = 1
        assert np.allclose(a.grad, 1.0)

    def test_tanh_gradient_nonzero(self):
        """Test tanh gradient computation at non-zero value."""
        a = Tensor([1.0])
        c = a.tanh()
        c.backward()
        t = (np.exp(2.0) - 1) / (np.exp(2.0) + 1)
        expected_grad = 1 - t**2
        assert np.allclose(a.grad, expected_grad, atol=1e-6)

    def test_gelu_gradient(self):
        """Test GELU gradient computation at zero."""
        a = Tensor([0.0])
        c = a.gelu()
        c.backward()
        # gelu'(0) ≈ 0.5
        assert np.allclose(a.grad, 0.5, atol=1e-6)

    def test_sum_gradient(self):
        """Test gradient computation for tensor sum operation."""
        a = Tensor([[1.0, 2.0], [3.0, 4.0]])
        b = a.sum(0)
        b.backward()
        # Gradient should broadcast back
        assert a.grad.shape == a.data.shape
        assert np.allclose(a.grad, np.ones_like(a.data))

    def test_transpose_gradient(self):
        """Test gradient computation for tensor transpose operation."""
        a = Tensor([[1.0, 2.0], [3.0, 4.0]])
        b = a.transpose()
        b.backward()
        # Gradient should be transposed back
        assert np.allclose(a.grad, np.ones_like(a.data))

    def test_matmul_gradient(self):
        """Test gradient computation for matrix multiplication."""
        a = Tensor([[1.0, 2.0], [3.0, 4.0]])
        b = Tensor([[5.0, 6.0], [7.0, 8.0]])
        c = a.matmul(b)
        c.backward()

        # Check gradients have correct shapes
        assert a.grad.shape == a.data.shape
        assert b.grad.shape == b.data.shape

        # Verify gradients are non-zero
        assert not np.allclose(a.grad, np.zeros_like(a.data))
        assert not np.allclose(b.grad, np.zeros_like(b.data))

    def test_expand_gradient(self):
        """Test gradient computation for tensor expand operation."""
        a = Tensor([[1.0, 2.0], [3.0, 4.0]])
        b = a.expand(0, 3)
        b.backward()

        # Gradient should sum over the expanded dimension
        # Each element should receive gradient 3 times
        assert np.allclose(a.grad, 3 * np.ones_like(a.data))

    def test_chain_rule(self):
        """Test gradient computation using chain rule."""
        a = Tensor([2.0, 3.0])
        b = Tensor([4.0, 5.0])
        c = a * b  # [8, 15]
        d = c + a  # [10, 18]
        d.backward()

        # dd/da = dd/dc * dc/da + dd/da = 1 * b + 1
        expected_a_grad = b.data + np.ones_like(a.data)
        assert np.allclose(a.grad, expected_a_grad)

        # dd/db = dd/dc * dc/db = 1 * a
        assert np.allclose(b.grad, a.data)

    def test_multi_use_gradient(self):
        """Test gradient accumulation when tensor is used multiple times."""
        a = Tensor([2.0, 3.0])
        b = a + a  # b = [4, 6]
        b.backward()
        # db/da = 1 + 1 = 2 (a is used twice)
        assert np.allclose(a.grad, 2 * np.ones_like(a.data))

    def test_complex_gradient(self):
        """Test gradient computation in complex neural network computation."""
        # Simulate a simple neural network computation
        x = Tensor([[1.0, 2.0], [3.0, 4.0]])
        w = Tensor([[0.5, 0.3], [0.2, 0.4]])

        # Forward pass
        z = x.matmul(w)
        a = z.relu()

        # Backward pass
        a.backward()

        # Check gradients exist and have correct shapes
        assert x.grad.shape == x.data.shape
        assert w.grad.shape == w.data.shape
        assert not np.allclose(x.grad, np.zeros_like(x.data))
        assert not np.allclose(w.grad, np.zeros_like(w.data))


class TestTensorEdgeCases:
    """Test edge cases for Tensor"""

    def test_zero_multiplication(self):
        """Test multiplication with zero values."""
        a = Tensor([0.0, 0.0])
        b = Tensor([5.0, 10.0])
        c = a * b
        c.backward()
        assert np.allclose(a.grad, b.data)
        assert np.allclose(b.grad, a.data)

    def test_power_zero(self):
        """Test power operation with zero exponent."""
        a = Tensor([5.0, 10.0])
        c = a ** 0
        assert np.allclose(c.data, np.ones(2))
        c.backward()
        assert np.allclose(a.grad, np.zeros(2))

    def test_power_one(self):
        """Test power operation with exponent of one."""
        a = Tensor([5.0, 10.0])
        c = a ** 1
        assert np.allclose(c.data, a.data)
        c.backward()
        assert np.allclose(a.grad, np.ones(2))

    def test_large_values(self):
        """Test operations with large numerical values."""
        a = Tensor([1000.0, 2000.0])
        b = Tensor([3000.0, 4000.0])
        c = a + b
        assert np.allclose(c.data, np.array([4000.0, 6000.0]))

    def test_small_values(self):
        """Test operations with very small numerical values."""
        a = Tensor([1e-10, 2e-10])
        b = Tensor([3e-10, 4e-10])
        c = a + b
        assert np.allclose(c.data, np.array([4e-10, 6e-10]))

    def test_3d_tensor(self):
        """Test operations with 3D tensors."""
        a = Tensor([[[1.0, 2.0], [3.0, 4.0]], [[5.0, 6.0], [7.0, 8.0]]])
        b = Tensor([[[1.0, 1.0], [1.0, 1.0]], [[1.0, 1.0], [1.0, 1.0]]])
        c = a + b
        assert c.data.shape == (2, 2, 2)
        c.backward()
        assert a.grad.shape == a.data.shape

    def test_single_element(self):
        """Test operations with single-element tensors."""
        a = Tensor([5.0])
        b = Tensor([3.0])
        c = a * b
        c.backward()
        assert a.grad[0] == 3.0
        assert b.grad[0] == 5.0

    def test_negative_power(self):
        """Test power operation with negative exponent."""
        a = Tensor([2.0, 4.0])
        c = a ** -1
        assert np.allclose(c.data, np.array([0.5, 0.25]))

    def test_matmul_chain(self):
        """Test chained matrix multiplication operations."""
        a = Tensor([[1.0, 2.0]])
        b = Tensor([[3.0], [4.0]])
        c = Tensor([[2.0]])
        d = a.matmul(b).matmul(c)
        d.backward()

        assert a.grad.shape == a.data.shape
        assert b.grad.shape == b.data.shape
        assert c.grad.shape == c.data.shape


class TestTensorIntegration:
    """Integration tests combining multiple operations"""

    def test_simple_mlp_forward(self):
        """Test simple multi-layer perceptron forward and backward pass."""
        # Input
        x = Tensor([[1.0, 2.0]])

        # Layer 1
        w1 = Tensor([[0.5, 0.3, 0.2], [0.1, 0.4, 0.6]])
        b1 = Tensor([[0.1, 0.2, 0.3]])
        h1 = (x.matmul(w1) + b1).relu()

        # Layer 2
        w2 = Tensor([[0.7], [0.8], [0.9]])
        b2 = Tensor([[0.5]])
        out = h1.matmul(w2) + b2

        # Backward
        out.backward()

        # All tensors should have gradients
        assert not np.allclose(x.grad, np.zeros_like(x.data))
        assert not np.allclose(w1.grad, np.zeros_like(w1.data))
        assert not np.allclose(b1.grad, np.zeros_like(b1.data))
        assert not np.allclose(w2.grad, np.zeros_like(w2.data))
        assert not np.allclose(b2.grad, np.zeros_like(b2.data))

    def test_batch_processing(self):
        """Test batch processing with multiple samples."""
        # Batch of 3 samples, 2 features each
        x = Tensor([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])
        w = Tensor([[0.5, 0.3], [0.2, 0.4]])

        out = x.matmul(w)
        out.backward()

        assert x.grad.shape == (3, 2)
        assert w.grad.shape == (2, 2)

    def test_activation_functions_composition(self):
        """Test composing different activation functions."""
        x = Tensor([[-1.0, 0.0, 1.0]])

        # Try different activations
        relu_out = x.relu()
        tanh_out = x.tanh()
        sigmoid_out = x.sigmoid()

        relu_out.backward()
        x.grad = np.zeros_like(x.data)  # Reset gradient

        tanh_out.backward()
        x.grad = np.zeros_like(x.data)  # Reset gradient

        sigmoid_out.backward()

        # All should work without errors
        assert relu_out.data.shape == x.data.shape
        assert tanh_out.data.shape == x.data.shape
        assert sigmoid_out.data.shape == x.data.shape


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
