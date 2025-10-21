from typing import Callable, List, Tuple, Union, Optional
import numpy as np
from numpy.typing import NDArray
from . import initialisations, activations

ActivationType = Callable[[NDArray], NDArray]
ActivationWithDerivative = Tuple[ActivationType, Callable[[NDArray, NDArray], NDArray]]
LayerType = Union['ComplexDense', ActivationType, ActivationWithDerivative]

class Dense:
    """A fully connected neural network layer (real or complex).

    This layer implements a dense (fully connected) operation:
    output = input @ weights + bias

    Args:
        input_dim: Number of input features
        output_dim: Number of output features
        weight_init: Weight initialization function
        bias_init: Bias initialization function
        real: If True, use real-valued weights and math. If False, use complex-valued.

    Attributes:
        input_dim: Dimension of input features
        output_dim: Dimension of output features
        W: Weight matrix of shape (input_dim, output_dim)
        b: Bias vector of shape (1, output_dim)
        x_cache: Cached input for backpropagation

    Example:
        >>> layer = Dense(input_dim=2, output_dim=3, real=True)
        >>> x = np.array([[1, 2]])
        >>> output = layer.forward(x)
    """
    def __init__(self, input_dim: int, output_dim: int, 
                 weight_init: Optional[Callable[[Tuple[int, ...]], NDArray]] = None,
                 bias_init: Optional[Callable[[Tuple[int, ...]], NDArray]] = None,
                 real: bool = False, complex: bool = True):
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.real = real if not complex else False
        self.complex = complex

        def resolve_init(init, shape):
            if init is None:
                if self.real:
                    return np.random.randn(*shape)
                else:
                    return np.random.randn(*shape) + 1j * np.random.randn(*shape)
            if isinstance(init, str):
                # Try to get from initialisations module
                if hasattr(initialisations, init):
                    fn = getattr(initialisations, init)
                    try:
                        return fn(shape, real=self.real)
                    except TypeError:
                        return fn(shape)
                else:
                    raise ValueError(f"Unknown initialisation method: {init}")
            if callable(init):
                try:
                    return init(shape, real=self.real)
                except TypeError:
                    return init(shape)
            raise ValueError("weight_init and bias_init must be a callable or string name of an initialisation method.")

        self.W = resolve_init(weight_init, (input_dim, output_dim))
        self.b = resolve_init(bias_init, (1, output_dim))
        self.x_cache = None

    def forward(self, x: NDArray) -> NDArray:
        """Forward pass computation.

        Args:
            x: Input tensor of shape (batch_size, input_dim)

        Returns:
            Output tensor of shape (batch_size, output_dim)
        """
        self.x_cache = x
        return x @ self.W + self.b

    def backward(self, grad_output: NDArray, lr: float = 0.01) -> NDArray:
        """Backward pass computation.

        Computes gradients and updates weights using gradient descent.

        Args:
            grad_output: Gradient of the loss with respect to layer output
            lr: Learning rate for gradient descent

        Returns:
            Gradient with respect to layer input
        """
        x = self.x_cache
        if self.real:
            dW = x.T @ grad_output
            db = np.sum(grad_output, axis=0, keepdims=True)
            dx = grad_output @ self.W.T
        else:
            dW = x.conj().T @ grad_output
            db = np.sum(grad_output, axis=0, keepdims=True)
            dx = grad_output @ self.W.conj().T
        # Update weights and biases
        self.W -= lr * dW
        self.b -= lr * db
        return dx

class Sequential:
    """A sequential container for layers in a neural network (real or complex).

    This container allows you to stack layers and activations in sequence.
    Supports automatic differentiation and backpropagation training.

    Args:
        layers: List of layers and activation functions to stack.
        real: If True, use real-valued math throughout. If False, use complex-valued.

    Example:
        >>> model = Sequential([
        ...     Dense(input_dim=2, output_dim=3, real=True),
        ...     np.tanh,
        ...     Dense(input_dim=3, output_dim=1, real=True),
        ...     np.tanh
        ... ], real=True)
    """
    def __init__(self, layers: List[LayerType], real: bool = False):
        self.layers: List[LayerType] = []
        self.real = real
        for l in layers:
            # Allow string activations
            if isinstance(l, str) and hasattr(activations, l):
                act = getattr(activations, l)
                self.layers.append((act, getattr(activations, l + "_deriv", None)))
            elif isinstance(l, tuple) and len(l) == 2:
                self.layers.append(l)
            else:
                self.layers.append(l)

    def forward(self, x):
        self.cache = []
        for l in self.layers:
            if hasattr(l, "forward"):
                x = l.forward(x)
                self.cache.append(("layer", l, None))
            elif isinstance(l, tuple) and callable(l[0]):
                # Cache the PRE-activation value for the derivative
                pre_activation = x.copy()
                x = l[0](x)
                self.cache.append(("activation", l, pre_activation))
            else:
                raise ValueError("Unknown layer/activation type")
        return x

    def backward(self, grad, lr=0.01):
        for kind, l, cached_value in reversed(self.cache):
            if kind == "activation":
                # l is (activation, derivative)
                if l[1] is not None:
                    # Use the cached PRE-activation value
                    grad = l[1](cached_value, grad)
                else:
                    raise ValueError("Activation missing derivative")
            else:
                grad = l.backward(grad, lr=lr)

    def fit(self, x: NDArray, y: NDArray, epochs: int = 1000, 
             lr: float = 0.01, verbose: bool = False) -> List[float]:
        """Train the model on the given data.

        Args:
            x: Input training data of shape (n_samples, input_dim)
            y: Target values of shape (n_samples, output_dim)
            epochs: Number of training epochs
            lr: Learning rate for gradient descent
            verbose: Whether to print training progress

        Returns:
            List of loss values for each epoch

        Example:
            >>> model = Sequential([ComplexDense(2, 1), (complex_sigmoid, complex_sigmoid_backward)])
            >>> x_train = np.array([[1+1j, 2+2j], [3+3j, 4+4j]])
            >>> y_train = np.array([[1], [0]])
            >>> history = model.fit(x_train, y_train, epochs=100, lr=0.01)
        """
        losses = []
        for epoch in range(epochs):
            out = self.forward(x)
            loss = np.mean(np.abs(out - y) ** 2)  # MSE loss
            grad = 2 * (out - y) / y.shape[0]  # MSE gradient
            self.backward(grad, lr=lr)
            losses.append(float(loss))
            if verbose and (epoch % (epochs // 10) == 0 or epoch == epochs - 1):
                print(f"Epoch {epoch+1}/{epochs}, Loss: {loss:.4f}")
        return losses
