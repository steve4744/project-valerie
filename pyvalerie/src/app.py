'''
Created on 21.05.2010

@author: i7
'''

import sys
import os

import MediaInfo
import DirectoryScanner

import Config
from Arts import Arts
from provider.ImdbProvider import ImdbProvider
from provider.TheMovieDbProvider import TheMovieDbProvider
from provider.TheTvDbProvider import TheTvDbProvider

from Database import Database

if __name__ == '__main__':
    
    reload(sys)
    #sys.setdefaultencoding( "latin-1" )
    sys.setdefaultencoding( "utf-8" )
    
    Config.load()
    
    db = Database()
    db.load()
    
    fconf = open("paths.conf", "r")
    filetypes = fconf.readline().strip().split('|')
    print filetypes
    for path in fconf.readlines(): 
        path = path.strip()
        
        if os.path.isdir(path):
            ds = DirectoryScanner.DirectoryScanner(path)
            elementList = ds.listDirectory(filetypes, "(sample)")
            
    i = 0
    for element in elementList:
        print "(",i,"/",len(elementList),")"
        i = i + 1
        
        if "RECYCLE.BIN" in element[0]:
            continue
        
        if db.checkDuplicate(element[0], element[1], element[2]):
            print "Already in db [ " + element[1] + "." + element[2] + " ]"
            continue
        else:
            print "New file [ " + element[1] + "." + element[2] + " ]"
        
        elementInfo = MediaInfo.MediaInfo(element[0], element[1], element[2])
        elementInfo.parse()
        #print elementInfo
        
        elementInfo = ImdbProvider().getMovieByTitle(elementInfo)
        #if elementInfo.isSerie:
        #    elementInfo = TheTvDbProvider().getSerieByImdbID(elementInfo)
        
        
        if elementInfo.isMovie:
            # Ask TheMovieDB for the local title and plot
            elementInfo = TheMovieDbProvider().getMovieByImdbID(elementInfo)
            elementInfo = TheMovieDbProvider().getArtByImdbId(elementInfo)
            db.add(elementInfo)
        elif elementInfo.isSerie:
            elementInfo = TheTvDbProvider().getSerieByImdbID(elementInfo)
            elementInfo = TheTvDbProvider().getArtByTheTvDbId(elementInfo)
            db.add(elementInfo)
            
            elementInfoe = elementInfo.copy()
            
            elementInfoe.isSerie = False
            elementInfoe.isEpisode = True
            
            elementInfoe = TheTvDbProvider().getEpisodeByTheTvDbId(elementInfoe)
            
            db.add(elementInfoe)
            
        Arts().download(elementInfo)
        
        
        print elementInfo
        f = open("test.txt", "a")
        f.write(elementInfo.__str__())
        f.close()
        
    fconf.close()
        
    print "(",i,"/",len(elementList),")"
    
    print db
    
    db.save()
    
    #exit(0)
