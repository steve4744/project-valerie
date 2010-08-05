'''
Created on 22.05.2010

@author: i3
'''

import os
import re
import urllib2
import codecs

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
        print "URL", url
        cacheFile = re.sub(r'(\"|/|\\|:|\?|<|>|\|)', "_", url)
        pageHtml = None
        if os.path.isfile(self.cacheDir + "/" + cacheFile + ".cache"):
            if encoding == "utf-8":
                f = codecs.open(self.cacheDir + "/" + cacheFile + ".cache", "r", "utf-8")
                pageHtml = f.read()[:-1]
                f.close()
            else:
                f = open(self.cacheDir + "/" + cacheFile + ".cache", 'r')
                pageHtml = f.read()
                f.close()
        else:
            try:
                page = urllib2.urlopen(url, timeout=10)
            except Exception, ex:
                print "URL", url
                print "urllib2.urlopen: ", ex
                return None
            if encoding == "utf-8":
                pageUnicode = page.read()
                #pageHtml = unicode('')
                try:
                    pageHtml =  unicode(pageUnicode, "utf-8")
                    #pageHtml += page.read()
                except UnicodeDecodeError, ex:
                    print "encoding == utf-8 ", ex
            elif encoding == "latin-1":
                pageHtml = page.read() # read as latin-1
                #print type(pageHtml)
                pageHtml = pageHtml.decode("latin-1")
                #pageHtml = unicode(pageHtml, "utf-8")
            
            try:
                f = open(self.cacheDir + "/" + cacheFile + ".cache", 'w')
                f.write(pageHtml.encode( "utf-8" ))
                f.close()
            except Exception, ex:
                print "create cache ", ex
        
        print "pageHtml: ", type(pageHtml)
        return pageHtml
    
    def grabFile(self, url, name):
        print "URL", url
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
