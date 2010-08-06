'''
Created on 22.05.2010

@author: i3
'''

import os
import re
import urllib2
import codecs
import socket
from sys import version_info

from HtmlEncoding import decode_htmlentities

class WebGrabber(object):
    '''
    classdocs
    '''

    cacheDir = "/hdd/valerie/cache"
    downloadDir = "/hdd/valerie/media"

    def __init__(self):
        '''
        Constructor
        '''
        
    def grab(self, url, encoding="utf-8"): #encoding="latin-1"):
        print "URL", url.encode('latin-1')
        cacheFile = re.sub(r'(\"|/|\\|:|\?|<|>|\|)', "_", url)
        pageHtml = None
        if os.path.isfile((self.cacheDir + "/" + cacheFile + ".cache").encode('latin-1')):
            if encoding == "utf-8":
                f = codecs.open(self.cacheDir + "/" + cacheFile + ".cache", "r", "utf-8")
                pageHtml = f.read()[:-1]
                f.close()
            else:
                f = open(self.cacheDir + "/" + cacheFile + ".cache", 'r')
                pageHtml = f.read()
                f.close()
        else:
            kwargs = {}
            if version_info[1] >= 6:
                kwargs['timeout'] = 10
            else:
                socket.setdefaulttimeout(10)
            try:
                page = urllib2.urlopen(url.encode('latin-1'), **kwargs)
            except Exception, ex:
                print "URL", url.encode('latin-1')
                print "urllib2.urlopen: ", ex
                return None
            if encoding == "utf-8":
                pageUnicode = page.read()
                try:
                    pageHtml =  unicode(pageUnicode, "utf-8")
                except UnicodeDecodeError, ex:
                    try:
                        pageHtml =  unicode(pageUnicode, "latin-1")
                    except UnicodeDecodeError, ex2:
                        print "Conversion to utf-8 failed!!!", ex2
            elif encoding == "latin-1":
                pageHtml = page.read() # read as latin-1
                #print type(pageHtml)
                pageHtml = pageHtml.decode("latin-1")
                #pageHtml = unicode(pageHtml, "utf-8")
            
            try:
                f = codecs.open(self.cacheDir + "/" + cacheFile + ".cache", 'w', "utf-8")
                f.write(pageHtml)
                f.close()
            except Exception, ex:
                print "create cache ", ex, type(pageHtml)
        
        print "pageHtml: ", type(pageHtml)
        return pageHtml
    
    def grabFile(self, url, name):
        print "URL", url.encode('latin-1')
        #cacheFile = url.split('/')
        #cacheFile = cacheFile[len(cacheFile)-1]
        #pageHtml = None
        if os.path.isfile(self.downloadDir + "/" + name) is False:
            for i in range(3):
                try:
                    page = urllib2.urlopen(url)
                    f = open(self.downloadDir + "/" + name, 'wb')
                    f.write(page.read())
                    f.close()
                    break
                except Exception, ex:
                    print ex
            
        return
