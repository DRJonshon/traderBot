from poloniex import Poloniex
import urllib3
import time, json, datetime, os, sys, random
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style

urllib3.disable_warnings()
polo = Poloniex('UUOLEZEG-YGAIX5UX-QMOO53NK-I6DMOO89','4fd2e22b010bfaaf7a8e75b92f5227451f2e47f52a2fa118d30b5c2ad367fe821dc0a3772dd44fae67e91a512acfbf0242e395f1ebdd9a6777e6f54352a92a72')

BTC = 0
ETH = 0
BTC_ETH = 0
on = True
xs = []
ys = []
t0 = time.time()

style.use('fivethirtyeight')
fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)

def getPrice():
    return polo.returnTicker()['BTC_ETH']['last']

def animate(i):
    global xs
    global ys
    global t0
    ys.append(getPrice())
    xs.append(len(ys))
    ax1.clear()
    ax1.plot(xs,ys)
    t = time.time()
    if t - t0 >= 60:
        t0 = t
        data = ""
        for i,p in enumerate(ys):
            data.join(p)
            print(i)
            if i != len(ys):
                data.join(",")
            
        with open("data.txt",'w') as file:
            file.write(data)
            file.close()
    
def show():
    ani = animation.FuncAnimation(fig, animate, interval=1000)
    plt.show()

show()
