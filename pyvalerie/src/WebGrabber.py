'''
Created on 22.05.2010

@author: i3
'''

import os
import urllib2
import socket
from sys import version_info
import sys, traceback

from HtmlEncoding import decode_htmlentities
#import twisted.web.microdom as microdom
import xml.dom.minidom as minidom
import Utf8
import re

cacheDir = "/hdd/valerie/cache"
downloadDir = "/hdd/valerie/media"

RETRIES = 3

import urllib
import urlparse

def url_fix(s):
    scheme, netloc, path, qs, anchor = urlparse.urlsplit(s)
    path = urllib.quote(path, '/%')
    qs = urllib.quote_plus(qs, ':&=')
    return urlparse.urlunsplit((scheme, netloc, path, qs, anchor))

def checkCache(url):
    cacheFile = re.sub(r'\W', "", url).strip()
    rtv = None
    if os.path.isfile(Utf8.utf8ToLatin(cacheDir + "/" + cacheFile + ".cache")):
        f = Utf8.Utf8(cacheDir + u"/" + cacheFile + u".cache", "r")
        rtv = f.read()
        f.close()
    
    return rtv

def addCache(url, text):
    cacheFile = re.sub(r'\W', "", url).strip()
    if text is not None and len(text) > 0:
        f = Utf8.Utf8(cacheDir + u"/" + cacheFile + u".cache", "w")
        f.write(text)
        f.close
     
def getXml(url):
    rawXml = getText(url) 
    decodedXml = None
    try:
        if rawXml is not None:
            #decodedXml = microdom.parseString(rawXml)
            print type(rawXml.encode( "utf-8" ))
            print type(Utf8.utf8ToLatin(rawXml))
            decodedXml = minidom.parseString(Utf8.utf8ToLatin(rawXml))
    except Exception, ex:
        print "URL", Utf8.utf8ToLatin(url)
        print "WebGrabber.getXml: ", ex
        
    return decodedXml
     
def getHtml(url):
    rawHtml = getText(url) 
    decodedHtml = None
    try:
        if rawHtml is not None:
            decodedHtml = decode_htmlentities(rawHtml)
    except Exception, ex:
        print "URL", Utf8.utf8ToLatin(url)
        print "WebGrabber.getHtml: ", ex
        
    return decodedHtml
     
def getText(url): 
    utfPage = checkCache(url)
    if utfPage is None:
        for i in range(RETRIES):
            page = None
            kwargs = {}
            if version_info[1] >= 6:
                kwargs['timeout'] = 10
            else:
                socket.setdefaulttimeout(10)
            try:
                opener = urllib2.build_opener()
                opener.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux x86_64; en-GB; rv:1.8.1.6) Gecko/20070723 Iceweasel/2.0.0.6 (Debian-2.0.0.6-0etch1)')]
                page = opener.open(url_fix(Utf8.utf8ToLatin(url)))
                
                
                #page = urllib2.urlopen(url_fix(Utf8.utf8ToLatin(url)), **kwargs)
            except Exception, ex:
                print "URL", Utf8.utf8ToLatin(url)
                print "urllib2::urlopen: ", ex
                continue
            
            if page is not None:
                rawPage = page.read()
                utfPage = Utf8.stringToUtf8(rawPage)
                
                addCache(url, utfPage)
                break
    
    print "utfPage: ", type(utfPage), "URL=", Utf8.utf8ToLatin(url)
    return utfPage
    
def getFile(url, name, retry=3):
    localFilename = downloadDir + "/" + name
    url = url.strip() # Just to be on the save side
    if os.path.isfile(Utf8.utf8ToLatin(localFilename)) is False:
        for i in range(retry):
            try:
                page = urllib2.urlopen(url_fix(Utf8.utf8ToLatin(url)))
                f = open(Utf8.utf8ToLatin(localFilename), 'wb')
                f.write(page.read())
                f.close()
                break
            except Exception, ex:
                print "File download failed: ", ex
                print "Name: ", Utf8.utf8ToLatin(name)
                print "Url: ", Utf8.utf8ToLatin(url)
                print type(ex)
                print '-'*60
                traceback.print_exc(file=sys.stdout)
                print '-'*60
        
    return
