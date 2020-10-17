import numpy as np
import random, os, time, datetime
from poloniex import Poloniex

on = True
t = 0
history = []
polo = Poloniex('UUOLEZEG-YGAIX5UX-QMOO53NK-I6DMOO89','4fd2e22b010bfaaf7a8e75b92f5227451f2e47f52a2fa118d30b5c2ad367fe821dc0a3772dd44fae67e91a512acfbf0242e395f1ebdd9a6777e6f54352a92a72')
start_price=polo.returnTicker()['BTC_ETH']["last"]
ETH = 0.0269541
BTC = ETH * start_price
BTC0 = BTC
class IA():
	def __init__(self,file):
		weights = np.load(file,allow_pickle=True,encoding='latin1')
		self.W1 = weights[0]
		self.W2 = weights[1]

	def forward(self, X):
		self.z = np.dot(X,self.W1)
		self.z2 = self.sigmoid(self.z)
		self.z3 = np.dot(self.z2,self.W2)
		o = self.sigmoid(self.z3)
		return o

	def sigmoid(self,x):
		return 1/(1+np.exp(-x))
def choose():
	brains = []
	for file in os.listdir("./"):
		if ".npy" in file:
			brains.append(float(file.split(".npy")[0]))
	brains.sort()
	bot = IA(str(brains[0])+".npy")
	return bot

def init():
	global history
	i = 1
	while i != 0:
		t = time.time()
		data = polo.returnChartData("BTC_ETH",300,t-3600,t)
		history = []
		for candle in data:
			history.insert(0,candle["open"])
		i = (t-data[len(data)-1]["date"])*(len(history)!=12)
		os.system("clear")
		print("loading: "+str(round(i/3,2))+"%")


def loop(bot):
	global t
	global ETH
	global BTC
	t1 = time.time()
	if t1 - t < 300:
		return -1
	t=t1
	internet = 0 
	for i in range(3):
		try:
			history.insert(0,polo.returnTicker()['BTC_ETH']['last'])
			internet = 1
			break
		except:
			continue
	if not internet: history.insert(0,history[0])
	if len(history) > 12:
		history.pop()
	elif len(history) < 12:
		return -1
	hour = history[0]-history[11]
	half = history[0]-history[5]
	ten = history[0]-history[1] 
	indicateurs = np.array([hour*100000,half*100000,ten*100000])
	o = bot.forward(indicateurs)[0]*100 - 50
	if o < -5 and ETH*o/100*history[0] > 0.0001:
	    ETH += ETH*o/100
	    BTC -= ETH*o/100*history[0]
	elif o > 5 and BTC*o/100 > 0.0001:
	    ETH += BTC*o/100/history[0]
	    BTC -= BTC*o/100
	print(datetime.datetime.now().strftime('[%H:%M]')+str(round(o))+"%")

if __name__ == "__main__":
	bot = choose()
	init()
	while on:
		try:
			loop(bot)
		except KeyboardInterrupt:
			on = False
	print("Total Benefits: "+str(ETH-0.0269541+BTC*start_price-BTC0)," ETH")