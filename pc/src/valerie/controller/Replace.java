/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package valerie.controller;

import java.util.Arrays;
import java.util.LinkedHashMap;
import java.util.Vector;
import valerie.Utf8;

/**
 *
 * @author i7
 */
public class Replace {
    private static Vector<String> replacementsOptions = new Vector<String>(Arrays.asList(new String[] {"pre", "post_tv", "post_movie"}));
    private static LinkedHashMap replacementsList = new LinkedHashMap();

    public static void reload() {
        clear();
        load();
    }

    public static void load() {
        for (String rf : replacementsOptions) {
            replacementsList.put(rf, new Vector<String[]>());
            Utf8 f = new Utf8("conf\\" + rf + ".conf", "r");
            for(String line : f.read().split("\n")) {
                String[] keys = line.split("=");
                if(keys.length == 2) {
                    keys[0] = keys[0].trim().replaceAll("[\'\"]", "");
                    keys[1] = keys[1].trim().replaceAll("[\'\"]", "");
                    //print "[" + rf + "] ", keys[0], " --> ", keys[1]
                    ((Vector<String[]>)replacementsList.get(rf)).add(new String[] {keys[0], keys[1],});
                    //#replacementsList[rf].append([keys[0],keys[1]])
                }
            }

            f.close();
        }
    }

    public static void clear() {
        replacementsList.clear();
    }

    public static Vector<String[]> replacements(String option) {
        if (replacementsOptions.contains(option))
            return ((Vector<String[]>)replacementsList.get(option));
        else
            return new Vector<String[]>();
    }


}
