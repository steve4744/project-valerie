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
