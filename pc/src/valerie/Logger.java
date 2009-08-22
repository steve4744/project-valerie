/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package valerie;

import java.util.Vector;

/**
 *
 * @author Admin
 */
public class Logger {
    static Vector outputHandlers = new Vector();

    public static void add(OutputHandler out) {
        outputHandlers.add(out);
    }

    public static void print(String s) {
        for(Object out : outputHandlers)
            ((OutputHandler)out).print(s);
    }

    public static void setWorking(boolean s) {
        for(Object out : outputHandlers)
            ((OutputHandler)out).setWorking(s);
    }

    public static void setProgress(int s) {
        for(Object out : outputHandlers)
            ((OutputHandler)out).setProgress(s);
    }
}
