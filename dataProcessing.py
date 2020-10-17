# -*- coding: utf-8 -*-

import os
toWrite = ''
#os.listdir('data/')
for fileName in ["3.json"]:
     with open('data/'+fileName,'r') as file:
         text = file.read()
         file.close()
     a = text.split('"open":')
     lastclose = a[0].split(',')[0]
     for i,thing in enumerate(a):
         if(i):
             print(thing)
             toWrite+='"open":'+lastclose+',"close":'+thing.split(',"close":')[1]
             lastclose = thing.split('"close":')[1].split(',')[0]
     with open('data/'+fileName,'w') as file:
         file.write(toWrite)
         file.close()

#for fileName in os.listdir('data/'):
#    with open('data/'+fileName,'r') as file:
#        text = file.read()
#        file.close()
#    text = text.split('},{')
#    text = '},\n{'.join(text)
#    with open('data/'+fileName,'w') as file:
#        file.write(text)
#        file.close()
