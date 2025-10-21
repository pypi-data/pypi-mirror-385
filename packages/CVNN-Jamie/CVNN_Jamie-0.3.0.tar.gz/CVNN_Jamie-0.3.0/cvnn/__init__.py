"""Complex-Valued Neural Network (CVNN) Library

A Python library for building and training neural networks with complex-valued
weights, activations, and operations. Supports various initialization schemes,
activation functions, and training methods specifically designed for complex
domain learning.
"""

__version__ = "0.3.0"

from .layers import Dense
from .model import Sequential
from .activations import jam, jam_derivative
from .activations import complex_relu, complex_relu_backward
from .activations import complex_tanh, complex_tanh_backward
from .activations import complex_sigmoid, complex_sigmoid_backward

from .initialisations import jamie, jamie_bias
from .initialisations import complex_zeros, complex_ones, complex_normal
from .initialisations import complex_glorot_uniform, complex_he_normal

__all__ = [
    'Dense',
    'Sequential',
    'jam',
    'jam_derivative',
    'complex_relu',
    'complex_relu_backward',
    'complex_tanh',
    'complex_tanh_backward',
    'complex_sigmoid',
    'complex_sigmoid_backward',
    'jamie',
    'jamie_bias',
    'complex_zeros',
    'complex_ones',
    'complex_normal',
    'complex_glorot_uniform',
    'complex_he_normal',
]
