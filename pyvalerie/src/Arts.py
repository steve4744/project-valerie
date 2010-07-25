'''
Created on 26.06.2010

@author: i3
'''

import Config
import subprocess
from WebGrabber import WebGrabber
from os import path
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
            if path.isfile(eInfo.ImdbId + "_poster.png") is False:
                if len(eInfo.Poster):
                    #print "URL: ", "http://val.duckbox.info/cgi-bin/convert.py?" + eInfo.ImdbId + ";poster;" + eInfo.Poster
                    url = WebGrabber().grab("http://val.duckbox.info/cgi-bin/convert.py?" + eInfo.ImdbId + ";poster;" + eInfo.Poster)
                    if url != "NONE":
                        WebGrabber().grabFile("http://val.duckbox.info" + url, eInfo.ImdbId + "_poster.png")
                    #retcode = subprocess.call(Config.getKey("pngquant") + " 256 " + , shell=False)
                
            if len(eInfo.Backdrop):
                if path.isfile(eInfo.ImdbId + "_backdrop.mvi") is False:
                    #WebGrabber().grabFile(eInfo.Backdrop, eInfo.ImdbId + "_backdrop.jpg")
                    #print "URL: ", "http://val.duckbox.info/cgi-bin/convert.py?" + eInfo.ImdbId + ";backdrop;" + eInfo.Backdrop
                    url = WebGrabber().grab("http://val.duckbox.info/cgi-bin/convert.py?" + eInfo.ImdbId + ";backdrop;" + eInfo.Backdrop)
                    if url != "NONE":
                        WebGrabber().grabFile("http://val.duckbox.info" + url, eInfo.ImdbId + "_backdrop.m1v")
                     #mf://" + fOutput.getName() + " -mf fps="+fps+":type=jpg -embeddedfonts -o " +  Output + " -ovc lavc -lavcopts vcodec=mpeg1video -vf scale="+Res
        else:
            if len(eInfo.Poster):
                if path.isfile(eInfo.TheTvDbId + "_poster.png") is False:
                    url = WebGrabber().grab("http://val.duckbox.info/cgi-bin/convert.py?" + eInfo.TheTvDbId + ";poster;" + eInfo.Poster)
                    if url != "NONE":
                        WebGrabber().grabFile("http://val.duckbox.info" + url, eInfo.TheTvDbId + "_poster.png")
                #WebGrabber().grabFile(eInfo.Poster, eInfo.TheTvDbId + "_poster.jpg")
                
            if len(eInfo.Backdrop):
                if path.isfile(eInfo.TheTvDbId + "_backdrop.mvi") is False:
                    #WebGrabber().grabFile(eInfo.Backdrop, eInfo.ImdbId + "_backdrop.jpg")
                    #print "URL: ", "http://val.duckbox.info/cgi-bin/convert.py?" + eInfo.TheTvDbId + ";backdrop;" + eInfo.Backdrop
                    url = WebGrabber().grab("http://val.duckbox.info/cgi-bin/convert.py?" + eInfo.TheTvDbId + ";backdrop;" + eInfo.Backdrop)
                    if url != "NONE":
                        WebGrabber().grabFile("http://val.duckbox.info" + url, eInfo.TheTvDbId + "_backdrop.m1v")
                