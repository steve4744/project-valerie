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

    public static Document getXML(String url) {
        Document doc = null;
        String rawXml = getText(url);

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
        return doc;
    }

    public static String getHtml(String url) {
        String rawHtml = getText(url);
        String decodedHtml = StringEscapeUtils.unescapeHtml(rawHtml);
        return decodedHtml;
    }

   public static String getText(String url) {
        try {
            return getText(new URL(url));
        } catch (Exception ex) {
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
