/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package valerie.Tasks;

import valerie.BackgroundWorker;
import valerie.Logger;
import valerie.MediaInfo;
import valerie.MediaInfoDB;

/**
 *
 * @author Admin
 */
public class ParseFilelistTask extends org.jdesktop.application.Task<Object, Void> {

    protected BackgroundWorker pWorker;
    protected int pThreadCount = 1;
    protected int pThreadId = 0;

    public ParseFilelistTask(org.jdesktop.application.Application app,
            BackgroundWorker worker,
            int threadCount,
            int threadId) {
        super(app);

        if(threadCount > 0) {
            pThreadCount = threadCount;
            if(threadId >= 0 && threadId < threadCount) {
                pThreadId = threadId;
            }
        }

        pWorker = worker;
    }

    @Override
    protected Object doInBackground() {

        if(pThreadId == 0) {
            Logger.setBlocked(true);
            Logger.printBlocked("Parse Filelist");
            Logger.setProgress(0);
        }
        this.setProgress((int)0);

        MediaInfoDB database = (MediaInfoDB)pWorker.get("Database");
        MediaInfo[] movies = database.getMediaInfo();

        for (int i = pThreadId; i < movies.length; i += pThreadCount) {
            Float progress = (float) i * 100;
            progress /= movies.length;
            this.setProgress(progress.intValue());

            Logger.setProgress(progress.intValue());

            MediaInfo movie = movies[i];
            
            if (movie.needsUpdate) {
                if (movie.Imdb == 0) {
                    Logger.print(movie.Filename + " : Using Title\"" + movie.SearchString + "\" to get title");
                    this.setMessage(movie.SearchString);
                    //System.out.println("movie=" + movie.SearchString + " ismovie=" + movie.isMovie);

                    if (movie.isMovie) {
                        getMediaInfoMovie(database, movie);
                    } else if (movie.isEpisode || movie.isSeries) {
                        getMediaInfoSeries(database, movie);
                    }

                    //movie.Title = "[" + pThreadId + "] " + movie.Title;

                    Logger.print(movie.Filename + " : Got title \"" + movie.Title + "\".");
                }
                else {
                    Logger.print(movie.Filename + " : Using Imdb\"" + movie.Imdb + "\" to get title");
                    this.setMessage("Imdb: "+movie.Imdb);
                    //System.out.println("movie=" + movie.Imdb + " ismovie=" + movie.isMovie);

                    if (movie.isMovie) {
                        getMediaInfoMovie(database, movie);
                    } else if (movie.isEpisode || movie.isSeries) {
                        getMediaInfoSeries(database, movie);
                    }

                    //movie.Title = "[" + pThreadId + "] " + movie.Title;

                    Logger.print(movie.Filename + " : Got title \"" + movie.Title + "\".");
                }
            }
        }



        // We have to recheck if alle series got episodes, else delete unneeded series
        MediaInfo[] series = database.getMediaInfoSeries();
        for(MediaInfo info : series) {
            MediaInfo[] episodes = database.getMediaInfoEpisodes(info.TheTvDb);
            if(episodes.length == 0)
                database.deleteMediaInfo(info.ID);
        }

        this.setProgress(100);
        this.succeeded(null);

        /*Logger.printBlocked("Finished");
        Logger.setBlocked(false);
        Logger.setProgress(0);*/

        return null;
    }

    @Override
    protected void succeeded(Object result) {
     }

    private void getMediaInfoMovie(MediaInfoDB database, MediaInfo movie) {
        
      //if we have no searchstring, than the movie was imported from the archive and we dont need to reparse
        if (movie.needsUpdate) {
            if (movie.Imdb == 0){
                System.out.println("Getting Data by Title.");
                movie.getDataByTitle();
            }
            else {
                System.out.println("Getting Data by ID.");
                movie.getDataById();                                
            }
        }

        if (movie.Title.length() > 0) {
            movie.Ignoring = false;
            movie.needsUpdate = false;
        } else {
            movie.Ignoring = true;
            movie.needsUpdate = true;
        }
    }

    private void getMediaInfoSeries(MediaInfoDB database, MediaInfo movie) {

        //Ignore all series and only check episodes
        if (!movie.isSeries && movie.needsUpdate) {
            MediaInfo Series;
            if(movie.ArtProvider == null)movie.ArtProvider = new valerie.provider.theTvDb();
            if(movie.DataProvider == null)movie.DataProvider = new valerie.provider.theTvDb();

            if (database.getMediaInfoForSeries(movie.SearchString) == null) {
                Series = movie.clone();

                Series.isSeries = true;
                Series.isEpisode = false;
                Series.getDataByTitle();
                Series.Filename = "";
                Series.Path = "";

                if (Series.Title.length() > 0) {
                    Series.Ignoring = false;
                    Series.needsUpdate = false;

                    //check if this is a duplicate
                    MediaInfo duplicate = database.getMediaInfoForSeries(Series.TheTvDb);
                    if (duplicate == null) {
                        database.addMediaInfo(Series);
                    } else {
                        if(duplicate.SearchString.length() > 0)
                            duplicate.SearchString = duplicate.SearchString.substring(0, duplicate.SearchString.length()) + "|" + movie.SearchString + ")";
                        else
                            duplicate.SearchString =  "(" + movie.SearchString + ")";
                    }
                }
            } else {
                Series = database.getMediaInfoForSeries(movie.SearchString);
            }

            if (Series != null) {
                movie.Title = Series.Title;
                movie.Year = Series.Year;
                movie.Imdb = Series.Imdb;
                movie.Poster = Series.Poster;
                movie.Backdrop = Series.Backdrop;
                movie.Banner = Series.Banner;
                movie.Runtime = Series.Runtime;
                movie.Plot = Series.Plot;
                movie.Directors = Series.Directors;
                movie.Writers = Series.Writers;
                movie.Genres = Series.Genres;
                movie.Tag = Series.Tag;
                movie.Popularity = Series.Popularity;
                movie.TheTvDb = Series.TheTvDb;


            } else {
                System.out.println("Does this happen ???");
                return;
            }

            movie.getDataByTitle();

            if (movie.Title.length() > 0) {
                movie.Ignoring = false;
                movie.needsUpdate = false;
            }

        } else {
            if (movie.Title.length() > 0) {
                movie.Ignoring = false;
                movie.needsUpdate = false;
            }
        }
    }
}
