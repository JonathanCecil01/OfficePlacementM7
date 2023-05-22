#Hardcoded single layer neural network

import numpy as np 
import math
import csv
from copy import deepcopy

def read_data():
    landmarks = []
    with open('Active_Landmarks.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            landmarks.append(row)
    file.close()
    for landmark in landmarks:
        landmark[1] = float(landmark[1])
        landmark[2] = float(landmark[2])
    start = landmarks[0][2]
    products = []


    with open('Products.csv', 'r') as file1:
        reader = csv.reader(file1)
        for row in reader:
            products.append(row) 
    for product in products:
        product[1] = float(product[1])
        product[2] = float(product[2])
    
    return [products, landmarks]




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
        self.xav_initialize_weight()
        for i in range(0, len(inputs)-10):
            self.back_propogation(np.array(inputs[i]), np.array(outputs[i]))

        prediction = self.feed_forward(inputs[0])
        prediction.shape = (self.output_node_count, )
        prediction = [round(x, 4) for x in prediction]
        print(prediction)
        predictions = []
        for i in inputs:
            predictions.append(self.feed_forward(i))
        return predictions
        



# NN = NeuralNetwork(8, 8, 16, 0.05)
# NN.xav_initialize_weight()
# inputs = np.array([[0, 0, 0], [0, 0, 1], [0, 1, 0], [0, 1, 1], [1, 0, 0], [1, 0, 1]])
# outputs = np.array([[0, 0, 0, 0, 0], [0, 0, 0, 0, 1],[0, 0, 0, 1, 0], [0, 0, 1, 0, 0],[0, 1, 0, 0, 0],[1, 0, 0, 0, 0]])
# NN.train(inputs, outputs)
data = read_data()
products = data[0]
landmarks = data[1]
time_stamp_ordered = {}

for row in landmarks:
    time_stamp_ordered[row[2]] = [{},[],[]]
for key in time_stamp_ordered.keys():
    for row in landmarks:
        time_stamp_ordered[key][0][row[0]] = -91
for row in landmarks:
    if time_stamp_ordered[row[2]][0][row[0]]<row[1]:
        time_stamp_ordered[row[2]][0][row[0]] = row[1]

for row in products:
    time_stamp_ordered[row[2]][1].append([row[0], row[1],int(row[3][-1])])
    #time_stamp_ordered[row[2]][2].append(int(row[3][-1]))

NN = NeuralNetwork(9, 8, 16, 0.05)
sets = len(time_stamp_ordered)
inputs = []
outputs = []

for i in range(sets):
    temp = list(time_stamp_ordered[i][0].values())
    for j in time_stamp_ordered[i][1]:
        temp1 = deepcopy(temp)
        temp1.append(j[1])
        inputs.append(temp1)

for i in range(sets):
    for j in time_stamp_ordered[i][1]:
        output = [0]*8
        output[j[2]]= 1
        temp = deepcopy(output)
        outputs.append(temp)

print(inputs[0])
print(outputs[0])
predictions = NN.train(inputs, outputs)
#NN.train()