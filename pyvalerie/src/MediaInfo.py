'''
Created on 21.05.2010

@author: i7
'''
import re

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
    Popularity = 0
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
    
    Season = 0
    Episode = 0
    
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
           
           
           
    def replacements(self):
        l = {}
        l["pre"] = []
        l["post"] = []
        l["pre"].append([r' (dd5|web|hdtv|dimension|avi|vob|dth|vc1|ac3d|dl|extcut|mkv|nhd|576p|720p|1080p|1080i|dircut|directors cut|dvdrip|dvdscreener|dvdscr|avchd|wmv|ntsc|pal|mpeg|dsr|hd|r5|dvd|dvdr|dvd5|dvd9|bd5|bd9|dts|ac3|bluray|blu-ray|hdtv|pdtv|stv|hddvd|xvid|divx|x264|dxva|m2ts|FESTIVAL|LIMITED|WS|FS|PROPER|REPACK|RERIP|REAL|RETAIL|EXTENDED|REMASTERED|UNRATED|CHRONO|THEATRICAL|DC|SE|UNCUT|INTERNAL|DUBBED|SUBBED)'," "])
        return l   
    
    def isEnigma2Recording(self, name):
        try:
            f = open(name + ".meta", "r")
            f.close()
        except Exception, ex:
            print ex
            return False
        return True
        
    def getEnigma2RecordingName(self, name):
        f = open(name + ".meta", "r")
        f.readline()
        name = f.readline()
        f.close()
        return name
 
    
    def parse(self):
        absFilename = str(self.Path) + "/" + str(self.Filename) + "." + str(self.Extension)
        if self.isEnigma2Recording(absFilename) is True:
            self.SearchString = self.getEnigma2RecordingName(absFilename).strip()
            return
        
        
        name = str(self.Filename).lower()
        
        name = re.sub(r'[.]', " ", name)
        
        ### Replacements PRE
        self.SearchString = name
        for replacement in self.replacements()["pre"]:
            self.SearchString = re.sub(replacement[0], replacement[1], self.SearchString)
        self.SearchString = self.SearchString.strip()
        
        ###
        m = re.search(r'(?P<imdbid>tt\d{7})', name)
        if m and m.group("imdbid"):
            self.ImdbId = m.group("imdbid")
            
        ###  
        m = re.search(r'\D(?P<year>\d{4})\D', name)
        if m and m.group("year"):
            self.Year = int(m.group("year"))
            self.SearchString = name[:m.start()]
            
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
                
        if self.Season == 0 or self.Episode == 0:
            m = re.search(r' s(?P<season>\d+)\D?e\D?(?P<episode>\d+)', name)
            if m and m.group("season") and m.group("episode"):
                self.isEpisode = True
                self.isMovie = False
                
                self.Season = int(m.group("season"))
                self.Episode = int(m.group("episode"))
                
                self.SearchString = re.sub(r' s(?P<season>\d+)\D?e\D?(?P<episode>\d+).*', " ", self.SearchString)
              
        if self.Season == 0 or self.Episode == 0:  
            m = re.search(r' (?P<season>\d+)\D?x\D?(?P<episode>\d+)', name)
            if m and m.group("season") and m.group("episode"):
                self.isEpisode = True
                self.isMovie = False
                
                self.Season = int(m.group("season"))
                self.Episode = int(m.group("episode"))
                
                self.SearchString = re.sub(r' (?P<season>\d+)\D?x\D?(?P<episode>\d+).*', " ", self.SearchString)
                
        if self.Season == 0 or self.Episode == 0:
            m = re.search(r'(?P<season>\d{1,2})(?P<episode>\d{2})', name)
            if m and m.group("season") and m.group("episode"):
                self.isEpisode = True
                self.isMovie = False
                
                self.Season = int(m.group("season"))
                self.Episode = int(m.group("episode"))
                
                self.SearchString = re.sub(r'(?P<season>\d{1,2})(?P<episode>\d{2}).*', " ", self.SearchString)
                    
        ### Replacements POST
        self.SearchString = re.sub(r'[-]', " ", self.SearchString)
        self.SearchString = re.sub(r' +', " ", self.SearchString)
        self.SearchString = self.SearchString.strip()
            
    def __str__(self):
        return str(self.Path) + " / " + str(self.Filename) + " . " + str(self.Extension) + \
    "\n\tImdbId:       " + str(self.ImdbId) + \
    "\n\tTheTvDbId:    " + str(self.TheTvDbId) + \
    "\n\tTitle:        " + str(self.Title) + \
    "\n\tSearchString: " + str(self.SearchString) + \
    "\n\tYear:         " + str(self.Year) + \
    "\n\tResolution:   " + str(self.Resolution) + \
    "\n\tSound:        " + str(self.Sound) + \
    "\n\tAlternatives: " + str(self.Alternatives) + \
    "\n\tDirectors:    " + str(self.Directors) + \
    "\n\tWriters:      " + str(self.Writers) + \
    "\n\tRuntime:      " + str(self.Runtime) + \
    "\n\tGenres:       " + str(self.Genres) + \
    "\n\tTagLine:      " + str(self.TagLine) + \
    "\n\tPopularity:   " + str(self.Popularity) + \
    "\n\tPlot:         " + str(self.Plot) + \
    "\n\tSeason:       " + str(self.Season) + \
    "\n\tEpisode:      " + str(self.Episode) + \
    "\n\tPoster:       " + str(self.Poster) + \
    "\n\tBackdrop:     " + str(self.Backdrop) + \
    "\n\n"
