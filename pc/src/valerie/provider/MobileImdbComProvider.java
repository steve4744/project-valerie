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
public class MobileImdbComProvider {
    private static final String URL = "http://m.imdb.com/";
    private static final String apiSearch = URL + "find?q=<search>";

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


    public static void getMoviesByTitle(MediaInfo info) {

        DebugOutput.printl(info.SearchString);

        String html = null;
        try {
            String url = apiSearch;
            url = url.replaceAll("<search>", String.valueOf(info.SearchString.replaceAll(" ", "+")));
            html = valerie.tools.WebGrabber.getText(new URL(url));
        } catch (Exception ex) {}

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
            break;
        }
    }
}
