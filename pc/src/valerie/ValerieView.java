/*
 * ValerieView.java
 */
package valerie;

import java.awt.Color;
import java.awt.Component;
import java.awt.Container;
import valerie.tools.pngquant;
import valerie.tools.mencoder;
import java.awt.Graphics;
import java.awt.Image;
import org.jdesktop.application.Action;
import org.jdesktop.application.ResourceMap;
import org.jdesktop.application.SingleFrameApplication;
import org.jdesktop.application.FrameView;
import org.jdesktop.application.Task;
import org.jdesktop.application.TaskMonitor;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.FocusEvent;
import java.awt.event.WindowEvent;
import java.awt.event.WindowListener;
import java.awt.event.WindowStateListener;
import java.awt.image.BufferedImage;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.Writer;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import javax.imageio.ImageIO;
import javax.swing.Icon;
import javax.swing.Timer;
import javax.swing.ImageIcon;
import javax.swing.JComponent;
import javax.swing.JDialog;
import javax.swing.JFrame;
import javax.swing.RowSorter;
import javax.swing.SortOrder;
import javax.swing.event.TableModelEvent;
import javax.swing.event.TableModelListener;
import javax.swing.table.DefaultTableModel;
import javax.swing.table.TableCellRenderer;
import javax.swing.table.TableModel;

import valerie.tools.DebugOutput;

/**
 * The application's main frame.
 */
public class ValerieView extends FrameView implements WindowStateListener {


    private String[] vArguments;

    class UIOutputHandler extends OutputHandler {

        //StatusPopup popup = null;

        UIOutputHandler()
        {
            super();

            //popup = new StatusPopup(null, true);
        }

        public void print(String s) {
            statusMessageLabel.setText(s);
        }

        public void printBlocked(String s) {
            statusMessageLabel.setText(s);
            statusPopup.setTitle(s);
            descLabel.setText(s);
        }

        public void setWorking(boolean s) {
            jButtonConnect.setEnabled(!s);
            jButtonSync.setEnabled(!s);
            jButtonParse.setEnabled(!s);
            jButtonArt.setEnabled(!s);
            jButtonUpload.setEnabled(!s);
        }

        public void setBlocked(boolean s) {
            setWorking(s);

            //mainPanel.getParent()
            Container rootPane = mainPanel.getParent().getParent().getParent();
            Container frame = rootPane.getParent();
            frame.setEnabled(!s);

            //if(frame.isVisible() == false)
            //    statusPopup.

            statusPopup.setLocationRelativeTo(mainPanel);
            statusPopup.validate();
            statusPopup.setVisible(s);
        }

        public void setProgress(int s) {
            progressBar.setValue(s);
        }
    }

    public ValerieView(SingleFrameApplication app, String[] arguments) {
        super(app);

        vArguments = arguments;

        /*vArguments = new String[] {
            "-a",
        };*/

        checkArguments("pre").run();

        this.getFrame().addWindowStateListener(this);

        class WListener implements WindowListener {
            public void windowDeactivated(WindowEvent e) {
                System.out.print(e);
            }
            public void windowActivated(WindowEvent e) {

                if(firstFocus) {
                    firstFocus = false;

                    checkArguments("post").execute();
                }

                System.out.print(e);
            }

            public void windowIconified(WindowEvent e) {
                System.out.print(e);
            }
            public void windowDeiconified(WindowEvent e) {
                System.out.print(e);
            }

            public void windowClosed(WindowEvent e) {
                System.out.print(e);
            }

            public void windowClosing(WindowEvent e) {
                System.out.print(e);
            }

            public void windowOpened(WindowEvent e) {
                System.out.print(e);
            }

         }

        this.getFrame().addWindowListener(new WListener());


        initComponents();

        // status bar initialization - message timeout, idle icon and busy animation, etc
        ResourceMap resourceMap = getResourceMap();
        int messageTimeout = resourceMap.getInteger("StatusBar.messageTimeout");
        messageTimer = new Timer(messageTimeout, new ActionListener() {

            public void actionPerformed(ActionEvent e) {
                statusMessageLabel.setText("");
            }
        });
        messageTimer.setRepeats(false);
        int busyAnimationRate = resourceMap.getInteger("StatusBar.busyAnimationRate");
        for (int i = 0; i < busyIcons.length; i++) {
            busyIcons[i] = resourceMap.getIcon("StatusBar.busyIcons[" + i + "]");
        }
        busyIconTimer = new Timer(busyAnimationRate, new ActionListener() {

            public void actionPerformed(ActionEvent e) {
                busyIconIndex = (busyIconIndex + 1) % busyIcons.length;
                statusAnimationLabel.setIcon(busyIcons[busyIconIndex]);
            }
        });
        idleIcon = resourceMap.getIcon("StatusBar.idleIcon");
        statusAnimationLabel.setIcon(idleIcon);
        progressBar.setVisible(false);

        // connecting action tasks to status bar via TaskMonitor
        TaskMonitor taskMonitor = new TaskMonitor(getApplication().getContext());
        taskMonitor.addPropertyChangeListener(new java.beans.PropertyChangeListener() {

            public void propertyChange(java.beans.PropertyChangeEvent evt) {
                String propertyName = evt.getPropertyName();
                if ("started".equals(propertyName)) {
                    if (!busyIconTimer.isRunning()) {
                        statusAnimationLabel.setIcon(busyIcons[0]);
                        busyIconIndex = 0;
                        busyIconTimer.start();
                    }
                    progressBar.setVisible(true);
                    //progressBar.setIndeterminate(true);
                } else if ("done".equals(propertyName)) {
                    busyIconTimer.stop();
                    statusAnimationLabel.setIcon(idleIcon);
                    progressBar.setVisible(false);
                    //progressBar.setValue(0);
                } else if ("message".equals(propertyName)) {
                    String text = (String) (evt.getNewValue());
                    statusMessageLabel.setText((text == null) ? "" : text);
                    messageTimer.restart();
                } else if ("progress".equals(propertyName)) {
                    int value = (Integer) (evt.getNewValue());
                    progressBar.setVisible(true);
                    //progressBar.setIndeterminate(false);
                    //progressBar.setValue(value);
                }
            }
        });

        //MY OWN CODE
        Logger.add(new UIOutputHandler());

        class TableChangedMovies implements TableModelListener {

            public void tableChanged(TableModelEvent e) {
                if (e.getType() == TableModelEvent.UPDATE) {
                    if(!isUpdating) {
                        System.out.println(e.getSource());

                        int row = e.getFirstRow();
                        int column = e.getColumn();

                        if (column == 0 || column == 2) {
                            TableModel model = jTableFilelist.getModel();
                            int id = ((Integer) model.getValueAt(row, 4)).intValue();
                            boolean use = ((Boolean) model.getValueAt(row, 0)).booleanValue();
                            String searchstring = ((String) model.getValueAt(row, 2));

                            MediaInfo toUpdate = database.getMediaInfoById(id);
                            toUpdate.Ignoring = !use;
                            toUpdate.SearchString = searchstring;
                            toUpdate.needsUpdate = true;

                            model.setValueAt(toUpdate.needsUpdate, row, 5);
                        }
                    }
                }
            }
        }
        jTableFilelist.getModel().addTableModelListener(new TableChangedMovies());

        class TableChangedEpisodes implements TableModelListener {

            public void tableChanged(TableModelEvent e) {
                if (e.getType() == TableModelEvent.UPDATE) {
                    if(!isUpdating) {
                        System.out.println(e.getSource());

                        int row = e.getFirstRow();
                        int column = e.getColumn();

                        if (column == 0 || column == 2 || column == 3 || column == 4) {
                            TableModel model = jTableFilelistEpisodes.getModel();
                            int id = ((Integer) model.getValueAt(row, 5)).intValue();
                            boolean use = ((Boolean) model.getValueAt(row, 0)).booleanValue();
                            String searchstring = ((String) model.getValueAt(row, 2));
                            int season = ((Integer) model.getValueAt(row, 3)).intValue();
                            int episode = ((Integer) model.getValueAt(row, 4)).intValue();

                            MediaInfo toUpdate = database.getMediaInfoById(id);
                            toUpdate.Ignoring = !use;
                            toUpdate.SearchString = searchstring;
                            toUpdate.Season = season;
                            toUpdate.Episode = episode;
                            toUpdate.needsUpdate = true;

                            model.setValueAt(toUpdate.needsUpdate, row, 6);
                        }
                    }
                }
            }
        }

        jTableFilelistEpisodes.getModel().addTableModelListener(new TableChangedEpisodes());

         /*class PropertyListener implements PropertyChangeListener {
            public void propertyChange(java.beans.PropertyChangeEvent event) {
                System.out.print(event);
            }

         }

        this.addPropertyChangeListener(new PropertyListener());

        this.firePropertyChange("shown", "false", "true");*/
    }

    boolean firstFocus = true;

    public void windowStateChanged(java.awt.event.WindowEvent event)
    {
        if(event.getNewState() == java.awt.event.WindowEvent.WINDOW_OPENED) {
            checkArguments("post").execute();
        }

    }

    public void focusGained(FocusEvent e) {
        if(firstFocus) {
            firstFocus = false;

            checkArguments("post").execute();
        }
    }

    public void focusLost(FocusEvent e) {
        //displayMessage("Focus lost", e);
    }

    @Action
    public Task checkArguments(String mode) { return new checkArgumentsTask(getApplication(), mode); }

    private class checkArgumentsTask extends org.jdesktop.application.Task<Object, Void> {

        private String pMode = "";

        checkArgumentsTask(org.jdesktop.application.Application app, String mode) {
            super(app);

            pMode = mode;

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

            for(int vIter = 0; vArguments != null && vIter < vArguments.length; vIter++) {
                if(     vArguments[vIter].startsWith("-?")
                    ||  vArguments[vIter].startsWith("-h")
                    ||  vArguments[vIter].startsWith("--help"))
                     showHelp = true;
                else if(    /*vArguments[vIter].startsWith("-a")
                        ||  */vArguments[vIter].startsWith("--auto")) {
                     setAuto = true;
                     setConnect = true;
                     setSync = true;
                     setParse = true;
                     setArt = true;
                     setUpload = true;
                } else if(    vArguments[vIter].startsWith("-c")
                        ||  vArguments[vIter].startsWith("--connect"))
                     setConnect = true;
                else if(    vArguments[vIter].startsWith("-s")
                        ||  vArguments[vIter].startsWith("--sync"))
                     setSync = true;
                else if(    vArguments[vIter].startsWith("-p")
                        ||  vArguments[vIter].startsWith("--parse"))
                     setParse = true;
                else if(    vArguments[vIter].startsWith("-a")
                        ||  vArguments[vIter].startsWith("--art"))
                     setArt = true;
                else if(    vArguments[vIter].startsWith("-u")
                        ||  vArguments[vIter].startsWith("--upload"))
                     setUpload = true;
                else if(    vArguments[vIter].startsWith("-q")
                        ||  vArguments[vIter].startsWith("--quit"))
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
                database.clear();

                loadArchive().run();
                updateTables();

                if(setConnect) {
                    connectNetwork().run();
                }
                if(setSync) {
                    syncFilelist().run();
                }
                if(setParse) {
                    parseFilelist().run();
                }
                if(setArt) {
                    getArt().run();
                }
                if(setUpload) {
                    uploadFiles().run();
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


    @Action
    public void showAboutBox() {
        if (aboutBox == null) {
            JFrame mainFrame = ValerieApp.getApplication().getMainFrame();
            aboutBox = new ValerieAboutBox(mainFrame);
            aboutBox.setLocationRelativeTo(mainFrame);
        }
        ValerieApp.getApplication().show(aboutBox);
    }

    /** This method is called from within the constructor to
     * initialize the form.
     * WARNING: Do NOT modify this code. The content of this method is
     * always regenerated by the Form Editor.
     */
    @SuppressWarnings("unchecked")
    // <editor-fold defaultstate="collapsed" desc="Generated Code">//GEN-BEGIN:initComponents
    private void initComponents() {

        mainPanel = new javax.swing.JPanel();
        jToolBar1 = new javax.swing.JToolBar();
        jButtonConnect = new javax.swing.JButton();
        jSeparator1 = new javax.swing.JToolBar.Separator();
        jButtonSync = new javax.swing.JButton();
        jSeparator2 = new javax.swing.JToolBar.Separator();
        jButtonParse = new javax.swing.JButton();
        jSeparator3 = new javax.swing.JToolBar.Separator();
        jButtonArt = new javax.swing.JButton();
        jSeparator4 = new javax.swing.JToolBar.Separator();
        jButtonUpload = new javax.swing.JButton();
        jComboBoxBoxinfo = new javax.swing.JComboBox();
        jSplitPane1 = new javax.swing.JSplitPane();
        jTabbedPane = new javax.swing.JTabbedPane();
        jPanelMovies = new javax.swing.JPanel();
        jScrollPane1 = new javax.swing.JScrollPane();
        jTableFilelist = new javax.swing.JTable() {
            public Component prepareRenderer(TableCellRenderer renderer, int rowIndex, int vColIndex) {
                Component c = super.prepareRenderer(renderer, rowIndex, vColIndex);
                if (c instanceof JComponent) {
                    JComponent jc = (JComponent) c;
                    Object jo = getValueAt(rowIndex, vColIndex);
                    if(jo != null)
                    jc.setToolTipText(jo.toString());

                    if(!super.isRowSelected(rowIndex)) {
                        jo = getValueAt(rowIndex, 5);
                        if(jo != null && jo.toString() == "true")
                        jc.setBackground(Color.orange);
                        else
                        jc.setBackground(null/*Color.white*/);
                    }
                }
                return c;
            }
        }
        ;
        jPanelSeries = new javax.swing.JPanel();
        jSplitPane2 = new javax.swing.JSplitPane();
        jScrollPane6 = new javax.swing.JScrollPane();
        jTableSeries = new javax.swing.JTable() {
            public Component prepareRenderer(TableCellRenderer renderer, int rowIndex, int vColIndex) {
                Component c = super.prepareRenderer(renderer, rowIndex, vColIndex);
                if (c instanceof JComponent) {
                    JComponent jc = (JComponent) c;
                    Object jo = getValueAt(rowIndex, vColIndex);
                    if(jo != null)
                    jc.setToolTipText(jo.toString());
                }
                return c;
            }
        }
        ;
        jScrollPane5 = new javax.swing.JScrollPane();
        jTableFilelistEpisodes = new javax.swing.JTable() {
            public Component prepareRenderer(TableCellRenderer renderer, int rowIndex, int vColIndex) {
                Component c = super.prepareRenderer(renderer, rowIndex, vColIndex);
                if (c instanceof JComponent) {
                    JComponent jc = (JComponent) c;
                    Object jo = getValueAt(rowIndex, vColIndex);
                    if(jo != null)
                    jc.setToolTipText(jo.toString());

                    if(!super.isRowSelected(rowIndex)) {
                        jo = getValueAt(rowIndex, 6);
                        if(jo != null && jo.toString() == "true")
                        jc.setBackground(Color.orange);
                        else
                        jc.setBackground(null/*Color.white*/);
                    }
                }

                return c;
            }
        }
        ;
        jPanel1 = new javax.swing.JPanel();
        jScrollPane3 = new javax.swing.JScrollPane();
        jTextAreaDescription = new javax.swing.JTextArea();
        jPanelThumbs = new javax.swing.JPanel();
        jLabelPoster = new javax.swing.JLabel();
        jLabelBackdrop = new javax.swing.JLabel();
        menuBar = new javax.swing.JMenuBar();
        javax.swing.JMenu fileMenu = new javax.swing.JMenu();
        javax.swing.JMenuItem exitMenuItem = new javax.swing.JMenuItem();
        jMenu1 = new javax.swing.JMenu();
        jMenuItem1 = new javax.swing.JMenuItem();
        javax.swing.JMenu helpMenu = new javax.swing.JMenu();
        javax.swing.JMenuItem aboutMenuItem = new javax.swing.JMenuItem();
        statusPanel = new javax.swing.JPanel();
        javax.swing.JSeparator statusPanelSeparator = new javax.swing.JSeparator();
        statusMessageLabel = new javax.swing.JLabel();
        statusAnimationLabel = new javax.swing.JLabel();
        progressBar = new javax.swing.JProgressBar();
        statusPopup = new javax.swing.JFrame();
        jPanel2 = new javax.swing.JPanel();
        animatedBar = new javax.swing.JLabel();
        descLabel = new javax.swing.JLabel();

        mainPanel.setName("mainPanel"); // NOI18N

        jToolBar1.setRollover(true);
        jToolBar1.setName("jToolBar1"); // NOI18N

        javax.swing.ActionMap actionMap = org.jdesktop.application.Application.getInstance(valerie.ValerieApp.class).getContext().getActionMap(ValerieView.class, this);
        jButtonConnect.setAction(actionMap.get("connectNetwork")); // NOI18N
        org.jdesktop.application.ResourceMap resourceMap = org.jdesktop.application.Application.getInstance(valerie.ValerieApp.class).getContext().getResourceMap(ValerieView.class);
        jButtonConnect.setText(resourceMap.getString("jButtonConnect.text")); // NOI18N
        jButtonConnect.setFocusable(false);
        jButtonConnect.setHorizontalTextPosition(javax.swing.SwingConstants.CENTER);
        jButtonConnect.setName("jButtonConnect"); // NOI18N
        jButtonConnect.setVerticalTextPosition(javax.swing.SwingConstants.BOTTOM);
        jToolBar1.add(jButtonConnect);

        jSeparator1.setName("jSeparator1"); // NOI18N
        jToolBar1.add(jSeparator1);

        jButtonSync.setAction(actionMap.get("syncFilelist")); // NOI18N
        jButtonSync.setText(resourceMap.getString("jButtonSync.text")); // NOI18N
        jButtonSync.setFocusable(false);
        jButtonSync.setHorizontalTextPosition(javax.swing.SwingConstants.CENTER);
        jButtonSync.setName("jButtonSync"); // NOI18N
        jButtonSync.setVerticalTextPosition(javax.swing.SwingConstants.BOTTOM);
        jToolBar1.add(jButtonSync);

        jSeparator2.setName("jSeparator2"); // NOI18N
        jToolBar1.add(jSeparator2);

        jButtonParse.setAction(actionMap.get("parseFilelist")); // NOI18N
        jButtonParse.setText(resourceMap.getString("jButtonParse.text")); // NOI18N
        jButtonParse.setFocusable(false);
        jButtonParse.setHorizontalTextPosition(javax.swing.SwingConstants.CENTER);
        jButtonParse.setName("jButtonParse"); // NOI18N
        jButtonParse.setVerticalTextPosition(javax.swing.SwingConstants.BOTTOM);
        jToolBar1.add(jButtonParse);

        jSeparator3.setName("jSeparator3"); // NOI18N
        jToolBar1.add(jSeparator3);

        jButtonArt.setAction(actionMap.get("getArt")); // NOI18N
        jButtonArt.setText(resourceMap.getString("jButtonArt.text")); // NOI18N
        jButtonArt.setFocusable(false);
        jButtonArt.setHorizontalTextPosition(javax.swing.SwingConstants.CENTER);
        jButtonArt.setName("jButtonArt"); // NOI18N
        jButtonArt.setVerticalTextPosition(javax.swing.SwingConstants.BOTTOM);
        jToolBar1.add(jButtonArt);

        jSeparator4.setName("jSeparator4"); // NOI18N
        jToolBar1.add(jSeparator4);

        jButtonUpload.setAction(actionMap.get("uploadFiles")); // NOI18N
        jButtonUpload.setText(resourceMap.getString("jButtonUpload.text")); // NOI18N
        jButtonUpload.setFocusable(false);
        jButtonUpload.setHorizontalTextPosition(javax.swing.SwingConstants.CENTER);
        jButtonUpload.setName("jButtonUpload"); // NOI18N
        jButtonUpload.setVerticalTextPosition(javax.swing.SwingConstants.BOTTOM);
        jToolBar1.add(jButtonUpload);

        jComboBoxBoxinfo.setBackground(resourceMap.getColor("jComboBoxBoxinfo.background")); // NOI18N
        jComboBoxBoxinfo.setName("jComboBoxBoxinfo"); // NOI18N
        jComboBoxBoxinfo.addItemListener(new java.awt.event.ItemListener() {
            public void itemStateChanged(java.awt.event.ItemEvent evt) {
                jComboBoxBoxinfoItemStateChanged(evt);
            }
        });

        jSplitPane1.setDividerLocation(400);
        jSplitPane1.setDividerSize(10);
        jSplitPane1.setName("jSplitPane1"); // NOI18N
        jSplitPane1.setOneTouchExpandable(true);

        jTabbedPane.setName("jTabbedPane"); // NOI18N

        jPanelMovies.setName("jPanelMovies"); // NOI18N

        jScrollPane1.setName("jScrollPane1"); // NOI18N

        jTableFilelist.setAutoCreateRowSorter(true);
        jTableFilelist.setModel(new javax.swing.table.DefaultTableModel(
            new Object [][] {
                {null, null, null, null, null, null}
            },
            new String [] {
                "Use", "Title", "Searchstring", "Year", "ID", "Update"
            }
        ) {
            Class[] types = new Class [] {
                java.lang.Boolean.class, java.lang.String.class, java.lang.String.class, java.lang.String.class, java.lang.String.class, java.lang.Boolean.class
            };
            boolean[] canEdit = new boolean [] {
                true, false, true, false, false, false
            };

            public Class getColumnClass(int columnIndex) {
                return types [columnIndex];
            }

            public boolean isCellEditable(int rowIndex, int columnIndex) {
                return canEdit [columnIndex];
            }
        });
        List <RowSorter.SortKey> sortKeysMovies
        = new ArrayList<RowSorter.SortKey>();
        sortKeysMovies.add(new RowSorter.SortKey(0, SortOrder.ASCENDING));
        sortKeysMovies.add(new RowSorter.SortKey(1, SortOrder.ASCENDING));

        jTableFilelist.getRowSorter().setSortKeys(sortKeysMovies);
        jTableFilelist.setName("jTableFilelist"); // NOI18N
        jTableFilelist.getTableHeader().setReorderingAllowed(false);
        jTableFilelist.addMouseListener(new java.awt.event.MouseAdapter() {
            public void mouseClicked(java.awt.event.MouseEvent evt) {
                jTableFilelistMouseClicked(evt);
            }
        });
        jTableFilelist.addKeyListener(new java.awt.event.KeyAdapter() {
            public void keyPressed(java.awt.event.KeyEvent evt) {
                jTableFilelistKeyPressed(evt);
            }
        });
        jScrollPane1.setViewportView(jTableFilelist);
        jTableFilelist.getColumnModel().getColumn(0).setResizable(false);
        jTableFilelist.getColumnModel().getColumn(0).setPreferredWidth(10);
        jTableFilelist.getColumnModel().getColumn(0).setHeaderValue(resourceMap.getString("jTableFilelist.columnModel.title5")); // NOI18N
        jTableFilelist.getColumnModel().getColumn(1).setResizable(false);
        jTableFilelist.getColumnModel().getColumn(1).setPreferredWidth(150);
        jTableFilelist.getColumnModel().getColumn(1).setHeaderValue(resourceMap.getString("jTableFilelist.columnModel.title1")); // NOI18N
        jTableFilelist.getColumnModel().getColumn(2).setResizable(false);
        jTableFilelist.getColumnModel().getColumn(2).setHeaderValue(resourceMap.getString("jTableFilelist.columnModel.title3")); // NOI18N
        jTableFilelist.getColumnModel().getColumn(3).setResizable(false);
        jTableFilelist.getColumnModel().getColumn(3).setPreferredWidth(30);
        jTableFilelist.getColumnModel().getColumn(3).setHeaderValue(resourceMap.getString("jTableFilelist.columnModel.title3")); // NOI18N
        jTableFilelist.getColumnModel().getColumn(4).setResizable(false);
        jTableFilelist.getColumnModel().getColumn(4).setPreferredWidth(10);
        jTableFilelist.getColumnModel().getColumn(4).setHeaderValue(resourceMap.getString("jTableFilelist.columnModel.title6")); // NOI18N
        jTableFilelist.getColumnModel().getColumn(5).setResizable(false);
        jTableFilelist.getColumnModel().getColumn(5).setPreferredWidth(1);
        jTableFilelist.getColumnModel().getColumn(5).setHeaderValue(resourceMap.getString("jTableFilelist.columnModel.title5")); // NOI18N

        javax.swing.GroupLayout jPanelMoviesLayout = new javax.swing.GroupLayout(jPanelMovies);
        jPanelMovies.setLayout(jPanelMoviesLayout);
        jPanelMoviesLayout.setHorizontalGroup(
            jPanelMoviesLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addComponent(jScrollPane1, javax.swing.GroupLayout.DEFAULT_SIZE, 394, Short.MAX_VALUE)
        );
        jPanelMoviesLayout.setVerticalGroup(
            jPanelMoviesLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addComponent(jScrollPane1, javax.swing.GroupLayout.DEFAULT_SIZE, 612, Short.MAX_VALUE)
        );

        jTabbedPane.addTab(resourceMap.getString("jPanelMovies.TabConstraints.tabTitle"), jPanelMovies); // NOI18N

        jPanelSeries.setName("jPanelSeries"); // NOI18N
        jPanelSeries.setPreferredSize(new java.awt.Dimension(586, 667));

        jSplitPane2.setDividerLocation(250);
        jSplitPane2.setDividerSize(8);
        jSplitPane2.setOrientation(javax.swing.JSplitPane.VERTICAL_SPLIT);
        jSplitPane2.setName("jSplitPane2"); // NOI18N
        jSplitPane2.setOneTouchExpandable(true);

        jScrollPane6.setName("jScrollPane6"); // NOI18N

        jTableSeries.setAutoCreateRowSorter(true);
        jTableSeries.setModel(new javax.swing.table.DefaultTableModel(
            new Object [][] {
                {null, null}
            },
            new String [] {
                "Series", "ID"
            }
        ) {
            Class[] types = new Class [] {
                java.lang.String.class, java.lang.String.class
            };
            boolean[] canEdit = new boolean [] {
                false, false
            };

            public Class getColumnClass(int columnIndex) {
                return types [columnIndex];
            }

            public boolean isCellEditable(int rowIndex, int columnIndex) {
                return canEdit [columnIndex];
            }
        });
        List <RowSorter.SortKey> sortKeysSeries
        = new ArrayList<RowSorter.SortKey>();
        sortKeysSeries.add(new RowSorter.SortKey(0, SortOrder.ASCENDING));

        jTableSeries.getRowSorter().setSortKeys(sortKeysSeries);
        jTableSeries.setName("jTableSeries"); // NOI18N
        jTableSeries.addMouseListener(new java.awt.event.MouseAdapter() {
            public void mouseClicked(java.awt.event.MouseEvent evt) {
                jTableSeriesMouseClicked(evt);
            }
        });
        jTableSeries.addKeyListener(new java.awt.event.KeyAdapter() {
            public void keyPressed(java.awt.event.KeyEvent evt) {
                jTableSeriesKeyPressed(evt);
            }
        });
        jScrollPane6.setViewportView(jTableSeries);
        jTableSeries.getColumnModel().getColumn(0).setResizable(false);
        jTableSeries.getColumnModel().getColumn(0).setHeaderValue(resourceMap.getString("jTableSeries.columnModel.title0")); // NOI18N
        jTableSeries.getColumnModel().getColumn(1).setResizable(false);
        jTableSeries.getColumnModel().getColumn(1).setPreferredWidth(10);
        jTableSeries.getColumnModel().getColumn(1).setHeaderValue(resourceMap.getString("jTableSeries.columnModel.title1")); // NOI18N

        jSplitPane2.setTopComponent(jScrollPane6);

        jScrollPane5.setName("jScrollPane5"); // NOI18N

        jTableFilelistEpisodes.setAutoCreateRowSorter(true);
        jTableFilelistEpisodes.setModel(new javax.swing.table.DefaultTableModel(
            new Object [][] {
                {null, null, null, null, null, null, null}
            },
            new String [] {
                "Use", "Title", "Searchstring", "S", "E", "ID", "Update"
            }
        ) {
            Class[] types = new Class [] {
                java.lang.Boolean.class, java.lang.String.class, java.lang.String.class, java.lang.Integer.class, java.lang.Integer.class, java.lang.String.class, java.lang.Boolean.class
            };
            boolean[] canEdit = new boolean [] {
                true, false, true, true, true, false, false
            };

            public Class getColumnClass(int columnIndex) {
                return types [columnIndex];
            }

            public boolean isCellEditable(int rowIndex, int columnIndex) {
                return canEdit [columnIndex];
            }
        });
        List <RowSorter.SortKey> sortKeysEpisodes
        = new ArrayList<RowSorter.SortKey>();
        sortKeysEpisodes.add(new RowSorter.SortKey(0, SortOrder.ASCENDING));
        sortKeysEpisodes.add(new RowSorter.SortKey(3, SortOrder.ASCENDING));
        sortKeysEpisodes.add(new RowSorter.SortKey(4, SortOrder.ASCENDING));

        jTableFilelistEpisodes.getRowSorter().setSortKeys(sortKeysEpisodes);
        jTableFilelistEpisodes.setName("jTableFilelistEpisodes"); // NOI18N
        jTableFilelistEpisodes.addMouseListener(new java.awt.event.MouseAdapter() {
            public void mouseClicked(java.awt.event.MouseEvent evt) {
                jTableFilelistEpisodesMouseClicked(evt);
            }
        });
        jTableFilelistEpisodes.addKeyListener(new java.awt.event.KeyAdapter() {
            public void keyPressed(java.awt.event.KeyEvent evt) {
                jTableFilelistEpisodesKeyPressed(evt);
            }
        });
        jScrollPane5.setViewportView(jTableFilelistEpisodes);
        jTableFilelistEpisodes.getColumnModel().getColumn(0).setResizable(false);
        jTableFilelistEpisodes.getColumnModel().getColumn(0).setPreferredWidth(10);
        jTableFilelistEpisodes.getColumnModel().getColumn(0).setHeaderValue(resourceMap.getString("jTableFilelist.columnModel.title5")); // NOI18N
        jTableFilelistEpisodes.getColumnModel().getColumn(1).setResizable(false);
        jTableFilelistEpisodes.getColumnModel().getColumn(1).setPreferredWidth(150);
        jTableFilelistEpisodes.getColumnModel().getColumn(1).setHeaderValue(resourceMap.getString("jTableFilelist.columnModel.title1")); // NOI18N
        jTableFilelistEpisodes.getColumnModel().getColumn(2).setResizable(false);
        jTableFilelistEpisodes.getColumnModel().getColumn(2).setHeaderValue(resourceMap.getString("jTableFilelist.columnModel.title3")); // NOI18N
        jTableFilelistEpisodes.getColumnModel().getColumn(3).setResizable(false);
        jTableFilelistEpisodes.getColumnModel().getColumn(3).setPreferredWidth(15);
        jTableFilelistEpisodes.getColumnModel().getColumn(3).setHeaderValue(resourceMap.getString("jTableFilelistEpisodes.columnModel.title7")); // NOI18N
        jTableFilelistEpisodes.getColumnModel().getColumn(4).setResizable(false);
        jTableFilelistEpisodes.getColumnModel().getColumn(4).setPreferredWidth(15);
        jTableFilelistEpisodes.getColumnModel().getColumn(4).setHeaderValue(resourceMap.getString("jTableFilelistEpisodes.columnModel.title8")); // NOI18N
        jTableFilelistEpisodes.getColumnModel().getColumn(5).setResizable(false);
        jTableFilelistEpisodes.getColumnModel().getColumn(5).setPreferredWidth(10);
        jTableFilelistEpisodes.getColumnModel().getColumn(5).setHeaderValue(resourceMap.getString("jTableFilelistEpisodes.columnModel.title6")); // NOI18N
        jTableFilelistEpisodes.getColumnModel().getColumn(6).setResizable(false);
        jTableFilelistEpisodes.getColumnModel().getColumn(6).setPreferredWidth(1);
        jTableFilelistEpisodes.getColumnModel().getColumn(6).setHeaderValue(resourceMap.getString("jTableFilelistEpisodes.columnModel.title6")); // NOI18N

        jSplitPane2.setRightComponent(jScrollPane5);

        javax.swing.GroupLayout jPanelSeriesLayout = new javax.swing.GroupLayout(jPanelSeries);
        jPanelSeries.setLayout(jPanelSeriesLayout);
        jPanelSeriesLayout.setHorizontalGroup(
            jPanelSeriesLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addComponent(jSplitPane2, javax.swing.GroupLayout.DEFAULT_SIZE, 394, Short.MAX_VALUE)
        );
        jPanelSeriesLayout.setVerticalGroup(
            jPanelSeriesLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addComponent(jSplitPane2, javax.swing.GroupLayout.DEFAULT_SIZE, 612, Short.MAX_VALUE)
        );

        jTabbedPane.addTab(resourceMap.getString("jPanelSeries.TabConstraints.tabTitle"), jPanelSeries); // NOI18N

        jSplitPane1.setLeftComponent(jTabbedPane);

        jPanel1.setName("jPanel1"); // NOI18N

        jScrollPane3.setName("jScrollPane3"); // NOI18N

        jTextAreaDescription.setColumns(20);
        jTextAreaDescription.setRows(5);
        jTextAreaDescription.setName("jTextAreaDescription"); // NOI18N
        jScrollPane3.setViewportView(jTextAreaDescription);

        jPanelThumbs.setBackground(resourceMap.getColor("jPanelThumbs.background")); // NOI18N
        jPanelThumbs.setBorder(new javax.swing.border.MatteBorder(null));
        jPanelThumbs.setName("jPanelThumbs"); // NOI18N

        jLabelPoster.setBackground(resourceMap.getColor("jLabelPoster.background")); // NOI18N
        jLabelPoster.setText(resourceMap.getString("jLabelPoster.text")); // NOI18N
        jLabelPoster.setBorder(javax.swing.BorderFactory.createLineBorder(new java.awt.Color(0, 0, 0)));
        jLabelPoster.setName("jLabelPoster"); // NOI18N
        jLabelPoster.setOpaque(true);

        jLabelBackdrop.setBackground(resourceMap.getColor("jLabelBackdrop.background")); // NOI18N
        jLabelBackdrop.setText(resourceMap.getString("jLabelBackdrop.text")); // NOI18N
        jLabelBackdrop.setBorder(javax.swing.BorderFactory.createLineBorder(new java.awt.Color(0, 0, 0)));
        jLabelBackdrop.setName("jLabelBackdrop"); // NOI18N
        jLabelBackdrop.setOpaque(true);

        javax.swing.GroupLayout jPanelThumbsLayout = new javax.swing.GroupLayout(jPanelThumbs);
        jPanelThumbs.setLayout(jPanelThumbsLayout);
        jPanelThumbsLayout.setHorizontalGroup(
            jPanelThumbsLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanelThumbsLayout.createSequentialGroup()
                .addGap(12, 12, 12)
                .addComponent(jLabelBackdrop, javax.swing.GroupLayout.PREFERRED_SIZE, 400, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                .addComponent(jLabelPoster, javax.swing.GroupLayout.PREFERRED_SIZE, 236, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addGap(29, 29, 29))
        );
        jPanelThumbsLayout.setVerticalGroup(
            jPanelThumbsLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(javax.swing.GroupLayout.Alignment.TRAILING, jPanelThumbsLayout.createSequentialGroup()
                .addContainerGap(javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                .addGroup(jPanelThumbsLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(jLabelPoster, javax.swing.GroupLayout.PREFERRED_SIZE, 218, javax.swing.GroupLayout.PREFERRED_SIZE)
                    .addComponent(jLabelBackdrop, javax.swing.GroupLayout.PREFERRED_SIZE, 218, javax.swing.GroupLayout.PREFERRED_SIZE))
                .addContainerGap())
        );

        javax.swing.GroupLayout jPanel1Layout = new javax.swing.GroupLayout(jPanel1);
        jPanel1.setLayout(jPanel1Layout);
        jPanel1Layout.setHorizontalGroup(
            jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addComponent(jScrollPane3, javax.swing.GroupLayout.DEFAULT_SIZE, 685, Short.MAX_VALUE)
            .addComponent(jPanelThumbs, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
        );
        jPanel1Layout.setVerticalGroup(
            jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(javax.swing.GroupLayout.Alignment.TRAILING, jPanel1Layout.createSequentialGroup()
                .addComponent(jScrollPane3, javax.swing.GroupLayout.DEFAULT_SIZE, 399, Short.MAX_VALUE)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addComponent(jPanelThumbs, javax.swing.GroupLayout.PREFERRED_SIZE, 235, javax.swing.GroupLayout.PREFERRED_SIZE))
        );

        jSplitPane1.setRightComponent(jPanel1);

        javax.swing.GroupLayout mainPanelLayout = new javax.swing.GroupLayout(mainPanel);
        mainPanel.setLayout(mainPanelLayout);
        mainPanelLayout.setHorizontalGroup(
            mainPanelLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(mainPanelLayout.createSequentialGroup()
                .addComponent(jToolBar1, javax.swing.GroupLayout.DEFAULT_SIZE, 640, Short.MAX_VALUE)
                .addGap(121, 121, 121)
                .addComponent(jComboBoxBoxinfo, javax.swing.GroupLayout.PREFERRED_SIZE, 324, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addContainerGap())
            .addComponent(jSplitPane1, javax.swing.GroupLayout.DEFAULT_SIZE, 1095, Short.MAX_VALUE)
        );
        mainPanelLayout.setVerticalGroup(
            mainPanelLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(mainPanelLayout.createSequentialGroup()
                .addGroup(mainPanelLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(jToolBar1, javax.swing.GroupLayout.PREFERRED_SIZE, 25, javax.swing.GroupLayout.PREFERRED_SIZE)
                    .addGroup(mainPanelLayout.createSequentialGroup()
                        .addContainerGap()
                        .addComponent(jComboBoxBoxinfo, javax.swing.GroupLayout.PREFERRED_SIZE, 24, javax.swing.GroupLayout.PREFERRED_SIZE)))
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addComponent(jSplitPane1, javax.swing.GroupLayout.DEFAULT_SIZE, 642, Short.MAX_VALUE))
        );

        menuBar.setName("menuBar"); // NOI18N

        fileMenu.setText(resourceMap.getString("fileMenu.text")); // NOI18N
        fileMenu.setName("fileMenu"); // NOI18N

        exitMenuItem.setAction(actionMap.get("quit")); // NOI18N
        exitMenuItem.setName("exitMenuItem"); // NOI18N
        fileMenu.add(exitMenuItem);

        menuBar.add(fileMenu);

        jMenu1.setText(resourceMap.getString("jMenu1.text")); // NOI18N
        jMenu1.setName("jMenu1"); // NOI18N

        jMenuItem1.setAction(actionMap.get("jMenuItemEditSettingsClicked")); // NOI18N
        jMenuItem1.setText(resourceMap.getString("jMenuItem1.text")); // NOI18N
        jMenuItem1.setName("jMenuItem1"); // NOI18N
        jMenu1.add(jMenuItem1);

        menuBar.add(jMenu1);

        helpMenu.setText(resourceMap.getString("helpMenu.text")); // NOI18N
        helpMenu.setName("helpMenu"); // NOI18N

        aboutMenuItem.setAction(actionMap.get("showAboutBox")); // NOI18N
        aboutMenuItem.setName("aboutMenuItem"); // NOI18N
        helpMenu.add(aboutMenuItem);

        menuBar.add(helpMenu);

        statusPanel.setName("statusPanel"); // NOI18N

        statusPanelSeparator.setName("statusPanelSeparator"); // NOI18N

        statusMessageLabel.setName("statusMessageLabel"); // NOI18N

        statusAnimationLabel.setHorizontalAlignment(javax.swing.SwingConstants.LEFT);
        statusAnimationLabel.setName("statusAnimationLabel"); // NOI18N

        progressBar.setName("progressBar"); // NOI18N

        javax.swing.GroupLayout statusPanelLayout = new javax.swing.GroupLayout(statusPanel);
        statusPanel.setLayout(statusPanelLayout);
        statusPanelLayout.setHorizontalGroup(
            statusPanelLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addComponent(statusPanelSeparator, javax.swing.GroupLayout.DEFAULT_SIZE, 1095, Short.MAX_VALUE)
            .addGroup(statusPanelLayout.createSequentialGroup()
                .addContainerGap()
                .addComponent(statusMessageLabel)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED, 1075, Short.MAX_VALUE)
                .addComponent(statusAnimationLabel)
                .addContainerGap())
            .addGroup(javax.swing.GroupLayout.Alignment.TRAILING, statusPanelLayout.createSequentialGroup()
                .addContainerGap(788, Short.MAX_VALUE)
                .addComponent(progressBar, javax.swing.GroupLayout.PREFERRED_SIZE, 297, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addContainerGap())
        );
        statusPanelLayout.setVerticalGroup(
            statusPanelLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(statusPanelLayout.createSequentialGroup()
                .addComponent(statusPanelSeparator, javax.swing.GroupLayout.PREFERRED_SIZE, 2, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                .addGroup(statusPanelLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                    .addComponent(statusMessageLabel)
                    .addComponent(statusAnimationLabel)
                    .addComponent(progressBar, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))
                .addGap(3, 3, 3))
        );

        statusPopup.setMinimumSize(new java.awt.Dimension(220, 50));
        statusPopup.setModalExclusionType(java.awt.Dialog.ModalExclusionType.TOOLKIT_EXCLUDE);
        statusPopup.setName("statusPopup"); // NOI18N
        statusPopup.setResizable(false);
        statusPopup.setUndecorated(true);

        jPanel2.setBorder(javax.swing.BorderFactory.createLineBorder(new java.awt.Color(0, 0, 0)));
        jPanel2.setAlignmentX(2.0F);
        jPanel2.setAlignmentY(2.0F);
        jPanel2.setName("jPanel2"); // NOI18N
        jPanel2.setLayout(new java.awt.BorderLayout());

        animatedBar.setIcon(new javax.swing.ImageIcon("E:\\Documents\\Valerie\\pc\\src\\valerie\\resources\\ajax-loader_transparent.gif")); // NOI18N
        animatedBar.setText(resourceMap.getString("animatedBar.text")); // NOI18N
        animatedBar.setName("animatedBar"); // NOI18N
        jPanel2.add(animatedBar, java.awt.BorderLayout.CENTER);

        descLabel.setFont(new java.awt.Font("Tahoma", 0, 18));
        descLabel.setHorizontalAlignment(javax.swing.SwingConstants.CENTER);
        descLabel.setText(resourceMap.getString("descLabel.text")); // NOI18N
        descLabel.setName("descLabel"); // NOI18N
        jPanel2.add(descLabel, java.awt.BorderLayout.NORTH);

        statusPopup.getContentPane().add(jPanel2, java.awt.BorderLayout.CENTER);

        setComponent(mainPanel);
        setMenuBar(menuBar);
        setStatusBar(statusPanel);
    }// </editor-fold>//GEN-END:initComponents

    private void drawPosters(ImageIcon poster, ImageIcon backdrop) {
        if(poster.getIconWidth() != -1)
            jLabelPoster.getGraphics().drawImage(poster.getImage(), 40, 2, jLabelPoster.getWidth() - 80, jLabelPoster.getHeight() - 4, null);
        else
            jLabelPoster.repaint();

        if(backdrop.getIconWidth() != -1)
            jLabelBackdrop.getGraphics().drawImage(backdrop.getImage(), 10, 2, jLabelBackdrop.getWidth() - 20, jLabelBackdrop.getHeight() - 4, null);
        else
            jLabelBackdrop.repaint();
    }

    private void jTableFilelistMouseClicked(java.awt.event.MouseEvent evt) {//GEN-FIRST:event_jTableFilelistMouseClicked
        int row = jTableFilelist.getSelectedRow();
        int id = (Integer) jTableFilelist.getValueAt(row, 4);

        MediaInfo info = database.getMediaInfoById(id);

        jTextAreaDescription.setText(info.toString());
        ImageIcon poster = new ImageIcon("converted/tt" + info.Imdb + "_poster.png");
        ImageIcon backdrop = new ImageIcon("download/tt" + info.Imdb + "_backdrop.jpg");
        drawPosters(poster, backdrop);
    }//GEN-LAST:event_jTableFilelistMouseClicked

    private void jTableFilelistKeyPressed(java.awt.event.KeyEvent evt) {//GEN-FIRST:event_jTableFilelistKeyPressed
        int row = jTableFilelist.getSelectedRow();

        if (evt.getKeyCode() == 38 && row > 0) {
            row--;
        } else if (evt.getKeyCode() == 40 && row + 1 < jTableFilelist.getRowCount()) {
            row++;
        }

        int id = (Integer) jTableFilelist.getValueAt(row, 4);
        MediaInfo info = database.getMediaInfoById(id);

        jTextAreaDescription.setText(info.toString());
        ImageIcon poster = new ImageIcon("converted/tt" + info.Imdb + "_poster.png");
        ImageIcon backdrop = new ImageIcon("download/tt" + info.Imdb + "_backdrop.jpg");
        drawPosters(poster, backdrop);
    }//GEN-LAST:event_jTableFilelistKeyPressed

    private void jTableFilelistEpisodesMouseClicked(java.awt.event.MouseEvent evt) {//GEN-FIRST:event_jTableFilelistEpisodesMouseClicked
        int row = jTableFilelistEpisodes.getSelectedRow();
        int id = (Integer) jTableFilelistEpisodes.getValueAt(row, 5);

        MediaInfo info = database.getMediaInfoById(id);

        jTextAreaDescription.setText(info.toString());
        ImageIcon poster = new ImageIcon("converted/" + info.TheTvDb + "_poster.png");
        ImageIcon backdrop = new ImageIcon("download/" + info.TheTvDb + "_backdrop.jpg");
        drawPosters(poster, backdrop);
    }//GEN-LAST:event_jTableFilelistEpisodesMouseClicked

    private void jTableFilelistEpisodesKeyPressed(java.awt.event.KeyEvent evt) {//GEN-FIRST:event_jTableFilelistEpisodesKeyPressed
        int row = jTableFilelistEpisodes.getSelectedRow();

        if (evt.getKeyCode() == 38 && row > 0) {
            row--;
        } else if (evt.getKeyCode() == 40 && row + 1 < jTableFilelistEpisodes.getRowCount()) {
            row++;
        }

        int id = (Integer) jTableFilelistEpisodes.getValueAt(row, 5);
        MediaInfo info = database.getMediaInfoById(id);

        jTextAreaDescription.setText(info.toString());
        ImageIcon poster = new ImageIcon("converted/" + info.TheTvDb + "_poster.png");
        ImageIcon backdrop = new ImageIcon("download/" + info.TheTvDb + "_backdrop.jpg");
        drawPosters(poster, backdrop);
    }//GEN-LAST:event_jTableFilelistEpisodesKeyPressed

    private void jTableSeriesMouseClicked(java.awt.event.MouseEvent evt) {//GEN-FIRST:event_jTableSeriesMouseClicked
        int row = jTableSeries.getSelectedRow();
        int id = (Integer) jTableSeries.getValueAt(row, 1);

        MediaInfo info = database.getMediaInfoById(id);
        if (info != null) {
            jTextAreaDescription.setText(info.toString());
            ImageIcon poster = new ImageIcon("converted/" + info.TheTvDb + "_poster.png");
            ImageIcon backdrop = new ImageIcon("download/" + info.TheTvDb + "_backdrop.jpg");
            drawPosters(poster, backdrop);
        }
        updateTablesEpisodes(id);
    }//GEN-LAST:event_jTableSeriesMouseClicked

    private void jTableSeriesKeyPressed(java.awt.event.KeyEvent evt) {//GEN-FIRST:event_jTableSeriesKeyPressed
        int row = jTableSeries.getSelectedRow();

        if (evt.getKeyCode() == 38 && row > 0) {
            row--;
        } else if (evt.getKeyCode() == 40 && row + 1 < jTableSeries.getRowCount()) {
            row++;
        }

        int id = (Integer) jTableSeries.getValueAt(row, 1);
        MediaInfo info = database.getMediaInfoById(id);
        if (info != null) {
            jTextAreaDescription.setText(info.toString());
            ImageIcon poster = new ImageIcon("converted/" + info.TheTvDb + "_poster.png");
            ImageIcon backdrop = new ImageIcon("download/" + info.TheTvDb + "_backdrop.jpg");
            drawPosters(poster, backdrop);
        }
        updateTablesEpisodes(id);
    }//GEN-LAST:event_jTableSeriesKeyPressed

    private void jComboBoxBoxinfoItemStateChanged(java.awt.event.ItemEvent evt) {//GEN-FIRST:event_jComboBoxBoxinfoItemStateChanged
        DebugOutput.printl("->");

        selectedBoxInfo = jComboBoxBoxinfo.getSelectedIndex();
        //clear database
        database.clear();

        loadArchive().run();
        updateTables();

        DebugOutput.printl("<-");
    }//GEN-LAST:event_jComboBoxBoxinfoItemStateChanged
    MediaInfoDB database = new MediaInfoDB();

    boolean isUpdating = false;

    public void updateTables() {
        DebugOutput.printl("->");

        MediaInfo[] movies = database.getMediaInfo();

        ((DefaultTableModel) jTableFilelist.getModel()).setRowCount(database.getMediaInfoMoviesCount());
        ((DefaultTableModel) jTableFilelistEpisodes.getModel()).setRowCount(database.getMediaInfoEpisodesCount());
        ((DefaultTableModel) jTableSeries.getModel()).setRowCount(database.getMediaInfoSeriesCount() + 2);

        int iteratorMovies = 0;
        int iteratorEpisodes = 0;
        int iteratorSeries = 0;

        isUpdating = true;
        jTableFilelist.setEnabled(false);
        jTableSeries.setEnabled(false);
        jTableFilelistEpisodes.setEnabled(false);

        ///
        jTableSeries.setValueAt("_Show all_", iteratorSeries, 0);
        jTableSeries.setValueAt(-1, iteratorSeries, 1);
        iteratorSeries++;
        jTableSeries.setValueAt("_Show unspecified_", iteratorSeries, 0);
        jTableSeries.setValueAt(-2, iteratorSeries, 1);
        iteratorSeries++;
        ///

        for (MediaInfo movie : movies) {
            if (movie.isMovie) {
                jTableFilelist.setValueAt(!movie.Ignoring, iteratorMovies, 0);

                jTableFilelist.setValueAt(movie.SearchString, iteratorMovies, 2);
                jTableFilelist.setValueAt(movie.Title, iteratorMovies, 1);

                jTableFilelist.setValueAt(movie.Year, iteratorMovies, 3);
                jTableFilelist.setValueAt(movie.ID, iteratorMovies, 4);

                jTableFilelist.setValueAt(movie.needsUpdate, iteratorMovies, 5);

                iteratorMovies++;
            } else if (movie.isEpisode) {
                jTableFilelistEpisodes.setValueAt(!movie.Ignoring, iteratorEpisodes, 0);

                jTableFilelistEpisodes.setValueAt(movie.SearchString, iteratorEpisodes, 2);
                jTableFilelistEpisodes.setValueAt(movie.Title, iteratorEpisodes, 1);

                jTableFilelistEpisodes.setValueAt(movie.Season, iteratorEpisodes, 3);
                jTableFilelistEpisodes.setValueAt(movie.Episode, iteratorEpisodes, 4);
                jTableFilelistEpisodes.setValueAt(movie.ID, iteratorEpisodes, 5);

                jTableFilelistEpisodes.setValueAt(movie.needsUpdate, iteratorEpisodes, 6);

                iteratorEpisodes++;
            } else if (movie.isSeries) {
                jTableSeries.setValueAt(movie.Title, iteratorSeries, 0);
                jTableSeries.setValueAt(movie.ID, iteratorSeries, 1);
                iteratorSeries++;
            }
        }

        jTableFilelist.setEnabled(true);
        jTableSeries.setEnabled(true);
        jTableFilelistEpisodes.setEnabled(true);

        jTableFilelist.getRowSorter().allRowsChanged();
        jTableSeries.getRowSorter().allRowsChanged();
        jTableFilelistEpisodes.getRowSorter().allRowsChanged();

        isUpdating = false;

        DebugOutput.printl("<-");
    }

    public void updateTablesEpisodes(int id) {

        MediaInfo[] movies;

        if (id == -1) {
            movies = database.getMediaInfoEpisodes();
        } else if (id == -2) {
            movies = database.getMediaInfoEpisodesUnspecified();
        } else {
            MediaInfo series = database.getMediaInfoById(id);
            movies = database.getMediaInfoEpisodes(series.TheTvDb);
        }

        ((DefaultTableModel) jTableFilelistEpisodes.getModel()).setRowCount(movies.length);

        isUpdating = true;
        jTableFilelistEpisodes.setEnabled(false);

        int iteratorEpisodes = 0;
        for (MediaInfo movie : movies) {
            jTableFilelistEpisodes.setValueAt(!movie.Ignoring, iteratorEpisodes, 0);
            jTableFilelistEpisodes.setValueAt(movie.SearchString, iteratorEpisodes, 2);
            jTableFilelistEpisodes.setValueAt(movie.Title, iteratorEpisodes, 1);

            jTableFilelistEpisodes.setValueAt(movie.Season, iteratorEpisodes, 3);
            jTableFilelistEpisodes.setValueAt(movie.Episode, iteratorEpisodes, 4);
            jTableFilelistEpisodes.setValueAt(movie.ID, iteratorEpisodes, 5);

            jTableFilelistEpisodes.setValueAt(movie.needsUpdate, iteratorEpisodes, 6);

            iteratorEpisodes++;
        }

        jTableFilelistEpisodes.setEnabled(true);

        jTableFilelistEpisodes.getRowSorter().allRowsChanged();

        isUpdating = false;
    }

    private void saveTables() {

        MediaInfo[] movies = database.getMediaInfo();

        //create db file
        try {
            Writer fwMovie = new FileWriter("db/moviedb.txt");
            Writer fwSeries = new FileWriter("db/seriesdb.txt");

            File episodes = new File("db/episodes");
            if (episodes.exists()) {
                for (File episode : episodes.listFiles()) {
                    episode.delete();
                }
            }

            episodes.mkdir();

            //Writer fwEpisode = new FileWriter( "db/episodedb.txt" );
            fwMovie.write("Created on " + Calendar.getInstance().getTime() + "\n");
            fwSeries.write("Created on " + Calendar.getInstance().getTime() + "\n");
            //fwEpisode.write("Created on " + Calendar.getInstance().getTime() + "\n");
            for (MediaInfo movie : movies) {
                if (!movie.Ignoring) {
                    if (movie.isMovie) {
                        fwMovie.append(movie.toString());
                    } else if (movie.isSeries) {
                        fwSeries.append(movie.toString());
                    } else if (movie.isEpisode) {
                        Writer fwEpisode = new FileWriter("db/episodes/" + movie.TheTvDb + ".txt", true);
                        fwEpisode.append(movie.toString());
                        fwEpisode.close();
                    }
                }
            }
            fwMovie.close();
            fwSeries.close();
        } catch (Exception ex) {
            System.out.println(ex.toString());
        }
    }


    @Action
    public Task loadArchive() { return new loadArchiveTask(getApplication()); }

    private class loadArchiveTask extends org.jdesktop.application.Task<Object, Void> {
        loadArchiveTask(org.jdesktop.application.Application app) {
            super(app);

            Logger.setBlocked(true);
            Logger.printBlocked("Loading Archive");

        }
        @Override protected Object doInBackground() {
            DebugOutput.printl("->");

            try {
                BufferedReader frMovie = new BufferedReader(new FileReader("db/moviedb.txt"));
                String moviedb = "";
                String line;
                while ((line = frMovie.readLine()) != null) {
                    moviedb += line + "\n";
                }

                String movies[] = moviedb.split("---BEGIN---\n");
                for (String movie : movies) {
                    MediaInfo info = new MediaInfo();
                    info.reparse(movie);
                    info.isMovie = true;
                    info.isArchiv = true;
                    info.needsUpdate = false;

                    info.DataProvider = new valerie.provider.Imdb();
                    info.ArtProvider = new valerie.provider.theMovieDb();

                    //ignore the entry as long as we havent confirmed that it still exists
                    info.Ignoring = true;
                    if (info.Title.length() > 0) {
                        if(database.getMediaInfoByPath(info.Path) == null)
                            database.addMediaInfo(info);
                    }
                }

            } catch (Exception ex) {
                System.out.println(ex.toString());
            }


            try {
                BufferedReader frMovie = new BufferedReader(new FileReader("db/seriesdb.txt"));
                String moviedb = "";
                String line;
                while ((line = frMovie.readLine()) != null) {
                    moviedb += line + "\n";
                }

                String movies[] = moviedb.split("---BEGIN---\n");
                for (String movie : movies) {
                    MediaInfo info = new MediaInfo();
                    info.reparse(movie);
                    info.isSeries = true;
                    info.isArchiv = true;
                    info.needsUpdate = false;

                    info.DataProvider = new valerie.provider.theTvDb();
                    info.ArtProvider = new valerie.provider.theTvDb();

                    //As this isnt represented by any file we have to set ignoring to false
                    info.Ignoring = false;
                    if (info.Title.length() > 0) {
                        if(database.getMediaInfoForSeries(info.TheTvDb) == null)
                            database.addMediaInfo(info);
                    }
                }

            } catch (Exception ex) {
                System.out.println(ex.toString());
            }

            try {
                MediaInfo infos[] = database.getMediaInfo();
                for (MediaInfo info : infos) {
                    if (info.isSeries) {
                        BufferedReader frMovie = new BufferedReader(new FileReader("db/episodes/" + info.TheTvDb + ".txt"));
                        String moviedb = "";
                        String line;
                        while ((line = frMovie.readLine()) != null) {
                            moviedb += line + "\n";
                        }

                        String movies[] = moviedb.split("---BEGIN---\n");
                        for (String movie : movies) {
                            MediaInfo movieinfo = new MediaInfo();
                            movieinfo.reparse(movie);
                            movieinfo.isEpisode = true;
                            movieinfo.isArchiv = true;
                            movieinfo.needsUpdate = false;

                            info.DataProvider = new valerie.provider.theTvDb();
                            info.ArtProvider = new valerie.provider.theTvDb();

                            //ignore the entry as long as we havent confirmed that it still exists
                            movieinfo.Ignoring = true;
                            if (movieinfo.Title.length() > 0) {
                                if(database.getMediaInfoByPath(movieinfo.Path) == null)
                                    database.addMediaInfo(movieinfo);
                            }
                        }
                    }
                }
            } catch (Exception ex) {
                System.out.println(ex.toString());
            }

            DebugOutput.printl("<-");
            return null;
        }

        @Override protected void succeeded(Object result) {
            Logger.printBlocked("Finished");
            Logger.setBlocked(false);
        }
    }

    @Action
    public Task connectNetwork() { return new ConnectNetworkTask(getApplication()); }

    private class ConnectNetworkTask extends org.jdesktop.application.Task<Object, Void> {
        ConnectNetworkTask(org.jdesktop.application.Application app) {
            // Runs on the EDT.  Copy GUI state that
            // doInBackground() depends on from parameters
            // to ConnectNetworkTask fields, here.
            super(app);
            
        }
        @Override protected Object doInBackground() {
            // Your Task's code here.  This method runs
            // on a background thread, so don't reference
            // the Swing GUI from here.

            DebugOutput.printl("->");
            jComboBoxBoxinfo.removeAllItems();
            boxInfos = new valerie.tools.BoxInfoParser().parse(new valerie.tools.Network().sendBroadcast());

            if (boxInfos != null) {
            selectedBoxInfo = 0;
            for (int i = 0; i < boxInfos.length; i++) {
                String vInfo = boxInfos[i].toShortString();
                jComboBoxBoxinfo.addItem (vInfo);
            }
            jComboBoxBoxinfo.setSelectedIndex(selectedBoxInfo);
            }

            DebugOutput.printl("<-");

            return null;
        }
        @Override protected void succeeded(Object result) {
            // Runs on the EDT.  Update the GUI based on
            // the result computed by doInBackground().
        }
    }

    @Action
    public Task syncFilelist() { return new SyncFilelistTask(getApplication()); }

    private class SyncFilelistTask extends org.jdesktop.application.Task<Object, Void> {

        SyncFilelistTask(org.jdesktop.application.Application app) {
            // Runs on the EDT.  Copy GUI state that
            // doInBackground() depends on from parameters
            // to SyncFilelistTask fields, here.
            super(app);
        }

        @Override
        protected Object doInBackground() {
            if(boxInfos == null)
                return null;

            Logger.setBlocked(true);
            Logger.printBlocked("Syncing Filelist");

            Logger.setProgress(0);

            searchMovies();
            searchSeries();

            //Delete the content of the database an readd everthing
            /*MediaInfo[] movies = database.getMediaInfo();
            database.clear();
            for (MediaInfo info : movies) {
                if(!(info.isArchiv && info.Ignoring))
                    database.addMediaInfo(info);
            }*/

            //Walk through the databasse and delete all failed entries
            MediaInfo[] movies = database.getMediaInfo();
            for (MediaInfo info : movies) {
                if(info.isArchiv && info.Ignoring)
                    database.deleteMediaInfo(info.ID);
            }

            Logger.printBlocked("Finished");
            Logger.setBlocked(false);
            Logger.setProgress(0);

            return null;  // return your result
        }

        @Override
        protected void succeeded(Object result) {

            updateTables();

            //Force Selection of Row "unspecified" and Force refresh
            if(jTableSeries.getRowCount() > 1)
                jTableSeries.setRowSelectionInterval(1, 1);
            jTableSeriesMouseClicked(null);
        }
        private ArrayList<String[]> getReplacements(){
        	ArrayList<String[]> replacements=new ArrayList<String[]>();
        	
        	replacements.add(new String[]{"[.]", " "});
        	replacements.add(new String[]{"_", " "});
        	replacements.add(new String[]{"-", " "});
        	replacements.add(new String[]{"tt\\d{7}", ""});
        	replacements.add(new String[]{"(\\b(vob|dth|vc1|ac3d|dl|extcut|mkv|nhd|576p|720p|1080p|1080i|dircut|directors cut|dvdrip|dvdscreener|dvdscr|avchd|wmv|ntsc|pal|mpeg|dsr|hd|r5|dvd|dvdr|dvd5|dvd9|bd5|bd9|dts|ac3|bluray|blu-ray|hdtv|pdtv|stv|hddvd|xvid|divx|x264|dxva|m2ts|(?-i)FESTIVAL|LIMITED|WS|FS|PROPER|REPACK|RERIP|REAL|RETAIL|EXTENDED|REMASTERED|UNRATED|CHRONO|THEATRICAL|DC|SE|UNCUT|INTERNAL|DUBBED|SUBBED)\\b([-].+?$)?)", ""});
        	BufferedReader frMovie;
			try {
				frMovie = new BufferedReader(new FileReader("replacements.txt"));
	            String line;
	            while ((line = frMovie.readLine()) != null) {
	            		String[] parts = line.split("=");
	            		replacements.add(new String[]{parts[0], parts[1]});
				}
			} catch (Exception e) {
				return replacements;
			}
			return replacements;
        }
        private void searchMovies() {
            String[] paths = new valerie.tools.Properties().getPropertyString("PATHS_MOVIES").split("\\|");
            ArrayList<String[]> replacements=getReplacements();
            for (int row = 0; row < paths.length; row++) {
                String filterString = "";
                String filter = new valerie.tools.Properties().getPropertyString("FILTER_MOVIES");
                String[] filters = filter.split("\\|");
                if(filters.length > 0)
                    filterString += " -name \"*." + filters[0] + "\"";

                for(int i = 1; i < filters.length; i++)
                    filterString += " -o -name \"*." + filters[i] + "\"";

                String[] entries = new valerie.tools.Network().sendCMD(boxInfos[selectedBoxInfo].IpAddress, "find \"" + paths[row] + "\"" + filterString + " -type f\n");

                for (int i = 0; i < entries.length; i++) {
                    Float progress = (float) i * 100;
                    progress /= entries.length;

                    Logger.setProgress(progress.intValue());

                    MediaInfo movie = new MediaInfo(entries[i]);

                    Pattern pFileFilter = Pattern.compile(".*(" + new valerie.tools.Properties().getPropertyString("FILTER_MOVIES") + ")$");
                    Matcher mFileFilter = pFileFilter.matcher(movie.Filename);
                    if (!mFileFilter.matches()) {
                        continue;
                    }

                    movie.isMovie = true;

                    Logger.print(movie.Filename + " : Parsing");

                    //Check if we already have this Movie in our Archiv!
                    //if so we dont need to extra inject it.
                    MediaInfo archiveEntry = null;
                    if ((archiveEntry = database.getMediaInfoByPath(movie.Path)) != null) {
                        if (archiveEntry.isArchiv) {
                            archiveEntry.Ignoring = false;
                            continue;
                        } else {
                            //this means that the file is a duplicate, what to do with that knowledge ?
                            continue;
                        }
                    }

                    //FileFilter
                    Pattern p = Pattern.compile("tt\\d{7}");
                    Matcher m = p.matcher(movie.Filename);
                    if (m.find()) {
                        System.out.printf("Imdb found: %d", Integer.valueOf(m.group()));
                    }

                    String filtered = movie.Filename.toLowerCase();
                    for (int iter = 0; iter < replacements.size(); iter++) {
                        filtered = filtered.replaceAll(replacements.get(iter)[0].toLowerCase(), replacements.get(iter)[1]);
                    }

                    filtered = filtered.trim();
                    filtered = filtered.replaceAll("\\s+", " ");

                    String[] parts = filtered.split(" ");
                    for (int possibleYearPosition = 0; possibleYearPosition < 3 && possibleYearPosition < parts.length; possibleYearPosition++) {
                        if (parts[parts.length - 1 - possibleYearPosition].matches("\\d{4}")) {
                            System.out.printf("Year found: %s", parts[parts.length - 1 - possibleYearPosition]);
                            movie.Year = Integer.valueOf(parts[parts.length - 1 - possibleYearPosition]);
                            filtered = filtered.substring(0, filtered.length() - 5);

                            break;
                        }
                    }

                    filtered = filtered.trim();

                    //Idee bei grossklein wechsel leerzeichen einfügen, auch bei buchstabe auf zahlen wechsel
                    for (int i2 = 0; i2 + 1 < filtered.length(); i2++) {
                        String p1 = filtered.substring(i2, i2 + 1);
                        String p2 = filtered.substring(i2 + 1, i2 + 2);

                        if ((p1.matches("[a-zA-Z]") && p2.matches("\\d")) ||
                                (p1.matches("\\d") && p2.matches("[a-zA-Z]"))) {
                            filtered = filtered.substring(0, i2 + 1) + " " + filtered.substring(i2 + 1, filtered.length());
                        }
                    }

                    //Idee alles was nach dem Erscheinungsjahr kommt wegwerfen, mögliche Fehlerquelle wenn bestandteil des Filmes ist.
                    if (movie.Year > 1950 && movie.Year < 2020) {
                        filtered = filtered.split(String.valueOf(movie.Year))[0];
                    }

                    //Sometimes the release groups insert their name in front of the title, so letzs check if the frist word contains a '-'
                    String firstWord = "";
                    String[] spaceSplit = filtered.split(" ", 2);
                    if (spaceSplit.length == 2) {
                        firstWord = spaceSplit[0];
                    } else {
                        firstWord = filtered;
                    }

                    String[] minusSplit = firstWord.split("-", 2);
                    if (minusSplit.length == 2) {
                        filtered = minusSplit[1] + (spaceSplit.length == 2 ? " " + spaceSplit[1] : "");
                    }

                    movie.SearchString = filtered;

                    //If parsing of Searchstring failed, set parameters so it is highlighted for the user
                    if(movie.SearchString.length() > 0) {
                        movie.Ignoring = false;
                        movie.needsUpdate = true;
                    } else {
                        movie.Ignoring = true;
                        movie.needsUpdate = false;
                    }

                    movie.DataProvider = new valerie.provider.Imdb();
                    movie.ArtProvider = new valerie.provider.theMovieDb();

                    database.addMediaInfo(movie);

                    Logger.print(movie.Filename + " : Using \"" + movie.SearchString + "\" to get title");
                }
            }
        }

        private void searchSeries() {
            String[] paths = new valerie.tools.Properties().getPropertyString("PATHS_SERIES").split("\\|");
            ArrayList<String[]> replacements=getReplacements();
            for (int row = 0; row < paths.length; row++) {
                String filterString = "";
                String filter = new valerie.tools.Properties().getPropertyString("FILTER_SERIES");
                String[] filters = filter.split("\\|");
                if(filters.length > 0)
                    filterString += " -name \"*." + filters[0] + "\"";

                for(int i = 1; i < filters.length; i++)
                    filterString += " -o -name \"*." + filters[i] + "\"";

                String[] entries = new valerie.tools.Network().sendCMD(boxInfos[selectedBoxInfo].IpAddress, "find \"" + paths[row] + "\"" + filterString + " -type f\n");

                //String[] entries = new valerie.tools.Network().sendCMD(boxInfos[selectedBoxInfo].IpAddress, "find \"" + paths[row] + "\" -type f\n");

                for (int i = 0; i < entries.length; i++) {
                    Float progress = (float) i * 100;
                    progress /= entries.length;

                    Logger.setProgress(progress.intValue());

                    MediaInfo movie = new MediaInfo(entries[i]);

                    //FileFilter
                    Pattern pFileFilter = Pattern.compile(".*(" + new valerie.tools.Properties().getPropertyString("FILTER_SERIES") + ")$");
                    Matcher mFileFilter = pFileFilter.matcher(movie.Filename);
                    if (!mFileFilter.matches()) {
                        continue;
                    }

                    movie.isEpisode = true;

                    Logger.print(movie.Filename + " : Parsing");

                    //Check if we already have this Movie in our Archiv!
                    //if so we dont need to extra inject it.
                    MediaInfo archiveEntry = null;
                    if ((archiveEntry = database.getMediaInfoByPath(movie.Path)) != null) {
                        if (archiveEntry.isArchiv) {
                            archiveEntry.Ignoring = false;
                            continue;
                        } else {
                            //this means that the file is a duplicate, what to do with that knowledge ?
                            continue;
                        }
                    }


                    Pattern p = Pattern.compile("tt\\d{7}");
                    Matcher m = p.matcher(movie.Filename);
                    if (m.find()) {
                        System.out.printf("Imdb found: %d", Integer.valueOf(m.group()));
                    }

                    String filtered = movie.Filename.toLowerCase();
                    for (int iter = 0; iter < replacements.size(); iter++) {
                        filtered = filtered.replaceAll(replacements.get(iter)[0].toLowerCase(), replacements.get(iter)[1]);
                    }

                    filtered = filtered.trim();
                    filtered = filtered.replaceAll("\\s+", " ");

                    //^.*?\\?(?<series>[^\\$]+?)(?:s(?<season>[0-3]?\d)\s?ep?(?<episode>\d\d)|(?<season>(?:[0-1]\d|(?<!\d)\d))x?(?<episode>\d\d))(?!\d)(?:[ .-]?(?:s\k<season>e?(?<episode2>\d{2}(?!\d))|\k<season>x?(?<episode2>\d{2}(?!\d))|(?<episode2>\d\d(?!\d))|E(?<episode2>\d\d))|)[ -.]*(?<title>(?![^\\]*?sample)[^\\]*?[^\\]*?)\.(?<ext>[^.]*)$
                    //^(?<series>[^\\$]+)\\[^\\$]*?(?:s(?<season>[0-1]?\d)ep?(?<episode>\d\d)|(?<season>(?:[0-1]\d|(?<!\d)\d))x?(?<episode>\d\d))(?!\d)(?:[ .-]?(?:s\k<season>e?(?<episode2>\d{2}(?!\d))|\k<season>x?(?<episode2>\d{2}(?!\d))|(?<episode2>\d\d(?!\d))|E(?<episode2>\d\d))|)[ -.]*(?<title>(?!.*sample)[^\\]*?[^\\]*?)\.(?<ext>[^.]*)$
                    //(?<series>[^\\\[]*) - \[(?<season>[0-9]{1,2})x(?<episode>[0-9\W]+)\](( |)(-( |)|))(?<title>(?![^\\]*?sample)[^$]*?)\.(?<ext>[^.]*)
                    //(?<series>[^\\$]*) - season (?<season>[0-9]{1,2}) - (?<title>(?![^\\]*?sample)[^$]*?)\.(?<ext>[^.]*)
                    //<series> - <season>x<episode> - <title>.<ext>
                    //<series>\Season <season>\Episode <episode> - <title>.<ext>
                    //<series>\<season>x<episode> - <title>.<ext>

                    /////////////////////////////////

                    String SeriesName = filtered.replaceAll(" s\\d+e\\d+.*", "");
                    SeriesName = SeriesName.replaceAll(" \\d+x\\d+.*", "");

                    //Sometimes the release groups insert their name in front of the title, so letzs check if the frist word contains a '-'
                    String firstWord = "";
                    String[] spaceSplit = SeriesName.split(" ", 2);
                    if (spaceSplit.length == 2) {
                        firstWord = spaceSplit[0];
                    } else {
                        firstWord = SeriesName;
                    }

                    String[] minusSplit = firstWord.split("-", 2);
                    if (minusSplit.length == 2) {
                        SeriesName = minusSplit[1] + (spaceSplit.length == 2 ? " " + spaceSplit[1] : "");
                    }

                    {
                        Pattern pSeasonEpisode = Pattern.compile(" s\\d+e\\d+");
                        Matcher mSeasonEpisode = pSeasonEpisode.matcher(filtered);
                        if (mSeasonEpisode.find()) {
                            String sSeasonEpisode = mSeasonEpisode.group().trim();

                            Matcher mSeason = Pattern.compile("s\\d+").matcher(sSeasonEpisode);
                            mSeason.find();
                            movie.Season = Integer.valueOf(mSeason.group().substring(1));

                            Matcher mEpisode = Pattern.compile("e\\d+").matcher(sSeasonEpisode);
                            mEpisode.find();
                            movie.Episode = Integer.valueOf(mEpisode.group().substring(1));
                        }
                    }

                    if (movie.Season == 0 && movie.Episode == 0) {
                        Pattern pSeasonEpisode = Pattern.compile(" \\d+x\\d+");
                        Matcher mSeasonEpisode = pSeasonEpisode.matcher(filtered);
                        if (mSeasonEpisode.find()) {
                            String sSeasonEpisode = mSeasonEpisode.group().trim();

                            Matcher mSeason = Pattern.compile("\\d+x").matcher(sSeasonEpisode);
                            if (mSeason.find()) {
                                movie.Season = Integer.valueOf(mSeason.group().substring(0, mSeason.group().length() - 1));
                            }

                            Matcher mEpisode = Pattern.compile("x\\d+").matcher(sSeasonEpisode);
                            if (mEpisode.find()) {
                                movie.Episode = Integer.valueOf(mEpisode.group().substring(1));
                            }
                        }
                    }

                    //Sometimes the Season and Episode info is like this 812 for Season: 8 Episode: 12
                    if (movie.Season == 0 && movie.Episode == 0) {
                        String[] sSeasonEpisodeA = SeriesName.split(" ");
                        SeriesName = "";
                        for (int iteratorSeasonEpisodeA = 0; iteratorSeasonEpisodeA < sSeasonEpisodeA.length; iteratorSeasonEpisodeA++) {
                            String sSeasonEpisode = sSeasonEpisodeA[iteratorSeasonEpisodeA];

                            Pattern pSeasonEpisode = Pattern.compile("\\d+");
                            Matcher mSeasonEpisode = pSeasonEpisode.matcher(sSeasonEpisode);
                            if (mSeasonEpisode.matches()) {
                                int iSeasonEpisode = Integer.valueOf(mSeasonEpisode.group());
                                if (iSeasonEpisode > 100 && iSeasonEpisode < 2400) {
                                    movie.Season = iSeasonEpisode / 100;
                                    movie.Episode = iSeasonEpisode % 100;

                                    break;
                                }
                            } else {
                                SeriesName += sSeasonEpisode + " ";
                            }
                        }
                    }

                    movie.SearchString = SeriesName.trim();

                    Logger.print(movie.Filename + " : Using \"" + movie.SearchString + "\" to get title");

                    if(movie.SearchString.length() > 0) {
                        movie.Ignoring = false;
                        movie.needsUpdate = true;
                    } else {
                        movie.Ignoring = true;
                        movie.needsUpdate = false;
                    }

                    movie.DataProvider = new valerie.provider.theTvDb();
                    movie.ArtProvider = new valerie.provider.theTvDb();

                    database.addMediaInfo(movie);
                }
            }
        }
    }

    @Action
    public Task parseFilelist() { return new ParseFilelistTask(getApplication()); }

    private class ParseFilelistTask extends org.jdesktop.application.Task<Object, Void> {

        ParseFilelistTask(org.jdesktop.application.Application app) {
            super(app);
        }

        @Override
        protected Object doInBackground() {

            Logger.setBlocked(true);
            Logger.printBlocked("Parse Filelist");
            Logger.setProgress(0);

            getMediaInfo();

            //Redraw Menu Tables
            updateTables();

            //Save to txt
            saveTables();

            Logger.printBlocked("Finished");
            Logger.setBlocked(false);
            Logger.setProgress(0);

            return null;
        }

        @Override
        protected void succeeded(Object result) {
            //Force Selection of Row "unspecified" and Force refresh
            if(jTableSeries.getRowCount() > 1)
                jTableSeries.setRowSelectionInterval(1, 1);
            jTableSeriesMouseClicked(null);
        }

        private void getMediaInfo() {

            //TODO: How can we do this in parallel ?

            MediaInfo[] movies = database.getMediaInfo();
            for (int i = 0; i < movies.length; i++) {
                Float progress = (float) i * 100;
                progress /= movies.length;
                Logger.setProgress(progress.intValue());

                MediaInfo movie = movies[i];

                if (movie.needsUpdate) {

                    Logger.print(movie.Filename + " : Using \"" + movie.SearchString + "\" to get title");

                    if (movie.isMovie) {
                        getMediaInfoMovie(movie);
                    } else if (movie.isEpisode || movie.isSeries) {
                        getMediaInfoSeries(movie);
                    }

                    Logger.print(movie.Filename + " : Got title \"" + movie.Title + "\".");
                }
            }

            //TODO: We have to recheck if alle series got episodes, else delete unneeded series
            MediaInfo[] series = database.getMediaInfoSeries();
            for(MediaInfo info : series) {
                MediaInfo[] episodes = database.getMediaInfoEpisodes(info.TheTvDb);
                if(episodes.length == 0)
                    database.deleteMediaInfo(info.ID);
            }
        }

        private void getMediaInfoMovie(MediaInfo movie) {

            

            //if we have no searchstring, than the movie was importet from the archive and we dont need to reparse
            if (movie.needsUpdate) {
                movie.getDataByTitle();
            }

            if (movie.Title.length() > 0) {
                movie.Ignoring = false;
                movie.needsUpdate = false;
            } else {
                movie.Ignoring = true;
                movie.needsUpdate = true;
            }

            //Dont add as we dont delete the datebase anylonger
            //database.addMediaInfo(movie);
        }

        private void getMediaInfoSeries(MediaInfo movie) {

            //Ignore all series and only check episodes
            if (!movie.isSeries && movie.needsUpdate) {
                MediaInfo Series;

                if (database.getMediaInfoForSeries(movie.SearchString) == null) {
                    Series = movie.clone();
                    Series.isSeries = true;
                    Series.isEpisode = false;
                    Series.getDataByTitle();
                    Series.Filename = "";
                    Series.Path = "";

                    if (Series.Title.length() > 0) {
                        Series.Ignoring = false;
                        Series.needsUpdate = false;

                        //check if this is a duplicate
                        MediaInfo duplicate = database.getMediaInfoForSeries(Series.TheTvDb);
                        if (duplicate == null) {
                            database.addMediaInfo(Series);
                        } else {
                            if(duplicate.SearchString.length() > 0)
                                duplicate.SearchString = duplicate.SearchString.substring(0, duplicate.SearchString.length()) + "|" + movie.SearchString + ")";
                            else
                                duplicate.SearchString =  "(" + movie.SearchString + ")";
                        }
                    }
                } else {
                    Series = database.getMediaInfoForSeries(movie.SearchString);
                }

                //boolean beforeDontDeletePolicity = false;

                //if(beforeDontDeletePolicity)
                //    MediaInfo Episode = null;

                if (Series != null) {
                    /*if(beforeDontDeletePolicity) {
                    Episode = Series.clone();
                    Episode.isSeries = false;
                    Episode.isEpisode = true;
                    Episode.Filename = movie.Filename;
                    Episode.SearchString = movie.SearchString;
                    Episode.Path = movie.Path;
                    Episode.Season = movie.Season;
                    Episode.Episode = movie.Episode;
                    }*/

                    movie.Title = Series.Title;
                    movie.Year = Series.Year;
                    movie.Imdb = Series.Imdb;
                    movie.Poster = Series.Poster;
                    movie.Backdrop = Series.Backdrop;
                    movie.Banner = Series.Banner;
                    movie.Runtime = Series.Runtime;
                    movie.Plot = Series.Plot;
                    movie.Directors = Series.Directors;
                    movie.Writers = Series.Writers;
                    movie.Genres = Series.Genres;
                    movie.Tag = Series.Tag;
                    movie.Popularity = Series.Popularity;
                    movie.TheTvDb = Series.TheTvDb;


                } else {
                    System.out.println("Does this happen ???");
                    return;
                }

                 /*if(beforeDontDeletePolicity) {
                Episode.getDataByTitle();

                Episode.ArtProvider = Episode.DataProvider;

                if (Episode.Title.length() > 0) {
                    Episode.Ignoring = false;
                    Episode.needsUpdate = false;
                }

                
                database.addMediaInfo(Episode);*/

                movie.getDataByTitle();

                if (movie.Title.length() > 0) {
                    movie.Ignoring = false;
                    movie.needsUpdate = false;
                }

            } else {
                if (movie.Title.length() > 0) {
                    movie.Ignoring = false;
                    movie.needsUpdate = false;
                }
            }
        }
    }

    @Action
    public Task getArt() {
        return new GetArtTask(getApplication());
    }

    private class GetArtTask extends org.jdesktop.application.Task<Object, Void> {

        GetArtTask(org.jdesktop.application.Application app) {
            // Runs on the EDT.  Copy GUI state that
            // doInBackground() depends on from parameters
            // to GetArtTask fields, here.
            super(app);
        }

        @Override
        protected Object doInBackground() {

            Logger.setBlocked(true);
            Logger.printBlocked("Getting Arts");
            Logger.setProgress(0);

            MediaInfo[] movies = database.getMediaInfo();

            int moviesSize = movies.length;
            int moviesIterator = 0;

            for (MediaInfo movie : movies) {
                Logger.setProgress((moviesIterator++ * 100) / moviesSize);
                if (movie.isMovie) {
                    getMediaArtMovie(movie);
                }
                if (movie.isSeries) {
                    getMediaArtSeries(movie);
                }
            }

            Logger.printBlocked("Finished");
            Logger.setBlocked(false);
            Logger.setProgress(0);

            return null;  // return your result
        }

        @Override
        protected void succeeded(Object result) {
            // Runs on the EDT.  Update the GUI based on
            // the result computed by doInBackground().
        }

        private void getMediaArtMovie(MediaInfo movie) {
            Logger.print(movie.Filename + " : Got title \"" + movie.Title + "\". Downloading posters");

            movie.ArtProvider.getArtById(movie);

            if (movie.Poster.length() > 0) {
                File checkIfFileAlreadyExists = new File("download/tt" + movie.Imdb + "_poster.jpg");
                if (checkIfFileAlreadyExists != null && checkIfFileAlreadyExists.exists()) {
                } else {
                    new valerie.tools.webgrabber().getFile(movie.Poster, "download/tt" + movie.Imdb + "_poster.jpg");
                }

                if (checkIfFileAlreadyExists != null && checkIfFileAlreadyExists.exists()) {
                    File checkIfFilePNGalreadyExists = new File("converted/tt" + movie.Imdb + "_poster.png");
                    if (checkIfFilePNGalreadyExists == null || !checkIfFilePNGalreadyExists.exists()) {
                        try {
                            BufferedImage image = ImageIO.read(checkIfFileAlreadyExists);
                            Image scaled = image.getScaledInstance(156, 214, Image.SCALE_SMOOTH);

                            BufferedImage bi = new BufferedImage(
                                    156,
                                    214,
                                    BufferedImage.TYPE_INT_RGB);
                            Graphics g = bi.getGraphics();
                            g.drawImage(scaled, 0, 0, null);

                            ImageIO.write(bi, "png", checkIfFilePNGalreadyExists);

                            new pngquant().exec("converted\\tt" + movie.Imdb + "_poster.png", "converted\\tt" + movie.Imdb + "_poster.png");

                        } catch (Exception ex) {
                            System.out.println(ex.toString());
                        }
                    }
                }
            }

            Logger.print(movie.Filename + " : Got title \"" + movie.Title + "\". Downloading and Converting backdrops");

            if (movie.Backdrop.length() > 0) {
                File downloaded = new File("download/tt" + movie.Imdb + "_backdrop.jpg");

                //Check if already downloaded
                if (downloaded == null || !downloaded.exists()) {
                    new valerie.tools.webgrabber().getFile(movie.Backdrop, "download/tt" + movie.Imdb + "_backdrop.jpg");
                }


                if (downloaded != null && downloaded.exists()) {
                    File converted = new File("converted/tt" + movie.Imdb + "_backdrop.m1v");

                    //check if file already converted
                    if (converted == null || !converted.exists()) {
                        new mencoder().exec("download/tt" + movie.Imdb + "_backdrop.jpg", "converted/tt" + movie.Imdb + "_backdrop.m1v");
                    }
                }
            }

            database.addMediaInfo(movie);
        }

        private void getMediaArtSeries(MediaInfo movie) {
            Logger.print(movie.Filename + " : Got title \"" + movie.Title + "\". Downloading posters");

            movie.ArtProvider.getArtById(movie);

            if (movie.Poster.length() > 0) {
                File checkIfFileAlreadyExists = new File("download/" + movie.TheTvDb + "_poster.jpg");
                if (checkIfFileAlreadyExists != null && checkIfFileAlreadyExists.exists()) {
                } else {
                    new valerie.tools.webgrabber().getFile(movie.Poster, "download/" + movie.TheTvDb + "_poster.jpg");
                }

                if (checkIfFileAlreadyExists != null && checkIfFileAlreadyExists.exists()) {
                    File checkIfFilePNGalreadyExists = new File("converted/" + movie.TheTvDb + "_poster.png");
                    if (checkIfFilePNGalreadyExists == null || !checkIfFilePNGalreadyExists.exists()) {
                        try {
                            BufferedImage image = ImageIO.read(checkIfFileAlreadyExists);
                            Image scaled = image.getScaledInstance(156, 214, Image.SCALE_SMOOTH);

                            BufferedImage bi = new BufferedImage(
                                    156,
                                    214,
                                    BufferedImage.TYPE_INT_RGB);
                            Graphics g = bi.getGraphics();
                            g.drawImage(scaled, 0, 0, null);

                            ImageIO.write(bi, "png", checkIfFilePNGalreadyExists);

                            new pngquant().exec("converted\\" + movie.TheTvDb + "_poster.png", "converted\\" + movie.TheTvDb + "_poster.png");

                        } catch (Exception ex) {
                            System.out.println(ex.toString());
                        }
                    }
                }
            }

            Logger.print(movie.Filename + " : Got title \"" + movie.Title + "\". Downloading and Converting backdrops");

            if (movie.Backdrop.length() > 0) {
                File checkIfFileJPEGAlreadyExists = new File("download/" + movie.TheTvDb + "_backdrop.jpg");
                if (checkIfFileJPEGAlreadyExists != null && checkIfFileJPEGAlreadyExists.exists()) {
                } else {
                    new valerie.tools.webgrabber().getFile(movie.Backdrop, "download/" + movie.TheTvDb + "_backdrop.jpg");
                }

                if (checkIfFileJPEGAlreadyExists != null && checkIfFileJPEGAlreadyExists.exists()) {
                    File checkIfFileMVIlreadyExists = new File("converted/" + movie.TheTvDb + "_backdrop.m1v");
                    if (checkIfFileMVIlreadyExists == null || !checkIfFileMVIlreadyExists.exists()) {
                        new mencoder().exec("download/" + movie.TheTvDb + "_backdrop.jpg", "converted/" + movie.TheTvDb + "_backdrop.m1v");
                    }
                }
            }

            database.addMediaInfo(movie);
        }
    }

    @Action
    public Task uploadFiles() {
        return new UploadFilesTask(getApplication());
    }

    private class UploadFilesTask extends org.jdesktop.application.Task<Object, Void> {

        UploadFilesTask(org.jdesktop.application.Application app) {
            // Runs on the EDT.  Copy GUI state that
            // doInBackground() depends on from parameters
            // to UploadFilesTask fields, here.
            super(app);
        }

        @Override
        protected Object doInBackground() {
            // Your Task's code here.  This method runs
            // on a background thread, so don't reference
            // the Swing GUI from here.

            Logger.setBlocked(true);
            Logger.printBlocked("Uploading");

            new valerie.tools.Network().sendFile(boxInfos[selectedBoxInfo].IpAddress, "db/moviedb.txt", "/hdd/valerie");
            new valerie.tools.Network().sendFile(boxInfos[selectedBoxInfo].IpAddress, "db/seriesdb.txt", "/hdd/valerie");

            File episodes = new File("db/episodes");
            if (!(episodes.exists())) {
                Logger.print("No such Folder \"db/episodes\"!");
            } else {
                String[] entries = episodes.list();

                for (int i = 0; i < entries.length; ++i) {
                    new valerie.tools.Network().sendFile(boxInfos[selectedBoxInfo].IpAddress, "db/episodes/" + entries[i], "/hdd/valerie/episodes");
                }
            }

            File folder = new File("converted");
            if (!(folder.exists())) {
                Logger.print("No such Folder \"converted\"!");
            } else {
                String[] entries = folder.list();

                for (int i = 0; i < entries.length; ++i) {

                    //Only upload arts if really needed so checbefore

                    String[] vLine = new valerie.tools.Network().sendCMD(boxInfos[selectedBoxInfo].IpAddress,
                            "ls /hdd/valerie/media/" + entries[i]);

                    if(vLine.length == 0 || !vLine[0].equals("/hdd/valerie/media/" + entries[i]))
                        new valerie.tools.Network().sendFile(boxInfos[selectedBoxInfo].IpAddress, "converted/" + entries[i], "/hdd/valerie/media");
                }
            }



            Logger.printBlocked("Finished");
            Logger.setBlocked(false);

            return null;  // return your result
        }

        @Override
        protected void succeeded(Object result) {
            // Runs on the EDT.  Update the GUI based on
            // the result computed by doInBackground().
        }
    }

    @Action
    public void jMenuItemEditSettingsClicked() {
        JDialog settingsDialog;
        {
            JFrame mainFrame = ValerieApp.getApplication().getMainFrame();
            settingsDialog = new Settings(mainFrame, true);
            settingsDialog.setLocationRelativeTo(mainFrame);
        }
        ValerieApp.getApplication().show(settingsDialog);
    }
    private valerie.tools.BoxInfo[] boxInfos;
    private int selectedBoxInfo = -1;
    // Variables declaration - do not modify//GEN-BEGIN:variables
    private javax.swing.JLabel animatedBar;
    private javax.swing.JLabel descLabel;
    private javax.swing.JButton jButtonArt;
    private javax.swing.JButton jButtonConnect;
    private javax.swing.JButton jButtonParse;
    private javax.swing.JButton jButtonSync;
    private javax.swing.JButton jButtonUpload;
    private javax.swing.JComboBox jComboBoxBoxinfo;
    private javax.swing.JLabel jLabelBackdrop;
    private javax.swing.JLabel jLabelPoster;
    private javax.swing.JMenu jMenu1;
    private javax.swing.JMenuItem jMenuItem1;
    private javax.swing.JPanel jPanel1;
    private javax.swing.JPanel jPanel2;
    private javax.swing.JPanel jPanelMovies;
    private javax.swing.JPanel jPanelSeries;
    private javax.swing.JPanel jPanelThumbs;
    private javax.swing.JScrollPane jScrollPane1;
    private javax.swing.JScrollPane jScrollPane3;
    private javax.swing.JScrollPane jScrollPane5;
    private javax.swing.JScrollPane jScrollPane6;
    private javax.swing.JToolBar.Separator jSeparator1;
    private javax.swing.JToolBar.Separator jSeparator2;
    private javax.swing.JToolBar.Separator jSeparator3;
    private javax.swing.JToolBar.Separator jSeparator4;
    private javax.swing.JSplitPane jSplitPane1;
    private javax.swing.JSplitPane jSplitPane2;
    private javax.swing.JTabbedPane jTabbedPane;
    private javax.swing.JTable jTableFilelist;
    private javax.swing.JTable jTableFilelistEpisodes;
    private javax.swing.JTable jTableSeries;
    private javax.swing.JTextArea jTextAreaDescription;
    private javax.swing.JToolBar jToolBar1;
    private javax.swing.JPanel mainPanel;
    private javax.swing.JMenuBar menuBar;
    private javax.swing.JProgressBar progressBar;
    private javax.swing.JLabel statusAnimationLabel;
    private javax.swing.JLabel statusMessageLabel;
    private javax.swing.JPanel statusPanel;
    private javax.swing.JFrame statusPopup;
    // End of variables declaration//GEN-END:variables
    private final Timer messageTimer;
    private final Timer busyIconTimer;
    private final Icon idleIcon;
    private final Icon[] busyIcons = new Icon[15];
    private int busyIconIndex = 0;
    private JDialog aboutBox;
}
