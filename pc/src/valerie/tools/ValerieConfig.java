/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package valerie.tools;

import valerie.Utf8;

/**
 *
 * @author i7
 */
public class ValerieConfig {

    public static void setString(String id, String value) {
        Utf8 conf = new Utf8("conf\\valerie.conf", "r");
        String[] lines = conf.read().split("\n");
        conf.close();
        conf = new Utf8("conf\\valerie.conf", "w");
        boolean found = false;
        for(String line : lines) {
            String[] val = line.split("=");
            if(val[0].equals(id)) {
                val[1] = value;
                found = true;
            }
            conf.write(val[0] + "=" + val[1] + "\n");
        }
        if(!found)
            conf.write(id + "=" + value + "\n");
        conf.close();
    }

    public static String getString(String id) {
        Utf8 conf = new Utf8("conf\\valerie.conf", "r");
        String[] lines = conf.read().split("\n");
        for(String line : lines) {
            String[] value = line.split("=");
            if(value[0].equals(id))
                return value[1];

        }
        return "0";
    }


}
