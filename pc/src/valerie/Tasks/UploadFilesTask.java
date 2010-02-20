/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package valerie.Tasks;

import java.io.File;
import valerie.BackgroundWorker;
import valerie.Logger;
import valerie.tools.BoxInfo;
import valerie.tools.FileUtils;

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
                File testentries = new File("db/episodes/" + entries[i]);
                if (testentries.isFile()){
                    new valerie.tools.Network().sendFile(pBoxInfo.IpAddress, "db/episodes/" + entries[i], "/hdd/valerie/episodes");
                }
            }
        }

        File folder = new File("converted");
        if (!(folder.exists())) {
            Logger.print("No such Folder \"converted\"!");
        } else {
            String[] entries = folder.list();

            for (int i = 0; i < entries.length; ++i) {
                System.out.println(entries[i]);
                if(entries[i].charAt(0) == '.')
                    continue;

                File testpicture = new File("converted/" + entries[i]);
                if (testpicture.isFile()){
                    //Only upload arts if really needed so checbefore
                    String[] vLine = new valerie.tools.Network().sendCMD(pBoxInfo.IpAddress,
                            "ls /hdd/valerie/media/" + entries[i]);

                    if(vLine.length == 0 || !vLine[0].equals("/hdd/valerie/media/" + entries[i]))
                        new valerie.tools.Network().sendFile(pBoxInfo.IpAddress, "converted/" + entries[i], "/hdd/valerie/media");
                }
            }
        }

        // Move imported pictures to hdd
        folder = new File("import");
        if (!(folder.exists())) {
            Logger.print("No such Folder \"import\"!");
        } else {
            String[] entries = folder.list();

            for (int i = 0; i < entries.length; ++i) {
                System.out.println(entries[i]);
                if(entries[i].charAt(0) == '.')
                    continue;
                new valerie.tools.Network().sendFile(pBoxInfo.IpAddress, "import/" + entries[i], "/hdd/valerie/media");
                FileUtils.deleteFile("import/" + entries[i]);
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
