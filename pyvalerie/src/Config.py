'''
Created on 26.06.2010

@author: i3
'''

conf = {}

def load():
    # Check default config
    try:
        print("Check "+"/hdd/valerie/valerie.conf")
        if os.path.isfile("/hdd/valerie/valerie.conf") is False:
            f = open("/hdd/valerie/valerie.conf", "wb")
            f.write("local=en\n")
            f.close()
            printl(" - Created")
        else:
            printl(" - OK")
    except Exception:
        printl(" - ERROR")
    
    f = open("/hdd/valerie/valerie.conf", "r")
    for line in f.readlines():
        key,value = line.split("=")
        conf[key] = value
    f.close()
        
def getKey(key):
    return conf[key].strip()
            
        
