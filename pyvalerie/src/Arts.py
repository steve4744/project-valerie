'''
Created on 26.06.2010

@author: i3
'''

import Config
import subprocess
from WebGrabber import WebGrabber

class Arts():
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        
    def download(self, eInfo):
        if eInfo.isMovie:
            if len(eInfo.Poster):
                print "URL: ", "http://val.duckbox.info/cgi-bin/convert.py?" + eInfo.ImdbId + ";" + eInfo.Poster
                url = WebGrabber().grab("http://val.duckbox.info/cgi-bin/convert.py?" + eInfo.ImdbId + ";" + eInfo.Poster)
                if url != "NONE":
                    WebGrabber().grabFile("http://val.duckbox.info" + url, eInfo.ImdbId + "_poster.png")
                #retcode = subprocess.call(Config.getKey("pngquant") + " 256 " + , shell=False)
                
            #if len(eInfo.Backdrop):
                #WebGrabber().grabFile(eInfo.Backdrop, eInfo.ImdbId + "_backdrop.jpg")
                 #mf://" + fOutput.getName() + " -mf fps="+fps+":type=jpg -embeddedfonts -o " +  Output + " -ovc lavc -lavcopts vcodec=mpeg1video -vf scale="+Res
        else:
            if len(eInfo.Poster):
                url = WebGrabber().grab("http://val.duckbox.info/cgi-bin/convert.py?" + eInfo.TheTvDbId + ";" + eInfo.Poster)
                if url != "NONE":
                    WebGrabber().grabFile("http://val.duckbox.info" + url, eInfo.TheTvDbId + "_poster.png")
                #WebGrabber().grabFile(eInfo.Poster, eInfo.TheTvDbId + "_poster.jpg")
                
            #if len(eInfo.Backdrop):
                #WebGrabber().grabFile(eInfo.Backdrop, eInfo.TheTvDbId + "_backdrop.jpg")
                