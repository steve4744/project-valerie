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
public class Resize {
    private static Semaphore sem = new Semaphore(1, true);

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
