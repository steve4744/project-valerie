/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package valerie;

import java.io.File;
import valerie.provider.provider;

/**
 *
 * @author Admin
 */
public class MediaInfo {


    public provider DataProvider;
    public provider ArtProvider;

    public int ID = 0;

    public boolean isArchiv = false;
    public boolean needsUpdate = false;

    public boolean isMovie = false;
    public boolean isSeries = false;
    public boolean isEpisode = false;
    public String Filename = "";
    public String Path = "";

    //TODO: change Searchstring to regex, as a series could hava multiple possible searchstrings
    public String SearchString = "";
    public String Title = "";
    public int Year = 0;
    public int Imdb = 0;
    public String Poster = "";
    public String Backdrop = "";
    public String Banner = "";
    public String Runtime = "";
    public String Plot = "";
    public String Directors = "";
    public String Writers = "";
    public String Genres = "";
    public String Tag = "";
    public int Popularity = 0;
    public int Season = 0;
    public int Episode = 0;
    public int TheTvDb = 0;
    //public int ref = -1;
    public boolean Ignoring = true;

    public void getDataById() {
        DataProvider.getDataById(this);
    }
    public void getDataByTitle() {
        DataProvider.getDataByTitle(this);
    }

    public MediaInfo(String filename) {
        Path = filename;
        //File file = new File(filename);
        String[] path = filename.split("/");
        Filename = path[path.length - 1];
    }

    public MediaInfo() {
    }

    public void reparse(String entry) {

        try {
            String lines[] = entry.split("\n");

            for(String line : lines) {
                if(line.contains(": ")) {
                    String keys[] = line.split(": ", 2);

                    if(keys.length != 2)
                        System.out.println("123");

                    if(keys[0].equals("TheTvDb"))
                        TheTvDb = Integer.valueOf(keys[1]);
                    else if(keys[0].equals("ImdbId"))
                        Imdb = Integer.valueOf(keys[1]);
                    else if(keys[0].equals("Title"))
                        Title = keys[1];
                    else if(keys[0].equals("Year"))
                        Year = Integer.valueOf(keys[1]);
                    else if(keys[0].equals("Path"))
                        Path = keys[1];
                    else if(keys[0].equals("Directors"))
                        Directors = keys[1];
                    else if(keys[0].equals("Writers"))
                        Writers = keys[1];
                    else if(keys[0].equals("Plot"))
                        Plot = keys[1];
                    else if(keys[0].equals("Runtime"))
                        Runtime = keys[1];
                    else if(keys[0].equals("Genres"))
                        Genres = keys[1];
                    else if(keys[0].equals("Tag"))
                        Tag = keys[1];
                    else if(keys[0].equals("Popularity"))
                        Popularity = Integer.valueOf(keys[1]);
                    else if(keys[0].equals("Season"))
                        Season = Integer.valueOf(keys[1]);
                    else if(keys[0].equals("Episode"))
                        Episode = Integer.valueOf(keys[1]);
                }
            }

            if(Path.length() > 0) {
                String[] path = Path.split("/");
                Filename = path[path.length - 1];
            }
        }catch (Exception ex) {
            System.out.println(ex.toString());
        }
    }

    public void checkStrings() {

        Title = Title.replaceAll("&#x27;", "'").replaceAll("&#x26;", "&").replaceAll("&#x22;", "");
        Runtime = Runtime.replaceAll("&#x27;", "'").replaceAll("&#x26;", "&").replaceAll("&#x22;", "");
        Plot = Plot.replaceAll("&#x27;", "'").replaceAll("&#x26;", "&").replaceAll("&#x22;", "");
        Directors = Directors.replaceAll("&#x27;", "'").replaceAll("&#x26;", "&").replaceAll("&#x22;", "");
        Writers = Writers.replaceAll("&#x27;", "'").replaceAll("&#x26;", "&").replaceAll("&#x22;", "");
        Genres = Genres.replaceAll("&#x27;", "'").replaceAll("&#x26;", "&").replaceAll("&#x22;", "");
        Tag = Tag.replaceAll("&#x27;", "'").replaceAll("&#x26;", "&").replaceAll("&#x22;", "");
    }

    public String toString() {
        //if(Imdb > 0)
        return  "---BEGIN---\n" +
                (isEpisode||isSeries?("TheTvDb: " + TheTvDb + "\n"):"") +
                "ImdbId: " + Imdb + "\n" +
                "Title: " + Title + "\n" +
                "Year: " + Year + "\n" +
                //"Filename: " + Filename + "\n" +
                (!isSeries?("Path: " + Path + "\n"):"") +
                "Directors: " + Directors + "\n" +
                "Writers: " + Writers + "\n" +
                "Plot: " + Plot + "\n" +
                "Runtime: " + Runtime + "\n" +
                "Genres: " + Genres + "\n" +
                "Tag: " + Tag + "\n" +
                "Popularity: " + Popularity + "\n" +
                (isEpisode?("Season: " + Season + "\n"):"") +
                (isEpisode?("Episode: " + Episode + "\n"):"") +
                "----END----\n\n";
        //else
        //    return "";
    }

    @Override
    protected MediaInfo clone() {
        MediaInfo rtv = new MediaInfo(Filename);

        rtv.DataProvider = DataProvider;
        rtv.ArtProvider = ArtProvider;

        rtv.isMovie = isMovie;
        rtv.isSeries = isSeries;
        rtv.isEpisode = isEpisode;
        rtv.Filename = Filename;
        rtv.Path = Path;
        rtv.SearchString = SearchString;
        rtv.Title = Title;
        rtv.Year = Year;
        rtv.Imdb = Imdb;
        rtv.Poster = Poster;
        rtv.Backdrop = Backdrop;
        rtv.Banner = Banner;
        rtv.Runtime = Runtime;
        rtv.Plot = Plot;
        rtv.Directors = Directors;
        rtv.Writers = Writers;
        rtv.Genres = Genres;
        rtv.Tag = Tag;
        rtv.Popularity = Popularity;
        rtv.Season = Season;
        rtv.Episode = Episode;
        rtv.TheTvDb = TheTvDb;

        rtv.Ignoring = Ignoring;
        rtv.isArchiv = isArchiv;
        rtv.needsUpdate = needsUpdate;
        return rtv;
    }


}
