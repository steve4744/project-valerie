# -*- coding: utf-8 -*-

import os

from Plugins.Extensions.ProjectValerie.DMC_Library import DMC_Library

from Plugins.Extensions.ProjectValerie.__common__ import printl2 as printl
from Plugins.Extensions.ProjectValerie.__plugin__ import Plugin, registerPlugin

#------------------------------------------------------------------------------------------

# +++ LAZY IMPORTS +++
Manager = None
utf8ToLatin = None
# --- LAZY IMPORTS ---

gAvailable = True

class DMC_JamendoLibrary(DMC_Library):

    top50 = """http://api.jamendo.com/get2/id+stream+name+album_name+album_id+album_genre+artist_id+artist_name+duration/track/xml/track_album+album_artist/?n=50&order=ratingmonth_desc"""

    def __init__(self, session):
        DMC_Library.__init__(self, session, "jamendo")

    ###
    # Return Value is expected to be:
    # (libraryArray, onEnterPrimaryKeys, onLeavePrimaryKeys, onLeaveSelectEntry
    def loadLibrary(self, primaryKeyValuePair):
        global utf8ToLatin
        if utf8ToLatin is None:
            from Plugins.Extensions.ProjectValerieSync.Utf8 import utf8ToLatin
        from  Plugins.Extensions.ProjectValerieSync.WebGrabber import getFile
        from Plugins.Extensions.ProjectValerieSync.Xml2Dict import Xml2Dict
        
        # Diplay all TVShows
        if primaryKeyValuePair is None:
            parsedLibrary = []
            
            #parsedLibrary.append(("Radio Rock", {"Section": "radio_rock"}, "radio_rock", "50"))
            parsedLibrary.append(("Top50 this month", {
                "Section": "top50", "ArtId": "jamendo_top50", "Year": 0, "Runtime": 0, "Popularity": 0, "Tag": "", "Plot": "", "Genres": []
                }, "top5", "50"))
            
            sort = [("Title", None, False), ]
            filter = [("All", (None, False), ("", )), ]
            return (parsedLibrary, ("Section", ), None, None, sort, filter)
        elif primaryKeyValuePair.has_key("Section") and primaryKeyValuePair["Section"] == "top50":
            parsedLibrary = []
            try:
                os.remove("/hdd/valerie/jamendo.xml")
            except:
                pass
            getFile(self.top50, "/hdd/valerie/jamendo.xml", fixurl=False)
            xmlFile = Xml2Dict("/hdd/valerie/jamendo.xml")
            xmlFile.load()
            
            xml = xmlFile.get()
            for i in range(len(xml["data"]["track"])):
                track = xml["data"]["track"][i]
                d = {}
                
                d["Top"]     = i+1
                d["ArtId"] = "jamendo_" + utf8ToLatin(track["album_id"])
                
                d["JamendoId"]  = utf8ToLatin(track["id"])
                d["Title"]   = "  [%d] %s" % (i+1, utf8ToLatin(track["name"]))
                d["Tag"]     = ""
                d["Year"]    = 1
                d["Month"]   = 1
                d["Day"]     = 1
                # Yeah its a bit supersufficial as date is already in it
                # But will allow the view to sort the list
                d["Date"]    = 0
                d["Path"]    = utf8ToLatin(track["stream"])
                d["Creation"] = 0
                d["Plot"]    = ""
                d["Runtime"] = "%s" % (int(utf8ToLatin(track["duration"])) / 60, )
                d["Popularity"] = 0
                if len(track["album_genre"]) > 0:
                    d["Genres"]  = (utf8ToLatin(track["album_genre"]), )
                else:
                    d["Genres"]  = []
                d["Resolution"]  = ""
                d["Sound"]  = ""
                
                parsedLibrary.append((d["Title"], d, d["Title"].lower(), "50"))
            sort = [("Top", "Top", False), ("Title", None, False), ]
            filter = [("All", (None, False), ("", )), ]
            return (parsedLibrary, ("play", "JamendoId", ), None, None, sort, filter)
        
        return None

    def buildInfoPlaybackArgs(self, entry):
        args = {}
        args["title"]   = entry["Title"]
        return args

#if gAvailable is True:
#	registerPlugin(Plugin(name=_("Jamendo"), start=DMC_JamendoLibrary, where=Plugin.MENU_MUSIC))
