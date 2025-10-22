import numpy as np
import layer
import backpropagation as bp

class NeuralNetwork:
    def __init__(self):
        self.layers:list[layer.Layer] = []
        self.learning_rate = 0.1
        self.sensitivities = {}
        self.n = {} # n values of each layer
        self.a = {} # a values of each layer
        self.weights = {}
        self.bias = {}
        self.error = 0

    def train(self, X, y, epochs):
        for _ in range(epochs):
            print(f"EPOCH : {_+1}\n\n\n")
            bp.forward(self, X, y)
            bp.calculate_sensitivities(self, X, y)
            bp.backprop(self, X, y)
        return self