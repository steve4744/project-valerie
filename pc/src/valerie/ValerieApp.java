/*
 * ValerieApp.java
 */

package valerie;

import Gui.ValerieView;
import org.jdesktop.application.Application;
import org.jdesktop.application.SingleFrameApplication;
import valerie.controller.Controller;

/**
 * The main class of the application.
 */
public class ValerieApp extends SingleFrameApplication {


    static String[] vArguments;
    static Controller controller;

    /**
     * At startup create and show the main frame of the application.
     */
    @Override protected void startup() {
        controller = new Controller();
        show(new ValerieView(this, controller, vArguments));
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
