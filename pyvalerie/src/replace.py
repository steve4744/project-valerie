import re
import os

replacementsOptions = ["pre", "post_tv", "post_movie"]
replacementsList = {}

def load():
    # Check default config
    try:
        print("Check "+"/hdd/valerie/pre.conf")
        if os.path.isfile("/hdd/valerie/pre.conf") is False:
            f = open("/hdd/valerie/pre.conf", "w")
            f.write('"^\S*-"=" "\n')
            f.write('" (720p|1080i|1080p)( |$)+"=" "\n')
            f.write('" (x264|blu-ray|hdtv|xvid)( |$)+"=" "\n')
            f.write('" (eng|rus)( |$)+"=" "\n')
            f.write('" (oar)( |$)+"=" "\n')
            f.write('" (miniseries)( |$)+"=" "\n')
            f.write('" (dts|dd5|ac3|stereo)( |$)+"=" "\n')
            f.close()
            print(" - Created\n")
        else:
            print(" - OK\n")
    except Exception, ex:
        print(" - ERROR\n"), ex
    
    try:
        print("Check "+"/hdd/valerie/post_movie.conf")
        if os.path.isfile("/hdd/valerie/post_movie.conf") is False:
            f = open("/hdd/valerie/post_movie.conf", "w")
            f.write('" disk\d+( |$)+"=" "\n')
            f.write('" part\d+( |$)+"=" "\n')
            f.write('" extended edition( |$)+"=" "\n')
            f.close()
            print(" - Created\n")
        else:
            print(" - OK\n")
    except Exception, ex:
        print(" - ERROR\n"), ex
    
    try:
        print("Check "+"/hdd/valerie/post_tv.conf")
        if os.path.isfile("/hdd/valerie/post_tv.conf") is False:
            f = open("/hdd/valerie/post_tv.conf", "w")
            f.write('" (oar|esir|miniseries)"=" "\n')
            f.write('"halycon-"=" "\n')
            f.write('"e7-"=" "\n')
            f.close()
            print(" - Created\n")
        else:
            print(" - OK\n")
    except Exception, ex:
        print(" - ERROR\n"), ex
    
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
