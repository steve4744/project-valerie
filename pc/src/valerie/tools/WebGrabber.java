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
import java.net.URLEncoder;
import org.apache.commons.lang.StringEscapeUtils;
import org.jdom.Document;
import org.jdom.input.SAXBuilder;
import valerie.Utf8;

/**
 *
 * @author Admin
 */
public class WebGrabber {

    private static final String CACHE_DIR = "cache/";
    private static final int RETRIES = 3;

    public static void init() {
        new File(CACHE_DIR).mkdir();
    }

    private static String checkCache(URL url) {
        //String filename = String.valueOf(url.toString().hashCode());//.replaceAll("(\"|/|\\|:|\\\\?|<|>|\\|)", "_");
        String filename = url.toString().replaceAll("\\W", "");
        if(new File(CACHE_DIR + filename).exists()) {
            try {
                Utf8 f;
                f = new Utf8(CACHE_DIR + filename, "r");
                String rtv = f.read();
                f.close();
                return rtv;
            } catch(Exception ex) {
                System.out.printf("Webgrabber: %s\n%s-----------------\n",
                    url.toString(), ex.getMessage());

            }
        }
        return null;
    }

    private static void addCache(URL url, String text) {

        if(text != null && text.length() > 0) {
            //String filename = String.valueOf(url.toString().hashCode());//.replaceAll("(\"|/|\\|:|\\\\?|<|>|\\|)", "_");
            String filename = url.toString().replaceAll("\\W", "");
            //DebugOutput.printl("->");
            try {
                Utf8 f;

                f = new Utf8(CACHE_DIR + filename, "w");
                String[] lines = text.split("\n");
                for( String line : lines) {
                     f.write(line);
                }
                f.close();

            } catch(Exception ex) {
                System.out.printf("Webgrabber: %s\n%s-----------------\n",
                        url.toString(), ex.getMessage());
            }
            //DebugOutput.printl("<-");
        }
    }

    public static Document getXml(String url) {
        Document doc = null;
        String rawXml = getText(url);
        if(rawXml != null) {
            String decodedXml = /*StringEscapeUtils.unescapeXml(*/rawXml/*)*/;

            if(decodedXml != null && decodedXml.length() > 0) {
                SAXBuilder builder = new SAXBuilder();
                StringReader xmlout = new StringReader(decodedXml);
                try {
                    doc = builder.build(xmlout);
                } catch (Exception ex) {
                    System.out.printf("Webgrabber: %s\n%s\n-----------------\n",
                            url.toString(), ex.getMessage());
                }
                xmlout.close();
            }
        }
        return doc;
    }

    public static String getHtml(String url) {
        String rawHtml = getText(url);
        String decodedHtml = null;
        if(rawHtml != null)
            decodedHtml = StringEscapeUtils.unescapeHtml(rawHtml);
        return decodedHtml;
    }

   public static String getText(String url) {
        try {
            URL urlParsed = new URL(url);
            String encodedURL = urlParsed.getProtocol() + "://" + urlParsed.getHost() + urlParsed.getPath();
            if(urlParsed.getQuery() != null)
                encodedURL += "?" + URLEncode.encodePath(urlParsed.getQuery());

            System.out.println("URL " + encodedURL);
            return getText(new URL(encodedURL));
        } catch (Exception ex) {
            System.out.println("URL " + url);
            System.out.println(ex.toString());
            System.out.println(ex.getMessage());
            return "";
        }
    }

    private static String getText(URL url) {
        String text = null;

        text = checkCache(url);
        if(text != null)
            return text;

        for(int i = 0; i < RETRIES; i++) {
            try {
                HttpURLConnection urlc = (HttpURLConnection)url.openConnection();
                //urlc.addRequestProperty("user-agent", "Firefox");
                urlc.setRequestProperty("User-Agent",
                                        "Mozilla/5.0 (X11; U; Linux x86_64; en-GB; rv:1.8.1.6) Gecko/20070723 Iceweasel/2.0.0.6 (Debian-2.0.0.6-0etch1)");
                BufferedReader in = new BufferedReader(new InputStreamReader(urlc.getInputStream()));

                StringWriter out = new StringWriter();
                String inputLine;
                while ( (inputLine = in.readLine()) != null)
                {
                  out.append(inputLine);
                }
                in.close();
                urlc.disconnect();
                text = out.toString();
                out.close();
                break;
            } catch (Exception ex) {
                System.out.printf("Webgrabber[%d]: %s\n", i, ex.getMessage());
            }
        }

        addCache(url, text);

        return text;
    }

    public static void getFile(String surl, String SaveAs) {

        getFile(surl, SaveAs, 3);
    }

    public static void getFile(String surl, String SaveAs, int retry) {

        //DebugOutput.printl(surl);

        boolean success = false;
        surl = surl.trim(); // just ot be on the safe side
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
