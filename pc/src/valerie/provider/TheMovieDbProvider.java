/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package valerie.provider;

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
                if(!ePlot.getText().equals("No overview found.")) {
                info.Plot = ePlot.getText().replaceAll("\r\n", " ").replaceAll("\n"," ");
                info.Plot += " [TMDB.ORG]";
                return true;
            }
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
            info.Runtime = Integer.valueOf(eRuntime.getText());
            return true;
        }
        return false;
    }

    public boolean getRating(MediaInfo info, org.jdom.Element elem) {
        org.jdom.Element eRating = elem.getChild("rating");
        if(eRating != null && eRating.getText() != null && eRating.getText().length() > 0) {
            if(!eRating.getText().equals("0.0")) {
                try {
                    Float fPopularity = Float.valueOf(eRating.getText());
                    info.Popularity = fPopularity.intValue();
                    return true;
                }catch(Exception ex) {
                }
            }
        }
        return false;
    }

    public boolean getGenre(MediaInfo info, org.jdom.Element elem) {
        String genre = "";
        org.jdom.Element eGenres = elem.getChild("categories");
        List<org.jdom.Element> children = eGenres.getChildren("category");
        for(org.jdom.Element eGenre : children) {
            if(eGenre != null && eGenre.getAttributeValue("type").equals("genre"))
                genre += eGenre.getAttributeValue("name") + "|";
        }

        if(genre.length() > 0) {
            info.Genres = genre.substring(0, genre.length() - 1);
            return true;
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
        xml = valerie.tools.WebGrabber.getXml(url);

        if (xml == null)
            return false;


        List<org.jdom.Element> moviesList = xml.getRootElement().getChildren("movies");
        if(moviesList.size() <= 0)
            return false;
        List<org.jdom.Element> movieList = moviesList.get(0).getChildren("movie");
        for(org.jdom.Element eMovie : movieList) {
            getTmdbId(info, eMovie);
            //getImdbId(info, eMovie);
            getName(info, eMovie);
            getOverview(info, eMovie);
            getReleased(info, eMovie);
            getRating(info, eMovie);
            getRuntime(info, eMovie);
            getGenre(info, eMovie);

            return true;
        }
        return false;
    }

    public boolean getMovie(MediaInfo info, String lang) {
        if(info.TmDbId.equals(info.TmDbIdNull))
            return false;

        lang = lang.toLowerCase();

        if(lang.equals("en")) // en already parsed using getMovieByImdbID()
            return true;

        Document xml = null;

        String url = apiGetInfo;
        url = url.replaceAll("<tmdbid>", String.valueOf(info.TmDbId));
        url = url.replaceAll("<lang>", lang);
        xml = valerie.tools.WebGrabber.getXml(url);

        if (xml == null)
            return false;

        List<org.jdom.Element> moviesList = xml.getRootElement().getChildren("movies");
        if(moviesList.size() <= 0)
            return false;
        List<org.jdom.Element> movieList = moviesList.get(0).getChildren("movie");
        for(org.jdom.Element eMovie : movieList) {

            if(!getTranslated(eMovie))
                continue;

            //getTmdbId(info, eMovie);
            //getImdbId(info, eMovie);
            getName(info, eMovie);
            getOverview(info, eMovie);
            getReleased(info, eMovie);
            getRating(info, eMovie);
            getRuntime(info, eMovie);
            getGenre(info, eMovie);

            return true;
        }
        return false;
    }

    public boolean getArtById(MediaInfo info) {
        if(info.ImdbId.equals(info.ImdbIdNull))
            return false;

        Document xml = null;
        String url = apiImdbLookup;
        url = url.replaceAll("<imdbid>", String.valueOf(info.ImdbId));
        url = url.replaceAll("<lang>", "en");
        xml = valerie.tools.WebGrabber.getXml(url);

        if (xml == null)
            return false;

        List<org.jdom.Element> moviesList = xml.getRootElement().getChildren("movies");
        if(moviesList.size() <= 0)
            return false;
        List<org.jdom.Element> movieList = moviesList.get(0).getChildren("movie");
        for(org.jdom.Element eMovie : movieList) {
            List<org.jdom.Element> imagesList = eMovie.getChildren("images");
            if(imagesList.size() <= 0)
                continue;
            List<org.jdom.Element> imageList = imagesList.get(0).getChildren("image");
            for(org.jdom.Element eImage : imageList) {
                if (eImage.getAttributeValue("type") != null && eImage.getAttributeValue("type").equals("poster")) {
                    if(info.Poster.length() == 0 && eImage.getAttributeValue("url") != null)
                        info.Poster = eImage.getAttributeValue("url");
                }
                if (eImage.getAttributeValue("type") != null && eImage.getAttributeValue("type").equals("backdrop")) {
                    if(info.Backdrop.length() == 0 && eImage.getAttributeValue("url") != null)
                        info.Backdrop = eImage.getAttributeValue("url");
                }
                
                if(info.Poster.length() > 0 && info.Backdrop.length() > 0)
                    return true;

                continue;
            }
        }
        return false;
    }

}
