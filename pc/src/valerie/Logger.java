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

    public static void setBlocked(boolean s) {
        for(Object out : outputHandlers)
            ((OutputHandler)out).setBlocked(s);
    }

    public static void printBlocked(String s) {
        for(Object out : outputHandlers)
            ((OutputHandler)out).printBlocked(s);
    }

    public static void setProgress(int s) {
        for(Object out : outputHandlers)
            ((OutputHandler)out).setProgress(s);
    }

    public static void setProgress(int s, int t) {
        for(Object out : outputHandlers)
            ((OutputHandler)out).setProgress(s, t);
    }

    public static void setMessage(String s, int t) {
        for(Object out : outputHandlers)
            ((OutputHandler)out).setMessage(s, t);
    }
}
