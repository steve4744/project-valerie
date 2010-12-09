/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package valerie.provider;

import java.util.ArrayList;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import valerie.MediaInfo;
import valerie.tools.DebugOutput;

/**
 *
 * @author i7
 */
public class MobileImdbComProvider {
    private static final String URL = "http://m.imdb.com/";
    private static final String apiSearch = URL + "find?q=<search>";
    private static final String apiDetails = URL + "title/<imdbid>/";

    private static final String testNoResults = "<div class=\"noResults\">No Results</div>";

    private static class ResultEntry {
        public String  ImdbId;
        public String  Title;
        public boolean IsTVSeries;
        public int Year;

        public ResultEntry() {
            IsTVSeries = false;
            Year = -1;
        }

        @Override
        public String toString() {
            return Title + ":" + Year + ":" + ImdbId + ":" + IsTVSeries;
        }
    }

    private static final String DIV_TITLE_START = "<div class=\"title\">";
    private static final String DIV_TITLE_FLAG = "<a href=";
    private static final String DIV_TITLE_END = "</div>";
    private static ArrayList<ResultEntry> getResults(String html) {
        ArrayList<ResultEntry> results = new ArrayList<ResultEntry>();

        String[] htmlSplitted = html.split(DIV_TITLE_START);
        for(String htmlSplitter : htmlSplitted) {
            htmlSplitter = htmlSplitter.trim();
            if(!htmlSplitter.startsWith(DIV_TITLE_FLAG))
                continue;

            int pos = htmlSplitter.indexOf(DIV_TITLE_END);
            if(pos < 0)
                continue;

            ResultEntry entry = new ResultEntry();
            String strEntry = htmlSplitter.substring(0, pos);

            if(strEntry.contains("TV series"))
                entry.IsTVSeries = true;

            Pattern pImdbId = Pattern.compile("/title/tt\\d*/");
            Matcher mImdbId = pImdbId.matcher(strEntry);
            if(mImdbId.find()) {
                String sImdbId = mImdbId.group();
                sImdbId = sImdbId.replaceAll("/title/", "");
                sImdbId = sImdbId.replaceAll("/", "");
                entry.ImdbId = sImdbId;
            }

            Pattern pTitle = Pattern.compile(">.+</a>");
            Matcher mTitle = pTitle.matcher(strEntry);
            if(mTitle.find()) {
                String sTitle = mTitle.group();
                sTitle = sTitle.replaceAll("</a>", "");
                sTitle = sTitle.replaceAll(">", "");
                entry.Title = sTitle;
            }

            Pattern pYear = Pattern.compile("\\(\\d{4}\\s?");
            Matcher mYear = pYear.matcher(strEntry);
            if(mYear.find()) {
                String sYear = mYear.group().substring(1).trim();
                entry.Year = Integer.valueOf(sYear);
            }

            results.add(entry);
        }

        return results;
    }

    private static final String DIV_INFO_START = "<div class=\"mainInfo\">";
    private static final String DIV_INFO_END = "</div>";
    private static final String DIV_TAG_START = "<p>";
    private static final String DIV_TAG_END = "</p>";
    private static final String DIV_VOTES_START = "<div class=\"votes\">";
    private static final String DIV_VOTES_END = "</strong>";

    private static String getInfo(String html) {
        String info = html;
        //if(title.contains(NO_PLOT_RESULT)) {
        //    return false;
        //}

        int pos = info.indexOf(DIV_INFO_START);
        if(pos < 0)
            return null;

        info = info.substring(pos + DIV_INFO_START.length());

        pos = info.indexOf(DIV_INFO_END);
        if(pos < 0)
            return null;

        return info.substring(0, pos).trim();
    }

    private static boolean getTag(MediaInfo info, String html) {
        String tag = getInfo(html);
        if(tag == null) {
            return false;
        }

        int pos = tag.indexOf(DIV_TAG_START);
        if(pos < 0)
            return false;

        tag = tag.substring(pos + DIV_TAG_START.length());

        pos = tag.indexOf(DIV_TAG_END);
        if(pos < 0)
            return false;

        info.Tag = tag.substring(0, pos).trim();
        return true;
    }

    private static boolean getVotes(MediaInfo info, String html) {
        String votes = html;
        if(votes == null) {
            return false;
        }

        int pos = votes.indexOf(DIV_VOTES_START);
        if(pos < 0)
            return false;

        votes = votes.substring(pos + DIV_VOTES_START.length());

        pos = votes.indexOf(DIV_VOTES_END);
        if(pos < 0)
            return false;

        votes = votes.substring(0, pos).trim();

        votes = votes.replaceAll("<strong>", "");
        votes = votes.trim();

        
        String vote = votes;
        if(votes.length() > 2) {
            vote = votes.split("[.]")[0];
        }
        info.Popularity = Integer.valueOf(vote);

        return true;
    }

    //////////////////////////////////

    public static void getMoviesByTitle(MediaInfo info) {

        DebugOutput.printl(info.SearchString);

        if(!info.ImdbId.equals(info.ImdbIdNull)) {
            if(getMoviesByImdbID(info))
                return;
        }

        String html = null;

        String url = apiSearch;
        url = url.replaceAll("<search>", info.SearchString);
        html = valerie.tools.WebGrabber.getHtml(url);

        if (html == null)
            return;

        if(html.contains(testNoResults)) {
            return;
        }

        ArrayList<ResultEntry> results = getResults(html);
        for(ResultEntry result : results) {
            if(info.isEpisode || info.isSerie) {
                if(!result.IsTVSeries)
                    continue;
            } else { // isMovie
                if(result.IsTVSeries)
                    continue;
            }

            info.ImdbId = result.ImdbId;
            info.Title = result.Title;

            if(getMoviesByImdbID(info))
                return;

            break;
        }
    }

    public static boolean getMoviesByImdbID(MediaInfo info) {

         String html = null;

        String url = apiDetails;
        url = url.replaceAll("<imdbid>", info.ImdbId);
        html = valerie.tools.WebGrabber.getHtml(url);

        if (html == null)
            return false;

        getTag(info, html);
        getVotes(info, html);

        return true;
    }
}
