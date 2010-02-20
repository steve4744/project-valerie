/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package valerie;

import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;
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
        public void done(int taskid, int taskcount, String id);
        public void notify(int taskid, int taskcount, String id);
    }

    protected class Listener implements TaskListener {

        ParentObject pParent;
        Tasks pTaskId;
        int pTaskIdInt;
        int pTaskCountInt;

        public Listener(ParentObject parent, Tasks taskId, int iTaskId, int iTaskCount) {
            pParent = parent;
            pTaskId = taskId;
            pTaskIdInt = iTaskId;
            pTaskCountInt = iTaskCount;
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
            pParent.done(pTaskIdInt, pTaskCountInt, pTaskId.toString());
        }
        public void process(TaskEvent evt) {
        }
        public void doInBackground(TaskEvent evt) {
        }
    }

    protected class PropertyListener implements PropertyChangeListener {

        ParentObject pParent;
        Tasks pTaskId;
        int pTaskIdInt;

        public PropertyListener(ParentObject parent, Tasks taskId, int iTaskId) {
            pParent = parent;
            pTaskId = taskId;
            pTaskIdInt = iTaskId;
        }

        @Override public void propertyChange( PropertyChangeEvent e )
        {
            //System.out.printf( "[%d]Property '%s': '%s' -> '%s'%n",
            //               pTaskIdInt, e.getPropertyName(), e.getOldValue(), e.getNewValue() );
            String propertyName = e.getPropertyName();
            if(propertyName.equals("progress"))
                Logger.setProgress((Integer)e.getNewValue(), pTaskIdInt);
            else if(propertyName.equals("message"))
                Logger.setMessage((String)e.getNewValue(), pTaskIdInt);
            //pParent.progress(pTaskId, e.getNewValue());
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

        int iTaskId = 0;
        int iTaskCount = 1;

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
                iTaskId = (int)((ThreadSize)obj).ThreadId;
                iTaskCount = (int) (int)((ThreadSize)obj).ThreadCount;
                vTask = new valerie.Tasks.ParseFilelistTask(pApp,
                        this,
                        (int)((ThreadSize)obj).ThreadCount,
                        (int)((ThreadSize)obj).ThreadId);
                break;

            case GET_ART:
                iTaskId = (int)((ThreadSize)obj).ThreadId;
                iTaskCount = (int) (int)((ThreadSize)obj).ThreadCount;
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
                vTask.addTaskListener(new Listener(parent, taskId, iTaskId, iTaskCount));
                vTask.addPropertyChangeListener(new PropertyListener(parent, taskId, iTaskId));
                vTask.execute();
            }
        }

        return true;
    }






    Hashtable pTable = new Hashtable();

    public void set(String name, Object obj) {

        if(obj != null)
            pTable.put(name, obj);
    }

    public Object get(String name) {
        return pTable.get(name);
    }
}
