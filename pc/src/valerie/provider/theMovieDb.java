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
public class theMovieDb extends provider {

    public void getDataByTitle(MediaInfo info) {
        if(info.isMovie)
            getMoviesByTitle(info);
    }

    public void getDataById(MediaInfo info) {
        if(info.isMovie)
            getMoviesById(info);        
    }

    public void getArtById(MediaInfo info) {
        if(info.isMovie)
            getMoviesArtById(info);
    }

    //////////////////////////////////////////////////
    //////////////////////////////////////////////////
    //////////////////////////////////////////////////
    private String APIKEY = "7bcd34bb47bc65d20a49b6b446a32866";
    private String apiImdbLookup = "http://api.themoviedb.org/2.0/Movie.imdbLookup?api_key=" + APIKEY + "&imdb_id=";
    private String apiSearch = "http://api.themoviedb.org/2.0/Movie.search?api_key=" + APIKEY + "&title=";
    private String apiGetInfo = "http://api.themoviedb.org/2.0/Movie.getInfo?api_key=" + APIKEY + "=";

     public void getMoviesByTitle(MediaInfo info) {
           Document xml = null;
           try {
               String urlTitle = info.SearchString;
               urlTitle = urlTitle.replaceAll(" ", "+");
               xml = new valerie.tools.webgrabber().getXML(new URL(apiSearch + urlTitle));
           } catch (Exception ex) {}

           if (xml == null)
                return;

           List movieList = ((org.jdom.Element)(xml.getRootElement().getChildren("moviematches")).get(0)).getChildren("movie");
           for(int i = 0; i < movieList.size(); i++)
           {
               org.jdom.Element eMovie = (org.jdom.Element) movieList.get(i);

               //<release>1984-10-26</release>
               if(info.Year > 1900 && info.Year < 2020) {
                   org.jdom.Element eRelease = eMovie.getChild("release");
                   if(eRelease != null) {
                        String sYear = eRelease.getText();
                        sYear = sYear.substring(0, sYear.indexOf("-"));

                        if(info.Year < Integer.valueOf(sYear) - 1 || info.Year > Integer.valueOf(sYear) + 1)
                            continue;

                        info.Year = Integer.valueOf(sYear);
                   }
               }
               org.jdom.Element eTitle = eMovie.getChild("title");
               if(eTitle != null)
                    info.Title = eTitle.getText();

               break;
           }
            return;
        }

    public void getMoviesById(MediaInfo info) {
           Document xml = null;
           try {               
               xml =  new valerie.tools.webgrabber().getXML(new URL(apiImdbLookup + "/tt" + String.format("%07d", info.Imdb)));
           } catch (Exception ex) {}

           if (xml == null)
                return;

           List movieList = ((org.jdom.Element)(xml.getRootElement().getChildren("moviematches")).get(0)).getChildren("movie");
           for(int i = 0; i < movieList.size(); i++)
           {
               org.jdom.Element eMovie = (org.jdom.Element) movieList.get(i);

               //<release>1984-10-26</release>
               if(info.Year > 1900 && info.Year < 2020) {
                   org.jdom.Element eRelease = eMovie.getChild("release");
                   if(eRelease != null) {
                        String sYear = eRelease.getText();
                        sYear = sYear.substring(0, sYear.indexOf("-"));

                        if(info.Year < Integer.valueOf(sYear) - 1 || info.Year > Integer.valueOf(sYear) + 1)
                            continue;

                        info.Year = Integer.valueOf(sYear);
                   }
               }
               org.jdom.Element eTitle = eMovie.getChild("title");
               if(eTitle != null)
                    info.Title = eTitle.getText();                    
               break;
           }
           
           return;
        }

    public void getMoviesArtById(MediaInfo info) {
           Document xml = null;
           try {
               xml =  new valerie.tools.webgrabber().getXML(new URL(apiImdbLookup + "tt" + String.format("%07d", info.Imdb)));
           } catch (Exception ex) {}

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
