/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package valerie.Tasks;

import java.io.BufferedReader;
import java.io.FileReader;
import java.util.ArrayList;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import valerie.BackgroundWorker;
import valerie.Logger;
import valerie.MediaInfo;
import valerie.MediaInfoDB;
import valerie.tools.BoxInfo;

/**
 *
 * @author Admin
 */
public class SyncFilelistTask extends org.jdesktop.application.Task<Object, Void> {

    protected BackgroundWorker pWorker;

    public SyncFilelistTask(org.jdesktop.application.Application app,
            BackgroundWorker worker) {
        super(app);

        pWorker = worker;
    }

    @Override
    protected Object doInBackground() {

        Logger.setBlocked(true);
        Logger.printBlocked("Syncing Filelist");

        Logger.setProgress(0);

        MediaInfoDB database = (MediaInfoDB)pWorker.get("Database");

        searchMovies(database);
        searchSeries(database);

        //Walk through the databasse and delete all failed entries
        
        MediaInfo[] movies = database.getMediaInfo();
        for (MediaInfo info : movies) {
            if(info.isArchiv && info.Ignoring)
                database.deleteMediaInfo(info.ID);
        }

        Logger.printBlocked("Finished");
        Logger.setBlocked(false);
        Logger.setProgress(0);

        return null;
    }

    @Override
    protected void succeeded(Object result) {
    }

    private ArrayList<String[]> getReplacements(){
        ArrayList<String[]> replacements = new ArrayList<String[]>();

        replacements.add(new String[]{"[.]", " "});
        replacements.add(new String[]{"_", " "});
        replacements.add(new String[]{"-", " "});
        replacements.add(new String[]{"tt\\d{7}", ""});
        replacements.add(new String[]{"(\\b(avi|vob|dth|vc1|ac3d|dl|extcut|mkv|nhd|576p|720p|1080p|1080i|dircut|directors cut|dvdrip|dvdscreener|dvdscr|avchd|wmv|ntsc|pal|mpeg|dsr|hd|r5|dvd|dvdr|dvd5|dvd9|bd5|bd9|dts|ac3|bluray|blu-ray|hdtv|pdtv|stv|hddvd|xvid|divx|x264|dxva|m2ts|(?-i)FESTIVAL|LIMITED|WS|FS|PROPER|REPACK|RERIP|REAL|RETAIL|EXTENDED|REMASTERED|UNRATED|CHRONO|THEATRICAL|DC|SE|UNCUT|INTERNAL|DUBBED|SUBBED)\\b([-].+?$)?)", ""});
        BufferedReader frMovie;
        try {
            frMovie = new BufferedReader(new FileReader("replacements.txt"));
            String line;
            while ((line = frMovie.readLine()) != null) {
                String[] parts = line.split("=");
                replacements.add(new String[]{parts[0], parts[1]});
            }
        } catch (Exception e) {
        }

        return replacements;
    }

    private void searchMovies( MediaInfoDB database) {
        String[] paths = new valerie.tools.Properties().getPropertyString("PATHS_MOVIES").split("\\|");
        ArrayList<String[]> replacements=getReplacements();
        for (int row = 0; row < paths.length; row++) {
            String filterString = "(";
            String filter = new valerie.tools.Properties().getPropertyString("FILTER_MOVIES");
            String[] filters = filter.split("\\|");
            if(filters.length > 0)
                filterString += "find \"" + paths[row] + "\" -name \"*." + filters[0] + "\"  -type f;";

            for(int i = 1; i < filters.length; i++)
                filterString += "find \"" + paths[row] + "\" -name \"*." + filters[0] + "\"  -type f;";
            filterString += ")";

            BoxInfo[] boxInfos = (BoxInfo[])pWorker.get("BoxInfos");
            int selectedBoxInfo = (Integer)pWorker.get("SelectedBoxInfo");
            String[] entries = new valerie.tools.Network().sendCMD(boxInfos[selectedBoxInfo].IpAddress, filterString + "\n");

            for (int i = 0; i < entries.length; i++) {
                Float progress = (float) i * 100;
                progress /= entries.length;

                Logger.setProgress(progress.intValue());

                MediaInfo movie = new MediaInfo(entries[i]);

                Pattern pFileFilter = Pattern.compile(".*(" + new valerie.tools.Properties().getPropertyString("FILTER_MOVIES") + ")$");
                Matcher mFileFilter = pFileFilter.matcher(movie.Filename);
                if (!mFileFilter.matches()) {
                    continue;
                }

                movie.isMovie = true;

                Logger.print(movie.Filename + " : Parsing");

                //Check if we already have this Movie in our Archiv!
                //if so we dont need to extra inject it.
                MediaInfo archiveEntry = null;
                if ((archiveEntry = database.getMediaInfoByPath(movie.Path)) != null) {
                    if (archiveEntry.isArchiv) {
                        archiveEntry.Ignoring = false;
                        continue;
                    } else {
                        //this means that the file is a duplicate, what to do with that knowledge ?
                        continue;
                    }
                }

                //FileFilter
                Pattern p = Pattern.compile("tt\\d{7}");
                Matcher m = p.matcher(movie.Filename);
                if (m.find()) {
                    System.out.printf("Imdb found: %d", Integer.valueOf(m.group()));
                }

                String filtered = movie.Filename.toLowerCase();
                for (int iter = 0; iter < replacements.size(); iter++) {
                    filtered = filtered.replaceAll(replacements.get(iter)[0].toLowerCase(), replacements.get(iter)[1]);
                }

                //filtered = filtered.trim();
                filtered = filtered.replaceAll("\\s+", " ");
                System.out.println("parsing :"+filtered);
                /*String[] parts = filtered.split(" ");
                for (int possibleYearPosition = 0; possibleYearPosition < 3 && possibleYearPosition < parts.length; possibleYearPosition++) {
                    if (parts[parts.length - 1 - possibleYearPosition].matches("\\d{4}")) {
                        System.out.printf("Year found: %s", parts[parts.length - 1 - possibleYearPosition]);
                        movie.Year = Integer.valueOf(parts[parts.length - 1 - possibleYearPosition]);
                        filtered = filtered.substring(0, filtered.length() - 5);

                        break;
                    }
                }*/
                {
                            Pattern pYear = Pattern.compile("\\D(\\d{4})\\D");
                        Matcher mYear = pYear.matcher(filtered);
                        if (mYear.find()) {
                            movie.Year= Integer.valueOf(mYear.group(1));
                        }
                }

                filtered = filtered.trim();

                //Idee bei grossklein wechsel leerzeichen einfügen, auch bei buchstabe auf zahlen wechsel
                for (int i2 = 0; i2 + 1 < filtered.length(); i2++) {
                    String p1 = filtered.substring(i2, i2 + 1);
                    String p2 = filtered.substring(i2 + 1, i2 + 2);

                    if ((p1.matches("[a-zA-Z]") && p2.matches("\\d")) ||
                            (p1.matches("\\d") && p2.matches("[a-zA-Z]"))) {
                        filtered = filtered.substring(0, i2 + 1) + " " + filtered.substring(i2 + 1, filtered.length());
                    }
                }

                //Idee alles was nach dem Erscheinungsjahr kommt wegwerfen, mögliche Fehlerquelle wenn bestandteil des Filmes ist.
                if (movie.Year > 1950 && movie.Year < 2020) {
                    Pattern pYear = Pattern.compile("(.*)(\\d{4})");
                    Matcher mYear = pYear.matcher(filtered);
                    if (mYear.find()) {
                            filtered = mYear.group(1);
                            System.out.println(mYear.group(1)+":"+mYear.group(2));
                    }

                }

                //Sometimes the release groups insert their name in front of the title, so letzs check if the frist word contains a '-'
                String firstWord = "";
                String[] spaceSplit = filtered.split(" ", 2);
                if (spaceSplit.length == 2) {
                    firstWord = spaceSplit[0];
                } else {
                    firstWord = filtered;
                }

                String[] minusSplit = firstWord.split("-", 2);
                if (minusSplit.length == 2) {
                    filtered = minusSplit[1] + (spaceSplit.length == 2 ? " " + spaceSplit[1] : "");
                }

                movie.SearchString = filtered;

                //If parsing of Searchstring failed, set parameters so it is highlighted for the user
                if(movie.SearchString.length() > 0) {
                    movie.Ignoring = false;
                    movie.needsUpdate = true;
                } else {
                    movie.Ignoring = true;
                    movie.needsUpdate = false;
                }

                movie.DataProvider = new valerie.provider.Imdb();
                movie.ArtProvider = new valerie.provider.theMovieDb();

                database.addMediaInfo(movie);

                Logger.print(movie.Filename + " : Using \"" + movie.SearchString + "\" to get title");
            }
        }
    }

    private void searchSeries( MediaInfoDB database) {
        String[] paths = new valerie.tools.Properties().getPropertyString("PATHS_SERIES").split("\\|");
        ArrayList<String[]> replacements = getReplacements();
        for (int row = 0; row < paths.length; row++) {
            if(paths[row].length() <= 0)
                continue;
            String filterString = "(";
            String filter = new valerie.tools.Properties().getPropertyString("FILTER_SERIES");
            String[] filters = filter.split("\\|");
            if(filters.length > 0)
                filterString += "find \"" + paths[row] + "\" -name \"*." + filters[0] + "\"  -type f;";

            for(int i = 1; i < filters.length; i++)
                filterString += "find \"" + paths[row] + "\" -name \"*." + filters[i] + "\"  -type f;";
            filterString += ")";

            BoxInfo[] boxInfos = (BoxInfo[])pWorker.get("BoxInfos");
            int selectedBoxInfo = (Integer)pWorker.get("SelectedBoxInfo");
            String[] entries = new valerie.tools.Network().sendCMD(boxInfos[selectedBoxInfo].IpAddress, filterString + "\n");

            //String[] entries = new valerie.tools.Network().sendCMD(boxInfos[selectedBoxInfo].IpAddress, "find \"" + paths[row] + "\" -type f\n");

            for (int i = 0; i < entries.length; i++) {
                Float progress = (float) i * 100;
                progress /= entries.length;

                Logger.setProgress(progress.intValue());

                MediaInfo movie = new MediaInfo(entries[i]);

                //FileFilter
                Pattern pFileFilter = Pattern.compile(".*(" + new valerie.tools.Properties().getPropertyString("FILTER_SERIES") + ")$");
                Matcher mFileFilter = pFileFilter.matcher(movie.Filename);
                if (!mFileFilter.matches()) {
                    continue;
                }

                movie.isEpisode = true;

                Logger.print(movie.Filename + " : Parsing");

                //Check if we already have this Movie in our Archiv!
                //if so we dont need to extra inject it.
                MediaInfo archiveEntry = null;
                if ((archiveEntry = database.getMediaInfoByPath(movie.Path)) != null) {
                    if (archiveEntry.isArchiv) {
                        archiveEntry.Ignoring = false;
                        continue;
                    } else {
                        //this means that the file is a duplicate, what to do with that knowledge ?
                        continue;
                    }
                }


                Pattern p = Pattern.compile("tt\\d{7}");
                Matcher m = p.matcher(movie.Filename);
                if (m.find()) {
                    System.out.printf("Imdb found: %d", Integer.valueOf(m.group()));
                }

                String filtered = movie.Filename.toLowerCase();
                for (int iter = 0; iter < replacements.size(); iter++) {
                    filtered = filtered.replaceAll(replacements.get(iter)[0].toLowerCase(), replacements.get(iter)[1]);
                }

                filtered = filtered.trim();
                filtered = filtered.replaceAll("\\s+", " ");

                //^.*?\\?(?<series>[^\\$]+?)(?:s(?<season>[0-3]?\d)\s?ep?(?<episode>\d\d)|(?<season>(?:[0-1]\d|(?<!\d)\d))x?(?<episode>\d\d))(?!\d)(?:[ .-]?(?:s\k<season>e?(?<episode2>\d{2}(?!\d))|\k<season>x?(?<episode2>\d{2}(?!\d))|(?<episode2>\d\d(?!\d))|E(?<episode2>\d\d))|)[ -.]*(?<title>(?![^\\]*?sample)[^\\]*?[^\\]*?)\.(?<ext>[^.]*)$
                //^(?<series>[^\\$]+)\\[^\\$]*?(?:s(?<season>[0-1]?\d)ep?(?<episode>\d\d)|(?<season>(?:[0-1]\d|(?<!\d)\d))x?(?<episode>\d\d))(?!\d)(?:[ .-]?(?:s\k<season>e?(?<episode2>\d{2}(?!\d))|\k<season>x?(?<episode2>\d{2}(?!\d))|(?<episode2>\d\d(?!\d))|E(?<episode2>\d\d))|)[ -.]*(?<title>(?!.*sample)[^\\]*?[^\\]*?)\.(?<ext>[^.]*)$
                //(?<series>[^\\\[]*) - \[(?<season>[0-9]{1,2})x(?<episode>[0-9\W]+)\](( |)(-( |)|))(?<title>(?![^\\]*?sample)[^$]*?)\.(?<ext>[^.]*)
                //(?<series>[^\\$]*) - season (?<season>[0-9]{1,2}) - (?<title>(?![^\\]*?sample)[^$]*?)\.(?<ext>[^.]*)
                //<series> - <season>x<episode> - <title>.<ext>
                //<series>\Season <season>\Episode <episode> - <title>.<ext>
                //<series>\<season>x<episode> - <title>.<ext>

                /////////////////////////////////

                String SeriesName = filtered.replaceAll(" s\\d+\\D?e\\D?\\d+.*", "");
                SeriesName = SeriesName.replaceAll(" \\d+\\D?x\\D?\\d+.*", "");

                //Sometimes the release groups insert their name in front of the title, so letzs check if the frist word contains a '-'
                /*String firstWord = "";
                String[] spaceSplit = SeriesName.split(" ", 2);
                if (spaceSplit.length == 2) {
                    firstWord = spaceSplit[0];
                } else {
                    firstWord = SeriesName;
                }

                String[] minusSplit = firstWord.split("-", 2);
                if (minusSplit.length == 2) {
                    SeriesName = minusSplit[1] + (spaceSplit.length == 2 ? " " + spaceSplit[1] : "");
                }*/

                {
                    Pattern pSeasonEpisode = Pattern.compile(" s(\\d+)\\D?e\\D?(\\d+)");
                    Matcher mSeasonEpisode = pSeasonEpisode.matcher(filtered);
                    if (mSeasonEpisode.find()) {
                            movie.Season = Integer.valueOf(mSeasonEpisode.group(1));
                            movie.Episode = Integer.valueOf(mSeasonEpisode.group(2));
                    }
                }

                if (movie.Season == 0 && movie.Episode == 0) {
                    Pattern pSeasonEpisode = Pattern.compile(" (\\d+)\\D?x\\D?(\\d+)");
                    Matcher mSeasonEpisode = pSeasonEpisode.matcher(filtered);
                    if (mSeasonEpisode.find()) {
                            movie.Season = Integer.valueOf(mSeasonEpisode.group(1));
                            movie.Episode = Integer.valueOf(mSeasonEpisode.group(2));
                    }
                }

                //Sometimes the Season and Episode info is like this 812 for Season: 8 Episode: 12
                if (movie.Season == 0 && movie.Episode == 0) {
                    Pattern pSeasonEpisode = Pattern.compile(" (\\d+)(\\d\\d)");
                    Matcher mSeasonEpisode = pSeasonEpisode.matcher(filtered);
                    String seasonStr="";
                    while (mSeasonEpisode.find()) { //use last one found because year 2008 is also that pattern
                            movie.Season = Integer.valueOf(mSeasonEpisode.group(1));
                            movie.Episode = Integer.valueOf(mSeasonEpisode.group(2));
                            seasonStr=mSeasonEpisode.group(1)+mSeasonEpisode.group(2);
                    }
                    // delete the last found and everything after that
                    SeriesName = SeriesName.replaceAll(" "+seasonStr+".*", "");
                }

                movie.SearchString = SeriesName.trim();
                Logger.print(movie.Filename + " : Using \"" + movie.SearchString + "\" to get title");

                if(movie.SearchString.length() > 0) {
                    movie.Ignoring = false;
                    movie.needsUpdate = true;
                } else {
                    movie.Ignoring = true;
                    movie.needsUpdate = false;
                }

                movie.DataProvider = new valerie.provider.theTvDb();
                movie.ArtProvider = new valerie.provider.theTvDb();

                database.addMediaInfo(movie);
            }
        }
    }
}
