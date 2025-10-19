# Tardigrad

A small PyTorch-like autograd engine and neural network library.

> *"As far as we tardigrades are concerned, Pluto is and always will be a planet. End of discussion."*
>
> ― Zeno Alexander, The Library of Ever

<img src="https://github.com/JGalego/tardigrad/raw/main/tardigrad.png" width="50%"/>

## Features

- **Automatic differentiation** for scalar (`Value`) and tensor (`Tensor`) operations
- **Neural network layers** (`Linear`, `Sequential`)
- **SGD optimizer** with gradient zeroing
- **Lightweight** with minimal dependencies (NumPy, SciPy)

## Quick Start

### Scalar Autograd

```python
from tardigrad.value import Value

a = Value(2.0, label='a')
b = Value(3.0, label='b')
c = a * b + Value(1.0)

c.backward()

print(c.data)  # 7.0
print(a.grad)  # 3.0
print(b.grad)  # 2.0
```

### Tensor Operations

```python
from tardigrad.tensor import Tensor

x = Tensor([[1, 2], [3, 4]])
y = Tensor([[5, 6], [7, 8]])
z = x.matmul(y)

z.backward()

print(z.data)
print(x.grad)
```

### Neural Network

```python
from tardigrad.layers import Linear, Sequential
from tardigrad.tensor import Tensor
from tardigrad.optim import SGD

model = Sequential([
    Linear(2, 3),
    Linear(3, 1)
])

optimizer = SGD(model.get_params(), alpha=0.01)

# Training loop
for epoch in range(10):
    y_pred = model.forward(x_train)
    loss = ((y_pred - y_train) ** 2).sum()
    loss.backward()
    optimizer.step()
```

## Project Structure

```
tardigrad/
├── value.py     # Scalar autograd engine
├── tensor.py    # Multi-dimensional tensor autograd
├── layers.py    # Neural network layers (Linear, Sequential)
└── optim.py     # SGD optimizer
```

## References

- [micrograd](https://github.com/karpathy/micrograd) by Andrej Karpathy
- [Grokking Deep Learning](https://github.com/iamtrask/Grokking-Deep-Learning) by Andrew Trask
