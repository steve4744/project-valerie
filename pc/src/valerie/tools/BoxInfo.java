/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package valerie.tools;

import java.net.InetAddress;
import java.net.UnknownHostException;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 *
 * @author Admin
 */
public class BoxInfo {
    public String Manufactor = "unknown";
    public String Model = "unknown";
    public InetAddress IpAddress;

    public BoxInfo() {
        try {
            IpAddress = InetAddress.getByName("127.0.0.1");
        } catch (UnknownHostException ex) {
            Logger.getLogger(BoxInfo.class.getName()).log(Level.SEVERE, null, ex);
        }
    }

    public String toLongString() {
        String rtv = "";

        rtv += "Manufactor = " + Manufactor + "\n";
        rtv += "Model = " + Model + "\n";
        rtv += "IpAddress = " + IpAddress.getHostAddress() + "\n";

        return rtv;
    }

    @Override
    public String toString() {
        String rtv = "";

        rtv += Manufactor + " " + Model + " on " + IpAddress.getHostAddress();
        return rtv;
    }

    public String toInternalString() {
        String rtv = "";

        rtv += "MANUFACTOR=" + Manufactor + ";MODEL=" + Model + ";IPADDR=" + IpAddress.getHostAddress() + ";";
        return rtv;
    }
}
