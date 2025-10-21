"""Initialization functions for complex-valued neural networks.

This module provides various initialization methods for complex-valued weights and biases,
including standard methods adapted for complex numbers and specialized initializers
for phase-based learning.
"""

from typing import Tuple, Union, List
import numpy as np
from numpy.typing import NDArray
import numpy.typing as npt

# Type alias for complex numpy arrays
ComplexArray = npt.NDArray[np.complex128]

# List of available initialization methods as strings
string_inits: List[str] = [
    "complex_zeros",
    "complex_ones",
    "complex_normal",
    "complex_glorot_uniform",
    "complex_he_normal",
    "complex_uniform",
    "complex_lecun_normal",
    "complex_lecun_uniform",
    "complex_rand_phase",
    "jamie",
    "jamie_bias",
    "zeros",
    "ones",
    "normal",
    "glorot_uniform",
    "he_normal"
]

def jamie(shape: Union[Tuple[int, ...], List[int]], real: bool = False) -> NDArray:
    """Special initialization for phase-based learning.

    Initializes weights with specific phases (π/4 or 5π/4) and carefully chosen moduli
    to optimize learning in phase-based architectures.

    Args:
        shape: Shape of the weight tensor to create

    Returns:
        Complex-valued array with controlled phases and moduli

    Example:
        >>> W = jamie((3, 2))
        >>> print(np.angle(W) / np.pi)  # Should be close to 0.25 or 1.25
    """
    if real:
        return np.random.normal(np.pi/np.sqrt(2), 0.2, size=shape)
    phases = np.random.choice([np.pi/4, 5*np.pi/4], size=shape)
    modulus = np.abs(np.random.normal(np.pi/np.sqrt(2), 0.2, size=shape))
    return modulus * np.exp(1j * phases)

def jamie_bias(shape: Union[Tuple[int, ...], List[int]], real: bool = False) -> NDArray:
    """Specialized bias initialization for phase-based learning.

    Creates purely imaginary biases to shift activation phases.

    Args:
        shape: Shape of the bias tensor to create

    Returns:
        Complex-valued array with purely imaginary values
    """
    if real:
        return np.abs(np.random.normal(np.pi/2, 0.2, size=shape))
    modulus = np.abs(np.random.normal(np.pi/2, 0.2, size=shape))
    return modulus * 1j  # Purely imaginary bias to shift phase activation

def complex_zeros(shape: Union[Tuple[int, ...], List[int]]) -> NDArray:
    """Initialize a complex tensor filled with zeros.

    Args:
        shape: Shape of the tensor to create

    Returns:
        Complex-valued array filled with zeros

    Example:
        >>> W = complex_zeros((2, 3))
        >>> np.allclose(W, 0)
        True
    """
    return np.zeros(shape, dtype=np.complex128)

def complex_ones(shape: Union[Tuple[int, ...], List[int]]) -> NDArray:
    """Initialize a complex tensor filled with ones.

    Args:
        shape: Shape of the tensor to create

    Returns:
        Complex-valued array filled with ones

    Example:
        >>> W = complex_ones((2, 3))
        >>> np.allclose(W, 1)
        True
    """
    return np.ones(shape, dtype=np.complex128)

def complex_normal(shape: Union[Tuple[int, ...], List[int]], 
                  mean: float = 0.0, std: float = 1.0) -> NDArray:
    """Initialize weights from a complex normal distribution.

    Both real and imaginary parts are drawn independently from
    normal distributions with the specified mean and standard deviation.

    Args:
        shape: Shape of the tensor to create
        mean: Mean of the normal distribution
        std: Standard deviation of the normal distribution

    Returns:
        Complex-valued array with normally distributed values

    Example:
        >>> W = complex_normal((1000, 1000))
        >>> np.abs(W.real.mean()) < 0.1  # Should be close to 0
        True
    """
    real = np.random.normal(mean, std, size=shape)
    imag = np.random.normal(mean, std, size=shape)
    return real + 1j * imag

def complex_glorot_uniform(shape: Union[Tuple[int, ...], List[int]]) -> NDArray:
    """Glorot/Xavier uniform initialization for complex weights.

    Draws samples from a uniform distribution within [-limit, limit] where
    limit = sqrt(6 / (fan_in + fan_out)).

    Args:
        shape: Shape of the tensor to create

    Returns:
        Complex-valued array with glorot uniform initialization

    Example:
        >>> W = complex_glorot_uniform((100, 200))
        >>> np.abs(W).mean() < 1.0  # Should be properly scaled
        True
    """
    limit = np.sqrt(6 / np.sum(shape))
    real = np.random.uniform(-limit, limit, size=shape)
    imag = np.random.uniform(-limit, limit, size=shape)
    return real + 1j * imag

def complex_he_normal(shape: Union[Tuple[int, ...], List[int]]) -> ComplexArray:
    """He/Kaiming normal initialization for complex weights.

    Draws samples from a normal distribution with std = sqrt(2/fan_in).

    Args:
        shape: Shape of the tensor to create

    Returns:
        Complex-valued array with He normal initialization

    Example:
        >>> W = complex_he_normal((100, 50))
        >>> np.abs(W).std() # Should be close to sqrt(2/100)
    """
    stddev = np.sqrt(2 / shape[0])
    real = np.random.normal(0, stddev, size=shape)
    imag = np.random.normal(0, stddev, size=shape)
    return real + 1j * imag

def zeros(shape: Union[Tuple[int, ...], List[int]]) -> NDArray:
    """Real-valued zeros initialisation."""
    return np.zeros(shape, dtype=np.float64)

def ones(shape: Union[Tuple[int, ...], List[int]]) -> NDArray:
    """Real-valued ones initialisation."""
    return np.ones(shape, dtype=np.float64)

def normal(shape: Union[Tuple[int, ...], List[int]], mean: float = 0.0, std: float = 1.0) -> NDArray:
    """Real-valued normal initialisation."""
    return np.random.normal(mean, std, size=shape)

def glorot_uniform(shape: Union[Tuple[int, ...], List[int]]) -> NDArray:
    """Real-valued Glorot/Xavier uniform initialisation."""
    limit = np.sqrt(6 / np.sum(shape))
    return np.random.uniform(-limit, limit, size=shape)

def he_normal(shape: Union[Tuple[int, ...], List[int]]) -> NDArray:
    """Real-valued He/Kaiming normal initialisation."""
    stddev = np.sqrt(2 / shape[0])
    return np.random.normal(0, stddev, size=shape)

def complex_uniform(shape: Union[Tuple[int, ...], List[int]], 
                   low: float = -1.0, high: float = 1.0) -> ComplexArray:
    """Initialize weights from a complex uniform distribution.

    Args:
        shape: Shape of the tensor to create
        low: Lower bound of the uniform distribution
        high: Upper bound of the uniform distribution

    Returns:
        Complex-valued array with uniformly distributed values
    """
    real = np.random.uniform(low, high, size=shape)
    imag = np.random.uniform(low, high, size=shape)
    return real + 1j * imag

def complex_lecun_normal(shape: Union[Tuple[int, ...], List[int]]) -> ComplexArray:
    """LeCun normal initialization for complex weights.

    Draws samples from a normal distribution with std = sqrt(1/fan_in).

    Args:
        shape: Shape of the tensor to create

    Returns:
        Complex-valued array with LeCun normal initialization
    """
    stddev = np.sqrt(1 / shape[0])
    real = np.random.normal(0, stddev, size=shape)
    imag = np.random.normal(0, stddev, size=shape)
    return real + 1j * imag

def complex_lecun_uniform(shape: Union[Tuple[int, ...], List[int]]) -> ComplexArray:
    """LeCun uniform initialization for complex weights.

    Draws samples from a uniform distribution within [-limit, limit]
    where limit = sqrt(3/fan_in).

    Args:
        shape: Shape of the tensor to create

    Returns:
        Complex-valued array with LeCun uniform initialization
    """
    limit = np.sqrt(3 / shape[0])
    real = np.random.uniform(-limit, limit, size=shape)
    imag = np.random.uniform(-limit, limit, size=shape)
    return real + 1j * imag

def complex_rand_phase(shape: Union[Tuple[int, ...], List[int]], 
                      modulus: float = 1.0) -> ComplexArray:
    """Initialize weights with random phases and fixed modulus.

    Args:
        shape: Shape of the tensor to create
        modulus: Fixed magnitude for all complex numbers

    Returns:
        Complex-valued array with random phases and fixed modulus
    """
    phases = np.random.uniform(0, 2 * np.pi, size=shape)
    return modulus * np.exp(1j * phases)