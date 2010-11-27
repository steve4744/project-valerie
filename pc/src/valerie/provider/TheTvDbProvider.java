/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package valerie.provider;

import java.net.URL;
import java.util.List;
import org.jdom.Document;
import valerie.MediaInfo;

/**
 *
 * @author Admin
 */
public class TheTvDbProvider {

    //////////////////////////////////////////////////
    //////////////////////////////////////////////////
    //////////////////////////////////////////////////

    private String APIKEY = "3A042860EF9F9160";
    private String apiSearch = "http://www.thetvdb.com/api/GetSeries.php?seriesname=";
    private String apiSearchEpisode = "http://www.thetvdb.com/api/" + APIKEY + "/series/<seriesid>/default/<season>/<episode>/<lang>.xml";
    private String apiSearchAllEpisodes = "http://www.thetvdb.com/api/" + APIKEY + "/series/<seriesid>/all/<lang>.xml";
    private String apiArt = "http://www.thetvdb.com/banners/";

    private String apiSeriesByID = "http://www.thetvdb.com/data/series/<seriesid>/<lang>.xml";;
    private String apiSeriesByImdbID = "http://thetvdb.com/api/GetSeriesByRemoteID.php?imdbid=";


    private static final int PLOT_MIN_LEN = 10;
    private static final int IMDBID_MIN_LEN = 3; // tt0

    public boolean getImdbId(MediaInfo info, org.jdom.Element elem) {
        org.jdom.Element eImdb = elem.getChild("IMDB_ID");
        if(eImdb != null && eImdb.getText() != null && eImdb.getText().length() >= IMDBID_MIN_LEN) {
            String strImdb = eImdb.getText();
            while(strImdb.endsWith("/"))
                strImdb = strImdb.substring(0, strImdb.length()-1);
            info.ImdbId = strImdb;
            return true;
        }
        return false;
    }

    public boolean getOverview(MediaInfo info, org.jdom.Element elem) {
        org.jdom.Element ePlot = elem.getChild("Overview");
        if(ePlot != null && ePlot.getText() != null && ePlot.getText().length() > PLOT_MIN_LEN) {
            info.Plot = ePlot.getText().replaceAll("\r\n", " ").replaceAll("\n"," ");
            info.Plot += " [THETVDB.COM]";
            return true;
        }
        return false;
    }

    public boolean getTvdbId(MediaInfo info, org.jdom.Element elem) {
        org.jdom.Element eID = elem.getChild("id");
        if(eID != null && eID.getText() != null && eID.getText().length() > 0) {
            info.TheTvDbId = eID.getText();
            return true;
        }
        return false;
    }

    public boolean getFirstAired(MediaInfo info, org.jdom.Element elem) {
        org.jdom.Element eYear = elem.getChild("FirstAired");
        if(eYear != null && eYear.getText() != null && eYear.getText().length() > 0) {
            String strYear = eYear.getText();
            try {
                info.Year = Integer.parseInt(strYear.substring(0, strYear.indexOf("-")));
                return true;
            }catch(Exception ex) {
            }
        }
        return false;
    }

    public boolean getSeriesName(MediaInfo info, org.jdom.Element elem) {
        org.jdom.Element eTitle = elem.getChild("SeriesName");
        if(eTitle != null && eTitle.getText() != null && eTitle.getText().length() > 0) {
            info.Title = eTitle.getText();
            return true;
        }
        return false;
    }

    public boolean getEpisodeAndSeasonNumber(MediaInfo info, org.jdom.Element elem) {
        org.jdom.Element eEpisodeNumber = elem.getChild("EpisodeNumber");
        org.jdom.Element eSeasonNumber  = elem.getChild("SeasonNumber");

        if(eEpisodeNumber != null && eSeasonNumber != null &&
                eEpisodeNumber.getText() != null && eEpisodeNumber.getText().length() > 0 &&
                eSeasonNumber.getText()  != null && eSeasonNumber.getText().length()  > 0) {
            try {
                info.Episode = Integer.parseInt(eEpisodeNumber.getText());
                info.Season = Integer.parseInt(eSeasonNumber.getText());
                return true;
            }catch(Exception ex) {
            }
        }
        return false;
    }

    public boolean getEpisodeName(MediaInfo info, org.jdom.Element elem) {
        org.jdom.Element eTitle = elem.getChild("EpisodeName");
        if(eTitle != null && eTitle.getText() != null && eTitle.getText().length() > 0) {
            info.Title = eTitle.getText();
            return true;
        }
        return false;
    }
    
    public boolean getDirector(MediaInfo info, org.jdom.Element elem) {
        org.jdom.Element eDirector = elem.getChild("Director");
        if(eDirector != null && eDirector.getText() != null && eDirector.getText().length() > 0) {
            info.Directors = eDirector.getText().replaceAll("\r\n", " ").replaceAll("\n","; ");
            return true;
        }
        return false;
    }
    
    public boolean getWriter(MediaInfo info, org.jdom.Element elem) {
        org.jdom.Element eWriter = elem.getChild("Writer");
        if(eWriter != null && eWriter.getText() != null && eWriter.getText().length() > 0) {
            info.Writers = eWriter.getText().replaceAll("\r\n", " ").replaceAll("\n","; ");
            return true;
        }
        return false;
    }
    
    public boolean getRuntime(MediaInfo info, org.jdom.Element elem) {
        org.jdom.Element eRuntime = elem.getChild("Runtime");
        if(eRuntime != null && eRuntime.getText() != null && eRuntime.getText().length() > 0) {
            info.Runtime = eRuntime.getText().replaceAll("\r\n", " ").replaceAll("\n"," ") + " min";
            return true;
        }
        return false;
    }

    public boolean getRating(MediaInfo info, org.jdom.Element elem) {
        org.jdom.Element eRating = elem.getChild("Rating");
        if(eRating != null && eRating.getText() != null && eRating.getText().length() > 0) {
            try {
                Float fPopularity = Float.valueOf(eRating.getText());
                info.Popularity = fPopularity.intValue();
                return true;
            }catch(Exception ex) {
            }
        }
        return false;
    }

    public String getLanguage(org.jdom.Element elem) {
        org.jdom.Element eLang = elem.getChild("Language");
        if(eLang != null && eLang.getText() != null && eLang.getText().length() > 0) {
            return eLang.getText();
        }
        return "en";
    }

    //////////////////////////////////////////////////

    public boolean getSerieByImdbID(MediaInfo info) {
        if(info.ImdbId.equals(info.ImdbIdNull))
            return false;

        Document xml = null;
        try {
            String url = apiSeriesByImdbID + info.ImdbId;
            xml = valerie.tools.WebGrabber.getXML(new URL(url));
        } catch (Exception ex) {}

        if (xml == null)
            return false;

        List movieList = xml.getRootElement().getChildren("Series");
        for(int i = 0; i < movieList.size(); i++)
        {
            org.jdom.Element eMovie = (org.jdom.Element) movieList.get(i);

            getTvdbId(info, eMovie);
            //getImdbId(info, eMovie);
            getSeriesName(info, eMovie);
            getOverview(info, eMovie);
            getFirstAired(info, eMovie);
            getRuntime(info, eMovie);
            getRating(info, eMovie);

            return true;
        }
        return false;
    }

    public boolean getSerie(MediaInfo info, String lang) {
        if(info.TheTvDbId.equals(info.TheTvDbIdNull))
            return false;

        lang = lang.toLowerCase();

        if(lang.equals("en")) // en already parsed using getSerieByImdbID()
            return true;

        Document xml = null;
        try {

            String url = apiSeriesByID;
            url = url.replaceAll("<seriesid>", String.valueOf(info.TheTvDbId));
            url = url.replaceAll("<lang>", lang);
            xml = valerie.tools.WebGrabber.getXML(new URL(url));
        } catch (Exception ex) {}

        if (xml == null)
            return false;

        List movieList = xml.getRootElement().getChildren("Series");
        for(int i = 0; i < movieList.size(); i++)
        {
            org.jdom.Element eMovie = (org.jdom.Element) movieList.get(i);

            String entryLang = getLanguage(eMovie).toLowerCase();
            if(!entryLang.equals(lang))
                continue;

            //getTvdbId(info, eMovie);
            //getImdbId(info, eMovie);
            getSeriesName(info, eMovie);
            getOverview(info, eMovie);
            getFirstAired(info, eMovie);
            getRuntime(info, eMovie);
            getRating(info, eMovie);

            return true;
        }
        return false;
    }

    public boolean getEpisode(MediaInfo info, String lang) {

        if( info.TheTvDbId.equals(info.TheTvDbIdNull) || info.Episode == -1 || info.Season == -1)
            return false;

        lang = lang.toLowerCase();

        Document xml = null;
        try {
           String url = apiSearchAllEpisodes; //apiSearchAllEpisodes;
           url = url.replaceAll("<seriesid>", String.valueOf(info.TheTvDbId));
           url = url.replaceAll("<lang>", lang);
           url = url.replaceAll("<season>", String.valueOf(info.Season));
           url = url.replaceAll("<episode>", String.valueOf(info.Episode));

           xml = valerie.tools.WebGrabber.getXML(new URL(url));
        } catch (Exception ex) {}

        if (xml == null)
            return false;

        List movieList = xml.getRootElement().getChildren("Episode");
        for(int i = 0; i < movieList.size(); i++) {
            org.jdom.Element eMovie = (org.jdom.Element) movieList.get(i);

            String entryLang = getLanguage(eMovie).toLowerCase();
            if(!entryLang.equals(lang))
                continue;

            int episode = info.Episode;
            int season  = info.Season;
            if(getEpisodeAndSeasonNumber(info, eMovie) == false) {
                info.Episode = episode;
                info.Season  = season;
                continue;
            }

            if(info.Episode != episode || info.Season != season) {
                info.Episode = episode;
                info.Season  = season;
                continue;
            }

            //getImdbId(info, eMovie);
            //getTvdbId(info, eMovie);
            getEpisodeName(info, eMovie);
            getOverview(info, eMovie);
            getFirstAired(info, eMovie);


            getDirector(info, eMovie);
            getWriter(info, eMovie);
            getRuntime(info, eMovie);
            getRating(info, eMovie);

            return true;
        }

        return false;
    }

    public void getArtById(MediaInfo info) {
       Document xml = null;
       try {
           String url = apiSeriesByID;
           url = url.replaceAll("<seriesid>", String.valueOf( info.TheTvDbId));
           url = url.replaceAll("<lang>", "en");
               xml = valerie.tools.WebGrabber.getXML(new URL(url));
       } catch (Exception ex) {}

       if (xml == null)
            return;

       List movieList = xml.getRootElement().getChildren("Series");
       for(int i = 0; i < movieList.size(); i++)
       {
           org.jdom.Element eMovie = (org.jdom.Element) movieList.get(i);

           org.jdom.Element eBanner = eMovie.getChild("banner");
           if(eBanner != null && eBanner.getText().length() > 0)
                info.Banner = apiArt + eBanner.getText();

           org.jdom.Element ePoster = eMovie.getChild("poster");
           if(ePoster != null && ePoster.getText().length() > 0)
                info.Poster = apiArt + ePoster.getText();

           org.jdom.Element eFanart = eMovie.getChild("fanart");
           if(eFanart != null && eFanart.getText().length() > 0)
                info.Backdrop = apiArt + eFanart.getText();

           break;
       }
        return;
    }
}
