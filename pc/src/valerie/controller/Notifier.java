/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package valerie.controller;

import java.util.LinkedList;

/**
 *
 * @author i7
 */
public class Notifier {
    LinkedList<Notification> notifyHandlers = new LinkedList<Notification>();

    public void add(Notification out) {
        out.init();
        notifyHandlers.add(out);
    }

    public void _notify(String type) {
        for(Object out : notifyHandlers)
            if (type.equals(((Notification)out).Type))
                ((Notification)out).callback(null);
    }

    public void _notify(Object o, String type) {
        for(Object out : notifyHandlers) {
            if (type.equals(((Notification)out).Type))
                ((Notification)out).callback(o);
        }
    }
}
