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
public class TheMovieDbProvider {

    //////////////////////////////////////////////////
    //////////////////////////////////////////////////
    //////////////////////////////////////////////////
    private String APIKEY = "7bcd34bb47bc65d20a49b6b446a32866";

    private String apiImdbLookup = "http://api.themoviedb.org/2.1/Movie.imdbLookup/<lang>/xml/" + APIKEY + "/<imdbid>";
    private String apiGetInfo = "http://api.themoviedb.org/2.1/Movie.getInfo/<lang>/xml/" + APIKEY + "/<tmdbid>";


    //private String apiImdbLookup = "http://api.themoviedb.org/2.0/Movie.imdbLookup?api_key=" + APIKEY + "&imdb_id=";
    //private String apiSearch = "http://api.themoviedb.org/2.0/Movie.search?api_key=" + APIKEY + "&title=";

    private static final int PLOT_MIN_LEN = 10;
    private static final int IMDBID_MIN_LEN = 3; // tt0

    public boolean getTmdbId(MediaInfo info, org.jdom.Element elem) {
        org.jdom.Element eID = elem.getChild("id");
        if(eID != null && eID.getText() != null && eID.getText().length() > 0) {
            info.TmDbId = eID.getText();
            return true;
        }
        return false;
    }

    public boolean getName(MediaInfo info, org.jdom.Element elem) {
        org.jdom.Element eTitle = elem.getChild("name");
        if(eTitle != null && eTitle.getText() != null && eTitle.getText().length() > 0) {
            info.Title = eTitle.getText();
            return true;
        }
        return false;
    }

    public boolean getOverview(MediaInfo info, org.jdom.Element elem) {
        org.jdom.Element ePlot = elem.getChild("overview");
        if(ePlot != null && ePlot.getText() != null && ePlot.getText().length() > PLOT_MIN_LEN) {
            info.Plot = ePlot.getText().replaceAll("\r\n", " ").replaceAll("\n"," ");
            info.Plot += " [TMDB.COM]";
            return true;
        }
        return false;
    }

    public boolean getReleased(MediaInfo info, org.jdom.Element elem) {
        org.jdom.Element eYear = elem.getChild("released");
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

    public boolean getRuntime(MediaInfo info, org.jdom.Element elem) {
        org.jdom.Element eRuntime = elem.getChild("runtime");
        if(eRuntime != null && eRuntime.getText() != null && eRuntime.getText().length() > 0) {
            info.Runtime = eRuntime.getText().replaceAll("\r\n", " ").replaceAll("\n"," ") + " min";
            return true;
        }
        return false;
    }

    public boolean getRating(MediaInfo info, org.jdom.Element elem) {
        org.jdom.Element eRating = elem.getChild("rating");
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

    public boolean getTranslated(org.jdom.Element elem) {
        org.jdom.Element eTranslated = elem.getChild("translated");
        if(eTranslated != null && eTranslated.getText() != null && eTranslated.getText().length() > 0) {
            if(eTranslated.getText().equals("true"))
                return true;
        }
        return false;
    }

    //////////////////////////////
    //////////////////////////////

    public boolean getMovieByImdbID(MediaInfo info) {
        if(info.ImdbId.equals(info.ImdbIdNull))
            return false;

        Document xml = null;
        String url = apiImdbLookup;
        url = url.replaceAll("<imdbid>", String.valueOf(info.ImdbId));
        url = url.replaceAll("<lang>", "en");
        xml = valerie.tools.WebGrabber.getXML(url);

        if (xml == null)
            return false;

        List moviesList = xml.getRootElement().getChildren("movies");
        if(moviesList != null && moviesList.size() > 0) {
            List movieList = ((org.jdom.Element) moviesList.get(0)).getChildren("movie");
            for(int i = 0; i < movieList.size(); i++)
            {
                org.jdom.Element eMovie = (org.jdom.Element) movieList.get(i);

                getTmdbId(info, eMovie);
                //getImdbId(info, eMovie);
                getName(info, eMovie);
                getOverview(info, eMovie);
                getReleased(info, eMovie);
                getRating(info, eMovie);
                getRuntime(info, eMovie);

                return true;
            }

        }
        return false;
    }

    public boolean getMovie(MediaInfo info, String lang) {
        if(info.TmDbId.equals(info.TmDbIdNull))
            return false;

        if(lang.equals("en")) // en already parsed using getMovieByImdbID()
            return true;

        Document xml = null;

        String url = apiGetInfo;
        url = url.replaceAll("<tmdbid>", String.valueOf(info.TmDbId));
        url = url.replaceAll("<lang>", lang);
        xml = valerie.tools.WebGrabber.getXML(url);

        if (xml == null)
            return false;

        List moviesList = xml.getRootElement().getChildren("movies");
        if(moviesList != null && moviesList.size() > 0) {
            List movieList = ((org.jdom.Element) moviesList.get(0)).getChildren("movie");
            for(int i = 0; i < movieList.size(); i++)
            {
                org.jdom.Element eMovie = (org.jdom.Element) movieList.get(i);

                if(getTranslated(eMovie))
                    return false;

                //getTmdbId(info, eMovie);
                //getImdbId(info, eMovie);
                getName(info, eMovie);
                getOverview(info, eMovie);
                getReleased(info, eMovie);
                getRating(info, eMovie);
                getRuntime(info, eMovie);

                return true;
            }
        }
        return false;
    }

    public void getArtById(MediaInfo info) {
           Document xml = null;
           String url = apiImdbLookup;
           url = url.replaceAll("<imdbid>", String.valueOf(info.ImdbId));
           url = url.replaceAll("<lang>", "en");
           xml = valerie.tools.WebGrabber.getXML(url);

           if (xml == null)
                return;

           List movieList = ((org.jdom.Element)(xml.getRootElement().getChildren("moviematches")).get(0)).getChildren("movie");
           for(int i = 0; i < movieList.size(); i++)
           {
               org.jdom.Element eMovie = (org.jdom.Element) movieList.get(i);

               List ePosters = eMovie.getChildren("poster");
               for( Object ePoster : ePosters) {
                   if(ePoster != null && ((org.jdom.Element)ePoster).getAttributeValue("size").equals("mid"))
                        info.Poster = ((org.jdom.Element)ePoster).getText();
               }

               List eBackdrops = eMovie.getChildren("backdrop");
               for( Object eBackdrop : eBackdrops) {
                   if(eBackdrop != null && ((org.jdom.Element)eBackdrop).getAttributeValue("size").equals("original"))
                        info.Backdrop = ((org.jdom.Element)eBackdrop).getText();
               }
               break;
           }
            return;
        }

}
