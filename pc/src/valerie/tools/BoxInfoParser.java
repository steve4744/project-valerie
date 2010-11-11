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
public final class BoxInfoParser {

    private ArrayList<BoxInfo> mList = new ArrayList<BoxInfo>();

    public BoxInfoParser() {
        load();
    }

    public void load() {

        mList.clear();

        String vManu = new valerie.tools.Properties().getPropertyString("IPADDR");
         if(vManu != null && vManu.length() > 0)
             for(String s : vManu.split("\\|"))
                parse(s);
    }

    public BoxInfo[] get() {
        return mList.toArray(new BoxInfo[1]);
    }

    public void parse(String info) {
      
        String[] Boxinfos = info.split("\n");
        for(String remaining : Boxinfos) {
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
            if(boxinfo.IpAddress != null) {
                boolean alreadyIn = false;
                String a = boxinfo.IpAddress.getHostAddress();
                for(int i = 0; i < mList.size(); i++) { //A little bit hacky
                    String b = ((BoxInfo)mList.get(i)).IpAddress.getHostAddress();
                    if (a.equals(b)) {
                        mList.remove(i);
                        //alreadyIn = true;
                        break;
                    }
                }

                if(!alreadyIn)
                    mList.add(boxinfo);
            }
        }

        return;
    }
}
