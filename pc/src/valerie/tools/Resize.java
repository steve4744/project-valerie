/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package valerie.tools;

import com.sun.image.codec.jpeg.JPEGCodec;
import com.sun.image.codec.jpeg.JPEGEncodeParam;
import com.sun.image.codec.jpeg.JPEGImageDecoder;
import com.sun.image.codec.jpeg.JPEGImageEncoder;
import com.sun.media.jai.codec.FileSeekableStream;
import com.sun.media.jai.codec.PNGDecodeParam;
import com.sun.media.jai.codec.SeekableStream;
import java.awt.Point;
import java.awt.image.BufferedImage;
import java.io.File;
import java.io.FileOutputStream;
import java.util.concurrent.Semaphore;

/**
 *
 * @author mguenther
 */
public class Resize {
    private static Semaphore sem = new Semaphore(1, true);

    public void internalExcec(String Input, String Output, Integer Resolution) {
        //excec(Input, Output, Resolution);
        excecJAI(Input, Output, Resolution);
    }

    // This does not Work, we have to check the color format and reconvert it if necessary
    public void excecJAI(String Input, String Output, Integer Resolution) {

        File InputFile = new File(Input);
        File OutputFile = new File(Output);

        SeekableStream s = null;
        FileOutputStream o = null;


        try {
            System.out.println(Input);
            Point res = new Point(1024,576);

            switch(Resolution)
            {
                case 0:
                    res = new Point(1024,576);
                    break;
                case 1:
                    res = new Point(1280,720);
                    break;
                case 2:
                    res = new Point(1920,1080);
                    break;
            }

            s = new FileSeekableStream(InputFile);
            o = new FileOutputStream(OutputFile);

            JPEGImageDecoder jpegDecoder = JPEGCodec.createJPEGDecoder(s);
            //ImageDecoder dec = ImageCodec.createImageDecoder("JPEG", s, jdecparam);
            BufferedImage jpgImage = jpegDecoder.decodeAsBufferedImage();
            //ImageIO.write(jpgImage, "jpg", OutputFile);

            JPEGImageEncoder encode = JPEGCodec.createJPEGEncoder(o);
            JPEGEncodeParam param = encode.getDefaultJPEGEncodeParam(jpgImage);
            param.setQuality(0.75f, true);
            encode.encode(jpgImage, param);
        } catch (Exception ex) {
            //"download/tt1054485_backdrop.jpg"
            System.out.println(ex.toString());
        }
        finally {
            
        }
        
        try {
            if(s != null)
                s.close();
            if(o != null)
                o.close();
        } catch (Exception ex) {
            //"download/tt1054485_backdrop.jpg"
            System.out.println(ex.toString());
        }
    }

    public void exec(String Input, String Output, Integer Resolution) {
         try {

            Process process;
            int exitval;

            String cmd = "";

            if(System.getProperty("file.separator").equals("/")) //Linux
                cmd = "convert";
            else //Windows
                cmd = "bin/convert.exe";

            String Res = "1024x576";

            switch(Resolution)
            {
                case 0:
                    Res = "1024x576";
                    break;
                case 1:
                    Res = "1280x720";
                    break;
                case 2:
                    Res = "1920x1088";
                    break;
            }

            cmd += " \""+Input+"\" -colorspace YUV -resize "+Res+"! -gravity Center -crop "+Res+"+0+0 +repage "+Output;

            sem.acquire();
            System.out.println("Resize>>>>>>");
            System.out.println(cmd);
            process = Runtime.getRuntime().exec(cmd);
            process.getErrorStream().close();
            process.getInputStream().close();
            process.getOutputStream().close();

            process.waitFor();
            exitval = process.exitValue();
            System.out.printf("Resize-Exit: %d\n",  exitval);
            System.out.println("<<<<<<Resize");        
            sem.release();
            
        } catch(Exception ex) {
            System.out.println("Resize: "+ex.toString());
        }
    }
}
