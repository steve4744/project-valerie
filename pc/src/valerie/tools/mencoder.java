/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package valerie.tools;

import valerie.*;
import java.io.File;

/**
 *
 * @author Admin
 */
public class mencoder {
    public void exec(String Input, String Output) {
         try {
            for(int retry = 0; retry < 2; retry++) {

                File fInput = new File(Input);
                File fOutput = new File(fInput.getName());

                new FileUtils().copyFile(fInput, fOutput);

                String cmd = "bin\\mencoder mf://" + fOutput.getName() + " -mf type=jpg -ovc lavc -lavcopts vcodec=mpeg2video -oac copy -o " +  Output + " -vf scale=1024:576";
                Process process = Runtime.getRuntime().exec(cmd);
                process.getErrorStream().close();
                process.getInputStream().close();
                process.getOutputStream().close();

                process.waitFor();
                int exitval = process.exitValue();
                System.out.printf("Exit: %d\n",  exitval);

               fOutput.delete();

                if( new File(Output).exists() && new File(Output).length() > 20000 )
                    break;

                new File(Output).delete();
            }
        } catch(Exception ex) {}
    }
}
