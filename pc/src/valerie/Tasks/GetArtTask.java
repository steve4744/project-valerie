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

        Database pDatabase = (Database)pWorker.get("Database");
        MediaInfo[] movies = pDatabase.getAsArray();

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
                if (movie.isSerie) {
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

        if (media.isMovie || media.isSerie) {

            media.ArtProvider.getArtById(media);

            String id = media.isMovie?media.ImdbId:media.TheTvDbId;
            if (id.equals(media.ImdbIdNull) || id.equals(media.TheTvDbIdNull))
                return;

            File checkIfFilePNGalreadyExists = new File("converted/" + id + "_poster.png");
            if (checkIfFilePNGalreadyExists == null || !checkIfFilePNGalreadyExists.exists()) {
                if (media.Poster.length() > 0) {
                    String url = new valerie.tools.WebGrabber().getText("http://val.duckbox.info/cgi-bin/convert.py?" + id + ";poster;" + media.Poster);
                    if(!url.equals("NONE"))
                        new valerie.tools.WebGrabber().getFile("http://val.duckbox.info" + url, "converted/" + id + "_poster.png");
                }

            }

            File checkIfFileM1ValreadyExists = new File("converted/" + id + "_backdrop.m1v");
            if (checkIfFileM1ValreadyExists == null || !checkIfFileM1ValreadyExists.exists()) {
                if (media.Backdrop.length() > 0) {
                    String url = new valerie.tools.WebGrabber().getText("http://val.duckbox.info/cgi-bin/convert.py?" + id + ";backdrop;" + media.Backdrop);
                    if(!url.equals("NONE")) {
                        new valerie.tools.WebGrabber().getFile("http://val.duckbox.info" + url, "converted/" + id + "_backdrop.m1v");
                        new valerie.tools.WebGrabber().getFile("http://val.duckbox.info" + url.replace("_mvi", "").replace("mvi", "png"), "converted/" + id + "_backdrop.png");
                    }
                }

            }
        }
    }

    private void getMediaArtMovie(MediaInfo movie, Integer Resize, String Encoder, Integer Resolution) {
        Logger.print(movie.Filename + " : Got title \"" + movie.Title + "\". Downloading posters");

        File checkIfFilePNGalreadyExists = new File("converted/" + movie.ImdbId + "_poster.png");
        if (checkIfFilePNGalreadyExists == null || !checkIfFilePNGalreadyExists.exists()) {

            File checkIfFileAlreadyExists = new File("download/" + movie.ImdbId + "_poster.jpg");
            if (checkIfFileAlreadyExists == null || !checkIfFileAlreadyExists.exists()) {

                movie.ArtProvider.getArtById(movie);
                if (movie.Poster.length() > 0) {
                    new valerie.tools.WebGrabber().getFile(movie.Poster, "download/" + movie.ImdbId + "_poster.jpg");
                }
            }



            checkIfFileAlreadyExists = new File("download/" + movie.ImdbId + "_poster.jpg");
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

                    new pngquant().exec("converted\\" + movie.ImdbId + "_poster.png", "converted\\" + movie.ImdbId + "_poster.png");

                } catch (Exception ex) {
                    System.out.println(ex.toString());
                }
            }
        }

        Logger.print(movie.Filename + " : Got title \"" + movie.Title + "\". Downloading backdrops");

        File converted = new File("converted/" + movie.ImdbId + "_backdrop.m1v");
        if (converted == null || !converted.exists()) {

            File downloaded = new File("download/" + movie.ImdbId + "_backdrop.jpg");
            if (downloaded == null || !downloaded.exists()) {
                if (movie.Backdrop == null || movie.Backdrop.length() <= 0) {
                    movie.ArtProvider.getArtById(movie);
                }

                if (movie.Backdrop.length() > 0) {
                    new valerie.tools.WebGrabber().getFile(movie.Backdrop, "download/" + movie.ImdbId + "_backdrop.jpg");
                }
            }



            downloaded = new File("download/" + movie.ImdbId + "_backdrop.jpg");
            if (downloaded != null && downloaded.exists()) {

                switch (Resize)
                {
                    case 0:
                        break;
                    case 1:
                        new Resize().internalExcec("download/" + movie.ImdbId + "_backdrop.jpg", "download/" + movie.ImdbId + "_backdrop.jpg", Resolution);
                        break;
                    case 2:
                        new Resize().exec("download/" + movie.ImdbId + "_backdrop.jpg", "download/" + movie.ImdbId + "_backdrop.jpg", Resolution);
                        break;
                }

                if (Encoder.equals("mencoder")) {
                    new mencoder().exec("download/" + movie.ImdbId + "_backdrop.jpg", "converted/" + movie.ImdbId + "_backdrop.m1v", Resolution);
                } else if(Encoder.equals("jepg2yuv+mpeg2enc")) {
                    new Encode().exec("download/" + movie.ImdbId + "_backdrop", "converted/" + movie.ImdbId + "_backdrop.m1v",Resolution);
                }
                
                
            }
        }
    }

    private void getMediaArtSeries(MediaInfo movie, Integer Resize, String Encoder, Integer Resolution) {
        Logger.print(movie.Filename + " : Got title \"" + movie.Title + "\". Downloading posters");

        File checkIfFilePNGalreadyExists = new File("converted/" + movie.TheTvDbId + "_poster.png");
        if (checkIfFilePNGalreadyExists == null || !checkIfFilePNGalreadyExists.exists()) {

            File checkIfFileAlreadyExists = new File("download/" + movie.TheTvDbId + "_poster.jpg");
            if (checkIfFileAlreadyExists == null || !checkIfFileAlreadyExists.exists()) {

                movie.ArtProvider.getArtById(movie);
                if (movie.Poster.length() > 0) {
                    new valerie.tools.WebGrabber().getFile(movie.Poster, "download/" + movie.TheTvDbId + "_poster.jpg");
                }
            }



            checkIfFileAlreadyExists = new File("download/" + movie.TheTvDbId + "_poster.jpg");
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

                    new pngquant().exec("converted\\" + movie.TheTvDbId + "_poster.png", "converted\\" + movie.TheTvDbId + "_poster.png");

                } catch (Exception ex) {
                    System.out.println(ex.toString());
                }
            }
        }

        Logger.print(movie.Filename + " : Got title \"" + movie.Title + "\". Downloading backdrops");

        File converted = new File("converted/" + movie.TheTvDbId + "_backdrop.m1v");
        if (converted == null || !converted.exists()) {

            File downloaded = new File("download/" + movie.TheTvDbId + "_backdrop.jpg");
            if (downloaded == null || !downloaded.exists()) {
                if (movie.Backdrop == null || movie.Backdrop.length() <= 0) {
                    movie.ArtProvider.getArtById(movie);
                }

                if (movie.Backdrop.length() > 0) {
                    new valerie.tools.WebGrabber().getFile(movie.Backdrop, "download/" + movie.TheTvDbId + "_backdrop.jpg");
                }
            }



            downloaded = new File("download/" + movie.TheTvDbId + "_backdrop.jpg");
            if (downloaded != null && downloaded.exists()) {

                switch (Resize)
                {
                    case 0:
                        break;
                    case 1:
                        new Resize().internalExcec("download/" + movie.TheTvDbId + "_backdrop.jpg", "download/" + movie.TheTvDbId + "_backdrop.jpg", Resolution);
                        break;
                    case 2:
                        new Resize().exec("download/" + movie.TheTvDbId + "_backdrop.jpg", "download/" + movie.TheTvDbId + "_backdrop.jpg", Resolution);
                        break;
                }

                if (Encoder.equals("mencoder")) {
                    new mencoder().exec("download/" + movie.TheTvDbId + "_backdrop.jpg", "converted/" + movie.TheTvDbId + "_backdrop.m1v", Resolution);
                } else if(Encoder.equals("jepg2yuv+mpeg2enc")) {
                    new Encode().exec("download/" + movie.TheTvDbId + "_backdrop", "converted/" + movie.TheTvDbId + "_backdrop.m1v", Resolution);
                }
            }
        }
    }
}
