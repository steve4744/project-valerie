/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package valerie.tools;

import java.io.File;

/**
 *
 * @author Admin
 */
public class pngquant {
    public void exec(String Input, String Output) {
         try {
            String cmd = "";
            //cmd = System.getProperty("file.separator");
            if(System.getProperty("file.separator").equals("/")) //Linux
                    cmd = "pngquant";
                else //Windows
                    cmd = "bin\\pngquant";

            cmd += " 256 " + Input;
            Process process = Runtime.getRuntime().exec(cmd);
            process.getErrorStream().close();
            process.getInputStream().close();
            process.getOutputStream().close();

            process.waitFor();
            int exitval = process.exitValue();
            System.out.printf("PNG Exit: %d\n",  exitval);

            String createdFile = Input.replaceAll(".png", "-fs8.png");

            if(Output.equals(Input))
                new File(Input).delete();

            new File(createdFile).renameTo(new File(Output));
        } catch(Exception ex) {}
    }
}
