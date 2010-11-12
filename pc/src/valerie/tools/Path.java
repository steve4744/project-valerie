/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package valerie.tools;

/**
 *
 * @author i7
 */
public class Path {

    public enum eContains {MOVIE, TV, MOVIE_AND_TV};

    public eContains type = eContains.MOVIE_AND_TV;
    public String path = "";

    public Path(String s) {
        if(s != null && s.length() > 0) {
            String[] p = s.split("\\|");
            path = p[0];
            if(p.length > 1) {
                if(p[1].equals("MOVIE"))
                    type = eContains.MOVIE;
                else if(p[1].equals("TV"))
                    type = eContains.TV;
                else /*if(p[1].equals("MOVIE_AND_TV"))*/
                    type = eContains.MOVIE_AND_TV;
            }
            else
                type = eContains.MOVIE_AND_TV;
        }
    }

    @Override
    public String toString() {
        return path + "|" + type;
    }
}
