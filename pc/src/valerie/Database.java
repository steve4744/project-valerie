
package valerie;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Calendar;
import java.util.LinkedHashMap;
import java.util.LinkedList;
import valerie.controller.Notifier;

/**
 *
 * @author Admin
 */
public class Database {

    Notifier pNotifier = null;

    public Database(Notifier notifier) {
        pNotifier = notifier;
    }

    private LinkedHashMap<Integer, MediaInfo> DB = new LinkedHashMap<Integer, MediaInfo>();

    private int IDCounter = 0;

    public int add(MediaInfo info) {
        info.checkStrings();
        info.ID = IDCounter;
        DB.put(IDCounter, info);



        IDCounter++;   

        return IDCounter-1;
    }

    public void clear() {
        DB.clear();
        IDCounter = 0;
    }

    public void save() {
        Utf8 f;

        f = new Utf8("db\\moviedb.txt", "w");
        f.write(String.valueOf(Calendar.getInstance().getTime()) + "\n");
        f.write(String.valueOf(getMoviesCount()) + "\n");
        for( MediaInfo i : getMovieAsArray()) {
             f.write(i.exportStr());
             //i.setValerieInfoLastAccessTime(i.Path);
        }
        f.close();

        f = new Utf8("db\\seriesdb.txt", "w");
        f.write(String.valueOf(Calendar.getInstance().getTime()) + "\n");
        f.write(String.valueOf(getSeriesCount() + getEpisodesCount()) + "\n");
        for( MediaInfo i : getSerieAsArray()) {
            if( getEpisodeAsArray(i.TheTvDbId).length > 0)
                f.write(i.exportStr());
        }
        f.close();

        for( MediaInfo serie : getSerieAsArray()) {
            String key = serie.TheTvDbId;
            f = new Utf8("db\\episodes\\" + key + ".txt", "w");
            f.write(String.valueOf(Calendar.getInstance().getTime()) + "\n");
            for( MediaInfo i : getEpisodeAsArray(key)) {
                f.write(i.exportStr());
                //i.setValerieInfoLastAccessTime(i.Path);
            }
            f.close();
        }
    }

    public void reload() {
        clear();
        load();
    }

    // Compatibility OK
    public void load() {
        Utf8 f;

        float count = 0;
        float countVar = 0;

        pNotifier._notify("Loading movies...", "PROGRESS");
        pNotifier._notify((float)0, "PROGRESS");

        try {
            f = new Utf8("db\\moviedb.txt", "r");
            String db = f.read();
            f.close();
            String[] movies = db.split("\n----END----\n");

            try {
                count = Integer.valueOf(movies[0].split("\n")[1]);
            } catch(Exception ex) {
                count = 1000;
            }
            countVar = 0;

            for (String movie : movies) {
                String[] _movie = movie.split("---BEGIN---\n");
                if (_movie.length == 2) {
                    MediaInfo m = new MediaInfo("", "", "");
                    m.importStr(movie, true, false, false);
                    if(m.Title.length() > 0)
                        this.add(m);

                    pNotifier._notify((float)(countVar++/count), "PROGRESS");
                }
            }
        } catch (Exception ex) {
            System.out.print(ex);
        }

        pNotifier._notify("Loading tv episodes...", "PROGRESS");
        pNotifier._notify((float)0, "PROGRESS");

        try {
            f = new Utf8("db\\seriesdb.txt", "r");
            String db = f.read();
            f.close();
            String[] movies = db.split("\n----END----\n");

            try {
                count = Integer.valueOf(movies[0].split("\n")[1]);
            } catch(Exception ex) {
                count = 1000;
            }
            countVar = 0;

            for (String movie : movies) {
                String[] _movie = movie.split("---BEGIN---\n");
                if (_movie.length == 2) {
                    MediaInfo m = new MediaInfo("", "", "");
                    m.importStr(movie, false, true, false);

                    if(m.Title.length() > 0)
                        this.add(m);

                    pNotifier._notify((float)(countVar++/count), "PROGRESS");
                }
            }
        } catch (Exception ex) {
            System.out.print(ex);
        }

        try {
            for( MediaInfo i : getSerieAsArray()) {
                String key = i.TheTvDbId;
                f = new Utf8("db\\episodes\\" + key + ".txt", "r");
                String db = f.read();
                f.close();
                String[] movies = db.split("\n----END----\n");
                for (String movie : movies) {
                    String[] _movie = movie.split("---BEGIN---\n");
                    if (_movie.length == 2) {
                        MediaInfo m = new MediaInfo("", "", "");
                        m.importStr(movie, false, false, true);

                        if(m.Title.length() > 0)
                            this.add(m);

                        pNotifier._notify((float)(countVar++/count), "PROGRESS");
                    }
                }
            }
        } catch (Exception ex) {
            System.out.print(ex);
        }
    }

    public void setAllToNotFound() {
        for(MediaInfo m : getAsArray())
            m.NotFound = true;
    }

    public void deleteAllNotFound() {
        for(MediaInfo m : getAsArray())
            if (m.NotFound)
                DB.remove(m);
    }

    public MediaInfo getByPath(String path) {
        for(Object element : DB.values()) {
            String elementPath = ((MediaInfo)element).Path + "/"+ ((MediaInfo)element).Filename + "." + ((MediaInfo)element).Extension;
            if(elementPath.equals(path))
                return (MediaInfo)element;
        }
        return null;
    }

    public MediaInfo getMediaInfoById(int id) {

        return (MediaInfo) DB.get(id);
    }

    public void delete(int id) {

        DB.remove(id);
    }


    public MediaInfo getMediaInfoByPath(String path) {

        String normalizedPath = path.toLowerCase().trim();

        MediaInfo info = null;
        for(Object element : DB.values()) {
            if(((MediaInfo)element).Path.equals(normalizedPath)) {
                info = (MediaInfo)element;
                break;
            }
        }
        return info;
    }

    public MediaInfo[] getAsArray() {
        MediaInfo[] list = new MediaInfo[DB.size()];
        int iterator = 0;
        for(Object element : DB.values()) {
            list[iterator++] = (MediaInfo)element;
        }

        Arrays.sort(list);

        return list;
    }



    public MediaInfo[] getMediaInfoEpisodeAsArray() {
        ArrayList<MediaInfo> vector = new ArrayList<MediaInfo>();
        for(Object element : DB.values()) {
            if(((MediaInfo)element).isEpisode)
                vector.add((MediaInfo)element);
        }

        MediaInfo[] list = new MediaInfo[vector.size()];
        vector.toArray(list);

        return list;
    }

    public MediaInfo[] getMovieAsArray() {
        ArrayList<MediaInfo> vector = new ArrayList<MediaInfo>();
        for(Object element : DB.values()) {
            if(((MediaInfo)element).isMovie)
                vector.add((MediaInfo)element);
        }
        MediaInfo[] list = new MediaInfo[vector.size()];
        vector.toArray(list);

        return list;
    }

    public LinkedList<MediaInfo> getSerieAsVector() {
        LinkedList<MediaInfo> vector = new LinkedList<MediaInfo>();
        for(Object element : DB.values()) {
            if(((MediaInfo)element).isSerie)
                vector.add((MediaInfo)element);
        }

        return vector;
    }

    public MediaInfo[] getSerieAsArray() {
        return getSerieAsVector().toArray(new MediaInfo[1]);
    }

    public MediaInfo[] getEpisodeAsArray() {
        ArrayList<MediaInfo> vector = new ArrayList<MediaInfo>();
        for(Object element : DB.values()) {
            if(((MediaInfo)element).isEpisode)
                vector.add((MediaInfo)element);
        }
        MediaInfo[] list = new MediaInfo[vector.size()];
        vector.toArray(list);

        return list;
    }

    public MediaInfo[] getEpisodeAsArray(String thetvdbId) {
        ArrayList<MediaInfo> vector = new ArrayList<MediaInfo>();
        for(Object element : DB.values()) {
            if(((MediaInfo)element).isEpisode && ((MediaInfo) element).TheTvDbId.equals(((MediaInfo) element).TheTvDbIdNull))
                vector.add((MediaInfo)element);
        }

        MediaInfo[] list = new MediaInfo[vector.size()];
        vector.toArray(list);

        return list;
    }

     public MediaInfo[] getMediaInfoEpisodesUnspecified() {
        ArrayList<MediaInfo> vector = new ArrayList<MediaInfo>();
        for(Object element : DB.values()) {
            if(((MediaInfo)element).isEpisode && ((MediaInfo)element).TheTvDbId.equals("0"))
                vector.add((MediaInfo)element);
        }

        MediaInfo[] list = new MediaInfo[vector.size()];
        vector.toArray(list);

        return list;
    }

    public MediaInfo getMediaInfoForSeries(String searchname) {
        MediaInfo info = null;
        for(Object element : DB.values()) {
            if(((MediaInfo)element).isSerie && ((MediaInfo)element).SearchString.equals(searchname)) {
                info = (MediaInfo)element;
                break;
            }
        }

        return info;
    }

    public MediaInfo getSerieByTheTvDbId(String thetvdbId) {
        MediaInfo info = null;
        for(Object element : DB.values()) {
            if(((MediaInfo)element).isSerie && ((MediaInfo)element).TheTvDbId.equals(thetvdbId)) {
                info = (MediaInfo)element;
                break;
            }
        }

        return info;
    }

    public int getMoviesCount() {
        int counter = 0;
        for(Object element : DB.values())
            if(((MediaInfo)element).isMovie) counter++;

        return counter;
    }

    public int getEpisodesCount() {
        int counter = 0;
        for(Object element : DB.values())
            if(((MediaInfo)element).isEpisode) counter++;

        return counter;
    }

    public int getSeriesCount() {
        int counter = 0;
        for(Object element : DB.values())
            if(((MediaInfo)element).isSerie) counter++;

        return counter;
    }
}
