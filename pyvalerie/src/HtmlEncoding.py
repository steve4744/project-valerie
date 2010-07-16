'''
Created on 22.05.2010

@author: i7
'''

#http://github.com/sku/python-twitter-ircbot/blob/321d94e0e40d0acc92f5bf57d126b57369da70de/html_decode.py

from htmlentitydefs import name2codepoint as n2cp
import re

def decode_htmlentities(string):
    def substitute_entity(match):
        ent = match.group(3)
        if match.group(1) == "#":
            # decoding by number
            if match.group(2) == '':
                # number is in decimal
                return unichr(int(ent))
            elif match.group(2) == 'x':
                # number is in hex
                return unichr(int('0x'+ent, 16))
        else:
            # they were using a name
            cp = n2cp.get(ent)
            if cp: return unichr(cp)
            else: return match.group()
    
    entity_re = re.compile(r'&(#?)(x?)(\w+);')
    try:
        var = entity_re.subn(substitute_entity, string)[0]
    except Exception, ex:
        print ex
        #source_encoding = "iso-8859-1"
        #string = string.encode(source_encoding)
        #string = unicode(string, 'utf-8')
        #var = entity_re.subn(substitute_entity, string)[0]
        var = ""
        
        
    return var
        