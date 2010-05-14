/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package valerie.tools;

import java.net.InetAddress;

/**
 *
 * @author Admin
 */
public class BoxInfo {
    public String Manufactor = "unknown";
    public String Model = "unknown";
    public InetAddress IpAddress;

    BoxInfo() {
    }

    @Override
    public String toString() {
        String rtv = "";

        rtv += "Manufactor = " + Manufactor + "\n";
        rtv += "Model = " + Model + "\n";
        rtv += "IpAddress = " + IpAddress + "\n";

        return rtv;
    }

    public String toShortString() {
        String rtv = "";

        rtv += Manufactor + " " + Model + " on " + IpAddress;
        return rtv;
    }
}
