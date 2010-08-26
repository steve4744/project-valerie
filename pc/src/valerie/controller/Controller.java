/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package valerie.controller;

import java.io.File;
import java.io.FilenameFilter;
import java.util.HashMap;
import valerie.Database;
import valerie.MediaInfo;
import valerie.provider.ImdbProvider;
import valerie.provider.TheMovieDbProvider;
import valerie.provider.TheTvDbProvider;
import valerie.tools.BoxInfo;
import valerie.tools.FileUtils;

/**
 *
 * @author i7
 */
public final class Controller extends Notifier {

     HashMap<String, Object> pObjects = new HashMap<String, Object>();

    public Controller() {
        set("Database", new Database(this));
        set("ConfPaths", new ConfPaths());

        Replace.reload();
    }

    public void set(String name, Object obj) {
        if(obj != null) pObjects.put(name, obj);
    }

    public Object get(String name) {
        return pObjects.get(name);
    }

    public void cancel() {
        
    }

    public void databaseLoad() {

        Database db = (Database)get("Database");
        db.reload();

        _notify("DB_REFRESH");
    }

    public void databaseSave() {
        Database db = (Database)get("Database");
        db.save();
    }

    public void networkConnect() {
        String response = new valerie.tools.Network().sendBroadcast();
        valerie.tools.BoxInfo[] bis = new valerie.tools.BoxInfoParser().parse(response);
        set("BoxInfos",  bis );

        _notify("BI_REFRESH");
    }

    public void networkTransferMO() {
        if(get("BoxInfos") == null || get("SelectedBoxInfo") == null)
            return;
        BoxInfo[] pBoxInfos = (BoxInfo[])get("BoxInfos");
        int selectedBoxInfo = (Integer)get("SelectedBoxInfo");
        if (selectedBoxInfo < 0)
            return;

        _notify("Transfer mobile originated ...", "PROGRESS");
        _notify((float)0, "PROGRESS");

        BoxInfo pBoxInfo = pBoxInfos[selectedBoxInfo];

        FileUtils.mkdir(new File("conf"));
        new valerie.tools.Network().getFile(pBoxInfo.IpAddress, "/hdd/valerie/paths.conf", "conf");
        new valerie.tools.Network().getFile(pBoxInfo.IpAddress, "/hdd/valerie/valerie.conf", "conf");
        new valerie.tools.Network().getFile(pBoxInfo.IpAddress, "/hdd/valerie/pre.conf", "conf");
        new valerie.tools.Network().getFile(pBoxInfo.IpAddress, "/hdd/valerie/post_movie.conf", "conf");
        new valerie.tools.Network().getFile(pBoxInfo.IpAddress, "/hdd/valerie/post_tv.conf", "conf");

        _notify((float)0.1, "PROGRESS");

        FileUtils.deleteFile("db.1");
        FileUtils.rename(new File("db"), new File("db.1"));
        FileUtils.mkdir(new File("db"));

        new valerie.tools.Network().getFile(pBoxInfo.IpAddress, "/hdd/valerie/moviedb.txt", "db");
        new valerie.tools.Network().getFile(pBoxInfo.IpAddress, "/hdd/valerie/seriesdb.txt", "db");

        _notify((float)0.2, "PROGRESS");

        {
        FileUtils.mkdir(new File("db/episodes"));
        String[] entries = new valerie.tools.Network().sendCMD(pBoxInfo.IpAddress, "find /hdd/valerie/episodes/*.txt -type f");
        for (int f = 0; f < entries.length; f++) {
            new valerie.tools.Network().getFile(pBoxInfo.IpAddress, entries[f], "db/episodes");
        }
        }

        _notify((float)0.4, "PROGRESS");

        {
        FileUtils.mkdir(new File("converted"));
        String[] entries = new valerie.tools.Network().sendCMD(pBoxInfo.IpAddress, "find /hdd/valerie/media/*.png -type f");
        for (int f = 0; f < entries.length; f++) {
            new valerie.tools.Network().getFile(pBoxInfo.IpAddress, entries[f], "converted");
        }
        }

        _notify((float)0.6, "PROGRESS");

        {
        FileUtils.mkdir(new File("converted"));
        String[] entries = new valerie.tools.Network().sendCMD(pBoxInfo.IpAddress, "find /hdd/valerie/media/*.m1v -type f");
        for (int f = 0; f < entries.length; f++) {
            new valerie.tools.Network().getFile(pBoxInfo.IpAddress, entries[f], "converted");
        }
        }

        _notify((float)0.8, "PROGRESS");

        //Reload ConfPaths due to changed target
        ((ConfPaths)get("ConfPaths")).reload();
        Replace.reload();

        ((Database)get("Database")).reload();

        _notify((float)1.0, "PROGRESS");
        _notify("DB_REFRESH");
    }

    public void networkTransferMT() {
        if(get("BoxInfos") == null || get("SelectedBoxInfo") == null)
            return;
        BoxInfo[] pBoxInfos = (BoxInfo[])get("BoxInfos");
        int selectedBoxInfo = (Integer)get("SelectedBoxInfo");
        if (selectedBoxInfo < 0)
            return;

        _notify("Transfer mobile terminated ...", "PROGRESS");
        _notify((float)0, "PROGRESS");

        BoxInfo pBoxInfo = pBoxInfos[selectedBoxInfo];

        new valerie.tools.Network().sendCMD(pBoxInfo.IpAddress, "mkdir -p /hdd/valerie");
        new valerie.tools.Network().sendFile(pBoxInfo.IpAddress, "conf\\paths.conf", "/hdd/valerie");
        new valerie.tools.Network().sendFile(pBoxInfo.IpAddress, "conf\\valerie.conf", "/hdd/valerie");
        new valerie.tools.Network().sendFile(pBoxInfo.IpAddress, "conf\\pre.conf", "/hdd/valerie");
        new valerie.tools.Network().sendFile(pBoxInfo.IpAddress, "conf\\post_movie.conf", "/hdd/valerie");
        new valerie.tools.Network().sendFile(pBoxInfo.IpAddress, "conf\\post_tv.conf", "/hdd/valerie");

        _notify((float)0.1, "PROGRESS");

        new valerie.tools.Network().sendFile(pBoxInfo.IpAddress, "db\\moviedb.txt", "/hdd/valerie");
        new valerie.tools.Network().sendFile(pBoxInfo.IpAddress, "db\\seriesdb.txt", "/hdd/valerie");

        _notify((float)0.2, "PROGRESS");

        new valerie.tools.Network().sendCMD(pBoxInfo.IpAddress, "mkdir -p /hdd/valerie/episodes");
        File episodes = new File("db/episodes");
        for(String entry : episodes.list(new FilenameFilter()
        { public boolean accept(File dir, String name) { return (name.endsWith(".txt")); }})) {
            new valerie.tools.Network().sendFile(pBoxInfo.IpAddress, "db\\episodes\\" + entry, "/hdd/valerie/episodes");
        }

        _notify((float)0.4, "PROGRESS");

        new valerie.tools.Network().sendCMD(pBoxInfo.IpAddress, "mkdir -p /hdd/valerie/media");
        File media = new File("converted");
        for(String entry : media.list(new FilenameFilter()
        { public boolean accept(File dir, String name) { return (name.endsWith(".png") || name.endsWith(".m1v")); }})) {
            new valerie.tools.Network().sendFile(pBoxInfo.IpAddress, "converted\\" + entry, "/hdd/valerie/media");
        }

        _notify((float)1.0, "PROGRESS");
    }

    public void networkFilesystem() {
        if(get("BoxInfos") == null || get("SelectedBoxInfo") == null)
            return;
        BoxInfo[] pBoxInfos = (BoxInfo[])get("BoxInfos");
        int selectedBoxInfo = (Integer)get("SelectedBoxInfo");
        if (selectedBoxInfo < 0)
            return;

        _notify("Syncing...", "PROGRESS");
        _notify((float)0, "PROGRESS");
        float count = 0;
        float countVar = 0;

        BoxInfo pBoxInfo = pBoxInfos[selectedBoxInfo];

        // We got several possibility how to do this.
        // on the box we walk thorug the db if every file exists
        // then we walk through the filesystem and add everything that does not exist
        // on the pc we could just get the filesystem once,
        // mark all file in db to "not found" and reset this flag for every file we found

        ((Database)get("Database")).setAllToNotFound();

        for(String path : ((ConfPaths)get("ConfPaths")).getPaths()) {
            for(String filter : ((ConfPaths)get("ConfPaths")).getFilter().split("\\|")) {
                String[] entries = new valerie.tools.Network().sendCMD(pBoxInfo.IpAddress, "find \"" + path + "\"" + " -name \"*." + filter + "\"" + " -type f");

                _notify("Syncing...\n@" + path, "PROGRESS");
                _notify((float)0, "PROGRESS");
                count = entries.length;
                countVar = 0;

                for(String entry : entries) {

                    _notify((float)(countVar++/count), "PROGRESS");

                    if(entry.contains("sample"))
                        continue;

                    if(entry.contains("RECYCLE.BIN"))
                        continue;

                    String pathS = entry;
                    String[] pathSplit = pathS.split("/");
                    String filenameS = pathSplit[pathSplit.length - 1];
                    pathS = pathS.substring(0, pathS.length() - filenameS.length() - 1);
                    String[] filenameSplit = filenameS.split("[.]");
                    String extensionS = filenameSplit[filenameSplit.length - 1];
                    filenameS = filenameS.substring(0, filenameS.length() - extensionS.length() - 1);

                    MediaInfo m = ((Database)get("Database")).getByPath(entry);
                    if(m != null)
                        m.NotFound = false;
                    else {
                        m = new MediaInfo(pathS, filenameS, extensionS);
			m.parse(this); // Well i dont like to give this class the controll, but at the moment i got now different solution
                        
                        // This is different to the box version
                        m.needsUpdate = true;
                        ((Database)get("Database")).add(m);
                    }
                }
            }
        }

        ((Database)get("Database")).deleteAllNotFound();

        _notify("DB_REFRESH");
    }

    public void jobParse() {

        _notify("Parsing...", "PROGRESS");
        _notify((float)0, "PROGRESS");
        float count = 0;
        float countVar = 0;

        MediaInfo[] elementInfoArray = ((Database)get("Database")).getAsArray();
        count = elementInfoArray.length;
        for(MediaInfo elementInfo : elementInfoArray) {
            _notify((float)(countVar++/count), "PROGRESS");

            if(!elementInfo.needsUpdate)
                continue;

            if(elementInfo.SearchString.length() == 0)
                elementInfo.parse(this);

            new ImdbProvider().getMoviesByTitle(elementInfo);

            _notify((float)(countVar/count), "PROGRESS");

            if(elementInfo.isMovie) {
                //# Ask TheMovieDB for the local title and plot
                new TheMovieDbProvider().getMoviesById(elementInfo);
                //new TheMovieDbProvider().getArtById(elementInfo);
                //Arts().download(elementInfo)
                //db.add(elementInfo)
                if(elementInfo.Title.length() > 0)
                    elementInfo.needsUpdate = false;
                _notify("DB_REFRESH");
            }
            else if (elementInfo.isEpisode) {
                //Change format to be more src compatible with box src
                //elementInfo.isEpisode = false;
                //elementInfo.isSerie = true;

                new TheTvDbProvider().getSerieByImdbID(elementInfo);
		//new TheTvDbProvider().getSeriesArtById(elementInfo);
                //#print elementInfo
                //db.add(elementInfo)

		MediaInfo elementInfoSerie = elementInfo.clone();
                elementInfoSerie.isSerie = true;
                elementInfoSerie.isEpisode = false;

                // Finish up Episode
                new TheTvDbProvider().getEpisode(elementInfo);
                if(elementInfo.Title.length() > 0)
                    elementInfo.needsUpdate = false;

                _notify((float)(countVar/count), "PROGRESS");

                // Finish up Serie
                if(elementInfoSerie.Title.length() > 0)
                    elementInfoSerie.needsUpdate = false;
                if(((Database)get("Database")).getSerieByTheTvDbId(elementInfoSerie.TheTvDbId) == null)
                    ((Database)get("Database")).add(elementInfoSerie);
                _notify("DB_REFRESH");

                //Arts().download(elementInfo)
                //self.info(str(elementInfo.TheTvDbId) + "_poster.png", elementInfo.Title, elementInfo.Year)

            }
        }
        
        _notify("DB_REFRESH");
    }

    public void jobArts() {

        _notify("Downloading arts...", "PROGRESS");
        _notify((float)0, "PROGRESS");
        float count = 0;
        float countVar = 0;

        MediaInfo[] elementInfoArray = ((Database)get("Database")).getAsArray();
        count = elementInfoArray.length;
        for(MediaInfo elementInfo : elementInfoArray) {
            _notify((float)(countVar++/count), "PROGRESS");
            new Arts().download(elementInfo);
        }
    }
}
