/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package valerie;

import java.util.Hashtable;
import org.jdesktop.application.Task;
import org.jdesktop.application.TaskEvent;
import org.jdesktop.application.TaskListener;

/**
 *
 * @author Admin
 */
public class BackgroundWorker {

     public enum Mode {
        NORMAL,
        BACKGROUND,
    };

     public enum Tasks {
        CHECK_ARGUMENTS,
        LOAD_ARCHIVE,
        CONNECT_NETWORK,
        SYNC_FILELIST,
        PARSE_FILELIST,
        GET_ART,
        UPLOAD_FILES,
    };

    public interface ParentObject {
        public void done(String id);
        public void notify(String id);
    }

    protected class Listener implements TaskListener {

        ParentObject pParent;
        Tasks pTaskId;

        public Listener(ParentObject parent, Tasks taskId) {
            pParent = parent;
            pTaskId = taskId;
        }

        public void finished(TaskEvent evt) {
        }
        public void interrupted(TaskEvent evt) {
        }
        public void cancelled(TaskEvent evt) {
        }
        public void failed(TaskEvent evt) {
        }
        public void succeeded(TaskEvent evt) {
            pParent.done(pTaskId.toString());
        }
        public void process(TaskEvent evt) {
        }
        public void doInBackground(TaskEvent evt) {
        }
    }

    ////////////////////////////////////////////

    org.jdesktop.application.Application pApp;

    ////////////////////////////////////////////

    public BackgroundWorker(org.jdesktop.application.Application app) {
        pApp = app;

        set("Database", new MediaInfoDB());
        set("SelectedBoxInfo", (int)-1);
        //set("BoxInfos", (valerie.tools.BoxInfo[])null);
    }

    public boolean doTask(Tasks taskId, Mode mode, ParentObject parent, Object obj) {

        Task vTask = null;

        switch(taskId) {
            case CHECK_ARGUMENTS:
                vTask = new valerie.Tasks.CheckArgumentsTask(pApp,
                        this,
                        parent,
                        (String)obj);
                break;

            case LOAD_ARCHIVE:
                vTask = new valerie.Tasks.LoadArchiveTask(pApp,
                        this);
                break;

            case CONNECT_NETWORK:
                 vTask = new valerie.Tasks.ConnectNetworkTask(pApp,
                        this);
                break;

            case SYNC_FILELIST:
                vTask = new valerie.Tasks.SyncFilelistTask(pApp,
                        this);
                break;

            case PARSE_FILELIST:
                vTask = new valerie.Tasks.ParseFilelistTask(pApp,
                        this,
                        (int)((ThreadSize)obj).ThreadCount,
                        (int)((ThreadSize)obj).ThreadId);
                break;

            case GET_ART:
                vTask = new valerie.Tasks.GetArtTask(pApp,
                        this,
                        (int)((ThreadSize)obj).ThreadCount,
                        (int)((ThreadSize)obj).ThreadId);
                break;
                
            case UPLOAD_FILES:
                vTask = new valerie.Tasks.UploadFilesTask(pApp,
                        this);
                break;
        }

        if(vTask != null) {
            if(mode == Mode.NORMAL) {
                vTask.run();
                
            } else if (mode == Mode.BACKGROUND) {
                vTask.addTaskListener(new Listener(parent, taskId));
                vTask.execute();
            }
        }

        return true;
    }






    Hashtable pTable = new Hashtable();

    public void set(String name, Object obj) {

        pTable.put(name, obj);
    }

    public Object get(String name) {
        return pTable.get(name);
    }
}
