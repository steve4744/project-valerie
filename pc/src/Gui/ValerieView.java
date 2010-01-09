/*
 * ValerieView.java
 */
package Gui;

import valerie.*;
import java.awt.Color;
import java.awt.Component;
import java.awt.Container;

import org.jdesktop.application.Action;
import org.jdesktop.application.ResourceMap;
import org.jdesktop.application.SingleFrameApplication;
import org.jdesktop.application.FrameView;
import org.jdesktop.application.TaskMonitor;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.FocusEvent;
import java.awt.event.WindowEvent;
import java.awt.event.WindowListener;
import java.awt.event.WindowStateListener;
import java.io.File;
import java.io.FileWriter;
import java.io.Writer;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.List;
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
import valerie.tools.BoxInfo;
import valerie.tools.DebugOutput;

/**
 * The application's main frame.
 */
public class ValerieView extends FrameView implements WindowStateListener {

    class UIOutputHandler extends OutputHandler {
        UIOutputHandler()
        {
            super();

            //popup = new StatusPopup(null, true);
        }

        @Override
        public void print(String s) {
            statusMessageLabel.setText(s);
        }

        @Override
        public void printBlocked(String s) {
            statusMessageLabel.setText(s);
            statusPopup.setTitle(s);
            descLabel.setText(s);
        }

        @Override
        public void setWorking(boolean s) {
            jButtonConnect.setEnabled(!s);
            jButtonSync.setEnabled(!s);
            jButtonParse.setEnabled(!s);
            jButtonArt.setEnabled(!s);
            jButtonUpload.setEnabled(!s);
        }

        @Override
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

        @Override
        public void setProgress(int s) {
            progressBar.setValue(s);
        }
    }

    BackgroundWorker pWorker = null;
    BackgroundWorker.ParentObject pCallback = null;

    protected class Callback implements BackgroundWorker.ParentObject {

        ValerieView pParent;

        Callback(ValerieView parent) {
            pParent = parent;
        }

        public void done(String id) {
            if(id.equals("CONNECT_NETWORK")) {
                notify("UPDATE_BOXINFOS");
            } else if(id.equals("SYNC_FILELIST")) {

                notify("UPDATE_TABLES");

                //Force Selection of Row "unspecified" and Force refresh
                if(jTableSeries.getRowCount() > 1)
                    jTableSeries.setRowSelectionInterval(1, 1);
                jTableSeriesMouseClicked(null);

            } else if(id.equals("PARSE_FILELIST")) {
                done("SYNC_FILELIST");

                pParent.saveTables();
            } else {
                notify(id);
            }
        }

        public void notify(String id) {
            if(id.equals("UPDATE_BOXINFOS")) {
                pParent.jComboBoxBoxinfo.removeAllItems();
                BoxInfo[] boxInfos = (BoxInfo[])pWorker.get("BoxInfos");
                if (boxInfos != null) {
                    pWorker.set("SelectedBoxInfo", (int)0);
                    for (int i = 0; i < boxInfos.length; i++) {
                        String vInfo = boxInfos[i].toShortString();
                        jComboBoxBoxinfo.addItem (vInfo);
                    }
                    jComboBoxBoxinfo.setSelectedIndex( 0 );
                } else {
                    pWorker.set("SelectedBoxInfo", (int)-1);
                    jComboBoxBoxinfo.setSelectedIndex( -1 );
                }
            }
            else if(id.equals("UPDATE_TABLES")) {
                pParent.updateTables();
            }

        }
    }

    public ValerieView(SingleFrameApplication app, String[] arguments) {
        super(app);

        pCallback = new Callback(this);

        pWorker = new BackgroundWorker(this.getApplication());

        pWorker.set("CmdArguments", arguments);

        //vArguments = arguments;

        pWorker.doTask( BackgroundWorker.Tasks.CHECK_ARGUMENTS, BackgroundWorker.Mode.NORMAL,
                pCallback, "pre");

        this.getFrame().addWindowStateListener(this);

        class WListener implements WindowListener {
            public void windowDeactivated(WindowEvent e) {
                System.out.print(e);
            }
            public void windowActivated(WindowEvent e) {
                if(firstFocus) {
                    firstFocus = false;

                    pWorker.doTask( BackgroundWorker.Tasks.CHECK_ARGUMENTS, BackgroundWorker.Mode.BACKGROUND,
                        pCallback, "post");
                }
            }
            public void windowIconified(WindowEvent e) { }
            public void windowDeiconified(WindowEvent e) { }
            public void windowClosed(WindowEvent e) { }
            public void windowClosing(WindowEvent e) { }
            public void windowOpened(WindowEvent e) { }
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

                            MediaInfoDB database = (MediaInfoDB)pWorker.get("Database");
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

                            MediaInfoDB database = (MediaInfoDB)pWorker.get("Database");
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
    }

    boolean firstFocus = true;

    public void windowStateChanged(java.awt.event.WindowEvent event)
    {
        if(event.getNewState() == java.awt.event.WindowEvent.WINDOW_OPENED) {
            pWorker.doTask( BackgroundWorker.Tasks.CHECK_ARGUMENTS, BackgroundWorker.Mode.NORMAL,
                pCallback, "post");
        }
    }

    public void focusGained(FocusEvent e) {
        if(firstFocus) {
            firstFocus = false;

            pWorker.doTask( BackgroundWorker.Tasks.CHECK_ARGUMENTS, BackgroundWorker.Mode.NORMAL,
                pCallback, "post");
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
        jMenuItemSettings = new javax.swing.JMenuItem();
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

        jMenuItemSettings.setAction(actionMap.get("jMenuItemEditSettingsClicked")); // NOI18N
        jMenuItemSettings.setText(resourceMap.getString("jMenuItemSettings.text")); // NOI18N
        jMenuItemSettings.setName("jMenuItemSettings"); // NOI18N
        jMenu1.add(jMenuItemSettings);

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

        MediaInfoDB database = (MediaInfoDB)pWorker.get("Database");
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
        MediaInfoDB database = (MediaInfoDB)pWorker.get("Database");
        MediaInfo info = database.getMediaInfoById(id);

        jTextAreaDescription.setText(info.toString());
        ImageIcon poster = new ImageIcon("converted/tt" + info.Imdb + "_poster.png");
        ImageIcon backdrop = new ImageIcon("download/tt" + info.Imdb + "_backdrop.jpg");
        drawPosters(poster, backdrop);
    }//GEN-LAST:event_jTableFilelistKeyPressed

    private void jTableFilelistEpisodesMouseClicked(java.awt.event.MouseEvent evt) {//GEN-FIRST:event_jTableFilelistEpisodesMouseClicked
        int row = jTableFilelistEpisodes.getSelectedRow();
        int id = (Integer) jTableFilelistEpisodes.getValueAt(row, 5);

        MediaInfoDB database = (MediaInfoDB)pWorker.get("Database");
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
        MediaInfoDB database = (MediaInfoDB)pWorker.get("Database");
        MediaInfo info = database.getMediaInfoById(id);

        jTextAreaDescription.setText(info.toString());
        ImageIcon poster = new ImageIcon("converted/" + info.TheTvDb + "_poster.png");
        ImageIcon backdrop = new ImageIcon("download/" + info.TheTvDb + "_backdrop.jpg");
        drawPosters(poster, backdrop);
    }//GEN-LAST:event_jTableFilelistEpisodesKeyPressed

    private void jTableSeriesMouseClicked(java.awt.event.MouseEvent evt) {//GEN-FIRST:event_jTableSeriesMouseClicked
        int row = jTableSeries.getSelectedRow();
        int id = (Integer) jTableSeries.getValueAt(row, 1);

        MediaInfoDB database = (MediaInfoDB)pWorker.get("Database");
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
        MediaInfoDB database = (MediaInfoDB)pWorker.get("Database");
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

        pWorker.set("SelectedBoxInfo", jComboBoxBoxinfo.getSelectedIndex());
        //clear database
        MediaInfoDB database = (MediaInfoDB)pWorker.get("Database");
        database.clear();

        pWorker.doTask(BackgroundWorker.Tasks.LOAD_ARCHIVE, BackgroundWorker.Mode.NORMAL, pCallback, null);
        updateTables();

        DebugOutput.printl("<-");
    }//GEN-LAST:event_jComboBoxBoxinfoItemStateChanged
    

    boolean isUpdating = false;

    public void updateTables() {
        DebugOutput.printl("->");

        MediaInfoDB database = (MediaInfoDB)pWorker.get("Database");
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
        MediaInfoDB database = (MediaInfoDB)pWorker.get("Database");

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

        MediaInfoDB database = (MediaInfoDB)pWorker.get("Database");
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
    public void connectNetwork() {
        pWorker.doTask(BackgroundWorker.Tasks.CONNECT_NETWORK, BackgroundWorker.Mode.BACKGROUND, pCallback, null);
    }

    @Action
    public void syncFilelist() {
        pWorker.doTask(BackgroundWorker.Tasks.SYNC_FILELIST, BackgroundWorker.Mode.BACKGROUND, pCallback, null);
    }

    @Action
    public void parseFilelist() {
        int ParallelTasks = 10;
        for(int i = 0; i < ParallelTasks; i++) {
            ThreadSize ts = new ThreadSize();
            ts.ThreadCount = ParallelTasks;
            ts.ThreadId = i;
            pWorker.doTask(BackgroundWorker.Tasks.PARSE_FILELIST, BackgroundWorker.Mode.BACKGROUND, pCallback, ts);
        }
    }

    @Action
    public void getArt() {
        int ParallelTasks = 10;
        for(int i = 0; i < ParallelTasks; i++) {
            ThreadSize ts = new ThreadSize();
            ts.ThreadCount = ParallelTasks;
            ts.ThreadId = i;
            pWorker.doTask(BackgroundWorker.Tasks.GET_ART, BackgroundWorker.Mode.BACKGROUND, pCallback, ts);
        }
    }

    @Action
    public void uploadFiles() {
        pWorker.doTask(BackgroundWorker.Tasks.UPLOAD_FILES, BackgroundWorker.Mode.BACKGROUND, pCallback, null);
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
    private javax.swing.JMenuItem jMenuItemSettings;
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