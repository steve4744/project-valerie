'''
Created on 26.06.2010

@author: i3
'''

import Config
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
                    url = WebGrabber().grab("http://val.duckbox.info/cgi-bin/convert.py?" + eInfo.ImdbId + ";poster;" + eInfo.Poster)
                    if url is not None and url != "NONE":
                        WebGrabber().grabFile("http://val.duckbox.info" + url, eInfo.ImdbId + "_poster.png")
                
            if len(eInfo.Backdrop):
                if path.isfile(eInfo.ImdbId + "_backdrop.mvi") is False:
                    url = WebGrabber().grab("http://val.duckbox.info/cgi-bin/convert.py?" + eInfo.ImdbId + ";backdrop;" + eInfo.Backdrop)
                    if url is not None and url != "NONE":
                        WebGrabber().grabFile("http://val.duckbox.info" + url, eInfo.ImdbId + "_backdrop.m1v")
        else:
            if len(eInfo.Poster):
                if path.isfile(eInfo.TheTvDbId + "_poster.png") is False:
                    url = WebGrabber().grab("http://val.duckbox.info/cgi-bin/convert.py?" + eInfo.TheTvDbId + ";poster;" + eInfo.Poster)
                    if url != "NONE":
                        WebGrabber().grabFile("http://val.duckbox.info" + url, eInfo.TheTvDbId + "_poster.png")
                
            if len(eInfo.Backdrop):
                if path.isfile(eInfo.TheTvDbId + "_backdrop.mvi") is False:
                    url = WebGrabber().grab("http://val.duckbox.info/cgi-bin/convert.py?" + eInfo.TheTvDbId + ";backdrop;" + eInfo.Backdrop)
                    if url is not None and url != "NONE":
                        WebGrabber().grabFile("http://val.duckbox.info" + url, eInfo.TheTvDbId + "_backdrop.m1v")
                
