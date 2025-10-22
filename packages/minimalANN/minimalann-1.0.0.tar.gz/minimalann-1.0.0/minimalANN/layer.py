import numpy as np

class Layer:
    def __init__(self, input_size:int, output_size:int, activation:str, seed:int = 42):
        '''
            seed:int = 42 for initialising weights randomly
        '''
        np.random.seed(seed)
        self.weights:np.ndarray = np.random.randn(output_size, input_size)
        self.bias = np.random.randn(output_size, 1)
        self.input = None
        self.output = None
        self.activation = activation

    def dot_product(self, input_data):
        assert input_data.shape[0] == self.weights.shape[1], "Input shape is wrong!"
        self.input = input_data
        self.output = np.dot(self.weights, input_data) + self.bias
        return self.output