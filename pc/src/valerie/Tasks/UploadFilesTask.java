/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package valerie.Tasks;

import java.io.File;
import valerie.BackgroundWorker;
import valerie.Logger;
import valerie.tools.BoxInfo;

/**
 *
 * @author Admin
 */
public class UploadFilesTask extends org.jdesktop.application.Task<Object, Void> {

    BackgroundWorker pWorker;

    public UploadFilesTask(org.jdesktop.application.Application app,
            BackgroundWorker worker) {

        super(app);

        pWorker = worker;
    }

    @Override
    protected Object doInBackground() {

        Logger.setBlocked(true);
        Logger.printBlocked("Uploading");

        BoxInfo[] pBoxInfos = (BoxInfo[])pWorker.get("BoxInfos");
        int selectedBoxInfo = (Integer)pWorker.get("SelectedBoxInfo");
        BoxInfo pBoxInfo = pBoxInfos[selectedBoxInfo];

        new valerie.tools.Network().sendFile(pBoxInfo.IpAddress, "db/moviedb.txt", "/hdd/valerie");
        new valerie.tools.Network().sendFile(pBoxInfo.IpAddress, "db/seriesdb.txt", "/hdd/valerie");

        File episodes = new File("db/episodes");
        if (!(episodes.exists())) {
            Logger.print("No such Folder \"db/episodes\"!");
        } else {
            String[] entries = episodes.list();

            for (int i = 0; i < entries.length; ++i) {
                new valerie.tools.Network().sendFile(pBoxInfo.IpAddress, "db/episodes/" + entries[i], "/hdd/valerie/episodes");
            }
        }

        File folder = new File("converted");
        if (!(folder.exists())) {
            Logger.print("No such Folder \"converted\"!");
        } else {
            String[] entries = folder.list();

            for (int i = 0; i < entries.length; ++i) {

                //Only upload arts if really needed so checbefore
                String[] vLine = new valerie.tools.Network().sendCMD(pBoxInfo.IpAddress,
                        "ls /hdd/valerie/media/" + entries[i]);

                if(vLine.length == 0 || !vLine[0].equals("/hdd/valerie/media/" + entries[i]))
                    new valerie.tools.Network().sendFile(pBoxInfo.IpAddress, "converted/" + entries[i], "/hdd/valerie/media");
            }
        }

        Logger.printBlocked("Finished");
        Logger.setBlocked(false);

        return null;
    }

    @Override
    protected void succeeded(Object result) {
    }
}
