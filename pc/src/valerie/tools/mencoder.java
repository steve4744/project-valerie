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

    public void exec(String Input, String Output) {
         try {
            for(int retry = 0; retry < 2; retry++) {

                File fInput = new File(Input);
                File fOutput = new File(fInput.getName());

                FileUtils.copyFile(fInput, fOutput);

                String cmd = "";

                if(System.getProperty("file.separator").equals("/")) //Linux
                    cmd = "mencoder";
                else //Windows
                    cmd = "bin\\mencoder";
                
                cmd += " mf://" + fOutput.getName() + " -mf type=jpg -ovc lavc -lavcopts vcodec=mpeg2video -oac copy -o " +  Output + " -vf scale=1024:576";
                sem.acquire();
                System.out.println("------>>>>>>");
                Process process = Runtime.getRuntime().exec(cmd);
                process.getErrorStream().close();
                process.getInputStream().close();
                process.getOutputStream().close();

                process.waitFor();
                int exitval = process.exitValue();
                System.out.printf("Exit: %d\n",  exitval);
                System.out.println("<<<<<<------");
                sem.release();

               fOutput.delete();

                if( new File(Output).exists() && new File(Output).length() > 2000 )
                    break;

                new File(Output).delete();
            }
        } catch(Exception ex) {
            System.out.println(ex.toString());

        }
    }
}
