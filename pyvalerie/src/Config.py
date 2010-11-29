'''
Created on 26.06.2010

@author: i3
'''

import os

conf = {}

def load():
    # Check default config
    try:
        print("Check "+"/hdd/valerie/valerie.conf")
        if os.path.isfile("/hdd/valerie/valerie.conf") is False:
            f = open("/hdd/valerie/valerie.conf", "w")
            f.write("local=en\n")
            f.close()
            print(" - Created\n")
        else:
            print(" - OK\n")
    except Exception, ex:
        print(" - ERROR\n"), ex
    
    f = open("/hdd/valerie/valerie.conf", "r")
    for line in f.readlines():
        key,value = line.split("=")
        conf[key] = value
    f.close()
        
def getKey(key):
    return conf[key].strip()

def getString(key):
    return getKey(key)
            
        
