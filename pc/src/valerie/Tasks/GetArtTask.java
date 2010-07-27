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
import valerie.tools.Resize;
import valerie.tools.Encode;
import valerie.tools.mencoder;
import valerie.tools.pngquant;
import java.util.*;

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

        Integer Resize = new valerie.tools.Properties().getPropertyInt("RESIZE_TYPE");
        String Encoder = new valerie.tools.Properties().getPropertyString("ENCODER_TYPE");
        Integer Resolution = new valerie.tools.Properties().getPropertyInt("RESOLUTION_TYPE");

        MediaInfoDB pDatabase = (MediaInfoDB)pWorker.get("Database");
        MediaInfo[] movies = pDatabase.getMediaInfo();

        int moviesSize = movies.length;

        for(int i = pThreadId; i < movies.length; i += pThreadCount) {
            MediaInfo movie = movies[i];

            Logger.setProgress((i * 100) / moviesSize);
            this.setProgress((i * 100) / moviesSize);
            this.setMessage(movie.Title);
            if(Encoder.equals("duckboxAPI")) {
                getMediaArtDuckboxAPI(movie);
            } else {
                if (movie.isMovie) {
                    getMediaArtMovie(movie, Resize, Encoder, Resolution);
                }
                if (movie.isSeries) {
                    getMediaArtSeries(movie, Resize, Encoder, Resolution);
                }
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

    private void getMediaArtDuckboxAPI(MediaInfo media) {

        if (media.isMovie || media.isSeries) {

            media.ArtProvider.getArtById(media);

            String id = media.isMovie?media.Imdb:media.TheTvDb;
            if (id.equals(media.ImdbNull) || id.equals(media.TheTvDbNull))
                return;

            File checkIfFilePNGalreadyExists = new File("converted/" + id + "_poster.png");
            if (checkIfFilePNGalreadyExists == null || !checkIfFilePNGalreadyExists.exists()) {
                if (media.Poster.length() > 0) {
                    String url = new valerie.tools.webgrabber().getText("http://val.duckbox.info/cgi-bin/convert.py?" + id + ";poster;" + media.Poster);
                    if(!url.equals("NONE"))
                        new valerie.tools.webgrabber().getFile("http://val.duckbox.info" + url, "converted/" + id + "_poster.png");
                }

            }

            File checkIfFileM1ValreadyExists = new File("converted/" + id + "_backdrop.m1v");
            if (checkIfFileM1ValreadyExists == null || !checkIfFileM1ValreadyExists.exists()) {
                if (media.Backdrop.length() > 0) {
                    String url = new valerie.tools.webgrabber().getText("http://val.duckbox.info/cgi-bin/convert.py?" + id + ";backdrop;" + media.Backdrop);
                    if(!url.equals("NONE")) {
                        new valerie.tools.webgrabber().getFile("http://val.duckbox.info" + url, "converted/" + id + "_backdrop.m1v");
                        new valerie.tools.webgrabber().getFile("http://val.duckbox.info" + url.replace("_mvi", "").replace("mvi", "png"), "converted/" + id + "_backdrop.png");
                    }
                }

            }
        }
    }

    private void getMediaArtMovie(MediaInfo movie, Integer Resize, String Encoder, Integer Resolution) {
        Logger.print(movie.Filename + " : Got title \"" + movie.Title + "\". Downloading posters");

        File checkIfFilePNGalreadyExists = new File("converted/" + movie.Imdb + "_poster.png");
        if (checkIfFilePNGalreadyExists == null || !checkIfFilePNGalreadyExists.exists()) {

            File checkIfFileAlreadyExists = new File("download/" + movie.Imdb + "_poster.jpg");
            if (checkIfFileAlreadyExists == null || !checkIfFileAlreadyExists.exists()) {

                movie.ArtProvider.getArtById(movie);
                if (movie.Poster.length() > 0) {
                    new valerie.tools.webgrabber().getFile(movie.Poster, "download/" + movie.Imdb + "_poster.jpg");
                }
            }



            checkIfFileAlreadyExists = new File("download/" + movie.Imdb + "_poster.jpg");
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

                    new pngquant().exec("converted\\" + movie.Imdb + "_poster.png", "converted\\" + movie.Imdb + "_poster.png");

                } catch (Exception ex) {
                    System.out.println(ex.toString());
                }
            }
        }

        Logger.print(movie.Filename + " : Got title \"" + movie.Title + "\". Downloading backdrops");

        File converted = new File("converted/" + movie.Imdb + "_backdrop.m1v");
        if (converted == null || !converted.exists()) {

            File downloaded = new File("download/" + movie.Imdb + "_backdrop.jpg");
            if (downloaded == null || !downloaded.exists()) {
                if (movie.Backdrop == null || movie.Backdrop.length() <= 0) {
                    movie.ArtProvider.getArtById(movie);
                }

                if (movie.Backdrop.length() > 0) {
                    new valerie.tools.webgrabber().getFile(movie.Backdrop, "download/" + movie.Imdb + "_backdrop.jpg");
                }
            }



            downloaded = new File("download/" + movie.Imdb + "_backdrop.jpg");
            if (downloaded != null && downloaded.exists()) {

                switch (Resize)
                {
                    case 0:
                        break;
                    case 1:
                        new Resize().internalExcec("download/" + movie.Imdb + "_backdrop.jpg", "download/" + movie.Imdb + "_backdrop.jpg", Resolution);
                        break;
                    case 2:
                        new Resize().exec("download/" + movie.Imdb + "_backdrop.jpg", "download/" + movie.Imdb + "_backdrop.jpg", Resolution);
                        break;
                }

                if (Encoder.equals("mencoder")) {
                    new mencoder().exec("download/" + movie.Imdb + "_backdrop.jpg", "converted/" + movie.Imdb + "_backdrop.m1v", Resolution);
                } else if(Encoder.equals("jepg2yuv+mpeg2enc")) {
                    new Encode().exec("download/" + movie.Imdb + "_backdrop", "converted/" + movie.Imdb + "_backdrop.m1v",Resolution);
                }
                
                
            }
        }
    }

    private void getMediaArtSeries(MediaInfo movie, Integer Resize, String Encoder, Integer Resolution) {
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

                switch (Resize)
                {
                    case 0:
                        break;
                    case 1:
                        new Resize().internalExcec("download/" + movie.TheTvDb + "_backdrop.jpg", "download/" + movie.TheTvDb + "_backdrop.jpg", Resolution);
                        break;
                    case 2:
                        new Resize().exec("download/" + movie.TheTvDb + "_backdrop.jpg", "download/" + movie.TheTvDb + "_backdrop.jpg", Resolution);
                        break;
                }

                if (Encoder.equals("mencoder")) {
                    new mencoder().exec("download/" + movie.TheTvDb + "_backdrop.jpg", "converted/" + movie.TheTvDb + "_backdrop.m1v", Resolution);
                } else if(Encoder.equals("jepg2yuv+mpeg2enc")) {
                    new Encode().exec("download/" + movie.TheTvDb + "_backdrop", "converted/" + movie.TheTvDb + "_backdrop.m1v", Resolution);
                }
            }
        }
    }
}
