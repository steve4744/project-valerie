/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package valerie.provider;

import java.util.regex.Matcher;
import java.util.regex.Pattern;
import valerie.MediaInfo;
import valerie.tools.DebugOutput;

/**
 *
 * @author i7
 */
public class GoogleProvider {

    private static final String URL = "http://www.google.com/";
    private static final String apiSearch = URL + "search?q=<search>";


    private static final String DIV_RESULT_START = "<li class=g>";
    private static final String DIV_RESULT_FLAG = "<h3 class=\"r\">";


    private boolean searchForSeasonAndEpisode(MediaInfo info, String result) {
        Matcher m = Pattern.compile("s\\d+e\\d+").matcher(result);
        if (m.find()) {
            String group = m.group();
            m = Pattern.compile("s\\d+").matcher(group.trim());
            if (m.find()) {
                info.Season = Integer.valueOf(m.group().substring(1).trim());
            }
            m = Pattern.compile("e\\d+").matcher(group.trim());
            if (m.find()) {
                info.Episode = Integer.valueOf(m.group().substring(1).trim());
            }
            return true;
        }
        return false;
    }

    public boolean getSeasonAndEpisodeFromEpisodeName(MediaInfo info) {
        DebugOutput.printl("");

        if(info.SearchString.length() <= 0)
            return false;

        String html = null;

        String url = apiSearch;
        url = url.replaceAll("<search>", info.SearchString);
        html = valerie.tools.WebGrabber.getHtml(url);

        if (html == null)
            return false;

        String[] htmlSplitted = html.split(DIV_RESULT_START);
        for(String htmlSplitter : htmlSplitted) {
            htmlSplitter = htmlSplitter.trim();
            if(!htmlSplitter.startsWith(DIV_RESULT_FLAG))
                continue;

            //int pos = htmlSplitter.indexOf(DIV_RESULT_END);
            //if(pos < 0)
            //    continue;

            if (searchForSeasonAndEpisode(info, htmlSplitter.toLowerCase()))
                return true;
            else
                continue;
        }
        return false;
    }
}
