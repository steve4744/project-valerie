/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package valerie;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;

/**
 *
 * @author i7
 */
public final class Utf8 {
    private BufferedWriter out = null;
    private BufferedReader in = null;

    public Utf8(String file, String arg) {
        open(file, arg);
    }

    public boolean open(String file, String arg) {
        boolean rtv = true;
        try {
            if(arg.equals("r"))
                in = new BufferedReader(
                    new InputStreamReader(new FileInputStream(file), "UTF8"));
            else if(arg.equals("w"))
                out = new BufferedWriter(
                    new OutputStreamWriter(new FileOutputStream(file), "UTF8"));
        } catch (Exception e) {
            rtv = false;
        }

        return rtv;
    }



    public void close() {
        try {
            if (out != null) out.close();
        } catch (Exception e) {
        }
        
        try {
            if (in != null) in.close();
        } catch (Exception e) {
        }

        out = null;
        in = null;
    }

    public void write(String text) {
        try {
            if (out != null) out.write(text);
        } catch (Exception e) {
        }

        return;
    }

    public void append(String text) {
        try {
            if (out != null) out.append(text);
        } catch (Exception e) {
        }

        return;
    }

    public String read() {
        String rtv = "";
        try {
            if (in != null) {
                String line;
                while((line = in.readLine()) != null) {
                    rtv+=line;
                    rtv+="\n";
                }
            }
        } catch (Exception e) {
        }

        return rtv;
    }
}
