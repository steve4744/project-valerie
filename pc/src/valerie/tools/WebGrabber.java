/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package valerie.tools;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.StringReader;
import java.io.StringWriter;
import java.net.HttpURLConnection;
import java.net.URL;
import java.net.URLConnection;
import java.util.ArrayList;

import java.util.concurrent.Semaphore;
import org.jdom.Document;
import org.jdom.input.SAXBuilder;

/**
 *
 * @author Admin
 */
public class WebGrabber {
	
    class cachedRequestXML{
        public URL Url;
        public Document doc;
        public cachedRequestXML(URL Url,Document doc){
            this.doc=doc;
            this.Url=Url;
        }
    }
    class cachedRequestURL{
        public URL Url;
        public String doc;
        public cachedRequestURL(URL Url,String doc){
            this.doc=doc;
            this.Url=Url;
        }
    }
    private int maxCacheEntrys=128;//30mb  256=60mb
    private static ArrayList<cachedRequestXML> cacheXML=null;
    private static ArrayList<cachedRequestURL> cacheURL=null;

    //private static Semaphore sem = new Semaphore(10, true);

    private int RETRIES = 40;
        
    public Document getXML(URL url) {
    	int x;
    	if(cacheXML==null)cacheXML=new ArrayList<cachedRequestXML>();
    	//DebugOutput.printl(url.toString());
    	for(x=0;x<cacheXML.size();x++){
    		if(url.equals(cacheXML.get(x).Url))return cacheXML.get(x).doc;
    	}
        
        //Serve the file
        Document doc = null;
        for(int i = 0; i < RETRIES; i++) {
            try {
                //sem.acquire();
                HttpURLConnection urlc = (HttpURLConnection)url.openConnection();
                //sem.release();
                urlc.addRequestProperty("user-agent", "Firefox");
                InputStream in = urlc.getInputStream();

                StringWriter out = new StringWriter();
                byte[] buf = new byte[4 * 1024]; // 4K buffer
                int bytesRead;
                while ((bytesRead = in.read(buf)) != -1) {
                    byte[] bufTrimmed = new byte[bytesRead];
                    for(int j = 0; j < bytesRead; j++)
                        bufTrimmed[j] = buf[j];
                    String fragment = new String(bufTrimmed, "UTF8");
                    out.append(fragment);

                }
                in.close();
                urlc.disconnect();
                String xmlString = out.toString();
                out.close();
                SAXBuilder builder = new SAXBuilder();
                StringReader xmlout = new StringReader(xmlString);
                doc = builder.build(xmlout);

                break;
            } catch (Exception ex) {
                System.out.printf("Webgrabber[%d]: %s\n", i, ex.getMessage());
            }
            try {
                Thread.sleep(100);
                if(i%10 == 0)
                  Thread.sleep(5000);
            } catch (Exception ex) {
                System.out.printf("Webgrabber[%d]: %s\n", i, ex.getMessage());

            }

        }

        //DebugOutput.printl("<-");
        if(cacheXML.size()>maxCacheEntrys)cacheXML.remove(0);
        cacheXML.add(new cachedRequestXML(url,doc));
        return doc;
    }

    public String getText(String url) {
        try {
            return getText(new URL(url));
        } catch (Exception ex) {
            return "";
        }
    }

    public String getText(URL url) {
    	int x;
    	if(cacheURL==null)cacheURL=new ArrayList<cachedRequestURL>();
        DebugOutput.printl(url.toString());
        for(x=0;x<cacheURL.size();x++){
    		if(url.equals(cacheURL.get(x).Url))return cacheURL.get(x).doc;
    	}
        
        //Serve the file
        String doc = null;

        for(int i = 0; i < RETRIES; i++) {
            try {
                //sem.acquire();
                HttpURLConnection urlc = (HttpURLConnection)url.openConnection();
                //sem.release();
                //urlc.setRequestProperty("User-Agent", "Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.0.4) Gecko/2008102920 Firefox/3.0.4");
                urlc.addRequestProperty("user-agent", "Firefox");
                BufferedReader in = new BufferedReader(new InputStreamReader(urlc.getInputStream()));

                StringWriter out = new StringWriter();
                String inputLine;
                while ( (inputLine = in.readLine()) != null)
                {
                  out.append(inputLine);
                }
                in.close();
                urlc.disconnect();
                doc = out.toString();
                out.close();
                break;
            } catch (Exception ex) {
                System.out.printf("Webgrabber[%d]: %s\n", i, ex.getMessage());
            }
        }

        //DebugOutput.printl("<-");
        if(cacheURL.size()>maxCacheEntrys)cacheURL.remove(0);
        cacheURL.add(new cachedRequestURL(url,doc));
        return doc;
    }

    public void getFile(String surl, String SaveAs) {

        getFile(surl, SaveAs, 3);
    }

    public void getFile(String surl, String SaveAs, int retry) {

        //DebugOutput.printl(surl);

        boolean success = false;

        for(int i = 0; i < retry && !success; i++) {

            success = true;

            File outputfile = new File (SaveAs);

            try {
                URL url = new URL(surl);
                DebugOutput.printl(surl + " --> " + SaveAs);
                URLConnection urlc = url.openConnection();
                urlc.addRequestProperty("user-agent", "Firefox");
                InputStream in = urlc.getInputStream();

                byte[] buf = new byte[4 * 1024]; // 4K buffer
                int bytesRead;

                FileOutputStream out = new FileOutputStream(outputfile);

                while ((bytesRead = in.read(buf)) != -1) {
                    out.write(buf, 0, bytesRead);
                }
                out.close();
                in.close();
            } catch (Exception ex) {
                DebugOutput.printl("error " + ex.getMessage());
                outputfile.delete();

                success = false;
            }
        }

        //DebugOutput.printl("<-");
    }
}
