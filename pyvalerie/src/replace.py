import re
import os

replacementsOptions = ["pre", "post_tv", "post_movie"]
replacementsList = {}

def load():
    for rf in replacementsOptions:
        replacementsList[rf] = []
        try:
            f = open("/hdd/valerie/" + rf + ".conf", "r")
            for line in f.readlines():
                keys = line.split("=")
                if len(keys) == 2:
                    keys[0] = keys[0].strip().strip('[\'\"]')
                    keys[1] = keys[1].strip().strip('[\'\"]')
                    print "[" + rf + "] ", keys[0], " --> ", keys[1]
                    replacementsList[rf].append([re.compile(keys[0]),keys[1]])
                    #replacementsList[rf].append([keys[0],keys[1]])
            f.flush()
            f.close()
        except Exception, ex:
            print "No " + "/hdd/valerie/" + rf + ".conf" + " available"
            print type(ex), ex

def replacements(option):
    if option in replacementsOptions:
        return replacementsList[option]
    else:
        return {}