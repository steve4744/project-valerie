/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package valerie.provider;

import java.net.URL;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import org.jdom.Document;
import valerie.MediaInfo;

/**
 *
 * @author Admin
 */
public class Imdb extends provider {
     public void getDataByTitle(MediaInfo info) {
        if(info.isMovie)
            getMoviesByTitleAndYear(info);
    }

    public void getDataById(MediaInfo info) {
        if(info.isMovie)
            getMoviesByImdbId(info);
    }

    public void getArtById(MediaInfo info) {
    }


    //////////////////////////////////////////////////
    //////////////////////////////////////////////////
    //////////////////////////////////////////////////
    String apiImdbLookup = "http://akas.imdb.com/title/tt";
    String apiSearch = "http://akas.imdb.com/find?s=tt;q=";

    public void getMoviesByImdbId(MediaInfo info) {
       String xml = null;

       if(info.Imdb == 0)
           return;

       try {
          xml = new valerie.tools.webgrabber().getText(new URL(apiImdbLookup + info.Imdb));
       } catch (Exception ex) {}

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


     public void getMoviesByTitleAndYear(MediaInfo info) {
       String xml = null;
       try {
            String urlTitle = info.SearchString;
            urlTitle = urlTitle.replaceAll(" ", "+");
            xml = new valerie.tools.webgrabber().getText(new URL(apiSearch + urlTitle));
       } catch (Exception ex) {}

       if (xml == null)
            return;
       Pattern pDetails = Pattern.compile("<title>.+?\\(\\d{4}[\\/IVX]*\\).*?</title>.+</body>");
       Matcher mDetails = pDetails.matcher(xml);
       if(mDetails.find()) {
           //Details Screen!
           parseDetailsScreen(info, xml/*mDetails.group()*/);
       } else {
           //Check if its the search result screen
           Pattern pSearchResult = Pattern.compile("<title>IMDb Title Search</title>");
           Matcher mSearchResult = pSearchResult.matcher(xml);
           if(mSearchResult.find()) {
                parseSearchResultScreen(info, xml);
                getMoviesByImdbId(info);
           }

       }

       return;
     }

     private void getMoviesPlot(MediaInfo info) {
       String xml = null;
       try {
          xml = new valerie.tools.webgrabber().getText(new URL(apiImdbLookup + info.Imdb + "/plotsummary"));
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
     
     private void getMoviesLocalLanguage(MediaInfo info) {
         String xml = null;
         try {
            xml = new valerie.tools.webgrabber().getText(new URL(apiImdbLookup + info.Imdb + "/releaseinfo"));
         } catch (Exception ex) {}

         if (xml == null)
              return;
         Pattern pPlot = Pattern.compile("Also Known As \\(AKA\\)</a></h5>(.*?)</table>");
         Matcher mPlot = pPlot.matcher(xml);
         if(mPlot.find()) {
              String sPlot = mPlot.group(1);
              Pattern pTitle = Pattern.compile("<tr><td>(.*?)</td><td>(.*?)</td></tr>");
              Matcher mTitle = pTitle.matcher(sPlot);
              info.LocalTitle = "";
              while(mTitle.find()){
            	  if(mTitle.group(2).contains("Germany")&& !mTitle.group(2).contains("Germany (working title)"))
            		  info.LocalTitle = mTitle.group(1);
              }
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
            sImdbId = sImdbId.replaceAll("/title/tt", "");
            sImdbId = sImdbId.replaceAll("/", "");

            info.Imdb = Integer.valueOf(sImdbId);
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

            sRuntime = sRuntime.replaceAll("<h5>Runtime:</h5>", "");
            info.Runtime = sRuntime;
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

        Pattern pTag = Pattern.compile("<h5>Tagline:</h5>.*?<");
        Matcher mTag = pTag.matcher(details);
        if(mTag.find()) {
            String sTag = mTag.group();

            sTag = sTag.replaceAll("<h5>Tagline:</h5>", "");
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
        
        Pattern pPopularity = Pattern.compile("<div class=\"meta\">.*?<b>(\\d+.\\d+)/10</b>");
        Matcher mPopularity = pPopularity.matcher(details);
        if(mPopularity.find()) {
            String sPopularity = mPopularity.group();

            sPopularity = sPopularity.replaceAll(".*<b>", "");
            sPopularity = sPopularity.replaceAll("/10</b>", "");
            Float fPopularity = Float.valueOf(sPopularity);
            info.Popularity = fPopularity.intValue();
        }

        getMoviesPlot(info);
        getMoviesLocalLanguage(info);
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
                sImdbId = sImdbId.replaceAll("/title/tt", "");
                sImdbId = sImdbId.replaceAll("/", "");

                info.Imdb = Integer.valueOf(sImdbId);
            }
        }

        return;
     }
}
