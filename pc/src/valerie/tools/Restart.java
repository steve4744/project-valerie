/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package valerie.tools;

import java.io.File;

/**
 *
 * @author i7
 */
public class Restart {
    public boolean  restartApplication( Object classInJarFile )
    {
        String javaBin = System.getProperty("java.home") + "/bin/java";
        File jarFile;
        try{
            jarFile = new File
            (classInJarFile.getClass().getProtectionDomain()
            .getCodeSource().getLocation().toURI());
        } catch(Exception e) {
            return false;
        }

        /* is it a jar file? */
        System.out.println(jarFile.toString());
        if ( !jarFile.getName().endsWith(".jar") )
        return false;   //no, it's a .class probably

        String  toExec[] = new String[] { javaBin, "-jar", jarFile.getPath() };
        try{
            Runtime.getRuntime().exec( toExec );
        } catch(Exception e) {
            //e.printStackTrace();
            return false;
        }

        System.exit(0);

        return true;
    }
}
