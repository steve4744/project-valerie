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


    public static boolean rename(File in, File out)
    {
        // Rename file (or directory)
        boolean success = in.renameTo(out);
        if (!success) {
            // File was not successfully renamed
            return false;
        }
        return true;
    }

    public static boolean mkdir(File in)
    {
        return in.mkdir();
    }

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

    public static boolean deleteFile(String Input) {
	File file = new File(Input);
        if (file.isDirectory()) {
            String[] children = file.list();
            for (int i=0; i<children.length; i++) {
                boolean success = deleteFile(Input + "\\" + children[i]);
                if (!success) {
                    return false;
                }
            }
        }

        return file.delete();
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