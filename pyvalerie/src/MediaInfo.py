'''
Created on 21.05.2010

@author: i7
'''
import re
import replace
import Utf8
import os

class MediaInfo(object):
    '''
    classdocs
    '''

    isMovie   = False
    isSerie   = False
    isEpisode = False
    
    LanguageOfPlot = u"en"
    
    Path         = u""
    Filename     = u""
    Extension    = u""
    SearchString = u""
    
    Title = u""
    Alternatives = {}
    
    Year = 0
    ImdbIdNull = u"tt0000000"
    ImdbId     = ImdbIdNull
    TheTvDbIdNull = u"0"
    TheTvDbId     = TheTvDbIdNull
    TmDbIdNull = u"0"
    TmDbId     = TmDbIdNull
    
    Runtime    = 0
    Resolution = u"576"
    Sound      = u"Stereo"
    Plot       = u""
    
    Directors  = []
    Writers    = []
    Genres     = u""
    Tag        = u""
    Popularity = 0
    
    Season  = -1
    Episode = -1
    
    Poster = u""
    Backdrop = u""
    Banner = u""

    def __init__(self, path, filename, extension):
        '''
        Constructor
        '''
        self.Path      = path
        self.Filename  = filename
        self.Extension = extension
        
        
        self.Alternatives = {}
        self.Directors    = []
        self.Writers      = []
           
           
    def copy(self):
        m = MediaInfo(self.Path, self.Filename, self.Extension)
        
        m.Alternatives = self.Alternatives
        m.Directors    = self.Directors
        m.Writers      = self.Writers
        m.Genres       = self.Genres
        m.Runtime      = self.Runtime
        m.Tag          = self.Tag
        m.Popularity   = self.Popularity
        m.Plot         = self.Plot
        
        m.ImdbId       = self.ImdbId
        m.TheTvDbId    = self.TheTvDbId
        m.Title        = self.Title
        m.Year         = self.Year
        m.Resolution   = self.Resolution
        m.Sound        = self.Sound
        m.isMovie      = self.isMovie
        m.isSerie      = self.isSerie
        m.isEpisode    = self.isEpisode
        m.Poster       = self.Poster
        m.Backdrop     = self.Backdrop
        m.Season       = self.Season
        m.Episode      = self.Episode
        m.SearchString = self.SearchString
        return m
    
    

    def isEnigma2Recording(self, name):
        if os.path.isfile(Utf8.utf8ToLatin(name + u".meta")):
            return True
        return False

    def getEnigma2RecordingName(self, name):
        f = Utf8.Utf8(name + u".meta", "r")
        lines = f.read()
        if lines is not None:
            lines = lines.split(u"\n")
            name = None
            if len(lines) >= 2:
                name = lines[1]
        f.close()
        return name

    def isValerieInfoAvailable(self, path):
        if os.path.isfile(Utf8.utf8ToLatin(path + u"/valerie.info")):
            return True
        return False

    def getValerieInfo(self, path):
        f = Utf8.Utf8(path + u"/valerie.info", "r")
        lines = f.read()
        if lines is not None:
            lines = lines.split(u"\n")
            name = None
            if len(lines) >= 1:
                name = lines[0]
        f.close()
        return name

    def getValerieInfoLastAccessTime(self, path):
        time = 0
        if os.path.isfile(Utf8.utf8ToLatin(path + u"/.access")):
            f = Utf8.Utf8(path + u"/.access", "r")
            lines = f.read()
            if lines is not None:
                lines = lines.split(u"\n")
                if len(lines) >= 1:
                    try:
                        time = int(lines[0])
                    except Exception, ex:
                        print ex
            f.close()
        return time

    def getValerieInfoAccessTime(self, path):
        time = 0
        if os.path.isfile(Utf8.utf8ToLatin(path + u"/valerie.info")):
            try:
                time = os.path.getmtime(Utf8.utf8ToLatin(path + u"/valerie.info"))
            except Exception, ex:
                print ex
        return time

    def setValerieInfoLastAccessTime(self, path):
        if os.path.isfile(Utf8.utf8ToLatin(path + u"/valerie.info")):
            time = os.path.getctime(Utf8.utf8ToLatin(path + u"/valerie.info"))
            f = Utf8.Utf8(path + u"/.access", "w")
            time = f.write(str(time) + u"\n")
            f.close()
        elif os.path.isfile(Utf8.utf8ToLatin(path + u"/.access")):
            os.remove(Utf8.utf8ToLatin(path + u"/.access"))



    def parse(self):
        absFilename = self.Path + u"/" + self.Filename + u"." + self.Extension
        name = self.Filename.lower()
        self.SearchString = name
        
        ### Replacements PRE
        for replacement in replace.replacements(u"pre"):
            #print "[pre] ", replacement[0], " --> ", replacement[1]
            self.SearchString = re.sub(replacement[0], replacement[1], self.SearchString)
        
        print ":-1: ", Utf8.utf8ToLatin(self.SearchString)
        
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
                # removing year from searchstring
                self.SearchString = re.sub(str(year), u" ", self.SearchString)
                #self.SearchString = name[:m.start()]
        
        #print ":0: ", self.SearchString
        
        ###    
        m = re.search(r'720p', name)
        if m:
            self.Resolution = u"720p"
        else:
            m = re.search(r'1080i', name)
            if m:
                self.Resolution = u"1080i"
            else:
                m = re.search(r'1080p', name)
                if m:
                    self.Resolution = u"1080p"
        
        ###    
        m = re.search(r'dts', name)
        if m:
            self.Sound = u"dts"
        else:
            m = re.search(r'dd5', name)
            if m:
                self.Sound = u"ac3"
            else:
                m = re.search(r'ac3', name)
                if m:
                    self.Sound = u"ac3"
        
        #nameConverted = name
        
        if self.isMovie is False:
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
                  
                    self.SearchString = re.sub(r's(?P<season>\d+)\s?e(?P<episode>\d+).*', u" ", self.SearchString)
          
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
                  
                    self.SearchString = re.sub(r's(?P<season>\d+)\s?e(?P<episode>\d+)[-]?\s?e?(?P<episode2>\d+).*', u" ", self.SearchString)
          
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
                  
                    self.SearchString = re.sub(r'(?P<season>\d+)x(?P<episode>\d+).*', u" ", self.SearchString)
          
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
                  
                    self.SearchString = re.sub(r'(part|pt)\s?(?P<episode>\d+).*', u" ", self.SearchString)
          
            #####
            #####  305
            #####
          
            if self.Season == -1 or self.Episode == -1:
          
                nameConverted = u""
                prevc = u"a"
                for c in self.SearchString:
                    if (prevc.isdigit() and c.isdigit()) or (prevc.isdigit() is False and c.isdigit() is False):
                        nameConverted += c
                    else:
                        nameConverted += " " + c
                    prevc = c
              
                print "[[[ ", Utf8.utf8ToLatin(nameConverted)
              
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
                      
                        self.SearchString = re.sub(r'(?P<seasonepisode>\d{3,4}).*', u" ", nameConverted)
        
        if self.Extension == u"ts" and self.isEnigma2Recording(absFilename) is True:
            self.SearchString = self.getEnigma2RecordingName(absFilename).strip()
            print ":: ", Utf8.utf8ToLatin(self.SearchString)
            return True
        
        if self.isValerieInfoAvailable(self.Path) is True:
            self.SearchString = self.getValerieInfo(self.Path).strip()
            print ":: ", Utf8.utf8ToLatin(self.SearchString)
            if self.SearchString == u"ignore":
                return False
            return True
        
        if self.isSerie == False:
            self.isMovie = True
        
        #print ":1: ", self.SearchString
        ### Replacements POST
        self.SearchString = re.sub(r'[-]', u" ", self.SearchString)
        self.SearchString = re.sub(r' +', u" ", self.SearchString)
        print ":2: ", Utf8.utf8ToLatin(self.SearchString)
        
        post = u"post"
        if self.isSerie:
            post = u"post_tv"
        elif self.isMovie:
            post = u"post_movie"
            
        for replacement in replace.replacements(post):
            #print "[" + post + "] ", replacement[0], " --> ", replacement[1]
            self.SearchString = re.sub(replacement[0], replacement[1], self.SearchString)
        
        self.SearchString = self.SearchString.strip()
        print ":3: ", Utf8.utf8ToLatin(self.SearchString)
        
        return True
    
    def __str__(self):
        ustr = self.Path + u" / " + self.Filename + u" . " + self.Extension
        print type(ustr)
        ustr += u"\n\tImdbId:       " + self.ImdbId
        ustr += u"\n\tTheTvDbId:    " + self.TheTvDbId
        ustr += u"\n\tTitle:        " + self.Title
        ustr += u"\n\tSearchString: " + self.SearchString
        ustr += u"\n\tYear:         " + unicode(self.Year)
        ustr += u"\n\tResolution:   " + self.Resolution
        ustr += u"\n\tSound:        " + self.Sound
        #ustr += "\n\tAlternatives: " + unicode(self.Alternatives)
        ustr += "\n\tDirectors:    " + unicode(self.Directors)
        ustr += "\n\tWriters:      " + unicode(self.Writers)
        ustr += "\n\tRuntime:      " + unicode(self.Runtime)
        ustr += "\n\tGenres:       " + unicode(self.Genres)
        ustr += "\n\tTagLine:      " + self.Tag
        ustr += "\n\tPopularity:   " + unicode(self.Popularity)
        ustr += "\n\tPlot:         " + self.Plot
        ustr += "\n\tSeason:       " + unicode(self.Season)
        ustr += "\n\tEpisode:      " + unicode(self.Episode)
        ustr += "\n\n"
        #ustr += "\n\tPoster:       " + unicode(self.Poster)
        #ustr += "\n\tBackdrop:     " + unicode(self.Backdrop)
        #ustr += "\n\n"
        print type(ustr)
        return Utf8.utf8ToLatin(ustr)

    def importStr(self, string, isMovie=False, isSerie=False, isEpisode=False):
        
        self.isMovie = isMovie
        self.isSerie = isSerie
        self.isEpisode = isEpisode
        
        lines = string.split(u'\n')
        for line in lines: 
            #print "Line: ", line
            if u":" in line: 
                key, value = (s.strip() for s in line.split(u":", 1)) 
    
            if key == u"ImdbId":
                self.ImdbId = value
            if key == u"TheTvDb":
                self.TheTvDbId = value
                
            elif key == u"Title":
                self.Title = value
                
            elif key == u"Year":
                if len(value) > 0:
                    try:
                        self.Year = int(value)
                    except Exception, ex:
                        print "-"*30
                        print value
                        print ex
                        print "-"*30
                        self.Year = 0
                else:
                    self.Year = 0
                
            elif key == u"Path":
                self.Path, self.Filename = value.rsplit(u"/", 1)
                #print self.Filename
                self.Filename, self.Extension = self.Filename.rsplit(u'.', 1)
                
            elif key == u"Plot":
                self.Plot = value
            elif key == u"Runtime":
                if len(value) > 0:
                    value = value.replace(u"min", "").strip()
                    try:
                        self.Runtime = int(value)
                    except Exception, ex:
                        print "-"*30
                        print value
                        print ex
                        print "-"*30
                        self.Runtime = 0
                else:
                    self.Runtime = 0
            elif key == u"Tag":
                self.Tag = value  
            elif key == u"Popularity":
                if len(value) > 0:
                    try:
                        self.Popularity = int(value)
                    except Exception, ex:
                        print "-"*30
                        print value
                        print ex
                        print "-"*30
                        self.Popularity = 0
                else:
                    self.Popularity = 0
            elif key == u"Season":
                if len(value) > 0:
                    try:
                        self.Season = int(value)
                    except Exception, ex:
                        print "-"*30
                        print value
                        print ex
                        print "-"*30
                        self.Season = 0
                else:
                    self.Season = 0
            elif key == u"Episode":
                if len(value) > 0:
                    try:
                        self.Episode = int(value)
                    except Exception, ex:
                        print "-"*30
                        print value
                        print ex
                        print "-"*30
                        self.Episode = 0
                else:
                    self.Episode = 0

    def export(self):
        stri = u'\n---BEGIN---'
        if self.isMovie:
            stri += u'\nImdbId: ' +     self.ImdbId
            stri += u'\nTitle: ' +      self.Title
            stri += u'\nYear: ' +       unicode(self.Year)
            stri += u'\nPath: ' +       self.Path + u"/" + self.Filename + u"." + self.Extension
            stri += u'\nPlot: ' +       self.Plot
            stri += u'\nRuntime: ' +    unicode(self.Runtime)
            stri += u'\nGenres: ' +     self.Genres
            stri += u'\nReleasedate: ' + u'2000-01-01'
            stri += u'\nTag: ' +        self.Tag
            stri += u'\nPopularity: ' + unicode(self.Popularity)
            stri += u'\nDirectors: ' +  u"---"
            stri += u'\nWriters: ' +    u"---"
        elif self.isSerie:
            stri += u'\nImdbId: ' +     self.ImdbId
            stri += u'\nTheTvDb: ' +    self.TheTvDbId
            stri += u'\nTitle: ' +      self.Title
            stri += u'\nYear: ' +       unicode(self.Year)
            stri += u'\nPlot: ' +       self.Plot
            stri += u'\nRuntime: ' +    unicode(self.Runtime)
            stri += u'\nGenres: ' +     self.Genres
            stri += u'\nReleasedate: ' + u'2000-01-01'
            stri += u'\nTag: ' +        self.Tag
            stri += u'\nPopularity: ' + unicode(self.Popularity)
            stri += u'\nDirectors: ' +  u"---"
            stri += u'\nWriters: ' +    u"---"
        elif self.isEpisode:
            stri += u'\nImdbId: ' +     self.ImdbId
            stri += u'\nTheTvDb: ' +    self.TheTvDbId
            stri += u'\nTitle: ' +      self.Title
            stri += u'\nYear: ' +       unicode(self.Year)
            stri += u'\nPath: ' +       self.Path + u"/" + self.Filename + u"." + self.Extension
            #print "stri: ", type(stri)
            #print "self.Plot: ", type(self.Plot)
            stri += u'\nPlot: ' +       self.Plot
            stri += u'\nRuntime: ' +    unicode(self.Runtime)
            stri += u'\nGenres: ' +     self.Genres
            stri += u'\nReleasedate: ' + u'2000-01-01'
            stri += u'\nTag: ' +        self.Tag
            stri += u'\nPopularity: ' + unicode(self.Popularity)
            stri += u'\nSeason: ' +     unicode(self.Season)
            stri += u'\nEpisode: ' +    unicode(self.Episode)
            stri += u'\nDirectors: ' +  u"---"
            stri += u'\nWriters: ' +    u"---"
            
        stri += u'\n----END----\n\n'
        return stri
            
