/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package valerie.Tasks;

import valerie.*;
import java.awt.Graphics;
import java.awt.Image;
import java.awt.image.BufferedImage;
import java.io.File;
import javax.imageio.ImageIO;
import valerie.BackgroundWorker.ParentObject;
import valerie.tools.mencoder;
import valerie.tools.pngquant;

public class GetArtTask extends org.jdesktop.application.Task<Object, Void> {

    protected BackgroundWorker pWorker;
    protected int pThreadCount = 1;
    protected int pThreadId = 0;

    public GetArtTask(org.jdesktop.application.Application app,
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
            Logger.printBlocked("Getting Arts");
            Logger.setProgress(0);
        }
        this.setProgress((int)0);

        MediaInfoDB pDatabase = (MediaInfoDB)pWorker.get("Database");
        MediaInfo[] movies = pDatabase.getMediaInfo();

        int moviesSize = movies.length;

        for(int i = pThreadId; i < movies.length; i += pThreadCount) {
            MediaInfo movie = movies[i];

            Logger.setProgress((i * 100) / moviesSize);
            this.setProgress((i * 100) / moviesSize);
            this.setMessage(movie.Title);
            if (movie.isMovie) {
                getMediaArtMovie(movie);
            }
            if (movie.isSeries) {
                getMediaArtSeries( movie);
            }
        }

        /*if(pThreadId == 1) {
            Logger.printBlocked("Finished");
            Logger.setBlocked(false);
            Logger.setProgress(0);
        }*/

        this.setProgress(100);
        this.succeeded(null);

        return null;
    }

    @Override
    protected void succeeded(Object result) {

    }

    private void getMediaArtMovie(MediaInfo movie) {
        Logger.print(movie.Filename + " : Got title \"" + movie.Title + "\". Downloading posters");

        File checkIfFilePNGalreadyExists = new File("converted/tt" + movie.Imdb + "_poster.png");
        if (checkIfFilePNGalreadyExists == null || !checkIfFilePNGalreadyExists.exists()) {

            File checkIfFileAlreadyExists = new File("download/tt" + movie.Imdb + "_poster.jpg");
            if (checkIfFileAlreadyExists == null || !checkIfFileAlreadyExists.exists()) {

                movie.ArtProvider.getArtById(movie);
                if (movie.Poster.length() > 0) {
                    new valerie.tools.webgrabber().getFile(movie.Poster, "download/tt" + movie.Imdb + "_poster.jpg");
                }
            }



            checkIfFileAlreadyExists = new File("download/tt" + movie.Imdb + "_poster.jpg");
            if (checkIfFileAlreadyExists != null && checkIfFileAlreadyExists.exists()) {
                try {
                    BufferedImage image = ImageIO.read(checkIfFileAlreadyExists);
                    Image scaled = image.getScaledInstance(156, 214, Image.SCALE_SMOOTH);

                    BufferedImage bi = new BufferedImage(
                            156,
                            214,
                            BufferedImage.TYPE_INT_RGB);
                    Graphics g = bi.getGraphics();
                    g.drawImage(scaled, 0, 0, null);

                    ImageIO.write(bi, "png", checkIfFilePNGalreadyExists);

                    new pngquant().exec("converted\\tt" + movie.Imdb + "_poster.png", "converted\\tt" + movie.Imdb + "_poster.png");

                } catch (Exception ex) {
                    System.out.println(ex.toString());
                }
            }
        }

        Logger.print(movie.Filename + " : Got title \"" + movie.Title + "\". Downloading backdrops");

        File converted = new File("converted/tt" + movie.Imdb + "_backdrop.m1v");
        if (converted == null || !converted.exists()) {

            File downloaded = new File("download/tt" + movie.Imdb + "_backdrop.jpg");
            if (downloaded == null || !downloaded.exists()) {
                if (movie.Backdrop == null || movie.Backdrop.length() <= 0) {
                    movie.ArtProvider.getArtById(movie);
                }

                if (movie.Backdrop.length() > 0) {
                    new valerie.tools.webgrabber().getFile(movie.Backdrop, "download/tt" + movie.Imdb + "_backdrop.jpg");
                }
            }



            downloaded = new File("download/tt" + movie.Imdb + "_backdrop.jpg");
            if (downloaded != null && downloaded.exists()) {
                new mencoder().exec("download/tt" + movie.Imdb + "_backdrop.jpg", "converted/tt" + movie.Imdb + "_backdrop.m1v");
            }
        }
    }

    private void getMediaArtSeries(MediaInfo movie) {
        Logger.print(movie.Filename + " : Got title \"" + movie.Title + "\". Downloading posters");

        File checkIfFilePNGalreadyExists = new File("converted/" + movie.TheTvDb + "_poster.png");
        if (checkIfFilePNGalreadyExists == null || !checkIfFilePNGalreadyExists.exists()) {

            File checkIfFileAlreadyExists = new File("download/" + movie.TheTvDb + "_poster.jpg");
            if (checkIfFileAlreadyExists == null || !checkIfFileAlreadyExists.exists()) {

                movie.ArtProvider.getArtById(movie);
                if (movie.Poster.length() > 0) {
                    new valerie.tools.webgrabber().getFile(movie.Poster, "download/" + movie.TheTvDb + "_poster.jpg");
                }
            }



            checkIfFileAlreadyExists = new File("download/" + movie.TheTvDb + "_poster.jpg");
            if (checkIfFileAlreadyExists != null && checkIfFileAlreadyExists.exists()) {
                try {
                    BufferedImage image = ImageIO.read(checkIfFileAlreadyExists);
                    Image scaled = image.getScaledInstance(156, 214, Image.SCALE_SMOOTH);

                    BufferedImage bi = new BufferedImage(
                            156,
                            214,
                            BufferedImage.TYPE_INT_RGB);
                    Graphics g = bi.getGraphics();
                    g.drawImage(scaled, 0, 0, null);

                    ImageIO.write(bi, "png", checkIfFilePNGalreadyExists);

                    new pngquant().exec("converted\\" + movie.TheTvDb + "_poster.png", "converted\\" + movie.TheTvDb + "_poster.png");

                } catch (Exception ex) {
                    System.out.println(ex.toString());
                }
            }
        }

        Logger.print(movie.Filename + " : Got title \"" + movie.Title + "\". Downloading backdrops");

        File converted = new File("converted/" + movie.TheTvDb + "_backdrop.m1v");
        if (converted == null || !converted.exists()) {

            File downloaded = new File("download/" + movie.TheTvDb + "_backdrop.jpg");
            if (downloaded == null || !downloaded.exists()) {
                if (movie.Backdrop == null || movie.Backdrop.length() <= 0) {
                    movie.ArtProvider.getArtById(movie);
                }

                if (movie.Backdrop.length() > 0) {
                    new valerie.tools.webgrabber().getFile(movie.Backdrop, "download/" + movie.TheTvDb + "_backdrop.jpg");
                }
            }



            downloaded = new File("download/" + movie.TheTvDb + "_backdrop.jpg");
            if (downloaded != null && downloaded.exists()) {
                new mencoder().exec("download/" + movie.TheTvDb + "_backdrop.jpg", "converted/" + movie.TheTvDb + "_backdrop.m1v");
            }
        }
    }
}
