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
public class BoxInfoParser {
    public BoxInfo parse(String info) {
        BoxInfo boxinfo = new BoxInfo();

        String remaining = info;

        while( remaining.contains(";")) {
            Integer semIndex = remaining.indexOf(';');
            String line = remaining.substring(0, semIndex);
            remaining = remaining.substring(semIndex + 1, remaining.length());

            if(!line.contains("="))
                continue;

            Integer eqIndex = line.indexOf('=');
            String prefix = line.substring(0, eqIndex);
            String attr = line.substring(eqIndex + 1, line.length());

            if (prefix.equals("MANUFACTOR")) {
                boxinfo.Manufactor = attr;
            }
            else if (prefix.equals("MODEL")) {
                boxinfo.Model = attr;
            }
             else if (prefix.equals("IPADDR")) {
                try {
                    boxinfo.IpAddress = InetAddress.getByName(attr);
                } catch(Exception ex) {

                }
            }
        }

        return boxinfo;
    }
}
