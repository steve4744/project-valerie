/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package valerie.provider;

import valerie.MediaInfo;

/**
 *
 * @author Admin
 */
public abstract class provider {
    public abstract void getDataById(MediaInfo m);
    public abstract void getDataByTitle(MediaInfo m);

    public abstract void getArtById(MediaInfo m);
}
