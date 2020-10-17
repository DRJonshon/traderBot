import numpy as np
import os

class NeuralNetwork:

    def __init__(self, x, y):
        self.input      = x
        self.weights1   = np.random.rand(self.input,4)
        self.weights2   = np.random.rand(4,1)
        self.y          = y
        self.output     = np.zeros((1,self.y))

    def feedforward(self,input):
        self.layer1 = self.sigmoid(np.dot(input, self.weights1))[0]
        self.output = self.sigmoid(np.dot(self.layer1, self.weights2))[0]


    def backprop(self,input):
        t = 0
        for n,i in enumerate(input):
            t += n*i
        goal = np.array([i])
        print(self.layer1.T)
        # application of the chain rule to find derivative of the loss function with respect to weights2 and weights1
        d_weights2 = np.dot(self.layer1.T, (2*(goal - self.output) * self.sigmoid(self.output)[1]))
        d_weights1 = np.dot(self.input.T,  (np.dot(2*(goal - self.output) * self.sigmoid(self.output)[1], self.weights2.T) * self.sigmoid(self.layer1)[1]))

        # update the weights with the derivative (slope) of the loss function
        self.weights1 += d_weights1
        self.weights2 += d_weights2

    def sigmoid(self,x):
        s=1/(1+np.exp(-x))
        ds=s*(1-s)
        return s,ds

def main():
    NN = NeuralNetwork(10,1)
    array = np.array([0,0,0,0,0,0,0,0,0,1])
    on = True
    while on:
        try:
            NN.feedforward(array)
            NN.backprop(array)
            os.system('clear')
            print(NN.output)
        except KeyboardInterrupt:
            on = False


if __name__ == '__main__':
    main()
