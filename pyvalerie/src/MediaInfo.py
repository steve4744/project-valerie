'''
Created on 21.05.2010

@author: i7
'''
import re
import os
import replace

class MediaInfo(object):
    '''
    classdocs
    '''

    Alternatives = {}
    Directors = []
    Writers = []
    Genres = ""
    Runtime = 0
    TagLine = ""
    Popularity = "0"
    Plot = ""

    ImdbId = "tt0000000"
    TheTvDbId = "0"
    Title = ""
    
    Filename = ""
    Path = ""
    Extension = ""
    Year = 0
    Resolution = "576"
    Sound = "Stereo"
    
    isMovie = True
    isSerie = False
    isEpisode = False
    
    Poster = ""
    Backdrop = ""
    
    Season = -1
    Episode = -1
    
    SearchString = ""

    def __init__(self, path, filename, extension):
        '''
        Constructor
        '''
        self.Path = path
        self.Filename = filename
        self.Extension = extension
        
        
        self.Alternatives = {}
        self.Directors = []
        self.Writers = []
           
           
    def copy(self):
        m = MediaInfo(self.Path, self.Filename, self.Extension)
        m.Alternatives = self.Alternatives
        m.Directors = self.Directors
        m.Writers = self.Writers
        m.Genres = self.Genres
        m.Runtime = self.Runtime
        m.TagLine = self.TagLine
        m.Popularity = self.Popularity
        m.Plot = self.Plot
        
        m.ImdbId = self.ImdbId
        m.TheTvDbId = self.TheTvDbId
        m.Title = self.Title
        m.Year = self.Year
        m.Resolution = self.Resolution
        m.Sound = self.Sound
        m.isMovie = self.isMovie
        m.isSerie = self.isSerie
        m.isEpisode = self.isEpisode
        m.Poster = self.Poster
        m.Backdrop = self.Backdrop
        m.Season = self.Season
        m.Episode = self.Episode
        m.SearchString = self.SearchString
        return m
    
    

    def isEnigma2Recording(self, name):
        try:
            f = open(name + ".meta", "r")
            f.close()
        except Exception, ex:
            #print ex
            return False
        return True

    def getEnigma2RecordingName(self, name):
        f = open(name + ".meta", "r")
        f.readline()
        name = f.readline()
        f.close()
        return name

    def isValerieInfoAvailable(self, path):
        try:
            f = open(path + "/valerie.info", "r")
            f.close()
        except Exception, ex:
            #print ex
            return False
        return True

    def getValerieInfo(self, path):
        f = open(path + "/valerie.info", "r")
        name = f.readline()
        f.close()
        return name

    def getValerieInfoLastAccessTime(self, path):
        time = 0
        try:
            f = open(path + "/.access", "r")
            time = int(f.readline())
            f.close()
        except Exception, ex:
            return time #print "no .access"
        return time

    def getValerieInfoAccessTime(self, path):
        time = 0
        if os.path.isfile(path + "/valerie.info"):
            time = os.path.getmtime(path + "/valerie.info")
        return time

    def setValerieInfoLastAccessTime(self, path):
        if os.path.isfile(path + "/valerie.info"):
            time = os.path.getmtime(path + "/valerie.info")
            f = open(path + "/.access", "w")
            time = f.write(str(time)+"\n")
            f.close()
        elif os.path.isfile(path + "/.access"):
            os.remove(path + "/.access")

    def parse(self):
        absFilename = unicode(self.Path) + "/" + unicode(self.Filename) + "." + unicode(self.Extension)
        name = unicode(self.Filename).lower()
        self.SearchString = name
        
        ### Replacements PRE
        for replacement in replace.replacements("pre"):
            #print "[pre] ", replacement[0], " --> ", replacement[1]
            self.SearchString = re.sub(replacement[0], replacement[1], self.SearchString)
        
        #print ":-1: ", self.SearchString
        
        ###
        m = re.search(r'(?P<imdbid>tt\d{7})', name)
        if m and m.group("imdbid"):
            self.ImdbId = m.group("imdbid")
        
        ###  
        m = re.search(r'\s(?P<year>\d{4})\s', name)
        if m and m.group("year"):
            year = int(m.group("year"))
            if year > 1940 and year < 2012:
                self.Year = year
                #self.SearchString = name[:m.start()]
        
        #print ":0: ", self.SearchString
        
        ###    
        m = re.search(r'720p', name)
        if m:
            self.Resolution = "720p"
        else:
            m = re.search(r'1080i', name)
            if m:
                self.Resolution = "1080i"
            else:
                m = re.search(r'1080p', name)
                if m:
                    self.Resolution = "1080p"
        
        ###    
        m = re.search(r'dts', name)
        if m:
            self.Sound = "dts"
        else:
            m = re.search(r'dd5', name)
            if m:
                self.Sound = "ac3"
            else:
                m = re.search(r'ac3', name)
                if m:
                    self.Sound = "ac3"
        
        #nameConverted = name
        
        #####
        #####  s03e05
        #####
        
        if self.Season == -1 or self.Episode == -1:
            m = re.search(r'\Ws(?P<season>\d+)\s?e(?P<episode>\d+)(\D|$)', self.SearchString)
            if m and m.group("season") and m.group("episode"):
                self.isSerie = True
                self.isMovie = False
                
                self.Season = int(m.group("season"))
                self.Episode = int(m.group("episode"))
                
                self.SearchString = re.sub(r's(?P<season>\d+)\s?e(?P<episode>\d+).*', " ", self.SearchString)
        
        #####
        #####  s03e05e06 s03e05-e06
        #####
        
        if self.Season == -1 or self.Episode == -1:
            m = re.search(r'\Ws(?P<season>\d+)\s?e(?P<episode>\d+)[-]?\s?e?(?P<episode2>\d+)(\D|$)', self.SearchString)
            if m and m.group("season") and m.group("episode"):
                self.isSerie = True
                self.isMovie = False
                
                self.Season = int(m.group("season"))
                self.Episode = int(m.group("episode"))
                
                self.SearchString = re.sub(r's(?P<season>\d+)\s?e(?P<episode>\d+)[-]?\s?e?(?P<episode2>\d+).*', " ", self.SearchString)
        
        #####
        #####  3x05
        #####
        
        if self.Season == -1 or self.Episode == -1:  
            m = re.search(r'\D(?P<season>\d+)x(?P<episode>\d+)(\D|$)', self.SearchString)
            if m and m.group("season") and m.group("episode"):
                self.isSerie = True
                self.isMovie = False
                
                self.Season = int(m.group("season"))
                self.Episode = int(m.group("episode"))
                
                self.SearchString = re.sub(r'(?P<season>\d+)x(?P<episode>\d+).*', " ", self.SearchString)
        
        #####
        #####  part 3
        #####
        
        if self.Season == -1 or self.Episode == -1:
            m = re.search(r'\W(part|pt)\s?(?P<episode>\d+)(\D|$)', self.SearchString)
            if m and m.group("episode"):
                self.isSerie = True
                self.isMovie = False
                
                self.Season = int(0)
                self.Episode = int(m.group("episode"))
                
                self.SearchString = re.sub(r'(part|pt)\s?(?P<episode>\d+).*', " ", self.SearchString)
        
        #####
        #####  305
        #####
        
        if self.Season == -1 or self.Episode == -1:
        
            nameConverted = ""
            prevc = "a"
            for c in self.SearchString:
                if (prevc.isdigit() and c.isdigit()) or (prevc.isdigit() is False and c.isdigit() is False):
                    nameConverted += c
                else:
                    nameConverted += " " + c
                prevc = c
            
            print "[[[ ", nameConverted.encode('latin-1')
            
            nameConverted = nameConverted.strip()
            
            m = re.search(r'\D(?P<seasonepisode>\d{3,4})(\D|$)', nameConverted)
            if m and m.group("seasonepisode"):
                se = int(-1)
                s = int(-1)
                e = int(-1)
                
                se = int(m.group("seasonepisode"))
                
                s = se / 100
                e = se % 100
                
                if (s == 2 and e == 64 or s == 7 and e == 20 or s == 10 and e == 80 or s == 0 or s == 19 and e >= 40 or s == 20 and e <= 14) is False:
                    self.isSerie = True
                    self.isMovie = False
                    
                    self.Season = s
                    self.Episode = e
                    
                    self.SearchString = re.sub(r'(?P<seasonepisode>\d{3,4}).*', " ", nameConverted)
        
        if self.Extension == "ts" and self.isEnigma2Recording(absFilename) is True:
            self.SearchString = self.getEnigma2RecordingName(absFilename).strip()
            print ":: ", self.SearchString.encode('latin-1')
            return
        
        if self.isValerieInfoAvailable(self.Path) is True:
            self.SearchString = self.getValerieInfo(self.Path).strip()
            print ":: ", self.SearchString.encode('latin-1')
            return
        
        #print ":1: ", self.SearchString
        ### Replacements POST
        self.SearchString = re.sub(r'[-]', " ", self.SearchString)
        self.SearchString = re.sub(r' +', " ", self.SearchString)
        print ":2: ", self.SearchString.encode('latin-1')
        
        post = "post"
        if self.isSerie:
            post = "post_tv"
        elif self.isMovie:
            post = "post_movie"
            
        for replacement in replace.replacements(post):
            #print "[" + post + "] ", replacement[0], " --> ", replacement[1]
            self.SearchString = re.sub(replacement[0], replacement[1], self.SearchString)
        
        self.SearchString = self.SearchString.strip()
        print ":3: ", self.SearchString.encode('latin-1')
        
    def __str__(self):
        ustr = unicode(self.Path) + " / " + unicode(self.Filename) + " . " + unicode(self.Extension)
        print type(ustr)
        ustr += "\n\tImdbId:       " + unicode(self.ImdbId)
        ustr += "\n\tTheTvDbId:    " + unicode(self.TheTvDbId)
        ustr += "\n\tTitle:        " + self.Title
        ustr += "\n\tSearchString: " + unicode(self.SearchString)
        ustr += "\n\tYear:         " + unicode(self.Year)
        ustr += "\n\tResolution:   " + unicode(self.Resolution)
        ustr += "\n\tSound:        " + unicode(self.Sound)
        #ustr += "\n\tAlternatives: " + unicode(self.Alternatives)
        ustr += "\n\tDirectors:    " + unicode(self.Directors)
        ustr += "\n\tWriters:      " + unicode(self.Writers)
        ustr += "\n\tRuntime:      " + unicode(self.Runtime)
        ustr += "\n\tGenres:       " + unicode(self.Genres)
        ustr += "\n\tTagLine:      " + unicode(self.TagLine)
        ustr += "\n\tPopularity:   " + unicode(self.Popularity)
        ustr += "\n\tPlot:         " + self.Plot
        ustr += "\n\tSeason:       " + unicode(self.Season)
        ustr += "\n\tEpisode:      " + unicode(self.Episode)
        ustr += "\n\n"
        #ustr += "\n\tPoster:       " + unicode(self.Poster)
        #ustr += "\n\tBackdrop:     " + unicode(self.Backdrop)
        #ustr += "\n\n"
        print type(ustr)
        return ustr.encode('latin-1')

    def importStr(self, string, isMovie=False, isSerie=False, isEpisode=False):
        
        self.isMovie = isMovie
        self.isSerie = isSerie
        self.isEpisode = isEpisode
        
        
        d = {} 
        lines = string.split('\n')
        for line in lines: 
            #print "Line: ", line
            if ":" in line: 
                key, value = (s.strip() for s in line.split(":", 1)) 
    
            if key == "ImdbId":
                self.ImdbId = value
            if key == "TheTvDb":
                self.TheTvDbId = value
                
            elif key == "Title":
                self.Title = value
            elif key == "LocalTitle":
                self.Title = value
                
            elif key == "Year":
                self.Year = int(value)
                
            elif key == "Path":
                self.Path, self.Filename = value.rsplit("/", 1)
                #print self.Filename
                self.Filename, self.Extension = self.Filename.rsplit('.', 1)
                
            elif key == "Plot":
                self.Plot = value
            elif key == "LocalPlot":
                self.Plot = value   
            elif key == "Runtime":
                self.Runtime = int(value)  
            elif key == "Tag":
                self.TagLine = value  
            elif key == "Popularity":
                self.Popularity = value  
            elif key == "Season":
                self.Season = int(value)  
            elif key == "Episode":
                self.Episode = int(value)
            
            

    def export(self):
        stri = u'\n---BEGIN---'
        if self.isMovie:
            stri += u'\nImdbId: ' +     unicode(self.ImdbId)
            stri += u'\nTitle: ' +      self.Title
            stri += u'\nLocalTitle: ' + self.Title
            stri += u'\nYear: ' +       unicode(self.Year)
            stri += u'\nPath: ' +       unicode(self.Path) + "/" + unicode(self.Filename) + "." + unicode(self.Extension)
            stri += u'\nPlot: ' +       self.Plot
            stri += u'\nLocalPlot: ' +  self.Plot
            stri += u'\nRuntime: ' +    unicode(self.Runtime)
            stri += u'\nGenres: ' +     unicode(self.Genres)
            stri += u'\nReleasedate: ' + u'2000-01-01'
            stri += u'\nTag: ' +        unicode(self.TagLine)
            stri += u'\nPopularity: ' + unicode(self.Popularity)
            stri += u'\nDirectors: ' +  "---"
            stri += u'\nWriters: ' +    "---"
        elif self.isSerie:
            stri += u'\nImdbId: ' +     unicode(self.ImdbId)
            stri += u'\nTheTvDb: ' +    unicode(self.TheTvDbId)
            stri += u'\nTitle: ' +      self.Title
            stri += u'\nLocalTitle: ' + self.Title
            stri += u'\nYear: ' +       unicode(self.Year)
            stri += u'\nPlot: ' +       self.Plot
            stri += u'\nLocalPlot: ' +  self.Plot
            stri += u'\nRuntime: ' +    unicode(self.Runtime)
            stri += u'\nGenres: ' +     unicode(self.Genres)
            stri += u'\nReleasedate: ' + u'2000-01-01'
            stri += u'\nTag: ' +        unicode(self.TagLine)
            stri += u'\nPopularity: ' + unicode(self.Popularity)
            stri += u'\nDirectors: ' +  "---"
            stri += u'\nWriters: ' +    "---"
        elif self.isEpisode:
            stri += u'\nImdbId: ' +     unicode(self.ImdbId)
            stri += u'\nTheTvDb: ' +    unicode(self.TheTvDbId)
            stri += u'\nTitle: ' +      self.Title
            stri += u'\nLocalTitle: ' + self.Title
            stri += u'\nYear: ' +       unicode(self.Year)
            stri += u'\nPath: ' +       unicode(self.Path) + "/" + unicode(self.Filename) + "." + unicode(self.Extension)
            #print "stri: ", type(stri)
            #print "self.Plot: ", type(self.Plot)
            stri += u'\nPlot: ' +       self.Plot
            stri += u'\nLocalPlot: ' +  self.Plot
            stri += u'\nRuntime: ' +    unicode(self.Runtime)
            stri += u'\nGenres: ' +     unicode(self.Genres)
            stri += u'\nReleasedate: ' + u'2000-01-01'
            stri += u'\nTag: ' +        unicode(self.TagLine)
            stri += u'\nPopularity: ' + unicode(self.Popularity)
            stri += u'\nSeason: ' +     unicode(self.Season)
            stri += u'\nEpisode: ' +    unicode(self.Episode)
            stri += u'\nDirectors: ' +  "---"
            stri += u'\nWriters: ' +    "---"
            
        stri += u'\n----END----\n\n'
        return stri
            
