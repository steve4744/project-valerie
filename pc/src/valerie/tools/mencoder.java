/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package valerie.tools;

import java.io.File;
import java.util.concurrent.Semaphore;

/**
 *
 * @author Admin
 */
public class mencoder {

    private static Semaphore sem = new Semaphore(1, true);

    public void exec(String Input, String Output, Integer Resolution) {
         try {

            Process process;
            int exitval;

            for(int retry = 0; retry < 1; retry++) {

                File fInput = new File(Input);
                File fOutput = new File(fInput.getName());

                FileUtils.copyFile(fInput, fOutput);

                String cmd = "";

                if(System.getProperty("file.separator").equals("/")) //Linux
                    cmd = "mencoder";
                else //Windows
                    cmd = "bin\\mencoder";
                
                String Res = "1024:576";
                String fps = "25";

                switch(Resolution)
                {
                    case 0:
                        Res = "1024:576";
                        fps = "25";
                        break;
                    case 1:
                        Res = "1280:720";
                        fps = "60";
                        break;
                    case 2:
                        Res = "1920:1080";
                        fps = "60";
                        break;
                }

                cmd += " mf://" + fOutput.getName() + " -mf fps="+fps+":type=jpg -embeddedfonts -o " +  Output + " -ovc lavc -lavcopts vcodec=mpeg1video -vf scale="+Res;                
                sem.acquire();
                System.out.println("mencoder "+Input+" >>>>>>");
                process = Runtime.getRuntime().exec(cmd);
                process.getErrorStream().close();
                process.getInputStream().close();
                process.getOutputStream().close();

                process.waitFor();
                exitval = process.exitValue();
                System.out.printf("mencoder-Exit: %d\n",  exitval);
                System.out.println("<<<<<<mencoder");
                sem.release();

               fOutput.delete();

                if( new File(Output).exists() && new File(Output).length() > 2000 )
                    break;

                new File(Output).delete();
            }
        } catch(Exception ex) {
            System.out.println("mencoder: "+ex.toString());

        }
    }
}

