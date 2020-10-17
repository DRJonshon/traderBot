# -*- coding: UTF-8 -*-
import json, random, os
import numpy as np

state = "None"
best = 0
n = 0

class Individu():
	def __init__(self):
		self.inputSize = 3
		self.hiddenSize = 5
		self.outputSize = 1

		self.W1 = np.random.randn(self.inputSize, self.hiddenSize)
		self.W2 = np.random.randn(self.hiddenSize, self.outputSize)

	def forward(self, X):
		self.z = np.dot(X,self.W1)
		self.z2 = self.sigmoid(self.z)
		self.z3 = np.dot(self.z2,self.W2)
		o = self.sigmoid(self.z3)
		return o

	def sigmoid(self,x):
		return 1/(1+np.exp(-x))

def createPop(n):
    pop = []
    for i in range(n):
        pop.append(Individu())
    return pop

def testIndividu(I, *args):
    score = 0
    b = 0
    s = 0
    for i in range(1,3):
        if len(args) >0:
            print("-------------------------------------------------------------")
        with open('../data/'+str(i)+'.json','r') as fp:
            obj = json.load(fp)
        ETH = 0.0269541
        BTC = ETH*obj[0]['open']

        for i,candle in enumerate(obj):
            try:
                    hour = candle["close"] - obj[i-11]["open"]
            except IndexError:
                    hour = 0
            try:
                    half = candle["close"] - obj[i-5]["open"]
            except IndexError:
                    half = 0
            try:
                    ten = candle["close"] - obj[i-1]["open"]
            except IndexError:
                    ten = 0
            indicateurs = np.array([hour*100000,half*100000,ten*100000])
            o = I.forward(indicateurs)[0]*100 - 50
            if len(args) > 0:
                print(indicateurs)
                print(o)
            if o < -5 and abs(ETH*o/100*candle["close"]) > 0.0001:
                ETH += ETH*o/100
                BTC -= ETH*o/100*candle["close"]
                s += 1
            elif o > 5 and BTC*o/100 > 0.0001:
                ETH += BTC*o/100/candle["close"]
                BTC -= BTC*o/100
                b+=1
        score+=(ETH + BTC/obj[-1]["close"]/0.0539083)
    if s==0 and b==0:
        print("canceled")
        score = 0

    return score/3

def display():
    os.system("clear")
    print("gen n°"+str(n)+"  -  best score: "+str(round(best*100,2))+"%")
    print(state)

def classerPop(pop):
    global state
    state = "[+]Classement de la pop..."
    scores = list()
    for x,ind in enumerate(pop):
        score = testIndividu(ind)
        scores.append(score)
        state = "[*]Test de l'individu "+str(x)
        display()
    pop = [x for _, x in sorted(zip(scores,pop), key=lambda pair: pair[0])]
    pop.reverse()
    return pop

def reproduce(a,b):
    c = Individu()
    for x in range(c.W1.shape[0]):
        for y in range(c.W1.shape[1]):
                if random.random() >= .5:
                    c.W1[x][y] = a.W1[x][y]
                else:
                    c.W1[x][y] = b.W1[x][y]
    for x in range(c.W2.shape[0]):
        for y in range(c.W2.shape[1]):
                if random.random() >= .5:
                    c.W2[x][y] = a.W2[x][y]
                else:
                    c.W2[x][y] = b.W2[x][y]
    return c

def reproduce_pop(pop):
    global state
    state = "[+]reproduction forcée..."
    display()
    children = list()
    for ind in pop:
        for ind1 in pop:
            if ind != ind1:
                children.append(reproduce(ind,ind1))
            else:
                children.append(Individu())
    return children

def mutate(ind):
    for x in range(ind.W1.shape[0]):
        for y in range(ind.W1.shape[1]):
            if random.random() <= 0.01:
                ind.W1[x][y] = random.randint(0,200)/100-1
    for x in range(ind.W2.shape[0]):
        for y in range(ind.W2.shape[1]):
            if random.random() <= 0.01:
                ind.W2[x][y] = random.randint(0,200)/100-1
    return ind

def mutate_pop(pop):
    global state
    state = "[+]douche de rayons gamma..."
    display()
    for ind in pop:
        ind = mutate(ind)
    return pop

def cycle(pop):
    global state
    state = "[+]extermination des faibles..."
    chanceux = (pop[random.randint(11,99)],pop[random.randint(11,99)])
    for i in range(92):
        pop.pop()
    for c in chanceux:
        pop.append(c)
    pop = reproduce_pop(pop)

    pop = mutate_pop(pop)

    pop = classerPop(pop)
    return pop

def saveIndividu(i):
        file = str(best)
        np.save(file,np.array([i.W1,i.W2]))

if __name__ == "__main__":
    pop = createPop(100)
    try:
        b = 0
        while b <= 1.5:
            b = testIndividu(pop[0],"glbskf")
            pop = cycle(pop)
            best=b
            n += 1
    except KeyboardInterrupt:
        pass
    saveIndividu(pop[0])
