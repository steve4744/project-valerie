/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package valerie.Tasks;

import valerie.BackgroundWorker;
import valerie.tools.DebugOutput;

/**
 *
 * @author Admin
 */
public class ConnectNetworkTask extends org.jdesktop.application.Task<Object, Void> {

    BackgroundWorker pWorker;

    public ConnectNetworkTask(org.jdesktop.application.Application app,
            BackgroundWorker worker) {
        super(app);

        pWorker = worker;

    }
    @Override protected Object doInBackground() {
        DebugOutput.printl("->");
        
        pWorker.set("BoxInfos", new valerie.tools.BoxInfoParser().parse(new valerie.tools.Network().sendBroadcast() ) );
        //pWorker.set("SelectedBoxInfo", 0);

        DebugOutput.printl("<-");
        return null;
    }
    @Override protected void succeeded(Object result) {
    }
}
