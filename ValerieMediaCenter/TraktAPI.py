
import urllib
import urllib2

class TraktAPI():
	URL = "http://api.trakt.tv"

	STATUS_IDLE     = "idle"
	STATUS_WATCHING = "watching"
	STATUS_WATCHED  = "watched"

	TYPE_TVSHOW = "TVShow"
	TYPE_MOVIE  = "Movie"

	mStatus     = STATUS_IDLE
	mMovieName  = ""
	mYear       = 0
	mSeason     = 0
	mEpisode    = 0
	mType       = TYPE_TVSHOW

	mUsername   = "noname"
	mPassword   = "nopass"
		
	def setStatus(self, status):
		self.mStatus = status

	def setName(self, name):
		self.mMovieName = name

	def setSeasonAndEpisode(self, season, episode):
		self.mSeason = season
		self.mEpisode = episode

	def setYear(self, year):
		self.mYear = year

	def setType(self, type):
		self.mType = type

	def setUsernameAndPassword(self, user, passwd):
		self.mUsername = user
		self.mPassword = passwd

	def send(self):
	
		
		if self.mType == self.TYPE_MOVIE:
			toSend = urllib.urlencode({
				"type":     self.TYPE_MOVIE,
				"status":   self.mStatus, 
				"title":    self.mMovieName, 
				"year":     self.mYear, 
				"username": self.mUsername, 
				"password": self.mPassword,
				"media_center": 'pvmc',
				"media_center_version": '1.0',
				"media_center_date": '1970-01-01'
			})
		elif self.mType == self.TYPE_TVSHOW:
			toSend = urllib.urlencode({
				"type":     self.TYPE_TVSHOW,
				"status":   self.mStatus, 
				"title":    self.mMovieName, 
				"year":     self.mYear, 
				"season":   self.mSeason,
				"episode":  self.mEpisode,
				"username": self.mUsername, 
				"password": self.mPassword,
				"media_center": 'pvmc',
				"media_center_version": '1.0',
				"media_center_date": '1970-01-01'
			})
		
		print "TOSEND", toSend
		
		req = urllib2.Request(self.URL,
			toSend, 
			headers = {"Accept": "*/*",
				"User-Agent": "Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)",
		})
		
		f = urllib2.urlopen(req)
		answer = f.read()
		print "ANSWER=", answer
		
