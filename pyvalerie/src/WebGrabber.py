'''
Created on 22.05.2010

@author: i3
'''

import io
import os
import re
import urllib2

class WebGrabber(object):
    '''
    classdocs
    '''

    cacheDir = "cache"

    def __init__(selfparams):
        '''
        Constructor
        '''
        
    def grab(self, url):
        cacheFile = re.sub(r'(\"|/|\\|:|\?|<|>|\|)', "_", url)
        pageHtml = None
        if os.path.isfile(self.cacheDir + "/" + cacheFile + ".cache"):
            f = open(self.cacheDir + "/" + cacheFile + ".cache", 'r')
            pageHtml = f.read()
            f.close()
        else:
            page = urllib2.urlopen(url)
            pageHtml = page.read()
            f = open(self.cacheDir + "/" + cacheFile + ".cache", 'w')
            f.write(pageHtml)
            f.close()
            
        return pageHtml