import numpy as np 
import math

def sigmoid(x):
    return 1/(1+np.exp(-x))

def der_sigmoid(x):
    return sigmoid(x)/(1-sigmoid(x))
class NeuralNetwork:
    
    def __init__(self, input, output, hidden, learning_rate):
        self.input_node_count = input
        self.output_node_count = output
        self.hidden_node_count = hidden
        self.learning_rate = learning_rate
        self.weights1 = []
        self.weights2 = []
        self.bias = 0.1

    def xav_initialize_weight(self):
        stdev1 = np.sqrt(2 / (self.input_node_count + self.hidden_node_count))
        self.weights1 = np.random.normal(loc=0, scale=stdev1, size=(self.input_node_count, self.hidden_node_count))
        stdev2 = np.sqrt(2 / (self.hidden_node_count + self.output_node_count))
        self.weights2 = np.random.normal(loc=0, scale=stdev2, size=(self.hidden_node_count, self.output_node_count))
        #print(self.weights2.shape)
        
        
    
    def feed_forward(self, input_vector):
        self.z = np.dot(input_vector, self.weights1) #dot product of X (input) and first set of weights (3x2)
        self.z2 = sigmoid(self.z) #activation function
        self.z2.shape = (1, self.hidden_node_count)
        self.z3 = np.dot(self.z2, self.weights2) #dot product of hidden layer (z2) and second set of weights (3x1)
        output = sigmoid(self.z3)
        output.shape = (1, self.output_node_count)
        return output

    def back_propogation(self, data, target_vector):
        output = self.feed_forward(data)
        self.output_error = target_vector - output # error in output
        self.output_delta = self.output_error * der_sigmoid(output)
        self.output_delta.shape = (1, self.output_node_count)
        self.z2_error = self.output_delta.dot(self.weights2.T) #z2 error: how much our hidden layer weights contribute to output error
        self.z2_delta = self.z2_error * der_sigmoid(self.z2) #applying derivative of sigmoid to z2 error
        data.shape = (1, self.input_node_count)
        self.z2_delta.shape = (1, self.hidden_node_count)
        self.weights1 += self.learning_rate*data.T.dot(self.z2_delta) # adjusting first set (input -> hidden) weights
        self.weights2 += self.learning_rate*self.z2.T.dot(self.output_delta) # adjusting second set (hidden -> output) weights
        
        
            
    def train(self, inputs, outputs):
        for epochs in range(10000):
            for i in range(0, 6):
                self.back_propogation(inputs[i], outputs[i])

        predictions = self.feed_forward(inputs[5])
        predictions.shape = (self.output_node_count, )
        for prediction in predictions:
            print(format(prediction, 'f'))


NN = NeuralNetwork(3, 5, 3, 0.05)
NN.xav_initialize_weight()
inputs = np.array([[0, 0, 0], [0, 0, 1], [0, 1, 0], [0, 1, 1], [1, 0, 0], [1, 0, 1]])
outputs = np.array([[0, 0, 0, 0, 0], [0, 0, 0, 0, 1],[0, 0, 0, 1, 0], [0, 0, 1, 0, 0],[0, 1, 0, 0, 0],[1, 0, 0, 0, 0]])
NN.train(inputs, outputs)