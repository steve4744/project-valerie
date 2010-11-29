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
 * @author Admin
 */
public class ImdbProvider {

    //////////////////////////////////////////////////


    //////////////////////////////////////////////////
    //////////////////////////////////////////////////
    String apiSearchTV = "http://www.imdb.com/search/title?title=<title>&title_type=tv_series,mini_series";
    String apiImdbLookup = "http://akas.imdb.com/title/";
    String apiSearch = "http://akas.imdb.com/find?s=tt;q=";

    public void getMoviesByImdbId(MediaInfo info) {
       String xml = null;

       if(info.ImdbId.equals(info.ImdbIdNull))
           return;

      xml = valerie.tools.WebGrabber.getHtml(apiImdbLookup + info.ImdbId);

       if (xml == null)
            return;
       Pattern pDetails = Pattern.compile("<title>.+?\\(\\d{4}[\\/IVX]*\\).*?</title>.+</body>");
       Matcher mDetails = pDetails.matcher(xml);
       if(mDetails.find()) {
           //Details Screen!
           parseDetailsScreen(info, xml/*mDetails.group()*/);
       }
       return;
     }


     public void getMoviesByTitle(MediaInfo mediaInfo) {
       String pageHtml = null;

       if(mediaInfo.isSerie ||mediaInfo.isEpisode) {
            String urlTitle = mediaInfo.SearchString;
            urlTitle = urlTitle.replaceAll(" ", "+");
            pageHtml = valerie.tools.WebGrabber.getHtml(apiSearchTV.replaceAll("<title>", urlTitle));

            if (pageHtml == null)
                return;

            Pattern pDetails = Pattern.compile("Most Popular TV Series/Mini-Series With Title Matching");
            Matcher mDetails = pDetails.matcher(pageHtml);
            if(mDetails.find()) {
                parseAdvancedSearchResultScreen(mediaInfo, pageHtml);
                getMoviesByImdbId(mediaInfo);

                if(!mediaInfo.ImdbId.equals(mediaInfo.ImdbIdNull))
                    return;
            }
       }


       try {
            String urlTitle = mediaInfo.SearchString;
            urlTitle = urlTitle.replaceAll(" ", "+");
            pageHtml = valerie.tools.WebGrabber.getText(apiSearch + urlTitle);
       } catch (Exception ex) {
           DebugOutput.printl("Download failed!");
           DebugOutput.printl(ex.getMessage());
       }

       if (pageHtml == null) {
           DebugOutput.printl("No page has been returned");
           return;
        }
       //Pattern pDetails = Pattern.compile("<title>.+?\\(\\d{4}[\\/IVX]*\\).*?</title>.+</body>");
       Pattern pDetails = Pattern.compile("content=\"http://www.imdb.com/title/tt\\d*/\" />");
       Matcher mDetails = pDetails.matcher(pageHtml);
       if(mDetails.find()) {
           //Details Screen!
           String details = mDetails.group();
           Pattern pImdbId = Pattern.compile("/title/tt\\d*/");
            Matcher mImdbId = pImdbId.matcher(details);
            if(mImdbId.find()) {
                String sImdbId = mImdbId.group();
                sImdbId = sImdbId.replaceAll("/title/", "");
                sImdbId = sImdbId.replaceAll("/", "");

                mediaInfo.ImdbId = sImdbId;
                getMoviesByImdbId(mediaInfo);
            }
           //parseDetailsScreen(mediaInfo, pageHtml/*mDetails.group()*/);

       } else {
           //Check if its the search result screen
           Pattern pSearchResult = Pattern.compile("<title>IMDb Title Search</title>");
           Matcher mSearchResult = pSearchResult.matcher(pageHtml);
           if(mSearchResult.find()) {
                parseSearchResultScreen(mediaInfo, pageHtml);
                getMoviesByImdbId(mediaInfo);
           }

       }

       return;
     }

     private void getMoviesPlot(MediaInfo info) {
       String xml = null;
       try {
          xml = valerie.tools.WebGrabber.getHtml(apiImdbLookup + info.ImdbId + "/plotsummary");
       } catch (Exception ex) {}

       if (xml == null)
            return;
       Pattern pPlot = Pattern.compile("<p class=\"plotpar\">\\s*(.+?)<i>.*?</i>.*?</p>");
       Matcher mPlot = pPlot.matcher(xml);
       if(mPlot.find()) {
            String sPlot = mPlot.group();
            sPlot = sPlot.replaceAll(".*plotpar\">", "");
            sPlot = sPlot.replaceAll("<i>.*", "");

            info.Plot = sPlot;
       }
       return;
     }
          
     private void parseDetailsScreen(MediaInfo info, String details)
     {
        Pattern pTitle = Pattern.compile("<title>.+?\\(\\d{4}[\\/IVX]*\\).*?</title>");
        Matcher mTitle = pTitle.matcher(details);

        if(mTitle.find()) {
            String sTitleAndYear = mTitle.group();
            sTitleAndYear = sTitleAndYear.replaceAll("<title>", "");
            sTitleAndYear = sTitleAndYear.replaceAll("</title>", "");
            sTitleAndYear = sTitleAndYear.trim();

            String sYear = "0";

            Pattern pYear = Pattern.compile("\\((\\d{4})[\\/IVX]*\\)");
            Matcher mYear = pYear.matcher(sTitleAndYear);
            if(mYear.find()) {
                sYear = mYear.group(1);
            }
            //sYear = sYear.replaceAll("(\\(|\\))", "").trim();
            String sTitle = "";

            Pattern pTitleString = Pattern.compile(".*\\(\\d{4}[\\/IVX]*\\)");
            Matcher mTitleString = pTitleString.matcher(sTitleAndYear);
            if(mTitleString.find()) {
                sTitle = mTitleString.group();
            }

            info.Title = sTitle.replaceAll("\\(\\d{4}[\\/IVX]*\\)", "").trim();
            try {
                info.Year = Integer.valueOf(sYear);
            } catch(Exception ex) {
                info.Year = 0;
            }
        }

        Pattern pImdbId = Pattern.compile("/title/tt\\d*/");
        Matcher mImdbId = pImdbId.matcher(details);
        if(mImdbId.find()) {
            String sImdbId = mImdbId.group();
            sImdbId = sImdbId.replaceAll("/title/", "");
            sImdbId = sImdbId.replaceAll("/", "");

            info.ImdbId = sImdbId;
        }

        Pattern pDirectorsBlock = Pattern.compile("<h5>Director[s]?:</h5>.*?</div>");
        Matcher mDirectorsBlock = pDirectorsBlock.matcher(details);
        if(mDirectorsBlock.find()) {
            String sDirectorsBlock = mDirectorsBlock.group();

            Pattern pDirectors = Pattern.compile("<a href=\"/name/nm\\d{7}/\"[^>]*>([^<]+)</a>");
            Matcher mDirectors = pDirectors.matcher(sDirectorsBlock);
            info.Directors="";
            while(mDirectors.find()) {
                String sDirectors = mDirectors.group();
                sDirectors = sDirectors.replaceAll(".*/\';\">", "");
                sDirectors = sDirectors.replaceAll("</a>", "");
                info.Directors += sDirectors + "; ";
            }
        }

        Pattern pWritersBlock = Pattern.compile("<div class=\"info\">\\s+<h5>Writer[s]?(?: <a href=\"[^\"]+\">\\([^)]+\\)</a>)?:</h5>.+?</div>");
        Matcher mWritersBlock = pWritersBlock.matcher(details);
        if(mWritersBlock.find()) {
            String sWritersBlock = mWritersBlock.group();

            Pattern pWriters = Pattern.compile("<a href=\"/name/nm\\d+/\"[^>]*>([^<]+)</a>");
            Matcher mWriters = pWriters.matcher(sWritersBlock);
            info.Writers="";
            while(mWriters.find()) {
                String sWriters = mWriters.group();
                sWriters = sWriters.replaceAll(".*/\';\">", "");
                sWriters = sWriters.replaceAll("</a>", "");
                info.Writers += sWriters + "; ";
            }
        }

        Pattern pRuntime = Pattern.compile("<h5>Runtime:</h5>.*?(\\d+) min\\s+");
        Matcher mRuntime = pRuntime.matcher(details);
        if(mRuntime.find()) {
            String sRuntime = mRuntime.group();

            sRuntime = sRuntime.replaceAll("<h5>Runtime:</h5>(<div class=\"info-content\">)?", "");
            info.Runtime = Integer.valueOf(sRuntime);
        }

        Pattern pGenresBlock = Pattern.compile("<h5>Genre:</h5>.+?</div>");
        Matcher mGenresBlock = pGenresBlock.matcher(details);
        if(mGenresBlock.find()) {
            String sGenresBlock = mGenresBlock.group();

            Pattern pGenres = Pattern.compile("<a href=\"/Sections/Genres/[^/]+/\">(.+?)</a>");
            Matcher mGenres = pGenres.matcher(sGenresBlock);
            info.Genres="";
            while(mGenres.find()) {
                String sGenres = mGenres.group();
                sGenres = sGenres.replaceAll(".*/\">", "");
                sGenres = sGenres.replaceAll("</a>", "");
                info.Genres += sGenres + "; ";
            }
        }

        // <h5>Tagline:</h5><div class="info-content">In the Year
        // /title/tt0088247/taglines
        // This site should be parsed later and alternativ taglines displayed if the first one is to long.
        
        Pattern pTag = Pattern.compile("<h5>Tagline:</h5><div class=\"info-content\">.*?<");
        Matcher mTag = pTag.matcher(details);
        if(mTag.find()) {
            String sTag = mTag.group();

            sTag = sTag.replaceAll("<h5>Tagline:</h5><div class=\"info-content\">", "");
            sTag = sTag.replaceAll("<", "");
            info.Tag = sTag;
        }
        
        Pattern pReleaseDate = Pattern.compile("<h5>Release Date:</h5>.*(\\d+) (\\w+) (\\d{4}).*<h5>Genre:</h5>");
        Matcher mReleaseDate = pReleaseDate.matcher(details);
        if(mReleaseDate.find()) {
            String sMonth = mReleaseDate.group(2).replaceAll("January", "01").replaceAll("February", "02").replaceAll("March", "03").replaceAll("April", "04");
            sMonth=sMonth.replaceAll("May", "05").replaceAll("June", "06").replaceAll("July", "07").replaceAll("August", "08");
            sMonth=sMonth.replaceAll("September", "09").replaceAll("October", "10").replaceAll("November", "11").replaceAll("December", "12");
            info.Releasedate = mReleaseDate.group(3)+"-"+sMonth+"-"+String.format("%02d", Integer.parseInt(mReleaseDate.group(1)));
        }
        
        Pattern pPopularity = Pattern.compile("<div class=\"(starbar-)?meta\">.*?<b>(\\d+.\\d+)/10</b>");
        Matcher mPopularity = pPopularity.matcher(details);
        if(mPopularity.find()) {
            String sPopularity = mPopularity.group();

            sPopularity = sPopularity.replaceAll(".*<b>", "");
            sPopularity = sPopularity.replaceAll("/10</b>", "");
            Float fPopularity = Float.valueOf(sPopularity);
            info.Popularity = fPopularity.intValue();
        }

        getMoviesPlot(info);
        info.checkStrings();
        return;
     }

     private void parseSearchResultScreen(MediaInfo info, String xml)
     {
        Pattern pMovies = Pattern.compile("><a href=\"/title/(tt\\d{7})/\"[^>]+>(?!&#34;)([^<]+)</a> \\((\\d{4})[\\/IVX]*\\)(?! \\(VG\\))([^<]*<br>&#160;aka(.+?)</td>)?");
        Matcher mMovies = pMovies.matcher(xml);
        if(mMovies.find()) {
            String sMovie = mMovies.group();

            Pattern pImdbId = Pattern.compile("/title/tt\\d*/");
            Matcher mImdbId = pImdbId.matcher(sMovie);
            if(mImdbId.find()) {
                String sImdbId = mImdbId.group();
                sImdbId = sImdbId.replaceAll("/title/", "");
                sImdbId = sImdbId.replaceAll("/", "");

                info.ImdbId = sImdbId;
            }
        }

        //alternatives
        info.AlternativesCount = 0;
        while(mMovies.find() && info.AlternativesCount < MediaInfo.alternativesMax) {
            String sMovie = mMovies.group();

            Pattern pImdbId = Pattern.compile("/title/tt\\d*/");
            Matcher mImdbId = pImdbId.matcher(sMovie);
            if(mImdbId.find()) {
                String sImdbId = mImdbId.group();
                sImdbId = sImdbId.replaceAll("/title/", "");
                sImdbId = sImdbId.replaceAll("/", "");

                info.AlternativImdbs[info.AlternativesCount] = sImdbId;
            }

            Pattern pTitle = Pattern.compile(";\">[^<]+</a>");
            Matcher mTitle = pTitle.matcher(sMovie);
            if(mTitle.find()) {
                String sTitle = mTitle.group();
                sTitle = sTitle.replaceAll(";\">", "");
                sTitle = sTitle.replaceAll("</a>", "");

                info.AlternativTitles[info.AlternativesCount] = sTitle;
            }

            info.AlternativesCount++;
        }

        return;
     }

     private void parseAdvancedSearchResultScreen(MediaInfo info, String xml)
     {
        //# <a href="/title/tt1219024/" title="Castle (2009 TV Series)">
        Matcher mMovies = Pattern.compile("<a href=\"/title/(tt\\d{7})/\" title=\"([^\\(]+)\\((\\d{4})[^)]*\\)\">").matcher(xml);
        if(mMovies.find()) {
            String sMovie = mMovies.group();

            Matcher mImdbId = Pattern.compile("/title/tt\\d*/").matcher(sMovie);
            if(mImdbId.find()) {
                String sImdbId = mImdbId.group();
                sImdbId = sImdbId.replaceAll("/title/", "");
                sImdbId = sImdbId.replaceAll("/", "");

                info.ImdbId = sImdbId;
            }

            Matcher mTitle = Pattern.compile("title=\"([^\\(]+)\\(").matcher(sMovie);
            if(mTitle.find()) {
                String group = mTitle.group();
                String title = group.replaceAll("title=\"", "");
                title = title.substring(0, title.length()-1).trim();


                title = title.replaceAll("[\\.]", "");
                info.Title = title;
            }
        }

        info.AlternativesCount = 0;
        info.AlternativImdbs[info.AlternativesCount]  = info.ImdbId;
        info.AlternativTitles[info.AlternativesCount] = info.Title;
        info.AlternativesCount++;

        //alternatives
        while(mMovies.find() && info.AlternativesCount < MediaInfo.alternativesMax) {
            String sMovie = mMovies.group();

            Pattern pImdbId = Pattern.compile("/title/tt\\d*/");
            Matcher mImdbId = pImdbId.matcher(sMovie);
            if(mImdbId.find()) {
                String sImdbId = mImdbId.group();
                sImdbId = sImdbId.replaceAll("/title/", "");
                sImdbId = sImdbId.replaceAll("/", "");

                info.AlternativImdbs[info.AlternativesCount] = sImdbId;
            }

            Pattern pTitle = Pattern.compile("title=\"([^\\(]+)\\(");
            Matcher mTitle = pTitle.matcher(sMovie);
            if(mTitle.find()) {
                String sTitle = mTitle.group();
                sTitle = sTitle.replaceAll("title=\"", "");
                sTitle = sTitle.substring(0, sTitle.length()-1).trim();

                sTitle = sTitle.replaceAll("[\\.]", "");
                info.AlternativTitles[info.AlternativesCount] = sTitle;
            }

            info.AlternativesCount++;
        }

        // Workaround for imdb, it seems that for some shows there is an POINT at the end of the title
        // e.g. http://www.imdb.com/title/tt1442464/



        if(!info.Title.toLowerCase().equals(info.SearchString.toLowerCase())) {
            for(int i = 0; i < info.AlternativesCount; i++) {
                if(info.AlternativTitles[i].toLowerCase().equals(info.SearchString.toLowerCase())) {
                    info.ImdbId = info.AlternativImdbs[i];
                    info.Title = info.AlternativTitles[i];

                    break;
                }
            }
        }

        return;
     }
}
