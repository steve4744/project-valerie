/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package valerie.provider;

import java.net.URL;
import java.util.ArrayList;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import valerie.MediaInfo;
import valerie.tools.DebugOutput;

/**
 *
 * @author i7
 */
public class LocalImdbProvider {
    private static final String URL = "http://www.imdb.<lang>/";
    private static final String apiSearch = URL + "find?q=<search>";
    private static final String apiPlot = URL + "title/<imdbid>/plotsummary";

    private static final String apiEpisodeList = URL + "title/<imdbid>/episodes";

    private static final String NO_PLOT_RESULT = "id=\"swiki_empty\"";

    private static final String DIV_TITLE_START_EXAMPLE = "<a class=\"main\" href=\"/title/tt0416449/\">";
    private static final String DIV_TITLE_START = "<a class=\"main\" href=\"/title/tt";
    private static final String DIV_TITLE_END = "</a>";

    private static final String DIV_PLOT_START = "<div id=\"swiki.2.1\">";
    private static final String DIV_PLOT_END = "</div>";


    private static class ResultEntry {
        public String  ImdbId;
        public String  Title;
        public int Season;
        public int Episode;

        public ResultEntry() {
            Season = -1;
            Episode = -1;
        }

        @Override
        public String toString() {
            return Title + ":" + Season + ":" + Episode + ":" + ImdbId;
        }
    }

    private static final String DIV_EPISODE_START = "<tr> <td valign=\"top\"><h3>";
    private static final String DIV_EPISODE_FLAG = ">";
    private static final String DIV_EPISODE_END = "</a></h3>";
    private static ArrayList<ResultEntry> getEpisodes(String html, String lang) {
        ArrayList<ResultEntry> results = new ArrayList<ResultEntry>();

        String[] htmlSplitted = html.split(DIV_EPISODE_START);
        for(String htmlSplitter : htmlSplitted) {
            htmlSplitter = htmlSplitter.trim();
            if(!htmlSplitter.startsWith(DIV_EPISODE_FLAG))
                continue;

            int pos = htmlSplitter.indexOf(DIV_EPISODE_END);
            if(pos < 0)
                continue;

            ResultEntry entry = new ResultEntry();
            String strEntry = htmlSplitter.substring(0, pos);

            Pattern pImdbId = Pattern.compile("/title/tt\\d*/");
            Matcher mImdbId = pImdbId.matcher(strEntry);
            if(mImdbId.find()) {
                String sImdbId = mImdbId.group();
                sImdbId = sImdbId.replaceAll("/title/", "");
                sImdbId = sImdbId.replaceAll("/", "");
                entry.ImdbId = sImdbId;
            }


            String season_start = "";
            String season_end = "";
            String episode_start = "";
            String episode_end = "";

            if(lang.equals("de")) {
                season_start = "Staffel ";
                season_end = ", ";
                episode_start = "Folge ";
                episode_end = ": ";
            } else if(lang.equals("it")) {
                season_start = "Stagione ";
                season_end = ", ";
                episode_start = "Episodio ";
                episode_end = ": ";
            } else if(lang.equals("es")) {
                season_start = "Temporada ";
                season_end = ", ";
                episode_start = "Episodio ";
                episode_end = ": ";
            } else if(lang.equals("fr")) {
                season_start = "Saison ";
                season_end = ", ";
                episode_start = "Episode ";
                episode_end = ": ";
            } else if(lang.equals("pt")) {
                season_start = "Temporada ";
                season_end = ", ";
                episode_start = "Epis&#xF3;dio "; //TODO: I dont belive that this will work as this should be already converted to UTF-8
                episode_end = ": ";
            }

            pos = strEntry.indexOf(season_start);
            if(pos >= 0) {
                String se = strEntry.substring(pos + season_start.length());
                pos = se.indexOf(season_end);
                if(pos >= 0) {
                    String season = se.substring(0, pos);
                    entry.Season = Integer.valueOf(season);


                }
            }

            pos = strEntry.indexOf(episode_start);
            if(pos >= 0) {
                String se = strEntry.substring(pos + episode_start.length());
                pos = se.indexOf(episode_end);
                if(pos >= 0) {
                    String episode = se.substring(0, pos);
                    entry.Episode = Integer.valueOf(episode);


                }
            }

            results.add(entry);
        }

        return results;
    }

    private static boolean getTitle(MediaInfo info, String html) {
        //<a class="main" href="/title/tt0416449/">300</a>
        String title = html;
        //if(title.contains(NO_PLOT_RESULT)) {
        //    return false;
        //}

        int pos = title.indexOf(DIV_TITLE_START);
        if(pos < 0)
            return false;

        title = title.substring(pos + DIV_TITLE_START_EXAMPLE.length());

        pos = title.indexOf(DIV_TITLE_END);
        if(pos < 0)
            return false;

        info.Title = title.substring(0, pos).replaceAll("\"", "").trim();

        ////

        title = html;
        pos = title.indexOf(DIV_TITLE_START, pos);
        if(pos < 0)
            return true;

        title = title.substring(pos + DIV_TITLE_START_EXAMPLE.length());

        pos = title.indexOf(DIV_TITLE_END);
        if(pos < 0)
            return true;

        info.Title = title.substring(0, pos).replaceAll("\"", "").trim();

        return true;
    }

    private static boolean getPlot(MediaInfo info, String html) {
        String plot = html;
        if(plot.contains(NO_PLOT_RESULT)) {
            return false;
        }

        int pos = plot.indexOf(DIV_PLOT_START);
        if(pos < 0)
            return false;

        plot = plot.substring(pos + DIV_PLOT_START.length());

        pos = plot.indexOf(DIV_PLOT_END);
        if(pos < 0)
            return false;

        info.Plot = plot.substring(0, pos).replaceAll("<br>", " ").trim() + " [IMDB.LOCAL]";
        return true;
    }


    public static boolean getMoviesByImdbID(MediaInfo info, String lang) {
        return getMoviesByImdbID(info, lang, null);
    }

    private static boolean getMoviesByImdbID(MediaInfo info, String lang, String imdbid) {

        DebugOutput.printl("");

        String html = null;

        String url = apiPlot;
        if(imdbid != null)
            url = url.replaceAll("<imdbid>", imdbid);
        else
            url = url.replaceAll("<imdbid>", info.ImdbId);
        url = url.replaceAll("<lang>", lang);
        html = valerie.tools.WebGrabber.getHtml(url);

        if (html == null)
            return false;

        getTitle(info, html);
        getPlot(info, html);

        return true;
    }

    public static boolean getEpisodeByImdbID(MediaInfo info, String lang) {

        DebugOutput.printl("");

        if(info.Episode == -1 || info.Season == -1)
            return false;

        String html = null;

        String url = apiEpisodeList;
        url = url.replaceAll("<imdbid>", info.ImdbId);
        url = url.replaceAll("<lang>", lang);
        html = valerie.tools.WebGrabber.getHtml(url);

        if (html == null)
            return false;

        ArrayList<ResultEntry> results = getEpisodes(html, lang);
        for(ResultEntry result : results) {
            if(result.Season == info.Season && result.Episode == info.Episode) {
                return getMoviesByImdbID(info, lang, result.ImdbId);
            }
        }

        return false;
    }


}
