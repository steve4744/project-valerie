/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package valerie.Tasks;

import java.io.File;
import valerie.BackgroundWorker;
import valerie.Logger;
import valerie.tools.BoxInfo;
import valerie.tools.DebugOutput;
import valerie.tools.FileUtils;

/**
 *
 * @author i7
 */
public class DownloadFromBoxTask extends org.jdesktop.application.Task<Object, Void> {
    protected BackgroundWorker pWorker;

    public DownloadFromBoxTask(org.jdesktop.application.Application app,
             BackgroundWorker worker) {
        super(app);

        pWorker = worker;

        Logger.setBlocked(true);
        Logger.printBlocked("Downloading archiv from box");

    }

    @Override protected Object doInBackground() {
        DebugOutput.printl("->");

        BoxInfo[] pBoxInfos = (BoxInfo[])pWorker.get("BoxInfos");
        int selectedBoxInfo = (Integer)pWorker.get("SelectedBoxInfo");
        if (selectedBoxInfo < 0)
            return null;
        
        BoxInfo pBoxInfo = pBoxInfos[selectedBoxInfo];

        FileUtils.rename(new File("db"), new File("db.1"));
        FileUtils.mkdir(new File("db"));

        new valerie.tools.Network().getFile(pBoxInfo.IpAddress, "/hdd/valerie/moviedb.txt", "db");
        new valerie.tools.Network().getFile(pBoxInfo.IpAddress, "/hdd/valerie/seriesdb.txt", "db");

        FileUtils.mkdir(new File("db/episodes"));
        String[] entries = new valerie.tools.Network().sendCMD(pBoxInfo.IpAddress, "find /hdd/valerie/episodes/*.txt -type f");
        for (int f = 0; f < entries.length; f++) {
            new valerie.tools.Network().getFile(pBoxInfo.IpAddress, entries[f], "db/episodes");
        }

        return null;
    }

    @Override
    protected void succeeded(Object result) {
    }
}
