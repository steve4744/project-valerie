/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package valerie;

import java.util.ArrayList;
import java.util.Hashtable;

/**
 *
 * @author Admin
 */
public class MediaInfoDB {

    Hashtable DB = new Hashtable();
    int IDCounter = 0;

    public boolean addMediaInfo(MediaInfo info) {
        info.checkStrings();
        info.ID = IDCounter;
        DB.put(IDCounter, info);
        IDCounter++;   

        return true;
    }

    public MediaInfo getMediaInfoById(int id) {

        return (MediaInfo) DB.get(id);
    }

    public void deleteMediaInfo(int id) {

        DB.remove(id);
    }


    public MediaInfo getMediaInfoByPath(String path) {

        MediaInfo info = null;
        for(Object element : DB.values()) {
            if(((MediaInfo)element).Path.equals(path)) {
                info = (MediaInfo)element;
                break;
            }
        }
        return info;
    }

    public MediaInfo[] getMediaInfo() {
        MediaInfo[] list = new MediaInfo[DB.size()];
        int iterator = 0;
        for(Object element : DB.values()) {
            list[iterator++] = (MediaInfo)element;
        }

        return list;
    }



    public MediaInfo[] getMediaInfoEpisodes() {
        ArrayList vector = new ArrayList();
        for(Object element : DB.values()) {
            if(((MediaInfo)element).isEpisode)
                vector.add((MediaInfo)element);
        }

        MediaInfo[] list = new MediaInfo[vector.size()];
        vector.toArray(list);

        return list;
    }

    public MediaInfo[] getMediaInfoSeries() {
        ArrayList vector = new ArrayList();
        for(Object element : DB.values()) {
            if(((MediaInfo)element).isSeries)
                vector.add((MediaInfo)element);
        }

        MediaInfo[] list = new MediaInfo[vector.size()];
        vector.toArray(list);

        return list;
    }

    public MediaInfo[] getMediaInfoEpisodes(int thetvdbId) {
        ArrayList vector = new ArrayList();
        for(Object element : DB.values()) {
            if(((MediaInfo)element).isEpisode && ((MediaInfo)element).TheTvDb == thetvdbId)
                vector.add((MediaInfo)element);
        }

        MediaInfo[] list = new MediaInfo[vector.size()];
        vector.toArray(list);

        return list;
    }

     public MediaInfo[] getMediaInfoEpisodesUnspecified() {
        ArrayList vector = new ArrayList();
        for(Object element : DB.values()) {
            if(((MediaInfo)element).isEpisode && ((MediaInfo)element).TheTvDb == 0)
                vector.add((MediaInfo)element);
        }

        MediaInfo[] list = new MediaInfo[vector.size()];
        vector.toArray(list);

        return list;
    }

    public MediaInfo getMediaInfoForSeries(String searchname) {
        MediaInfo info = null;
        for(Object element : DB.values()) {
            if(((MediaInfo)element).isSeries && ((MediaInfo)element).SearchString.equals(searchname)) {
                info = (MediaInfo)element;
                break;
            }
        }

        return info;
    }

    public MediaInfo getMediaInfoForSeries(int thetvdbId) {
        MediaInfo info = null;
        for(Object element : DB.values()) {
            if(((MediaInfo)element).isSeries && ((MediaInfo)element).TheTvDb == thetvdbId) {
                info = (MediaInfo)element;
                break;
            }
        }

        return info;
    }

    public int getMediaInfoMoviesCount() {
        int counter = 0;
        for(Object element : DB.values())
            if(((MediaInfo)element).isMovie) counter++;

        return counter;
    }

    public int getMediaInfoEpisodesCount() {
        int counter = 0;
        for(Object element : DB.values())
            if(((MediaInfo)element).isEpisode) counter++;

        return counter;
    }

    public int getMediaInfoSeriesCount() {
        int counter = 0;
        for(Object element : DB.values())
            if(((MediaInfo)element).isSeries) counter++;

        return counter;
    }

    public void clear() {
        DB.clear();
        IDCounter = 0;
    }
}
