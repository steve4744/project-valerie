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
        try {
         String vManu = new valerie.tools.Properties().getPropertyString("MANUAL_MANUFACTOR");
         if(vManu != null && vManu.length() > 0)
             Manufactor = vManu;

         String vModel = new valerie.tools.Properties().getPropertyString("MANUAL_MODEL");
         if(vModel != null && vModel.length() > 0)
             Model = vModel;

         String vIp = new valerie.tools.Properties().getPropertyString("MANUAL_IPADDRESS");
         if(vIp != null && vIp.length() > 0)
             IpAddress = InetAddress.getByName(vIp);
        }catch(Exception e) {}
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
