'''
Created on 26.06.2010

@author: i3
'''

conf = {}

def load():
    '''
    Constructor
    '''
    f = open("/hdd/valerie/valerie.conf", "r")
    for line in f.readlines():
        key,value = line.split("=")
        conf[key] = value
    f.close()
        
def getKey(key):
    return conf[key].strip()
            
        