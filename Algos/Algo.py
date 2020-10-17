from poloniex import Poloniex
import urllib3
import time, json, datetime, os, sys, random, datetime, math

urllib3.disable_warnings()
polo = Poloniex('UUOLEZEG-YGAIX5UX-QMOO53NK-I6DMOO89','4fd2e22b010bfaaf7a8e75b92f5227451f2e47f52a2fa118d30b5c2ad367fe821dc0a3772dd44fae67e91a512acfbf0242e395f1ebdd9a6777e6f54352a92a72')
cn = 0
on = True

with open('data/'+str(random.randint(0,7))+'.json','r') as fp:
    obj = json.load(fp)

def getPrice():
    return polo.returnTicker()['BTC_ETH']['last']

def createCandle():
    t = time.time()
    date = t
    end = t +60
    p = getPrice()
    open = p
    high = p
    low = p
    while time.time()< end:
        p = getPrice()
        if p > high:
            high = p
        elif p < low:
            low = p
    close = p
    return {'date':date,'high':high,'low':low,'open':open,'close':close}


def fetchCandles():
    global cn
    try:
        candle = {'date':obj[cn]['date'],'high':obj[cn]['high'],'low':obj[cn]['low'],'open':obj[cn]['open'],'close':obj[cn]['close']}
        cn +=1
    except:
        print("end of data")
        raise KeyboardInterrupt()
    return  candle

def buy(ETH,BTC,amount,price):
    BTC1 = BTC*(1-amount)
    ETH = ETH + (BTC-BTC1)/price
    return ETH,BTC1

def sell(ETH,BTC,amount,price):
    ETH1 = ETH*(1-amount)
    BTC = BTC+(ETH-ETH1)*price
    return ETH1,BTC

def main(mode):
    global on
    if mode == "-rt":
        getCandle = createCandle
    else:
        getCandle = fetchCandles
    t0 = time.time()
    try:
        first = getCandle()['close']
        ETH = 0.0269541*10
        BTC = first*ETH
        iamount = buy(ETH,BTC,1,first)[0]
        history = []
        while on:
            candle = getCandle()
            action = 0
            if len(history) == 10:
                av = 0
                for c in history:
                    av += c[0]['close']
                av=av/10
                confidence = 0
                for c in history:
                    confidence += c[0]['close']>0
                amount_buy = confidence/10*0.35
                amount_sell = (10 - confidence)/10*0.35
                if candle['close'] > av:
                    e,b = sell(ETH,BTC,amount_sell,candle['close'])
                    if buy(e,b,1,candle['close']) > buy(ETH,BTC,1,candle['close']):
                        ETH,BTC = e,b
                        action = -amount_sell
                elif candle['close'] < av:
                    e,b = buy(ETH,BTC,amount_buy,candle['close'])
                    if buy(e,b,1,candle['close']) > buy(ETH,BTC,1,candle['close']):
                        ETH,BTC = e,b
                        action = amount_buy
                history.pop(9)
            history.insert(0,(candle,action))
            os.system('clear')
            t1 = time.time()
            dt = (t1-t0)
            s = math.floor(dt)
            m = math.floor(dt/60)
            h = math.floor(m/60)
            d = math.floor(h/24)
            print(('running for %sd %sh %sm %ss')%(d,h%24,m%60,s%60))
            print('last data: '+str(datetime.datetime.fromtimestamp(history[0][0]['date'])))
            print("profit: "+str((buy(ETH,BTC,1,first)[0]-iamount)/iamount*100)+' % ('+str(round((buy(ETH,BTC,1,first)[0]-iamount)*154.86,2))+"$)")

    except KeyboardInterrupt:
        on = False


if __name__ == "__main__":
    if len(sys.argv) >1:
        args = sys.argv[1]
    else:
            args = ''
    main(args)
