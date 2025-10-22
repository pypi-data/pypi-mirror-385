import numpy as np
import network
import activations
import layer

def f_dot_matrix(nn:network.NeuralNetwork, m:int):
    '''
        n:int = no. of layer
    '''
    act_funct = activations.Activation(nn.layers[m].activation)
    layer_a = nn.a[m]
    # print(f"layer_a = {layer_a}")
    final_matrix = np.zeros((len(layer_a), len(layer_a)))
    for i in range(len(layer_a)):
        final_matrix[i][i] = act_funct(float(layer_a[i][0]), derivative=True)
    return final_matrix

def forward(nn:network.NeuralNetwork,X,y):
    nn.weights = {}
    nn.bias = {}
    nn.a = {}
    for i in range(len(nn.layers)):
        layer = nn.layers[i]
        activation = layer.activation
        print(f"layer[{i}] weights = {layer.weights}, shape = {layer.weights.shape}\n")
        print(f"layer[{i}] bias = {layer.bias}, shape = {layer.bias.shape}\n")
        n = layer.dot_product(X)
        nn.weights[i] = layer.weights
        nn.bias[i] = layer.bias
        a = activations.Activation(activation)(n)
        nn.a[i] = a
        print(f"layer[{i}] n = {n}, n.shape = {n.shape}")
        print(f"layer[{i}] a = {a}, a.shape = {a.shape}")
        print("-----")
        X = a
    print(nn.weights)
    nn.error = y-a
    print(f"error = {nn.error}, error.shape = {nn.error.shape}")

def calculate_sensitivities(nn:network.NeuralNetwork, X, y):
    nn.sensitivities = {}
    for i in reversed(range(len(nn.layers))):
        if i == len(nn.layers) - 1:
            act_funct = activations.Activation(nn.layers[i].activation)
            nn.sensitivities[i] = -2 * (y - nn.a[i]) * act_funct(nn.a[i], derivative=True)
        else:
            act_funct = activations.Activation(nn.layers[i].activation)
            f_dot = f_dot_matrix(nn, i)
            nn.sensitivities[i] = np.dot(f_dot, nn.weights[i + 1].T) * nn.sensitivities[i + 1]
        print(f"Sensitivity of layer {i}: {nn.sensitivities[i]}, shape: {nn.sensitivities[i].shape}")

def backprop(nn:network.NeuralNetwork, X, y):
    for i in reversed(range(len(nn.layers))):
        layer = nn.layers[i]
        sensitivity = nn.sensitivities[i]
        input_a = nn.a[i - 1] if i > 0 else None
        if input_a is not None:
            weights_gradient = np.dot(sensitivity, input_a.T)
        else:
            weights_gradient = np.dot(sensitivity, X.T)
        layer.weights -= nn.learning_rate * weights_gradient
        layer.bias -= nn.learning_rate * sensitivity
        print(f"Updated weights of layer {i}: {layer.weights}")
        print(f"Updated bias of layer {i}: {layer.bias}")
    print(f"\n\n\n Error = {nn.error}")
    print("\n\n\n--------------------\n\n\n")


if __name__ == "__main__":
    nn = network.NeuralNetwork()
    nn.layers.append(layer.Layer(1, 2,'sigmoid'))
    # nn.layers.append(layer.Layer(3, 5))
    nn.layers[0].weights = np.array([[-0.27], [-0.41]])
    nn.layers[0].bias = np.array([[-0.48], [-0.13]])

    nn.layers.append(layer.Layer(2, 1,'linear'))
    # nn.layers.append(layer.Layer(5, 2))
    nn.layers[1].weights = np.array([[0.09, -0.17]])
    nn.layers[1].bias = np.array([[0.48]])

    # X = np.array([[1], [2], [3]]) # Should be 3 x 1
    # y = np.array([[1], [0]]) # Should be 2 x 1

    X = np.array([[1]])
    y = np.array([1.707])

    forward(nn, X, y)
    print("\n\n-----\n\n")
    # print(f_dot_matrix(nn, 0))
    calculate_sensitivities(nn, X, y)
    print(nn.sensitivities)
    print("\n\n-----\n\n")
    backprop(nn, X, y)