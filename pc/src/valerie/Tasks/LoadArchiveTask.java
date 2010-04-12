/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package valerie.Tasks;

import java.io.BufferedReader;
import java.io.FileInputStream;
import java.io.FileReader;
import java.io.InputStreamReader;
import valerie.BackgroundWorker;
import valerie.Logger;
import valerie.MediaInfo;
import valerie.MediaInfoDB;
import valerie.provider.Imdb;
import valerie.provider.theMovieDb;
import valerie.provider.theTvDb;
import valerie.tools.DebugOutput;

/**
 *
 * @author Admin
 */
public class LoadArchiveTask extends org.jdesktop.application.Task<Object, Void> {

    protected BackgroundWorker pWorker;

    public LoadArchiveTask(org.jdesktop.application.Application app,
             BackgroundWorker worker) {
        super(app);

        pWorker = worker;

        Logger.setBlocked(true);
        Logger.printBlocked("Loading Archive");

    }
    @Override protected Object doInBackground() {
        DebugOutput.printl("->");
        theTvDb tvdb = new valerie.provider.theTvDb();
        Imdb imdb = new valerie.provider.Imdb();
        theMovieDb theMovieDB = new valerie.provider.theMovieDb();
        MediaInfoDB database = (MediaInfoDB)pWorker.get("Database");

        String charset = "UTF-8";
        //String charset = "ISO-8859-1";

        try {
            BufferedReader frMovie = new BufferedReader(new InputStreamReader(new FileInputStream("db/moviedb.txt"), charset));
            String line;
            String Movie="";
            while ((line = frMovie.readLine()) != null) {
                    if(line.equals("---BEGIN---")){
                            Movie="";
                    }
                    Movie += line + "\n";
                    if(line.equals("----END----")){
                            MediaInfo info = new MediaInfo();
                    info.reparse(Movie);
                    info.isMovie = true;
                    info.isArchiv = true;
                    info.needsUpdate = false;

                    info.DataProvider = imdb;
                    info.ArtProvider = theMovieDB;

                    //ignore the entry as long as we havent confirmed that it still exists
                    info.Ignoring = true;
                    if (info.Title.length() > 0) {
                        if(database.getMediaInfoByPath(info.Path) == null)
                            database.addMediaInfo(info);
                    }
                    }
            }

        } catch (Exception ex) {
            System.out.println(ex.toString());
        }


        try {

            BufferedReader frMovie = new BufferedReader(new InputStreamReader(new FileInputStream("db/seriesdb.txt"), charset));
            String line;
            String Movie="";

            while ((line = frMovie.readLine()) != null) {
                    if(line.equals("---BEGIN---")){
                            Movie="";
                    }
                    Movie += line + "\n";
                    if(line.equals("----END----")){
                            MediaInfo info = new MediaInfo();
                    info.reparse(Movie);
                    info.isSeries = true;
                    info.isArchiv = true;
                    info.needsUpdate = false;

                    info.DataProvider = tvdb;
                    info.ArtProvider = tvdb;

                    //As this isnt represented by any file we have to set ignoring to false
                    info.Ignoring = false;
                    if (info.Title.length() > 0) {
                        if(database.getMediaInfoForSeries(info.TheTvDb) == null)
                            database.addMediaInfo(info);
                    }
                    }
            }

        } catch (Exception ex) {
            System.out.println(ex.toString());
        }

        try {
            MediaInfo infos[] = database.getMediaInfo();
            for (MediaInfo info : infos) {
                if (info.isSeries) {
                    BufferedReader frMovie = new BufferedReader(new InputStreamReader(new FileInputStream("db/episodes/" + info.TheTvDb + ".txt"), charset));
                    String line;
                    String Movie="";
                    while ((line = frMovie.readLine()) != null) {
                            if(line.equals("---BEGIN---")){
                                    Movie="";
                            }
                            Movie += line + "\n";
                            if(line.equals("----END----")){
                                    MediaInfo movieinfo = new MediaInfo();
                            movieinfo.reparse(Movie);
                            movieinfo.isEpisode = true;
                            movieinfo.isArchiv = true;
                            movieinfo.needsUpdate = false;

                            info.DataProvider = tvdb;
                            info.ArtProvider = tvdb;

                            //ignore the entry as long as we havent confirmed that it still exists
                            movieinfo.Ignoring = true;
                            if (movieinfo.Title.length() > 0) {
                                if(database.getMediaInfoByPath(movieinfo.Path) == null)
                                    database.addMediaInfo(movieinfo);
                            }
                            }
                    }
                }
            }
        } catch (Exception ex) {
            System.out.println(ex.toString());
        }

        DebugOutput.printl("<-");
        return null;
    }

    @Override protected void succeeded(Object result) {
        Logger.printBlocked("Finished");
        Logger.setBlocked(false);
    }
}
