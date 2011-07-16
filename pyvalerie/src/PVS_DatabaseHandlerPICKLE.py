# -*- coding: utf-8 -*-
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#   PVS_DatabaseHandlerPICKLE.py
#   Project Valerie - Database Handler for PICKLE
#
#   Created by Zuki on 20/05/2011.
#   Interface for working with PICKLE Files
#   
#   Revisions:
#   v0 - ../06/2011 - Zuki - Let's import the Pickle Interface from database.py
#
#   v1 - 15/07/2011 - Zuki - added Config Record to pickle's to save the structure version
#			   - added Upgrade Database function's (to apply conversions)
#
#   v2 - 16/07/2011 - Zuki - upgrade database is now working
#			     DB Patch 1 will update fields MediaInfo.MediaType
#
#   v
#
#   v
#
#   v
#
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

import os
import time
import cPickle   as pickle
from Components.config import config
from   MediaInfo         import MediaInfo
from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl
from Plugins.Extensions.ProjectValerie.__common__ import log as log

gDatabaseHandler = None
gConnection = None

class databaseHandlerPICKLE(object):
	DB_PATH           = config.plugins.pvmc.configfolderpath.value

	FAILEDDB   = DB_PATH + "failed.db"
	MOVIESDB   = DB_PATH + "movies.db"
	TVSHOWSDB  = DB_PATH + "tvshows.db"
	EPISODESDB = DB_PATH + "episodes.db"

	TESTDB     = DB_PATH + "test.db"
	CONFIGKEY  = -999999
	DB_VERSION = 1
	IDMODEAUTO = False	

	def __init__(self):
		printl("->", self)
		
	def getInstance(self):
		printl("", self, "D")
		global gDatabaseHandler
		if gDatabaseHandler is None:			
			printl("PICKLE - New Instance", self)
			gDatabaseHandler = self
		return gDatabaseHandler

#########################################################################

	def getAllMovies(self):
		printl("->", self)
		records = {}
		try:
			if os.path.exists(self.MOVIESDB):
				fd = open(self.MOVIESDB, "rb")
				records = pickle.load(fd)
				fd.close()
				#for key in records:
				#	if type(records[key]) is MediaInfo:
				#		log("Rec: "+str(key)+" IsMovie:" + str(records[key].isMovie) + " mediatype:" + str(records[key].MediaType)  )
				self._upgradeMovies(records)
			else:
				self.setDBVersion(records, self.DB_VERSION)

		except Exception, ex:
			print ex
			print '-'*60
			import sys, traceback
			traceback.print_exc(file=sys.stdout)
			print '-'*60
				
		return (records)
		
	def getAllSeries(self):
		printl("->", self)
		records = {}
		try:
			if os.path.exists(self.TVSHOWSDB):
				fd = open(self.TVSHOWSDB, "rb")
				records = {}
				records = pickle.load(fd)
				fd.close()
				#for key in records:
				#	if type(records[key]) is MediaInfo:
				#		log("Rec: "+str(key)+" IsSerie:" + str(records[key].isSerie) + " mediatype:" + str(records[key].MediaType) )
				self._upgradeSeries(records)
			else:
				self.setDBVersion(records, self.DB_VERSION)
				
		except Exception, ex:
			print ex
			print '-'*60
			import sys, traceback
			traceback.print_exc(file=sys.stdout)
			print '-'*60
		
		return (records)

	def getAllEpisodes(self):
		printl("->", self)
		records = {}
		try:
			if os.path.exists(self.EPISODESDB):
				fd = open(self.EPISODESDB, "rb")
				records = pickle.load(fd)
				fd.close()
				for serie in records:
					if serie != self.CONFIGKEY: #not ConfigRecord
						for season in records[serie]:
							for episode in records[serie][season]:
								if type(records[serie][season][episode]) is MediaInfo:
									log("Rec: "+str(episode)+" IsEpisode:"  + str(records[serie][season][episode].isEpisode) + " mediatype:" + str(records[serie][season][episode].MediaType) )
				self._upgradeEpisodes(records)
			else:
				self.setDBVersion(records, self.DB_VERSION)
				
		except Exception, ex:
			print ex
			print '-'*60
			import sys, traceback
			traceback.print_exc(file=sys.stdout)
			print '-'*60

		return (records)


	def getFailedFiles(self):
		printl("->", self)
		start_time = time.time()
		records = []
		try:		
			if os.path.exists(self.FAILEDDB):
				fd = open(self.FAILEDDB, "rb")
				records = pickle.load(fd)
				fd.close()
			
		except Exception, ex:
			print ex
			print '-'*60
			import sys, traceback
			traceback.print_exc(file=sys.stdout)
			print '-'*60
		
		elapsed_time = time.time() - start_time
		printl("Took (failed.db): " + str(elapsed_time), self)
		
		return (records)


	def saveMovies(self, records):		
		printl("->", self)
		start_time = time.time()
		try:		
			fd = open(self.MOVIESDB, "wb")
			pickle.dump(records, fd, pickle.HIGHEST_PROTOCOL)
			fd.close()
			
		except Exception, ex:
			print ex
			print '-'*60
			import sys, traceback
			traceback.print_exc(file=sys.stdout)
			print '-'*60
		
		elapsed_time = time.time() - start_time
		printl("Took (movies.db): " + str(elapsed_time), self)
		
	def saveSeries(self, records):
		
		printl("->", self)
		start_time = time.time()
		try:		
			fd = open(self.TVSHOWSDB, "wb")
			pickle.dump(records, fd, pickle.HIGHEST_PROTOCOL)
			fd.close()
			
		except Exception, ex:
			print ex
			print '-'*60
			import sys, traceback
			traceback.print_exc(file=sys.stdout)
			print '-'*60
		
		elapsed_time = time.time() - start_time
		printl("Took (tvshows.db): " + str(elapsed_time), self)
		
	def saveEpisodes(self, records):
		
		printl("->", self)
		start_time = time.time()
		try:		
			fd = open(self.EPISODESDB, "wb")
			pickle.dump(records, fd, pickle.HIGHEST_PROTOCOL)
			fd.close()
			
		except Exception, ex:
			print ex
			print '-'*60
			import sys, traceback
			traceback.print_exc(file=sys.stdout)
			print '-'*60
		
		elapsed_time = time.time() - start_time
		printl("Took (episodes.db): " + str(elapsed_time), self)
		
	def saveFailed(self, records):
		printl("->", self)
		start_time = time.time()
		try:		
			fd = open(self.FAILEDDB, "wb")
			pickle.dump(records, fd, pickle.HIGHEST_PROTOCOL)
			fd.close()
		except Exception, ex:
			print ex
			print '-'*60
			import sys, traceback
			traceback.print_exc(file=sys.stdout)
			print '-'*60
	
		elapsed_time = time.time() - start_time
		printl("Took (failed.db): " + str(elapsed_time), self)
		
	def saveFailed2(self, records):
		pass
	
############################  DB VERSION CONTROL  #############################
	def getDBVersion(self, records):
		if records.has_key(self.CONFIGKEY):
			return records[self.CONFIGKEY]
		else:
			printl ("DB without version")
			return 0
		
	def setDBVersion(self, records, version):
		records[self.CONFIGKEY] = version
		printl ("DB version set to "+ str(version))
		
############################    UPGRADE MOVIES    #############################
	def _upgradeMovies(self, records):
		printl("->",self)
		currentDBVersion = self.getDBVersion(records)
		printl("DBVersion: " + str(currentDBVersion))
		if self.DB_VERSION == currentDBVersion:
			printl("DB already updated!")
		else:
			printl("Upgrading database to version: " + str(self.DB_VERSION) )
			#   Let's run some Upgrade Scripts... :)
			for updateToVersion in range(currentDBVersion+1, self.DB_VERSION+1):
				printl("Applying upgrade to version : " + str(updateToVersion))
				if updateToVersion==1:
					self._upgrade_m_1(records)
					self.setDBVersion(records, updateToVersion)
					
				elif updateToVersion==2:
					#self._upgrade_m_2(records)
					#self.setDBVersion(records, updateToVersion)
					pass
				elif updateToVersion==3:
					pass		
				elif updateToVersion==4:
					pass
				elif updateToVersion==5:
					pass
				elif updateToVersion==6:
					pass
				
			self.saveMovies(records)
	
	# Migrate isMovie,isSerie,isEpisode to MediaType (1,2,3)
	# can be used by movies.db and tvshows.db
	def _upgrade_m_1(self, records):
		for rec in records:
			if type(records[rec]) is MediaInfo:
				records[rec].getMediaType() # will populate mediatype field
			
	def _upgrade_m_2(self, records):
		pass
	
############################    UPGRADE SERIES    #############################
	def _upgradeSeries(self, records):
		printl("->",self)
		currentDBVersion = self.getDBVersion(records)
		printl("DBVersion: " + str(currentDBVersion))
		if self.DB_VERSION == currentDBVersion:
			printl("DB already updated!")
		else:
			printl("Upgrading database to version: " + str(self.DB_VERSION) )
			#   Let's run some Upgrade Scripts... :)
			for updateToVersion in range(currentDBVersion+1, self.DB_VERSION+1):
				printl("Applying upgrade to version : " + str(updateToVersion))
				if updateToVersion==1:
					self._upgrade_m_1(records) #use Movies upgrade
					self.setDBVersion(records, updateToVersion)
					
				elif updateToVersion==2:
					pass
				elif updateToVersion==3:
					pass
				elif updateToVersion==4:
					pass
				elif updateToVersion==5:
					pass
				elif updateToVersion==6:
					pass
				
			self.saveSeries(records)
	
	def _upgrade_s_2(self, records):
		pass
	
############################    UPGRADE EPISODES    #############################
	def _upgradeEpisodes(self, records):
		printl("->",self)
		currentDBVersion = self.getDBVersion(records)
		printl("DBVersion: " + str(currentDBVersion))
		if self.DB_VERSION == currentDBVersion:
			printl("DB already updated!")
		else:
			printl("Upgrading database to version: " + str(self.DB_VERSION) )
			#   Let's run some Upgrade Scripts... :)
			for updateToVersion in range(currentDBVersion+1, self.DB_VERSION+1):
				printl("Applying upgrade to version : " + str(updateToVersion))
				if updateToVersion==1:
					self._upgrade_e_1(records) #use Movies upgrade
					self.setDBVersion(records, updateToVersion)
				elif updateToVersion==2:
					pass					
				elif updateToVersion==3:
					pass
				elif updateToVersion==4:
					pass
				elif updateToVersion==5:
					pass
				elif updateToVersion==6:
					pass

			self.saveEpisodes(records)


	def _upgrade_e_1(self, records):
		for serie in records:
			for season in records[serie]:
				for episode in records[serie][season]:
					if type(records[serie][season][episode]) is MediaInfo:
						records[serie][season][episode].getMediaType() # will populate mediatype field
			







#########################################################################
		#self.doTest_DuplicateTestDB()
		#printl("TEST 1 ************************************************", self)
		#self.doTest_Speed()
		#printl("TEST 2 ************************************************", self)
		#self.doTest_Speed()
		#printl("TEST 3 ************************************************", self)
		#self.doTest_Speed()
		#printl("TEST 4 ************************************************", self)
		#self.doTest_Speed()
		#printl("TEST 5 ************************************************", self)
		
	def doTest_DuplicateTestDB(self):
		printl("->", self)
		start_time = time.time()
		if os.path.exists(self.TESTDB):
			fd = open(self.TESTDB, "rb")
			records = pickle.load(fd)
			fd.close()
		elapsed_time = time.time() - start_time
		printl("Read Took (TESTDB): " + str(elapsed_time), self)

		cnt=0			
		db2 = {}
		start_time = time.time()
		for key in records:
			db2[cnt] = records[key]
			cnt+=1
		for key in records:
			db2[cnt] = records[key]
			cnt+=1
		elapsed_time = time.time() - start_time
		printl("final DB: "+str(cnt)+" records. Took: " + str(elapsed_time), self)

		start_time = time.time()
		fd = open(self.TESTDB, "wb")
		pickle.dump(db2, fd, pickle.HIGHEST_PROTOCOL)
		fd.close()
		elapsed_time = time.time() - start_time
		printl("Write New TestDB. Took : " + str(elapsed_time), self)
		
	def doTest_Speed(self):
		printl("->", self)
		start_time = time.time()
		if os.path.exists(self.TESTDB):
			fd = open(self.TESTDB, "rb")
			records = pickle.load(fd)
			fd.close()
		elapsed_time = time.time() - start_time
		printl("Read test.db with " +str(len(records))+" records. Took: " + str(elapsed_time), self)

		start_time = time.time()
		cnt=0
		for key in records:
			records[key].Id = "blab1341414141cvbgdfghdfg24123123123la"
			cnt+=1
		elapsed_time = time.time() - start_time
		printl("change "+str(cnt)+" records, Took : " + str(elapsed_time), self)

		start_time = time.time()
		cnt=0
		for key in records:
			if records.has_key(key):
				records[key].Id = "blab1341414141cvbgdfghdfg24123123123lb"
				cnt+=1
		elapsed_time = time.time() - start_time
		printl("Change "+str(cnt)+" records, using -Has_key- Took : " + str(elapsed_time), self)

		start_time = time.time()
		cnt=0
		for key in records:
			if key in records:
				records[key].Id = "blab1341414141cvbgdfghdfg24123123123lc"
				cnt+=1
		elapsed_time = time.time() - start_time
		printl("Change "+str(cnt)+" records, using -key in- Took : " + str(elapsed_time), self)

		dbTest = {}
		start_time = time.time()
		cnt=0
		for key in records:
			dbTest[key] = records[key]
			cnt+=1
			
		elapsed_time = time.time() - start_time
		printl("Duplicate "+str(cnt)+" records, Took : " + str(elapsed_time), self)

		for key in records:
			if records[key].ImdbId == "tt99009900":
				records[key].Id = "blab1341414141cvbgdfghdfg24123123123lb"
				cnt+=1
		elapsed_time = time.time() - start_time
		printl("Query "+str(cnt)+" records, using -if equal- Took : " + str(elapsed_time), self)

