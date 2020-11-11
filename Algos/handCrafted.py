# coding: utf8

import random
import json
import math
import pygame
from datetime import datetime

n = 0
on = True
states = []
BTC = 0.09
ETH = 0.5
cursor = 0
displaying = 1
start_pos = 0
#fileNum = random.randint(1,3)
fileNum = 10
grab = pygame.cursors.load_xbm('grab.xbm','grab.xbm')
precision = pygame.cursors.load_xbm('precision.xbm','precision.xbm')
nCandles = 100

lastCandle = None
count = 1

with open('../data/'+str(fileNum)+'.json','r') as fp:
    data = json.load(fp)

iValue = ETH + BTC/data[0]['close']

def events():
    global cursor
    global displaying
    global start_pos
    global nCandles
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            displaying = 0
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 : start_pos = event.pos[0]
            elif event.button == 4: nCandles += 5
            elif event.button == 5 and nCandles > 5: nCandles -= 5
            return True
        elif event.type == pygame.MOUSEMOTION and start_pos !=0:
            cursor = cursor + event.pos[0] - start_pos
            start_pos = event.pos[0]
            if cursor < 0:
                cursor=0
            pygame.mouse.set_cursor(*grab)
            return True
        elif event.type == pygame.MOUSEBUTTONUP:
            start_pos = 0
            pygame.mouse.set_cursor(*precision)
            return True

def display():
    global n
    pygame.init()
    pygame.display.set_caption('TraderBot Mk2 Visualisation Tool')
    screen = pygame.display.set_mode((1000,500))
    Font = pygame.font.Font(None,22)
    Clock = pygame.time.Clock()


    while displaying:
        Clock.tick(60)
        if events():
            screen.fill((255,255,255))
            candleSize = 1000/nCandles
            #number of candles to skip
            missing_candles = math.floor(cursor/candleSize)
            n1 = n - missing_candles -1
            cursor_modulo = cursor%candleSize
            candles = []
            high = 0
            low = 10

            for i in range(nCandles+5):
                indexes = getIndexes(n1-i)
                candle = {'MMS7':indexes[0],'MMS20':indexes[1],'MMS200':indexes[2],'date':data[n1-i]['date'],'high':data[n1-i]['high'],'low':data[n1-i]['low'],'open':data[n1-i]['open'],'close':data[n1-i]['close']}
                if candle['low'] < low:
                    low = candle['low']
                elif candle['high'] > high:
                    high = candle['high']
                candles.append(candle)
            center = data[n1]['close']
            distance = (high-low)/500
            for i,candle in enumerate(candles):
                x = 1000-i*candleSize+cursor_modulo
                if candle['close'] > candle['open']:
                    color = (0,200,0)
                    start = candle['close']
                else:
                    color = (200,0,0)
                    start = candle['open']
                y = 500-(start-low)/distance
                thinY = 500-(candle['high']-low)/distance
                pygame.draw.rect(screen, color, (x,y,candleSize,(abs(candle['open']-candle['close'])/distance)))
                pygame.draw.rect(screen, color, (x+candleSize/2-candleSize/20,thinY,candleSize/10,(candle['high']-candle['low'])/distance))
                pygame.draw.rect(screen, (0,0,0), (x,y,candleSize,(abs(candle['open']-candle['close'])/distance)),width=1)
                if i > 0:
                    pygame.draw.line(screen, (255,0,0),(x+candleSize/2,500-(candles[i-1]['MMS7']-low)/distance),(x-candleSize/2,500-(candle['MMS7']-low)/distance))
                    pygame.draw.line(screen, (0,255,0),(x+candleSize/2,500-(candles[i-1]['MMS20']-low)/distance),(x-candleSize/2,500-(candle['MMS20']-low)/distance))
                    aMMS = (x+candleSize/2,500-(candles[i-1]['MMS200']-low)/distance)
                    bMMS = (x-candleSize/2,500-(candle['MMS200']-low)/distance)
                    if aMMS[1] < 0: aMMS=(aMMS[0],1)
                    if aMMS[1] > 500: aMMS=(aMMS[0],499)
                    if bMMS[1] < 0: bMMS=(bMMS[0],1)
                    if bMMS[1] > 500: bMMS=(bMMS[0],499)
                    pygame.draw.line(screen, (0,0,255),bMMS,aMMS)
                screen.blit(Font.render(datetime.utcfromtimestamp(candles[0]['date']).strftime('%Y-%m-%d %H:%M:%S'),True, (0,0,0)),(10,10))
                screen.blit(Font.render(str(round(Clock.get_fps()))+" fps",True, (0,0,0)),(950,10))
            pygame.display.update()
def fetchCandles():
    global n
    try:
        candle = {'date':data[n]['date'],'high':data[n]['high'],'low':data[n]['low'],'open':data[n]['open'],'close':data[n]['close']}
        n +=1
    except IndexError:
        print("end of data")
        raise KeyboardInterrupt()
    return candle

def getIndexes(n1=0):
    if not n1:
        global n
        n1 = n
    MMS200 = 0
    MMS20 = 0
    MMS7 = 0

    if n1 >= 7:
        for i in range(7):
            MMS7 += data[n1-1-i]['close']
        MMS7 = MMS7/7
    if n1 >= 20:
        for i in range(20):
            MMS20 += data[n1-1-i]['close']
        MMS20 = MMS20/20
    if n1 >= 200:
        for i in range(200):
            MMS200 += data[n1-1-i]['close']
        MMS200 = MMS200/200
    return (MMS7,MMS20,MMS200)

def short(price):
    global BTC
    global ETH
    amount = 0.1*ETH
    amount_BTC = amount*data[n]['close']
    value_before = ETH + BTC/data[0]['close']
    ETH -= amount
    BTC += amount_BTC
    pts = 0
    while pts<3:
        candle = fetchCandles()
        pts = abs(price-candle['close'])*10000

    BTC -= amount_BTC
    ETH += amount_BTC/data[n]['close']
    print("sold, result:")
    print(ETH + BTC/data[0]['close']-value_before)

def long(price):
    global BTC
    global ETH

    amount = 0.1 *BTC
    amount_ETH = amount/data[n]['close']
    value_before = ETH + BTC/data[0]['close']
    ETH += amount_ETH
    BTC -= amount
    pts = 0
    while pts<3:
        candle = fetchCandles()
        pts = abs(price-candle['close'])*10000


    ETH -= amount_ETH
    BTC += amount*data[n]['close']
    print("bought, result:")
    print(ETH + BTC/data[0]['close']-value_before)

def buy(price):
    global BTC
    global ETH
    amount = 0.1 *BTC
    amount_ETH = amount/price
    value_before = ETH + BTC/price
    ETH += amount_ETH
    BTC -= amount
    #print("bought, result:")
    #print(ETH + BTC/data[0]['close'])

def sell(price):
    global BTC
    global ETH
    amount = 0.1*ETH
    amount_BTC = amount*price
    value_before = ETH + BTC/price
    ETH -= amount
    BTC += amount_BTC
    #print("sold, result:")
    #print(ETH + BTC/data[0]['close'])

def wait():
    global state
    global lastCandle
    global count

    candle = fetchCandles()
    candleTrend = (candle['close']-candle['open'])>0

    if candleTrend == lastCandle:
        count += 1
    elif candleTrend != lastCandle and lastCandle != None:
        count = 1

    for i,state in enumerate(states):
        states[i][1] -= 1
        if state[1]==0:
            if state[0]:
                buy(candle['close'])
            else:
                sell(candle['close'])
            states.remove(state)


    if count == 1:
        states.append([candleTrend,0])
        if not candleTrend:
            buy(candle['close'])
        else:
            sell(candle['close'])



    lastCandle = candleTrend


def main():
    global on
    print('start balance:'+str(ETH + BTC/data[0]['close']))
    while on:
        try:
            wait()
        except KeyboardInterrupt:
            on = False
    print('end balance:'+str(ETH + BTC/data[0]['close']))
    fValue = ETH + BTC/data[0]['close']
    print(str(fValue/iValue*100)+" %")
    display()
if __name__ == '__main__':
    main()
