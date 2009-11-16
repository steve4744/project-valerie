/*
 * ValerieApp.java
 */

package valerie;

import org.jdesktop.application.Application;
import org.jdesktop.application.SingleFrameApplication;

/**
 * The main class of the application.
 */
public class ValerieApp extends SingleFrameApplication {


    static String[] vArguments;

    /**
     * At startup create and show the main frame of the application.
     */
    @Override protected void startup() {

        show(new ValerieView(this, vArguments));
        //ValerieView v = new ValerieView(this, vArguments);
        //v.getFrame().setVisible(true);
    }

    /**
     * This method is to initialize the specified window by injecting resources.
     * Windows shown in our application come fully initialized from the GUI
     * builder, so this additional configuration is not needed.
     */
    @Override protected void configureWindow(java.awt.Window root) {
    }

    /**
     * A convenient static getter for the application instance.
     * @return the instance of ValerieApp
     */
    public static ValerieApp getApplication() {
        return Application.getInstance(ValerieApp.class);
    }

    /**
     * Main method launching the application.
     */
    public static void main(String[] args) {

        vArguments = args;

        launch(ValerieApp.class, args);
    }
}
