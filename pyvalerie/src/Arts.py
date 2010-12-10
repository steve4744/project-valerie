'''
Created on 26.06.2010

@author: i3
'''

import Config
import WebGrabber
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
            if len(eInfo.Poster):
                if path.isfile(eInfo.ImdbId + "_poster.png") is False:
                    url = WebGrabber.getText("http://val.duckbox.info/cgi-bin/convert.py?" + eInfo.ImdbId + ";poster;" + eInfo.Poster)
                    if url is not None and url != "NONE":
                        WebGrabber.getFile("http://val.duckbox.info" + url, eInfo.ImdbId + "_poster.png")
                
            if len(eInfo.Backdrop):
                if path.isfile(eInfo.ImdbId + "_backdrop.m1v") is False or path.isfile(eInfo.ImdbId + "_backdrop_low.m1v") is False or path.isfile(eInfo.ImdbId + "_backdrop.png") is False:
                    url = WebGrabber.getText("http://val.duckbox.info/cgi-bin/convert.py?" + eInfo.ImdbId + ";backdrop;" + eInfo.Backdrop)
                    if url is not None and url != "NONE":
                        urls = url.split("<br />")
                        if urls is not None and len(urls) >= 3:
                            WebGrabber.getFile("http://val.duckbox.info" + urls[0].strip(), eInfo.ImdbId + "_backdrop.m1v")
                            WebGrabber.getFile("http://val.duckbox.info" + urls[1].strip(), eInfo.ImdbId + "_backdrop_low.m1v")
                            WebGrabber.getFile("http://val.duckbox.info" + urls[2].strip(), eInfo.ImdbId + "_backdrop.png")
                        
        elif eInfo.isSerie:
            if len(eInfo.Poster):
                if path.isfile(eInfo.TheTvDbId + "_poster.png") is False:
                    url = WebGrabber.getText("http://val.duckbox.info/cgi-bin/convert.py?" + eInfo.TheTvDbId + ";poster;" + eInfo.Poster)
                    if url != "NONE":
                        WebGrabber.getFile("http://val.duckbox.info" + url, eInfo.TheTvDbId + "_poster.png")
                
            if len(eInfo.Backdrop):
                if path.isfile(eInfo.TheTvDbId + "_backdrop.m1v") is False or path.isfile(eInfo.TheTvDbId + "_backdrop_low.m1v") is False or path.isfile(eInfo.TheTvDbId + "_backdrop.png") is False:
                    url = WebGrabber.getText("http://val.duckbox.info/cgi-bin/convert.py?" + eInfo.TheTvDbId + ";backdrop;" + eInfo.Backdrop)
                    if url is not None and url != "NONE":
                        urls = url.split("<br />")
                        if urls is not None and len(urls) >= 3:
                            WebGrabber.getFile("http://val.duckbox.info" + urls[0].strip(), eInfo.TheTvDbId + "_backdrop.m1v")
                            WebGrabber.getFile("http://val.duckbox.info" + urls[1].strip(), eInfo.TheTvDbId + "_backdrop_low.m1v")
                            WebGrabber.getFile("http://val.duckbox.info" + urls[2].strip(), eInfo.TheTvDbId + "_backdrop.png")
                
