/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package valerie.tools;

import java.net.InetAddress;
import java.util.ArrayList;

/**
 *
 * @author Admin
 */
public class BoxInfoParser {
    public BoxInfo[] parse(String info) {

        ArrayList list = new ArrayList();

        String[] Boxinfos = info.split("\n");
        for(String remaining : Boxinfos) {
        //String remaining = info;

            BoxInfo boxinfo = new BoxInfo();

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
            
            list.add(boxinfo);
        }
        if(list.size()> 0) {
            BoxInfo[] boxinfos = new BoxInfo[list.size()];
            for(int i = 0; i < list.size(); i++)
                boxinfos[i] = (BoxInfo)list.get(i);

            return boxinfos;
        }
        
        return null;
    }
}
