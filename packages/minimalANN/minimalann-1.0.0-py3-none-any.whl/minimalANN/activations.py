import numpy as np

class Activation:
	def __init__(self, mode):
		self.mode = mode
		
	def relu(self, x, derivative=False):
		if derivative:
			return np.where(x > 0, 1, 0)
		return np.maximum(0, x)
	def sigmoid(self, x, derivative=False):
		s = 1 / (1 + np.exp(-x))
		if derivative:
			return x * (1 - x)
		return s
	def tanh(self, x, derivative=False):
		if derivative:
			return 1 - x ** 2
		return np.tanh(x)
	def softmax(self, x, derivative=False):
		e_x = np.exp(x - np.max(x, axis=1, keepdims=True))
		s = e_x / np.sum(e_x, axis=1, keepdims=True)
		if derivative:
			return s * (1 - s)
		return s
	def linear(self, x, derivative=False):
		if derivative:
			return np.ones_like(x)
		return x

	def __call__(self, x, derivative=False):
		if self.mode == "relu":
			return self.relu(x, derivative)
		elif self.mode == "sigmoid":
			return self.sigmoid(x, derivative)
		elif self.mode == "tanh":
			return self.tanh(x, derivative)
		elif self.mode == "softmax":
			return self.softmax(x, derivative)
		elif self.mode == "linear":
			return self.linear(x, derivative)
		else:
			raise ValueError("Unsupported activation function")

# relu = Activation()
if __name__ == "__main__":
	activation = Activation("relu")
	X = np.array([-2, -1, 0, 1, 2])
	print(activation(X))
