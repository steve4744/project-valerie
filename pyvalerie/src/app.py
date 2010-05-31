'''
Created on 21.05.2010

@author: i7
'''
import MediaInfo
import DirectoryScanner

from provider.ImdbProvider import ImdbProvider
from provider.TheMovieDbProvider import TheMovieDbProvider
from provider.TheTvDbProvider import TheTvDbProvider

if __name__ == '__main__':
    #ds = DirectoryScanner.DirectoryScanner('\\\\I7-PC\\lots')
    ds = DirectoryScanner.DirectoryScanner('F:\LegendOfTheSeeker')
    elementList = ds.listDirectory(["mkv"], "(-sample)")
    i = 0
    for element in elementList:
        print "(",i,"/",len(elementList),")"
        i = i + 1
        
        elementInfo = MediaInfo.MediaInfo(element[0], element[1], element[2])
        elementInfo.parse()
        #print elementInfo
        
        elementInfo = ImdbProvider().getMovieByTitle(elementInfo)
        if elementInfo.isEpisode:
            elementInfo = TheTvDbProvider().getSerieByTitle(elementInfo)
        
        
        if elementInfo.isMovie:
            elementInfo = TheMovieDbProvider().getArtByImdbId(elementInfo)
        elif elementInfo.isEpisode:
            elementInfo = TheTvDbProvider().getArtByTheTvDbId(elementInfo)
        print elementInfo
        f = open("test.txt", "a")
        f.write(elementInfo.__str__())
        f.close()
        
    print "(",i,"/",len(elementList),")"