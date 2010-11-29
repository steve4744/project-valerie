'''
Created on 28.11.2010

@author: i7
'''

import codecs

##
# Converts RAW strings to UTF-8 strings
# @param rawString: The RAW string 
# @return: The UTF-8 string or None if conversion failed

def stringToUtf8(rawString):
    utf8String = None
    if rawString is not None:
        try:
            utf8String = unicode(rawString, "utf-8")
        except UnicodeDecodeError, ex:
            print "Conversion to utf-8 failed, trying different approach!", ex
            try:
                print type(rawString)
                utf8String = unicode(rawString, "latin-1")
            except UnicodeDecodeError, ex2:
                print "Conversion to utf-8 failed!!! Ignoring", ex2
                utf8String = None
                
        except Exception, ex:
            print "Conversion to utf-8 failed!!! Something unexpected happened", ex
            utf8String = None
        
    return utf8String
    
##
# Converts UTF-8 strings to Latin-1 strings
# @param utfString: The UTF-8 string 
# @return: The Latin-1 string or an empty string if conversion failed

def utf8ToLatin(utfString):
    latinString = None
    if utfString is not None:
        try:
            latinString = utfString.encode('latin-1')
        except Exception, ex:
            print "Conversion to latin failed!!!", ex
            latinString = None
        
    if latinString is None:
        latinString = " "
        
    return latinString
        
        
class Utf8():
    fd = None
    
    def __init__(self, file, arg):
        self.open(file, arg)
        
    def open(self, file, arg):
        try:
            self.fd = codecs.open(file, arg, "utf-8")
            return True
        except Exception, ex:
            print "-"*30
            print "Utf8::open"
            print ex
            print "-"*30
            return False
        
    def close(self):
        if self.fd is not None:
            self.fd.close()
        
    def write(self, text):
        if self.fd is not None:
            try:
                self.fd.write(text)
            except Exception, ex:
                print "-"*30
                print "Utf8::write"
                print ex
                print "-"*30
        
    def read(self):
        if self.fd is not None:
            try:
                rtv = self.fd.read()[:-1]
                return rtv
            except Exception, ex:
                print "-"*30
                print "Utf8::read"
                print ex
                print "-"*30
                return None
        return None
        
        