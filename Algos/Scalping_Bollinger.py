# coding: utf8

#chandelles de 5min
#Calculer MMS 20
#Calculer les bandes de Bollinger: MMS20 +/- 2 écart-types

#Quand une chandelle casse la MMS20, on s'attend à ce qu'elle continue jusqu'a la Bollinger.

#Si baisse et traverse la MMS20, take = Bollinger(-), stop = Bollinger(+)
#Si hausse et traverse la MMS20, take = Bollinger(+), stop = Bollinger(-)

import random
import json
import math
import pygame
from datetime import datetime

n = 0
on = True
states = ['under MMS20']
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
won = 0
lost = 0

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
                candle = {'bollingerLow':indexes[0],'MMS20':indexes[1],'bollingerHigh':indexes[2],'date':data[n1-i]['date'],'high':data[n1-i]['high'],'low':data[n1-i]['low'],'open':data[n1-i]['open'],'close':data[n1-i]['close']}
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
                    pygame.draw.line(screen, (255,0,0),(x+candleSize/2,500-(candles[i-1]['bollingerLow']-low)/distance),(x-candleSize/2,500-(candle['bollingerLow']-low)/distance))
                    pygame.draw.line(screen, (0,255,0),(x+candleSize/2,500-(candles[i-1]['MMS20']-low)/distance),(x-candleSize/2,500-(candle['MMS20']-low)/distance))
                    pygame.draw.line(screen, (0,0,255),(x+candleSize/2,500-(candles[i-1]['bollingerHigh']-low)/distance),(x-candleSize/2,500-(candle['bollingerHigh']-low)/distance))

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
    bollingerLow = 0
    bollingerHigh = 0
    MMS20 = 0



    if n1 >= 20:
        #calcul de la moyenne
        for i in range(20):
            MMS20 += data[n1-1-i]['close']
        MMS20 = MMS20/20

        #calcul de l'écart type
        sd = 0
        for i in range(20):
            sd += math.pow(data[n1-1-i]['close']-MMS20,2)
        sd = sd/20
        sd = math.sqrt(sd)

        #calcul des bandes de bollinger

        bollingerLow = MMS20 - 3*sd
        bollingerHigh = MMS20 + 3*sd

    return (bollingerLow,MMS20,bollingerHigh)

def short(take,stop):
    global BTC
    global ETH
    global won
    global lost
    start_ETH = ETH
    price = data[n]['close']
    low = data[n]['low']
    high = data[n]['high']
    start_price = price
    amount = 0.1*ETH
    amount_BTC = amount*price
    value_before = ETH + BTC/data[0]['close']
    ETH -= amount
    BTC += amount_BTC


    while low > take and high < stop:
        candle = fetchCandles()
        price  = candle['close']
        low = candle['low']
        high = candle['high']
        indexes = getIndexes()
        stop = indexes[2]
        take = indexes[0]



    BTC -= amount_BTC
    ETH += amount_BTC/data[n]['close']
    print("sold on "+datetime.utcfromtimestamp(data[n]['date']).strftime('%Y-%m-%d %H:%M:%S')+", result:")
    print('price:'+str(price)+', start_price:'+str(start_price))
    print(ETH - start_ETH)
    if ETH - start_ETH >0:
        won += 1
    elif ETH - start_ETH <0:
        lost += 1


def Long(take,stop):
    global BTC
    global ETH
    global won
    global lost
    start_BTC = BTC
    price = data[n]['close']
    low = data[n]['low']
    high = data[n]['high']
    amount = 0.1 *BTC
    amount_ETH = amount/price
    value_before = ETH + BTC/data[0]['close']
    ETH += amount_ETH
    BTC -= amount



    while high < take and low > stop:
        candle = fetchCandles()
        price = candle['close']
        low = candle['low']
        high = candle['high']
        indexes = getIndexes()
        take = indexes[2]
        stop = indexes[0]
    #while pts<3:
    #    candle = fetchCandles()
    #    pts = abs(price-candle['close'])*10000


    ETH -= amount_ETH
    BTC += amount_ETH*data[n]['close']
    print("bought on "+datetime.utcfromtimestamp(data[n]['date']).strftime('%Y-%m-%d %H:%M:%S')+", result:")
    print(BTC - start_BTC)
    if BTC - start_BTC > 0:
        won += 1
    elif BTC - start_BTC < 0:
        lost +=1

def wait():
    global states

    candle  = fetchCandles()

    indexes = getIndexes()
    bollingerHigh = indexes[2]
    MMS20 = indexes[1]
    bollingerLow = indexes[0]

    if candle['close'] < MMS20:
        if 'over MMS20' in states:
            states.append('under MMS20')
            states.remove('over MMS20')
            if candle['low'] > bollingerLow:
                print('short on ' + datetime.utcfromtimestamp(candle['date']).strftime('%Y-%m-%d %H:%M:%S'))
                return short(bollingerLow,bollingerHigh)
    else:
        if 'under MMS20' in states:
            states.append('over MMS20')
            states.remove('under MMS20')
            if candle['high'] < bollingerHigh:
                print('long on ' + datetime.utcfromtimestamp(candle['date']).strftime('%Y-%m-%d %H:%M:%S'))
                return Long(bollingerHigh,bollingerLow)

    #if 'croisement_bear' in states:
    #    if MMS7 < MMS20:
    #        states.remove('croisement_bear')
    #        return short(candle['close'])




    #if MMS200 < MMS20 and MMS20 < candle['close'] and candle['close'] < MMS7 and not 'retracement_bull' in states:
    #    states.append('retracement_bull')
    #    print("retracement_bull added on "+datetime.utcfromtimestamp(candle['date']).strftime('%Y-%m-%d %H:%M:%S'))

def main():
    global on
    while on:
        try:
            wait()
        except KeyboardInterrupt:
            on = False

    fValue = ETH + BTC/data[0]['close']
    print(str(fValue/iValue*100)+" %")
    print(str(won)+' won / '+str(lost)+' lost')
    print('worked on file '+str(fileNum))
    display()
if __name__ == '__main__':
    main()
