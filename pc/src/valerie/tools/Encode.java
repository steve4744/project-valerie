/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package valerie.tools;

import java.util.concurrent.Semaphore;

/**
 *
 * @author mguenther
 */
public class Encode {
    private static Semaphore sem = new Semaphore(1, true);

    public void exec(String Input, String Output, Integer Resolution) {
         try {

            Process process;
            int exitval;

            String cmd = "";
            
            if(System.getProperty("file.separator").equals("/")) //Linux
                cmd = "jpeg2yuv";
            else //Windows
                cmd = "cmd /c bin\\jpeg2yuv.exe";

            String ResX = "1024";
            String ResY = "576";
            String fps = "25";
            String Mode = "3";

            switch(Resolution)
            {
                case 0:
                    ResX = "1024";
                    ResY = "576";
                    fps = "25";
                    Mode = "3";
                    break;
                case 1:
                    ResX = "1280";
                    ResY = "720";
                    fps = "60";
                    Mode = "12";
                    break;
                case 2:
                    ResX = "1920";
                    ResY = "1088";
                    fps = "30";
                    Mode = "13";
                    break;
            }

            cmd += " -v 0 -f "+fps+" -n1 -I p -A 16:9 -j "+Input+".jpg > "+Input+".yuv";

            sem.acquire();
            System.out.println("YUV>>>>>>");
            System.out.println(cmd);
            process = Runtime.getRuntime().exec(cmd);
            //process.getErrorStream().close();
            //process.getInputStream().close();
            //process.getOutputStream().close();

            process.waitFor();
            exitval = process.exitValue();
            System.out.printf("YUV-Exit: %d\n",  exitval);
            System.out.println("<<<<<<YUV");

            if(System.getProperty("file.separator").equals("/")) //Linux
                cmd = "mpeg2enc";
            else //Windows
                cmd = "cmd /c bin\\mpeg2enc.exe ";            

            cmd += Input+".yuv -v 0 -f "+Mode+" -x "+ResX+" -y "+ResY+" -a 3 -4 1 -2 1 -q 1 -H --level high -o "+Output;

            System.out.println("enc>>>>>>");
            System.out.println(cmd);
            process = Runtime.getRuntime().exec(cmd);
            //process.getErrorStream().close();
            //process.getInputStream().close();
            //process.getOutputStream().close();

            process.waitFor();
            exitval = process.exitValue();
            System.out.printf("enc-Exit: %d\n",  exitval);
            System.out.println("<<<<<<enc");

            FileUtils.deleteFile(Input+".yuv");

            sem.release();
        } catch(Exception ex) {
            System.out.println("enc: "+ex.toString());
        }
    }
}
