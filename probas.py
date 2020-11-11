#le but de ce script est de calculer la longueur moyenne d'une série de bulls/bears

import json
import colored




with open('data/10.json','r') as fp:
    obj = json.load(fp)

trends = []

for i,candle in enumerate(obj):
    if i:
        trends.append(candle['close']-obj[i-1]['close']>0)

current = None
counts = [[],[]]#liste des longueurs des séries enregistrées; bears = 0, bulls=1
count = 1

for trend in trends:

    if trend == current:
        count+=1

    elif trend != current and current != None:
        counts[trend].append(count)
        count = 1

    current = trend

def summarize(counts):

    sommaire = {}
    dictKeys = []
    for i in counts:
        if not i in dictKeys:
            dictKeys.append(i)
            sommaire[i] = i
        else:
            sommaire[i] = sommaire[i]+i
    return {key: value for key, value in sorted(
        sommaire.items(), key=lambda item: item[0])}

sommaire = summarize(counts[0]+counts[1])
sommaireBear = summarize(counts[0])
sommaireBull = summarize(counts[1])

print(sommaire)
print(colored.stylize(sommaireBear,colored.fg(160) + colored.attr(1)))
print(colored.stylize(sommaireBull,colored.fg(190) + colored.attr(1)))

#160 = rouge gras
#190 = vert gras
#print(colored.stylize("rouge",colored.fg(160) + colored.attr(1)))
#print(colored.stylize("vert",colored.fg(190) + colored.attr(1)))
