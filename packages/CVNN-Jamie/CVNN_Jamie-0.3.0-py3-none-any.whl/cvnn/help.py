# CVNN_Jamie Help Module
def show():
		"""
		Print a guide on how to use CVNN_Jamie, including model creation, layers, activations, initializations, and main methods.
		"""
		print("""
CVNN_Jamie: Complex-Valued Neural Network Framework
==================================================

How to Build a Model:
---------------------
from cvnn import Sequential
from cvnn.layers import Dense
from cvnn.activations import complex_relu, complex_tanh


## Example: 2-layer complex model (default)
model = Sequential([
	Dense(input_dim=4, output_dim=8),
	complex_relu,
	Dense(input_dim=8, output_dim=2),
	complex_tanh
])

## Example: 2-layer real model
model_real = Sequential([
	Dense(input_dim=4, output_dim=8, real=True),
	(lambda x: complex_relu(x, real=True), lambda z, g: complex_relu_backward(z, g, real=True)),
	Dense(input_dim=8, output_dim=2, real=True),
	(lambda x: complex_tanh(x, real=True), lambda z, g: complex_tanh_backward(z, g, real=True))
], complex=False)

# Forward pass
import numpy as np
x = np.random.randn(1, 4) + 1j * np.random.randn(1, 4)
out = model.forward(x)
print(out)

# Training
y = np.random.randn(1, 2) + 1j * np.random.randn(1, 2)
model.fit(x, y, epochs=100, lr=0.01)

Layers:
-------
- Dense(input_dim, output_dim, weight_init=..., bias_init=..., real=False)

Activations:
------------
- complex_relu, complex_sigmoid, complex_tanh, modrelu, jam
	(all support complex or real numbers; pass real=True for real-valued)

Initialisation Methods:
----------------------
- complex_zeros, complex_ones, complex_normal, complex_glorot_uniform, complex_he_normal, jamie
	(see cvnn.initialisations)

Main Model Methods:
-------------------
- model.forward(x): Forward pass
- model.fit(x, y, epochs, lr): Train model
- model.predict(x): Predict output
- model.loss_history: List of loss values per epoch
- model.weights_history: List of weights per epoch (if tracked)

Custom Activations/Derivatives:
------------------------------
You can pass (activation, derivative) tuples in the Sequential list for custom output layer behavior.

For more, see the README or source code.
		""")
