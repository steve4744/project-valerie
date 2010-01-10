/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package valerie.Tasks;

import valerie.Logger;
import valerie.MediaInfoDB;
import valerie.BackgroundWorker;
import valerie.BackgroundWorker.ParentObject;

/**
 *
 * @author Admin
 */
public class CheckArgumentsTask extends org.jdesktop.application.Task<Object, Void> {

        private String pMode = "";
        private BackgroundWorker pWorker;
        private ParentObject pParent;

        public CheckArgumentsTask(
                org.jdesktop.application.Application app,
                BackgroundWorker worker,
                ParentObject parent,
                String mode) {

            super(app);

            pMode = mode;
            pWorker = worker;
            pParent = parent;

            Logger.setBlocked(true);
            Logger.printBlocked("Loading Archive");
        }

        @Override protected Object doInBackground() {

            boolean showHelp = false;
            boolean setAuto = false;
            boolean setConnect = false;
            boolean setSync = false;
            boolean setParse = false;
            boolean setArt = false;
            boolean setUpload = false;
            boolean setQuit = false;

            String[] pArguments = (String[])pWorker.get("CmdArguments");

            for(int vIter = 0; pArguments != null && vIter < pArguments.length; vIter++) {
                if(     pArguments[vIter].startsWith("-?")
                    ||  pArguments[vIter].startsWith("-h")
                    ||  pArguments[vIter].startsWith("--help"))
                     showHelp = true;
                else if(    /*vArguments[vIter].startsWith("-a")
                        ||  */pArguments[vIter].startsWith("--auto")) {
                     setAuto = true;
                     setConnect = true;
                     setSync = true;
                     setParse = true;
                     setArt = true;
                     setUpload = true;
                } else if(    pArguments[vIter].startsWith("-c")
                        ||  pArguments[vIter].startsWith("--connect"))
                     setConnect = true;
                else if(    pArguments[vIter].startsWith("-s")
                        ||  pArguments[vIter].startsWith("--sync"))
                     setSync = true;
                else if(    pArguments[vIter].startsWith("-p")
                        ||  pArguments[vIter].startsWith("--parse"))
                     setParse = true;
                else if(    pArguments[vIter].startsWith("-a")
                        ||  pArguments[vIter].startsWith("--art"))
                     setArt = true;
                else if(    pArguments[vIter].startsWith("-u")
                        ||  pArguments[vIter].startsWith("--upload"))
                     setUpload = true;
                else if(    pArguments[vIter].startsWith("-q")
                        ||  pArguments[vIter].startsWith("--quit"))
                     setQuit = true;
            }

            if(pMode.equals("pre")) {
                if(showHelp) {
                    System.out.printf("\t%20s: %20s\n", "(-?|-h|--help)", "Show this help");
                    System.out.printf("\t%20s: %20s\n", "(-c|--connect)", "Connects on startup");
                    System.out.printf("\t%20s: %20s\n", "(-s|--sync)", "Sync on startup");
                    System.out.printf("\t%20s: %20s\n", "(-p|--parse)", "Parse on startup");
                    System.out.printf("\t%20s: %20s\n", "(-a|--art)", "Download arts on startup");
                    System.out.printf("\t%20s: %20s\n", "(-u|--upload)", "Upload files on startup");
                    System.out.printf("\t%20s: %20s\n", "(-q|--quit)", "Quits after parsing cmdline");
                    System.out.printf("\t%20s: %20s\n", "(--auto)", "Auto mode,");
                    System.out.printf("\t%20s: %20s\n", "", "equeal to -c -s -p -a -u");
                    System.exit(0);
                }
            }

            if(pMode.equals("post")) {

                //INIT ALL
                //clear database
                MediaInfoDB pDatabase = (MediaInfoDB)pWorker.get("Database");
                pDatabase.clear();

                pWorker.doTask(BackgroundWorker.Tasks.LOAD_ARCHIVE, BackgroundWorker.Mode.NORMAL, null, null);
                pParent.notify(0, 1, "UPDATE_TABLES");
                
                if(setConnect) {
                    pWorker.doTask(BackgroundWorker.Tasks.CONNECT_NETWORK, BackgroundWorker.Mode.NORMAL, null, null);
                }
                if(setSync) {
                    pWorker.doTask(BackgroundWorker.Tasks.SYNC_FILELIST, BackgroundWorker.Mode.NORMAL, null, null);
                }
                if(setParse) {
                    pWorker.doTask(BackgroundWorker.Tasks.PARSE_FILELIST, BackgroundWorker.Mode.NORMAL, null, null);
                }
                if(setArt) {
                    pWorker.doTask(BackgroundWorker.Tasks.GET_ART, BackgroundWorker.Mode.NORMAL, null, null);
                }
                if(setUpload) {
                    pWorker.doTask(BackgroundWorker.Tasks.UPLOAD_FILES, BackgroundWorker.Mode.NORMAL, null, null);
                }

                if(setQuit) {
                    System.exit(0);
                }
            }
            return null;
        }

        @Override protected void succeeded(Object result) {

        }
    }
