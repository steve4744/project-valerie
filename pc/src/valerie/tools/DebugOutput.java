/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package valerie.tools;

import java.util.Calendar;
import java.util.Date;
import java.util.LinkedList;

/**
 *
 * @author Admin
 */
public class DebugOutput {

    public static class OutputHandler {
        public void print(String s) { }
    }

    static LinkedList<OutputHandler> outputHandlers = new LinkedList<OutputHandler>();

    public static void add(OutputHandler out) {
        outputHandlers.add(out);
    }

    public static void printl(String msg) {
        _print(msg + "\n");
    }

    public static void print(String msg) {
        _print(msg);
    }

    private static void _print(String msg) {
        Calendar d = Calendar.getInstance();
        java.lang.Exception e = new java.lang.Exception();
        StackTraceElement ste[] = e.getStackTrace();
        String s = String.format("%02d:%02d:%02d %s %s %s[%4d] : %s",
                d.get(Calendar.HOUR), d.get(Calendar.MINUTE), d.get(Calendar.SECOND),
                ste[2].getFileName(),   ste[2].getClassName(),
                ste[2].getMethodName(), ste[2].getLineNumber(), msg);

        for(Object out : outputHandlers)
            ((OutputHandler)out).print(s);
    }
}
