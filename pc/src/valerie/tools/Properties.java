/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package valerie.tools;

import java.io.FileInputStream;
import java.io.FileOutputStream;

/**
 *
 * @author Admin
 */
public class Properties {
    private java.util.Properties properties = null;

    public Properties() {
        try {
            properties = new java.util.Properties();
            FileInputStream stream = new FileInputStream("valerie.properties");
            properties.load(stream);
            stream.close();
        }
        catch(Exception ex) {}
    }

    public void save() {
        try {
            FileOutputStream stream = new FileOutputStream("valerie.properties");
            properties.store(stream, "");
        }
        catch(Exception ex) {}
    }

    public void load() {
        try {
            FileInputStream stream = new FileInputStream("valerie.properties");
            properties.load(stream);
            stream.close();
        }
        catch(Exception ex) {}
    }

    public String getPropertyString(String s) {
        String rtv = properties.getProperty(s);
        return rtv!=null?rtv:"";
    }

    public int getPropertyInt(String s) {
        try {
            return Integer.decode(properties.getProperty(s));
        } catch(Exception ex)
        {
            return -1;
        }
    }

    public boolean getPropertyBoolean(String s) {
        try {
            return Boolean.parseBoolean(properties.getProperty(s));
        } catch(Exception ex)
        {
            return false;
        }
    }

    public void setProperty(String s, String v) {
        properties.setProperty(s, v);
    }

    public void setProperty(String s, Boolean v) {
        properties.setProperty(s, v.toString());
    }
}
