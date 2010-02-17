/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package valerie.tools;

/**
 *
 * @author Admin
 */
import java.io.*;
import java.nio.channels.*;

public class FileUtils{
    public static void copyFile(File in, File out)
        throws IOException
    {
        FileChannel inChannel = new
            FileInputStream(in).getChannel();
        FileChannel outChannel = new
            FileOutputStream(out).getChannel();
        try {
            inChannel.transferTo(0, inChannel.size(),
                    outChannel);
        }
        catch (IOException e) {
            throw e;
        }
        finally {
            if (inChannel != null) inChannel.close();
            if (outChannel != null) outChannel.close();
        }
    }

    public static void deleteFile(String Input) {
	File file = new File(Input);

	//Zuvor alle mit dem File assoziierten Streams schließen...

	if(file.exists()){
            file.delete();
	}

		//System.out.println("File deleted");
    }

    public static void copy(String from, String to) throws IOException{
        InputStream in = null;
        OutputStream out = null;
        try {
            InputStream inFile = new FileInputStream(from);
            in = new BufferedInputStream(inFile);
            OutputStream outFile = new FileOutputStream(to);
            out = new BufferedOutputStream(outFile);
            while (true) {
                int data = in.read();
                if (data == -1) {
                    break;
                }
                out.write(data);
            }
        } finally {
            if (in != null) {
                in.close();
            }
            if (out != null) {
                out.close();
            }

        }
    }

}