/*
 * ValerieView.java
 */
package Gui;

import java.awt.event.MouseEvent;
import java.beans.PropertyChangeEvent;
import org.jdesktop.application.Task;
import org.jdesktop.application.TaskEvent;
import valerie.*;
import java.awt.Color;
import java.awt.Component;
import org.jdesktop.application.Action;
import org.jdesktop.application.ResourceMap;
import org.jdesktop.application.SingleFrameApplication;
import org.jdesktop.application.FrameView;
import org.jdesktop.application.TaskMonitor;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.beans.PropertyChangeListener;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.net.URL;
import java.util.List;
import javax.swing.BorderFactory;
import javax.swing.Timer;
import javax.swing.JComponent;
import javax.swing.JFrame;
import javax.swing.JProgressBar;
import javax.swing.JTable;
import javax.swing.event.TableModelEvent;
import javax.swing.event.TableModelListener;
import javax.swing.table.DefaultTableCellRenderer;
import javax.swing.table.TableCellRenderer;
import javax.swing.table.TableModel;
import valerie.tools.BoxInfo;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import javax.swing.ButtonGroup;
import javax.swing.Icon;
import javax.swing.ImageIcon;
import javax.swing.JComboBox;
import javax.swing.JDialog;
import javax.swing.JLabel;
import javax.swing.JOptionPane;
import javax.swing.JRadioButton;
import javax.swing.table.DefaultTableModel;
import org.jdesktop.application.TaskListener;
import org.jdom.Document;
import valerie.controller.Controller;
import valerie.controller.Notification;
import valerie.tools.DebugOutput;
import valerie.tools.Restart;



/**
 * The application's main frame.
 */
public class ValerieView extends FrameView {
    Controller pController;

    public ValerieView(SingleFrameApplication app, Controller controller, String[] arguments) {
        super(app);

        pController = controller;
        pController.add(new Notification() {

            @Override
            public void init() {
                Type = "DB_REFRESH";
            }

            @Override
            public void callback(Object o) {
                tablesUpdate();
            }
        });

        pController.add(new Notification() {

            @Override
            public void init() {
                Type = "BI_REFRESH";
            }

            @Override
            public void callback(Object o) {
                boxInfosUpdate();
            }
        });
     
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
                    progressBar.setIndeterminate(true);
                } else if ("done".equals(propertyName)) {
                    busyIconTimer.stop();
                    statusAnimationLabel.setIcon(idleIcon);
                    progressBar.setVisible(false);
                    progressBar.setValue(0);
                } else if ("message".equals(propertyName)) {
                    String text = (String) (evt.getNewValue());
                    statusMessageLabel.setText((text == null) ? "" : text);
                    messageTimer.restart();
                } else if ("progress".equals(propertyName)) {
                    int value = (Integer) (evt.getNewValue());
                    progressBar.setVisible(true);
                    progressBar.setIndeterminate(false);
                    progressBar.setValue(value);
                }
            }
        });

        //MY OWN CODE
        //showConsole(false);

        DebugOutput.add(new DebugOutput.OutputHandler() {
            @Override
            public void print(String s) {
                System.out.print(s);
            }
        }
        );

        //.add(new UIOutputHandler());

        class TableChangedMovies implements TableModelListener {

            public void tableChanged(TableModelEvent e) {
                if (e.getType() == TableModelEvent.UPDATE) {
                    if(!isUpdating) {
                        System.out.println(e.getSource());

                        int row = e.getFirstRow();
                        int column = e.getColumn();

                        if (column == 1) {
                            TableModel model = jTableMovies.getModel();
                            int id = ((Integer) model.getValueAt(row, 3)).intValue();
                            String searchstring = ((String) model.getValueAt(row, 1));

                            Database database = (Database)pController.get("Database");
                            MediaInfo toUpdate = database.getMediaInfoById(id);

                            Matcher mImdb = Pattern.compile("tt\\d{4,7}").matcher(searchstring);
                            if (mImdb.find()/*.matches()*/) {
                                toUpdate.ImdbId = searchstring;
                                toUpdate.SearchString = searchstring;
                            } else {
                                toUpdate.ImdbId = toUpdate.ImdbIdNull;
                                toUpdate.SearchString = searchstring;
                            }
                            toUpdate.needsUpdate = true;

                            model.setValueAt(toUpdate.needsUpdate, row, 4);
                        }
                    }
                }
            }
        }
        jTableMovies.getModel().addTableModelListener(new TableChangedMovies());

        class TableChangedEpisodes implements TableModelListener {

            public void tableChanged(TableModelEvent e) {
                if (e.getType() == TableModelEvent.UPDATE) {
                    if(!isUpdating) {
                        //System.out.println(e.getSource());

                        int row = e.getFirstRow();
                        int column = e.getColumn();

                        if (column == 1 || column == 2 || column == 3) {
                            TableModel model = jTableEpisodes.getModel();
                            int id = ((Integer) model.getValueAt(row, 4)).intValue();
                            String searchstring = ((String) model.getValueAt(row, 1));
                            int season = ((Integer) model.getValueAt(row, 2)).intValue();
                            int episode = ((Integer) model.getValueAt(row, 3)).intValue();

                            Database database = (Database)pController.get("Database");
                            MediaInfo toUpdate = database.getMediaInfoById(id);

                            toUpdate.SearchString = searchstring;
                            toUpdate.Season = season;
                            toUpdate.Episode = episode;

                            toUpdate.needsUpdate = true;

                            model.setValueAt(toUpdate.needsUpdate, row, 5);
                        }
                    }
                }
            }
        }
        jTableEpisodes.getModel().addTableModelListener(new TableChangedEpisodes());

        actionNetworkConnect().run();
        jComboBoxBoxinfoItemStateChanged(null);
    }

    boolean firstFocus = true;

    @Action
    public void showAboutBox() {
        if (aboutBox == null) {
            JFrame mainFrame = ValerieApp.getApplication().getMainFrame();
            aboutBox = new ValerieAboutBox(mainFrame);
            aboutBox.setLocationRelativeTo(mainFrame);
        }
        ValerieApp.getApplication().show(aboutBox);

        //jTableTasks.getColumnModel().getColumn(2).setCellRenderer( new ProgressRenderer() );
    }

    class ProgressRenderer extends DefaultTableCellRenderer {
        private final JProgressBar b = new JProgressBar(0, 100);

        public ProgressRenderer() {
            super();
            setOpaque(true);
            b.setBorder(BorderFactory.createEmptyBorder(1,1,1,1));
        }

        @Override
        public Component getTableCellRendererComponent(JTable table, Object value,
                                                        boolean isSelected, boolean hasFocus,
                                                        int row, int column) {
            Integer i = (Integer)value;
            String text = "Done";
            if(i != null) {
                if(i < 0) {
                    text = "Canceled";
                }else if(i < 100) {
                    b.setValue(i);
                    return b;
                }
            } else {
                b.setValue(0);
                return b;
            }

            super.getTableCellRendererComponent(table, text, isSelected, hasFocus, row, column);
            return this;
        }
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
        jButtonSync = new javax.swing.JButton();
        jButtonParse = new javax.swing.JButton();
        jButtonArt = new javax.swing.JButton();
        jSeparator3 = new javax.swing.JToolBar.Separator();
        jButtonDownloadFromBox = new javax.swing.JButton();
        jButtonUploadToBox = new javax.swing.JButton();
        jButtonConnect = new javax.swing.JButton();
        jComboBoxBoxinfo = new javax.swing.JComboBox();
        jSplitPane1 = new javax.swing.JSplitPane();
        jTabbedPane = new javax.swing.JTabbedPane();
        jPanelMovies = new javax.swing.JPanel();
        jScrollPane1 = new javax.swing.JScrollPane();
        jTableMovies = new javax.swing.JTable() {
            public Component prepareRenderer(TableCellRenderer renderer, int rowIndex, int vColIndex) {
                Component c = super.prepareRenderer(renderer, rowIndex, vColIndex);
                if (c instanceof JComponent) {
                    JComponent jc = (JComponent) c;
                    Object jo = getValueAt(rowIndex, vColIndex);
                    if(jo != null) {
                        jc.setToolTipText(String.valueOf(jo));
                    }
                    if(!super.isRowSelected(rowIndex)) {
                        jo = getValueAt(rowIndex, 4);
                        if(jo != null && Boolean.valueOf(jo.toString()) == true) {
                            jc.setBackground(Color.orange);
                        } else {
                            jc.setBackground(null/*Color.white*/);
                        }
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
                    if(jo != null) {
                        jc.setToolTipText(jo.toString());
                    }
                }
                return c;
            }
        }
        ;
        jScrollPane5 = new javax.swing.JScrollPane();
        jTableEpisodes = new javax.swing.JTable() {
            public Component prepareRenderer(TableCellRenderer renderer, int rowIndex, int vColIndex) {
                Component c = super.prepareRenderer(renderer, rowIndex, vColIndex);
                if (c instanceof JComponent) {
                    JComponent jc = (JComponent) c;
                    Object jo = getValueAt(rowIndex, vColIndex);
                    if(jo != null) {
                        jc.setToolTipText(String.valueOf(jo));
                    }
                    if(!super.isRowSelected(rowIndex)) {
                        jo = getValueAt(rowIndex, 5);
                        if(jo != null && Boolean.valueOf(jo.toString()) == true) {
                            jc.setBackground(Color.orange);
                        } else {
                            jc.setBackground(null/*Color.white*/);
                        }
                    }
                }

                return c;
            }
        }
        ;
        jPanelDetails = new javax.swing.JPanel();
        jScrollPane3 = new javax.swing.JScrollPane();
        jTextAreaDescription = new javax.swing.JTextArea();
        jLabelDetailsTitle = new javax.swing.JLabel();
        jLabelDetailsPoster = new javax.swing.JLabel();
        jLabelDetailsBackdrop = new javax.swing.JLabel();
        jLabelDetailsTagline = new javax.swing.JLabel();
        jLabelDetailsPlot = new javax.swing.JLabel();
        jScrollPaneDetailsPlot = new javax.swing.JScrollPane();
        jTextAreaDetailsPlot = new javax.swing.JTextArea();
        jLabelDetailsStar1 = new javax.swing.JLabel();
        jLabelDetailsStar2 = new javax.swing.JLabel();
        jLabelDetailsStar3 = new javax.swing.JLabel();
        jLabelDetailsStar4 = new javax.swing.JLabel();
        jLabelDetailsStar5 = new javax.swing.JLabel();
        jLabelDetailsStar6 = new javax.swing.JLabel();
        jLabelDetailsStar7 = new javax.swing.JLabel();
        jLabelDetailsStar8 = new javax.swing.JLabel();
        jLabelDetailsStar9 = new javax.swing.JLabel();
        jLabelDetailsStar10 = new javax.swing.JLabel();
        jLabelDetailsYear = new javax.swing.JLabel();
        jButton1 = new javax.swing.JButton();
        menuBar = new javax.swing.JMenuBar();
        javax.swing.JMenu fileMenu = new javax.swing.JMenu();
        jMenuItem1 = new javax.swing.JMenuItem();
        jMenuItem2 = new javax.swing.JMenuItem();
        javax.swing.JMenuItem exitMenuItem = new javax.swing.JMenuItem();
        jMenu1 = new javax.swing.JMenu();
        jMenuItem3 = new javax.swing.JMenuItem();
        jSeparator6 = new javax.swing.JPopupMenu.Separator();
        jMenuItemSettings = new javax.swing.JMenuItem();
        jMenuItemalternatives = new javax.swing.JMenuItem();
        javax.swing.JMenu helpMenu = new javax.swing.JMenu();
        updateMenuItem = new javax.swing.JMenuItem();
        jSeparator5 = new javax.swing.JPopupMenu.Separator();
        javax.swing.JMenuItem aboutMenuItem = new javax.swing.JMenuItem();
        jMenuDebug = new javax.swing.JMenu();
        jMenuItem4 = new javax.swing.JMenuItem();
        jMenuItem5 = new javax.swing.JMenuItem();
        jMenuItem6 = new javax.swing.JMenuItem();
        jMenuItem7 = new javax.swing.JMenuItem();
        jMenuItem8 = new javax.swing.JMenuItem();
        jMenuItem9 = new javax.swing.JMenuItem();
        jMenuItem10 = new javax.swing.JMenuItem();
        jMenuItem11 = new javax.swing.JMenuItem();
        statusPanel = new javax.swing.JPanel();
        javax.swing.JSeparator statusPanelSeparator = new javax.swing.JSeparator();
        statusMessageLabel = new javax.swing.JLabel();
        statusAnimationLabel = new javax.swing.JLabel();
        progressBar = new javax.swing.JProgressBar();
        statusPopup = new javax.swing.JFrame();
        jPanel2 = new javax.swing.JPanel();
        descLabel = new javax.swing.JLabel();
        jScrollPane2 = new javax.swing.JScrollPane();
        jTableTasks = new javax.swing.JTable();
        jImportBackdrop = new javax.swing.JFrame();
        jLabelBackdrop1 = new javax.swing.JLabel();
        jButton3 = new javax.swing.JButton();
        jButtonBackdropOpen = new javax.swing.JButton();
        jButton5 = new javax.swing.JButton();
        jJPEGOpen = new javax.swing.JFileChooser();
        jImportPoster = new javax.swing.JFrame();
        jLabelPoster1 = new javax.swing.JLabel();
        jButtonPosterCancel = new javax.swing.JButton();
        jButtonPosterOpen = new javax.swing.JButton();
        jButtonPosterSave = new javax.swing.JButton();

        mainPanel.setName("mainPanel"); // NOI18N

        jToolBar1.setRollover(true);
        jToolBar1.setName("jToolBar1"); // NOI18N

        javax.swing.ActionMap actionMap = org.jdesktop.application.Application.getInstance(valerie.ValerieApp.class).getContext().getActionMap(ValerieView.class, this);
        jButtonSync.setAction(actionMap.get("actionNetworkFilesystem")); // NOI18N
        org.jdesktop.application.ResourceMap resourceMap = org.jdesktop.application.Application.getInstance(valerie.ValerieApp.class).getContext().getResourceMap(ValerieView.class);
        jButtonSync.setIcon(resourceMap.getIcon("jButtonSync.icon")); // NOI18N
        jButtonSync.setText(resourceMap.getString("jButtonSync.text")); // NOI18N
        jButtonSync.setToolTipText(resourceMap.getString("jButtonSync.toolTipText")); // NOI18N
        jButtonSync.setFocusable(false);
        jButtonSync.setHorizontalTextPosition(javax.swing.SwingConstants.CENTER);
        jButtonSync.setName("jButtonSync"); // NOI18N
        jButtonSync.setVerticalTextPosition(javax.swing.SwingConstants.BOTTOM);
        jToolBar1.add(jButtonSync);

        jButtonParse.setAction(actionMap.get("actionJobParse")); // NOI18N
        jButtonParse.setIcon(resourceMap.getIcon("jButtonParse.icon")); // NOI18N
        jButtonParse.setText(resourceMap.getString("jButtonParse.text")); // NOI18N
        jButtonParse.setToolTipText(resourceMap.getString("jButtonParse.toolTipText")); // NOI18N
        jButtonParse.setFocusable(false);
        jButtonParse.setHorizontalTextPosition(javax.swing.SwingConstants.CENTER);
        jButtonParse.setName("jButtonParse"); // NOI18N
        jButtonParse.setVerticalTextPosition(javax.swing.SwingConstants.BOTTOM);
        jToolBar1.add(jButtonParse);

        jButtonArt.setAction(actionMap.get("actionJobArts")); // NOI18N
        jButtonArt.setIcon(resourceMap.getIcon("jButtonArt.icon")); // NOI18N
        jButtonArt.setText(resourceMap.getString("jButtonArt.text")); // NOI18N
        jButtonArt.setToolTipText(resourceMap.getString("jButtonArt.toolTipText")); // NOI18N
        jButtonArt.setFocusable(false);
        jButtonArt.setHorizontalTextPosition(javax.swing.SwingConstants.CENTER);
        jButtonArt.setName("jButtonArt"); // NOI18N
        jButtonArt.setVerticalTextPosition(javax.swing.SwingConstants.BOTTOM);
        jToolBar1.add(jButtonArt);

        jSeparator3.setName("jSeparator3"); // NOI18N
        jToolBar1.add(jSeparator3);

        jButtonDownloadFromBox.setAction(actionMap.get("actionNetworkTransferMO")); // NOI18N
        jButtonDownloadFromBox.setIcon(resourceMap.getIcon("jButtonDownloadFromBox.icon")); // NOI18N
        jButtonDownloadFromBox.setText(resourceMap.getString("jButtonDownloadFromBox.text")); // NOI18N
        jButtonDownloadFromBox.setToolTipText(resourceMap.getString("jButtonDownloadFromBox.toolTipText")); // NOI18N
        jButtonDownloadFromBox.setFocusable(false);
        jButtonDownloadFromBox.setHorizontalTextPosition(javax.swing.SwingConstants.CENTER);
        jButtonDownloadFromBox.setName("jButtonDownloadFromBox"); // NOI18N
        jButtonDownloadFromBox.setPressedIcon(resourceMap.getIcon("jButtonDownloadFromBox.pressedIcon")); // NOI18N
        jButtonDownloadFromBox.setVerticalTextPosition(javax.swing.SwingConstants.BOTTOM);
        jToolBar1.add(jButtonDownloadFromBox);

        jButtonUploadToBox.setAction(actionMap.get("actionNetworkTransferMT")); // NOI18N
        jButtonUploadToBox.setIcon(resourceMap.getIcon("jButtonUploadToBox.icon")); // NOI18N
        jButtonUploadToBox.setText(resourceMap.getString("jButtonUploadToBox.text")); // NOI18N
        jButtonUploadToBox.setToolTipText(resourceMap.getString("jButtonUploadToBox.toolTipText")); // NOI18N
        jButtonUploadToBox.setFocusable(false);
        jButtonUploadToBox.setHorizontalTextPosition(javax.swing.SwingConstants.CENTER);
        jButtonUploadToBox.setName("jButtonUploadToBox"); // NOI18N
        jButtonUploadToBox.setPressedIcon(resourceMap.getIcon("jButtonUploadToBox.pressedIcon")); // NOI18N
        jButtonUploadToBox.setVerticalTextPosition(javax.swing.SwingConstants.BOTTOM);
        jToolBar1.add(jButtonUploadToBox);

        jButtonConnect.setAction(actionMap.get("actionNetworkConnect")); // NOI18N
        jButtonConnect.setText(resourceMap.getString("jButtonConnect.text")); // NOI18N
        jButtonConnect.setToolTipText(resourceMap.getString("jButtonConnect.toolTipText")); // NOI18N
        jButtonConnect.setFocusable(false);
        jButtonConnect.setHorizontalTextPosition(javax.swing.SwingConstants.CENTER);
        jButtonConnect.setName("jButtonConnect"); // NOI18N
        jButtonConnect.setVerticalTextPosition(javax.swing.SwingConstants.BOTTOM);
        jToolBar1.add(jButtonConnect);

        jComboBoxBoxinfo.setBackground(resourceMap.getColor("jComboBoxBoxinfo.background")); // NOI18N
        jComboBoxBoxinfo.setName("jComboBoxBoxinfo"); // NOI18N
        jComboBoxBoxinfo.addItemListener(new java.awt.event.ItemListener() {
            public void itemStateChanged(java.awt.event.ItemEvent evt) {
                jComboBoxBoxinfoItemStateChanged(evt);
            }
        });

        jSplitPane1.setDividerLocation(500);
        jSplitPane1.setDividerSize(10);
        jSplitPane1.setName("jSplitPane1"); // NOI18N
        jSplitPane1.setOneTouchExpandable(true);

        jTabbedPane.setName("jTabbedPane"); // NOI18N

        jPanelMovies.setName("jPanelMovies"); // NOI18N

        jScrollPane1.setName("jScrollPane1"); // NOI18N

        jTableMovies.setAutoCreateRowSorter(true);
        jTableMovies.setModel(new javax.swing.table.DefaultTableModel(
            new Object [][] {
                {null, null, null, null, null}
            },
            new String [] {
                "Title", "Searchstring", "Year", "ID", "U"
            }
        ) {
            Class[] types = new Class [] {
                java.lang.String.class, java.lang.String.class, java.lang.Integer.class, java.lang.Integer.class, java.lang.Boolean.class
            };
            boolean[] canEdit = new boolean [] {
                false, true, false, false, false
            };

            public Class getColumnClass(int columnIndex) {
                return types [columnIndex];
            }

            public boolean isCellEditable(int rowIndex, int columnIndex) {
                return canEdit [columnIndex];
            }
        });
        jTableMovies.setColumnSelectionAllowed(true);
        jTableMovies.setName("jTableMovies"); // NOI18N
        jTableMovies.getTableHeader().setReorderingAllowed(false);
        jTableMovies.addMouseListener(new java.awt.event.MouseAdapter() {
            public void mouseClicked(java.awt.event.MouseEvent evt) {
                jTableMoviesMouseClicked(evt);
            }
        });
        jTableMovies.addKeyListener(new java.awt.event.KeyAdapter() {
            public void keyPressed(java.awt.event.KeyEvent evt) {
                jTableMoviesKeyPressed(evt);
            }
        });
        jScrollPane1.setViewportView(jTableMovies);
        java.util.ResourceBundle bundle = java.util.ResourceBundle.getBundle("Gui/resources/ValerieView"); // NOI18N
        jTableMovies.getColumnModel().getSelectionModel().setSelectionMode(javax.swing.ListSelectionModel.SINGLE_SELECTION);
        jTableMovies.getColumnModel().getColumn(0).setPreferredWidth(150);
        jTableMovies.getColumnModel().getColumn(0).setHeaderValue(bundle.getString("jTableFilelist.columnModel.title1")); // NOI18N
        jTableMovies.getColumnModel().getColumn(1).setPreferredWidth(100);
        jTableMovies.getColumnModel().getColumn(1).setHeaderValue(bundle.getString("jTableFilelist.columnModel.title2")); // NOI18N
        jTableMovies.getColumnModel().getColumn(2).setPreferredWidth(30);
        jTableMovies.getColumnModel().getColumn(2).setHeaderValue(bundle.getString("jTableFilelist.columnModel.title3")); // NOI18N
        jTableMovies.getColumnModel().getColumn(3).setPreferredWidth(10);
        jTableMovies.getColumnModel().getColumn(3).setHeaderValue(bundle.getString("jTableFilelist.columnModel.title5")); // NOI18N
        jTableMovies.getColumnModel().getColumn(4).setPreferredWidth(1);
        jTableMovies.getColumnModel().getColumn(4).setHeaderValue(bundle.getString("jTableFilelist.columnModel.title0")); // NOI18N

        javax.swing.GroupLayout jPanelMoviesLayout = new javax.swing.GroupLayout(jPanelMovies);
        jPanelMovies.setLayout(jPanelMoviesLayout);
        jPanelMoviesLayout.setHorizontalGroup(
            jPanelMoviesLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addComponent(jScrollPane1, javax.swing.GroupLayout.DEFAULT_SIZE, 494, Short.MAX_VALUE)
        );
        jPanelMoviesLayout.setVerticalGroup(
            jPanelMoviesLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addComponent(jScrollPane1, javax.swing.GroupLayout.Alignment.TRAILING, javax.swing.GroupLayout.DEFAULT_SIZE, 628, Short.MAX_VALUE)
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
                java.lang.String.class, java.lang.Integer.class
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
        jTableSeries.setColumnSelectionAllowed(true);
        jTableSeries.setName("jTableSeries"); // NOI18N
        jTableSeries.getTableHeader().setReorderingAllowed(false);
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
        jTableSeries.getColumnModel().getSelectionModel().setSelectionMode(javax.swing.ListSelectionModel.SINGLE_SELECTION);
        jTableSeries.getColumnModel().getColumn(0).setResizable(false);
        jTableSeries.getColumnModel().getColumn(0).setHeaderValue(resourceMap.getString("jTableSeries.columnModel.title0")); // NOI18N
        jTableSeries.getColumnModel().getColumn(1).setResizable(false);
        jTableSeries.getColumnModel().getColumn(1).setPreferredWidth(10);
        jTableSeries.getColumnModel().getColumn(1).setHeaderValue(resourceMap.getString("jTableSeries.columnModel.title1")); // NOI18N

        jSplitPane2.setTopComponent(jScrollPane6);

        jScrollPane5.setName("jScrollPane5"); // NOI18N

        jTableEpisodes.setAutoCreateRowSorter(true);
        jTableEpisodes.setModel(new javax.swing.table.DefaultTableModel(
            new Object [][] {
                {null, null, null, null, null, null}
            },
            new String [] {
                "Title", "Searchstring", "S", "E", "ID", "U"
            }
        ) {
            Class[] types = new Class [] {
                java.lang.String.class, java.lang.String.class, java.lang.Integer.class, java.lang.Integer.class, java.lang.Integer.class, java.lang.Boolean.class
            };
            boolean[] canEdit = new boolean [] {
                false, true, true, true, false, false
            };

            public Class getColumnClass(int columnIndex) {
                return types [columnIndex];
            }

            public boolean isCellEditable(int rowIndex, int columnIndex) {
                return canEdit [columnIndex];
            }
        });
        jTableEpisodes.setColumnSelectionAllowed(true);
        jTableEpisodes.setName("jTableEpisodes"); // NOI18N
        jTableEpisodes.getTableHeader().setReorderingAllowed(false);
        jTableEpisodes.addMouseListener(new java.awt.event.MouseAdapter() {
            public void mouseClicked(java.awt.event.MouseEvent evt) {
                jTableEpisodesMouseClicked(evt);
            }
        });
        jTableEpisodes.addKeyListener(new java.awt.event.KeyAdapter() {
            public void keyPressed(java.awt.event.KeyEvent evt) {
                jTableEpisodesKeyPressed(evt);
            }
        });
        jScrollPane5.setViewportView(jTableEpisodes);
        jTableEpisodes.getColumnModel().getSelectionModel().setSelectionMode(javax.swing.ListSelectionModel.SINGLE_SELECTION);
        jTableEpisodes.getColumnModel().getColumn(0).setResizable(false);
        jTableEpisodes.getColumnModel().getColumn(0).setPreferredWidth(150);
        jTableEpisodes.getColumnModel().getColumn(0).setHeaderValue(resourceMap.getString("jTableFilelist.columnModel.title1")); // NOI18N
        jTableEpisodes.getColumnModel().getColumn(1).setResizable(false);
        jTableEpisodes.getColumnModel().getColumn(1).setHeaderValue(resourceMap.getString("jTableEpisodes.columnModel.title0")); // NOI18N
        jTableEpisodes.getColumnModel().getColumn(2).setResizable(false);
        jTableEpisodes.getColumnModel().getColumn(2).setPreferredWidth(15);
        jTableEpisodes.getColumnModel().getColumn(2).setHeaderValue(resourceMap.getString("jTableFilelistEpisodes.columnModel.title7")); // NOI18N
        jTableEpisodes.getColumnModel().getColumn(3).setResizable(false);
        jTableEpisodes.getColumnModel().getColumn(3).setPreferredWidth(15);
        jTableEpisodes.getColumnModel().getColumn(3).setHeaderValue(resourceMap.getString("jTableFilelistEpisodes.columnModel.title8")); // NOI18N
        jTableEpisodes.getColumnModel().getColumn(4).setResizable(false);
        jTableEpisodes.getColumnModel().getColumn(4).setPreferredWidth(10);
        jTableEpisodes.getColumnModel().getColumn(4).setHeaderValue(resourceMap.getString("jTableFilelistEpisodes.columnModel.title6")); // NOI18N
        jTableEpisodes.getColumnModel().getColumn(5).setResizable(false);
        jTableEpisodes.getColumnModel().getColumn(5).setPreferredWidth(1);
        jTableEpisodes.getColumnModel().getColumn(5).setHeaderValue(resourceMap.getString("jTableEpisodes.columnModel.title6")); // NOI18N

        jSplitPane2.setRightComponent(jScrollPane5);

        javax.swing.GroupLayout jPanelSeriesLayout = new javax.swing.GroupLayout(jPanelSeries);
        jPanelSeries.setLayout(jPanelSeriesLayout);
        jPanelSeriesLayout.setHorizontalGroup(
            jPanelSeriesLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addComponent(jSplitPane2, javax.swing.GroupLayout.DEFAULT_SIZE, 494, Short.MAX_VALUE)
        );
        jPanelSeriesLayout.setVerticalGroup(
            jPanelSeriesLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addComponent(jSplitPane2, javax.swing.GroupLayout.DEFAULT_SIZE, 628, Short.MAX_VALUE)
        );

        jTabbedPane.addTab(resourceMap.getString("jPanelSeries.TabConstraints.tabTitle"), jPanelSeries); // NOI18N

        jSplitPane1.setLeftComponent(jTabbedPane);

        jPanelDetails.setName("jPanelDetails"); // NOI18N

        jScrollPane3.setName("jScrollPane3"); // NOI18N

        jTextAreaDescription.setColumns(20);
        jTextAreaDescription.setEditable(false);
        jTextAreaDescription.setRows(5);
        jTextAreaDescription.setName("jTextAreaDescription"); // NOI18N
        jScrollPane3.setViewportView(jTextAreaDescription);

        jLabelDetailsTitle.setFont(resourceMap.getFont("jLabelDetailsTitle.font")); // NOI18N
        jLabelDetailsTitle.setText(resourceMap.getString("jLabelDetailsTitle.text")); // NOI18N
        jLabelDetailsTitle.setAutoscrolls(true);
        jLabelDetailsTitle.setName("jLabelDetailsTitle"); // NOI18N

        jLabelDetailsPoster.setBackground(resourceMap.getColor("jLabelDetailsPoster.background")); // NOI18N
        jLabelDetailsPoster.setText(resourceMap.getString("jLabelDetailsPoster.text")); // NOI18N
        jLabelDetailsPoster.setBorder(javax.swing.BorderFactory.createLineBorder(new java.awt.Color(0, 0, 0)));
        jLabelDetailsPoster.setName("jLabelDetailsPoster"); // NOI18N
        jLabelDetailsPoster.setOpaque(true);
        jLabelDetailsPoster.addMouseListener(new java.awt.event.MouseAdapter() {
            public void mouseClicked(java.awt.event.MouseEvent evt) {
                jLabelDetailsPosterMouseClicked(evt);
            }
        });

        jLabelDetailsBackdrop.setBackground(resourceMap.getColor("jLabelDetailsBackdrop.background")); // NOI18N
        jLabelDetailsBackdrop.setText(resourceMap.getString("jLabelDetailsBackdrop.text")); // NOI18N
        jLabelDetailsBackdrop.setBorder(javax.swing.BorderFactory.createLineBorder(new java.awt.Color(0, 0, 0)));
        jLabelDetailsBackdrop.setName("jLabelDetailsBackdrop"); // NOI18N
        jLabelDetailsBackdrop.setOpaque(true);
        jLabelDetailsBackdrop.addMouseListener(new java.awt.event.MouseAdapter() {
            public void mouseClicked(java.awt.event.MouseEvent evt) {
                jLabelDetailsBackdropMouseClicked(evt);
            }
        });

        jLabelDetailsTagline.setFont(resourceMap.getFont("jLabelDetailsTagline.font")); // NOI18N
        jLabelDetailsTagline.setText(resourceMap.getString("jLabelDetailsTagline.text")); // NOI18N
        jLabelDetailsTagline.setName("jLabelDetailsTagline"); // NOI18N

        jLabelDetailsPlot.setFont(resourceMap.getFont("jLabelDetailsPlot.font")); // NOI18N
        jLabelDetailsPlot.setText(resourceMap.getString("jLabelDetailsPlot.text")); // NOI18N
        jLabelDetailsPlot.setName("jLabelDetailsPlot"); // NOI18N

        jScrollPaneDetailsPlot.setName("jScrollPaneDetailsPlot"); // NOI18N

        jTextAreaDetailsPlot.setBackground(resourceMap.getColor("jTextAreaDetailsPlot.background")); // NOI18N
        jTextAreaDetailsPlot.setColumns(20);
        jTextAreaDetailsPlot.setEditable(false);
        jTextAreaDetailsPlot.setLineWrap(true);
        jTextAreaDetailsPlot.setRows(5);
        jTextAreaDetailsPlot.setWrapStyleWord(true);
        jTextAreaDetailsPlot.setAutoscrolls(false);
        jTextAreaDetailsPlot.setName("jTextAreaDetailsPlot"); // NOI18N
        jTextAreaDetailsPlot.setVerifyInputWhenFocusTarget(false);
        jScrollPaneDetailsPlot.setViewportView(jTextAreaDetailsPlot);

        jLabelDetailsStar1.setIcon(resourceMap.getIcon("jLabelDetailsStar1.icon")); // NOI18N
        jLabelDetailsStar1.setText(resourceMap.getString("jLabelDetailsStar1.text")); // NOI18N
        jLabelDetailsStar1.setName("jLabelDetailsStar1"); // NOI18N

        jLabelDetailsStar2.setIcon(resourceMap.getIcon("jLabelDetailsStar2.icon")); // NOI18N
        jLabelDetailsStar2.setName("jLabelDetailsStar2"); // NOI18N

        jLabelDetailsStar3.setIcon(resourceMap.getIcon("jLabelDetailsStar3.icon")); // NOI18N
        jLabelDetailsStar3.setName("jLabelDetailsStar3"); // NOI18N

        jLabelDetailsStar4.setIcon(resourceMap.getIcon("jLabelDetailsStar4.icon")); // NOI18N
        jLabelDetailsStar4.setName("jLabelDetailsStar4"); // NOI18N

        jLabelDetailsStar5.setIcon(resourceMap.getIcon("jLabelDetailsStar5.icon")); // NOI18N
        jLabelDetailsStar5.setName("jLabelDetailsStar5"); // NOI18N

        jLabelDetailsStar6.setIcon(resourceMap.getIcon("jLabelDetailsStar6.icon")); // NOI18N
        jLabelDetailsStar6.setName("jLabelDetailsStar6"); // NOI18N

        jLabelDetailsStar7.setIcon(resourceMap.getIcon("jLabelDetailsStar7.icon")); // NOI18N
        jLabelDetailsStar7.setName("jLabelDetailsStar7"); // NOI18N

        jLabelDetailsStar8.setIcon(resourceMap.getIcon("jLabelDetailsStar8.icon")); // NOI18N
        jLabelDetailsStar8.setName("jLabelDetailsStar8"); // NOI18N

        jLabelDetailsStar9.setIcon(resourceMap.getIcon("jLabelDetailsStar9.icon")); // NOI18N
        jLabelDetailsStar9.setName("jLabelDetailsStar9"); // NOI18N

        jLabelDetailsStar10.setIcon(resourceMap.getIcon("jLabelDetailsStar10.icon")); // NOI18N
        jLabelDetailsStar10.setName("jLabelDetailsStar10"); // NOI18N

        jLabelDetailsYear.setFont(resourceMap.getFont("jLabelDetailsYear.font")); // NOI18N
        jLabelDetailsYear.setText(resourceMap.getString("jLabelDetailsYear.text")); // NOI18N
        jLabelDetailsYear.setName("jLabelDetailsYear"); // NOI18N

        jButton1.setText(resourceMap.getString("jButton1.text")); // NOI18N
        jButton1.setName("jButton1"); // NOI18N

        javax.swing.GroupLayout jPanelDetailsLayout = new javax.swing.GroupLayout(jPanelDetails);
        jPanelDetails.setLayout(jPanelDetailsLayout);
        jPanelDetailsLayout.setHorizontalGroup(
            jPanelDetailsLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanelDetailsLayout.createSequentialGroup()
                .addContainerGap()
                .addComponent(jLabelDetailsTitle, javax.swing.GroupLayout.DEFAULT_SIZE, 469, Short.MAX_VALUE)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addComponent(jButton1)
                .addContainerGap())
            .addGroup(jPanelDetailsLayout.createSequentialGroup()
                .addGap(20, 20, 20)
                .addGroup(jPanelDetailsLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addGroup(javax.swing.GroupLayout.Alignment.TRAILING, jPanelDetailsLayout.createSequentialGroup()
                        .addGroup(jPanelDetailsLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.TRAILING)
                            .addComponent(jLabelDetailsTagline, javax.swing.GroupLayout.Alignment.LEADING, javax.swing.GroupLayout.DEFAULT_SIZE, 500, Short.MAX_VALUE)
                            .addGroup(javax.swing.GroupLayout.Alignment.LEADING, jPanelDetailsLayout.createSequentialGroup()
                                .addGap(20, 20, 20)
                                .addGroup(jPanelDetailsLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                                    .addComponent(jScrollPaneDetailsPlot, javax.swing.GroupLayout.Alignment.TRAILING, javax.swing.GroupLayout.DEFAULT_SIZE, 480, Short.MAX_VALUE)
                                    .addComponent(jScrollPane3, javax.swing.GroupLayout.DEFAULT_SIZE, 480, Short.MAX_VALUE))))
                        .addGap(24, 24, 24))
                    .addGroup(jPanelDetailsLayout.createSequentialGroup()
                        .addGroup(jPanelDetailsLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                            .addGroup(jPanelDetailsLayout.createSequentialGroup()
                                .addComponent(jLabelDetailsStar1)
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                                .addComponent(jLabelDetailsStar2)
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                                .addComponent(jLabelDetailsStar3)
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                                .addComponent(jLabelDetailsStar4)
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                                .addComponent(jLabelDetailsStar5)
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                                .addComponent(jLabelDetailsStar6)
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                                .addComponent(jLabelDetailsStar7)
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                                .addComponent(jLabelDetailsStar8)
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                                .addComponent(jLabelDetailsStar9)
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                                .addComponent(jLabelDetailsStar10)
                                .addGap(30, 30, 30)
                                .addComponent(jLabelDetailsYear))
                            .addGroup(jPanelDetailsLayout.createSequentialGroup()
                                .addComponent(jLabelDetailsPoster, javax.swing.GroupLayout.PREFERRED_SIZE, 146, javax.swing.GroupLayout.PREFERRED_SIZE)
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                                .addComponent(jLabelDetailsBackdrop, javax.swing.GroupLayout.PREFERRED_SIZE, 320, javax.swing.GroupLayout.PREFERRED_SIZE))
                            .addComponent(jLabelDetailsPlot))
                        .addContainerGap(52, Short.MAX_VALUE))))
        );
        jPanelDetailsLayout.setVerticalGroup(
            jPanelDetailsLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanelDetailsLayout.createSequentialGroup()
                .addContainerGap()
                .addGroup(jPanelDetailsLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(jLabelDetailsTitle)
                    .addComponent(jButton1))
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addGroup(jPanelDetailsLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.TRAILING)
                    .addComponent(jLabelDetailsStar1)
                    .addComponent(jLabelDetailsStar2)
                    .addComponent(jLabelDetailsStar3)
                    .addComponent(jLabelDetailsStar4)
                    .addComponent(jLabelDetailsStar5)
                    .addComponent(jLabelDetailsStar6)
                    .addComponent(jLabelDetailsStar7)
                    .addComponent(jLabelDetailsStar8)
                    .addComponent(jLabelDetailsStar9)
                    .addComponent(jLabelDetailsStar10)
                    .addComponent(jLabelDetailsYear))
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addComponent(jLabelDetailsTagline)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addGroup(jPanelDetailsLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(jLabelDetailsBackdrop, javax.swing.GroupLayout.PREFERRED_SIZE, 180, javax.swing.GroupLayout.PREFERRED_SIZE)
                    .addGroup(jPanelDetailsLayout.createSequentialGroup()
                        .addComponent(jLabelDetailsPoster, javax.swing.GroupLayout.PREFERRED_SIZE, 214, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                        .addComponent(jLabelDetailsPlot)))
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addComponent(jScrollPaneDetailsPlot, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                .addComponent(jScrollPane3, javax.swing.GroupLayout.PREFERRED_SIZE, 169, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addGap(15, 15, 15))
        );

        jSplitPane1.setRightComponent(jPanelDetails);

        javax.swing.GroupLayout mainPanelLayout = new javax.swing.GroupLayout(mainPanel);
        mainPanel.setLayout(mainPanelLayout);
        mainPanelLayout.setHorizontalGroup(
            mainPanelLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(javax.swing.GroupLayout.Alignment.TRAILING, mainPanelLayout.createSequentialGroup()
                .addComponent(jToolBar1, javax.swing.GroupLayout.DEFAULT_SIZE, 637, Short.MAX_VALUE)
                .addGap(84, 84, 84)
                .addComponent(jComboBoxBoxinfo, javax.swing.GroupLayout.PREFERRED_SIZE, 324, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addContainerGap())
            .addComponent(jSplitPane1, javax.swing.GroupLayout.DEFAULT_SIZE, 1055, Short.MAX_VALUE)
        );
        mainPanelLayout.setVerticalGroup(
            mainPanelLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(mainPanelLayout.createSequentialGroup()
                .addGroup(mainPanelLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING, false)
                    .addComponent(jComboBoxBoxinfo)
                    .addComponent(jToolBar1, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE))
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addComponent(jSplitPane1, javax.swing.GroupLayout.DEFAULT_SIZE, 658, Short.MAX_VALUE))
        );

        menuBar.setName("menuBar"); // NOI18N

        fileMenu.setAction(actionMap.get("SaveDB")); // NOI18N
        fileMenu.setText(resourceMap.getString("fileMenu.text")); // NOI18N
        fileMenu.setName("fileMenu"); // NOI18N

        jMenuItem1.setAction(actionMap.get("SaveDB")); // NOI18N
        jMenuItem1.setText(resourceMap.getString("jMenuItem1.text")); // NOI18N
        jMenuItem1.setName("jMenuItem1"); // NOI18N
        fileMenu.add(jMenuItem1);

        jMenuItem2.setAction(actionMap.get("exportFilelist")); // NOI18N
        jMenuItem2.setText(resourceMap.getString("jMenuItem2.text")); // NOI18N
        jMenuItem2.setName("jMenuItem2"); // NOI18N
        fileMenu.add(jMenuItem2);

        exitMenuItem.setAction(actionMap.get("quit")); // NOI18N
        exitMenuItem.setName("exitMenuItem"); // NOI18N
        fileMenu.add(exitMenuItem);

        menuBar.add(fileMenu);

        jMenu1.setAction(actionMap.get("showSelectAlternativeTitelPopup")); // NOI18N
        jMenu1.setText(resourceMap.getString("jMenu1.text")); // NOI18N
        jMenu1.setName("jMenu1"); // NOI18N

        jMenuItem3.setAction(actionMap.get("showConsole")); // NOI18N
        jMenuItem3.setText(resourceMap.getString("jMenuItem3.text")); // NOI18N
        jMenuItem3.setName("jMenuItem3"); // NOI18N
        jMenu1.add(jMenuItem3);

        jSeparator6.setName("jSeparator6"); // NOI18N
        jMenu1.add(jSeparator6);

        jMenuItemSettings.setAction(actionMap.get("jMenuItemEditSettingsClicked")); // NOI18N
        jMenuItemSettings.setText(resourceMap.getString("jMenuItemSettings.text")); // NOI18N
        jMenuItemSettings.setName("jMenuItemSettings"); // NOI18N
        jMenu1.add(jMenuItemSettings);

        jMenuItemalternatives.setAction(actionMap.get("showSelectAlternativeTitelPopup")); // NOI18N
        jMenuItemalternatives.setText(resourceMap.getString("jMenuItemalternatives.text")); // NOI18N
        jMenuItemalternatives.setName("jMenuItemalternatives"); // NOI18N
        jMenu1.add(jMenuItemalternatives);

        menuBar.add(jMenu1);

        helpMenu.setText(resourceMap.getString("helpMenu.text")); // NOI18N
        helpMenu.setName("helpMenu"); // NOI18N

        updateMenuItem.setAction(actionMap.get("checkForUpdate")); // NOI18N
        updateMenuItem.setText(resourceMap.getString("updateMenuItem.text")); // NOI18N
        updateMenuItem.setName("updateMenuItem"); // NOI18N
        helpMenu.add(updateMenuItem);

        jSeparator5.setName("jSeparator5"); // NOI18N
        helpMenu.add(jSeparator5);

        aboutMenuItem.setAction(actionMap.get("showAboutBox")); // NOI18N
        aboutMenuItem.setText(resourceMap.getString("aboutMenuItem.text")); // NOI18N
        aboutMenuItem.setName("aboutMenuItem"); // NOI18N
        helpMenu.add(aboutMenuItem);

        menuBar.add(helpMenu);

        jMenuDebug.setText(resourceMap.getString("jMenuDebug.text")); // NOI18N
        jMenuDebug.setName("jMenuDebug"); // NOI18N

        jMenuItem4.setAction(actionMap.get("actionDatabaseLoad")); // NOI18N
        jMenuItem4.setText(resourceMap.getString("jMenuItem4.text")); // NOI18N
        jMenuItem4.setName("jMenuItem4"); // NOI18N
        jMenuDebug.add(jMenuItem4);

        jMenuItem5.setAction(actionMap.get("actionDatabaseSave")); // NOI18N
        jMenuItem5.setText(resourceMap.getString("jMenuItem5.text")); // NOI18N
        jMenuItem5.setName("jMenuItem5"); // NOI18N
        jMenuDebug.add(jMenuItem5);

        jMenuItem6.setAction(actionMap.get("actionNetworkConnect")); // NOI18N
        jMenuItem6.setText(resourceMap.getString("jMenuItem6.text")); // NOI18N
        jMenuItem6.setName("jMenuItem6"); // NOI18N
        jMenuDebug.add(jMenuItem6);

        jMenuItem7.setAction(actionMap.get("actionNetworkTransferMO")); // NOI18N
        jMenuItem7.setText(resourceMap.getString("jMenuItem7.text")); // NOI18N
        jMenuItem7.setName("jMenuItem7"); // NOI18N
        jMenuDebug.add(jMenuItem7);

        jMenuItem8.setAction(actionMap.get("actionNetworkTransferMT")); // NOI18N
        jMenuItem8.setText(resourceMap.getString("jMenuItem8.text")); // NOI18N
        jMenuItem8.setName("jMenuItem8"); // NOI18N
        jMenuDebug.add(jMenuItem8);

        jMenuItem9.setAction(actionMap.get("actionNetworkFilesystem")); // NOI18N
        jMenuItem9.setText(resourceMap.getString("jMenuItem9.text")); // NOI18N
        jMenuItem9.setName("jMenuItem9"); // NOI18N
        jMenuDebug.add(jMenuItem9);

        jMenuItem10.setAction(actionMap.get("actionJobParse")); // NOI18N
        jMenuItem10.setText(resourceMap.getString("jMenuItem10.text")); // NOI18N
        jMenuItem10.setName("jMenuItem10"); // NOI18N
        jMenuDebug.add(jMenuItem10);

        jMenuItem11.setAction(actionMap.get("actionJobArts")); // NOI18N
        jMenuItem11.setText(resourceMap.getString("jMenuItem11.text")); // NOI18N
        jMenuItem11.setName("jMenuItem11"); // NOI18N
        jMenuDebug.add(jMenuItem11);

        menuBar.add(jMenuDebug);

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
            .addComponent(statusPanelSeparator, javax.swing.GroupLayout.DEFAULT_SIZE, 1055, Short.MAX_VALUE)
            .addGroup(statusPanelLayout.createSequentialGroup()
                .addContainerGap()
                .addComponent(statusMessageLabel)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED, 1035, Short.MAX_VALUE)
                .addComponent(statusAnimationLabel)
                .addContainerGap())
            .addGroup(javax.swing.GroupLayout.Alignment.TRAILING, statusPanelLayout.createSequentialGroup()
                .addContainerGap(748, Short.MAX_VALUE)
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

        statusPopup.setMinimumSize(new java.awt.Dimension(317, 220));
        statusPopup.setModalExclusionType(java.awt.Dialog.ModalExclusionType.TOOLKIT_EXCLUDE);
        statusPopup.setName("statusPopup"); // NOI18N
        statusPopup.setResizable(false);
        statusPopup.setUndecorated(true);

        jPanel2.setBorder(javax.swing.BorderFactory.createLineBorder(new java.awt.Color(0, 0, 0)));
        jPanel2.setAlignmentX(2.0F);
        jPanel2.setAlignmentY(2.0F);
        jPanel2.setName("jPanel2"); // NOI18N
        jPanel2.setLayout(new java.awt.BorderLayout());

        descLabel.setFont(new java.awt.Font("Tahoma", 0, 18));
        descLabel.setHorizontalAlignment(javax.swing.SwingConstants.CENTER);
        descLabel.setText(resourceMap.getString("descLabel.text")); // NOI18N
        descLabel.setName("descLabel"); // NOI18N
        jPanel2.add(descLabel, java.awt.BorderLayout.NORTH);

        jScrollPane2.setName("jScrollPane2"); // NOI18N

        jTableTasks.setModel(new javax.swing.table.DefaultTableModel(
            new Object [][] {
                {null, null, null},
                {null, null, null},
                {null, null, null},
                {null, null, null},
                {null, null, null},
                {null, null, null},
                {null, null, null},
                {null, null, null},
                {null, null, null},
                {null, null, null}
            },
            new String [] {
                "Task", "Progress", "Description"
            }
        ) {
            Class[] types = new Class [] {
                java.lang.Integer.class, java.lang.Object.class, java.lang.String.class
            };
            boolean[] canEdit = new boolean [] {
                false, false, false
            };

            public Class getColumnClass(int columnIndex) {
                return types [columnIndex];
            }

            public boolean isCellEditable(int rowIndex, int columnIndex) {
                return canEdit [columnIndex];
            }
        });
        jTableTasks.setName("jTableTasks"); // NOI18N
        jTableTasks.getColumnModel().getColumn(0).setMinWidth(40);
        jTableTasks.getColumnModel().getColumn(0).setPreferredWidth(40);

        jTableTasks.getColumnModel().getColumn(1).setMinWidth(60);
        jTableTasks.getColumnModel().getColumn(1).setPreferredWidth(60);

        jTableTasks.getColumnModel().getColumn(2).setMinWidth(800);
        jTableTasks.getColumnModel().getColumn(2).setPreferredWidth(800);
        jScrollPane2.setViewportView(jTableTasks);
        jTableTasks.getColumnModel().getColumn(1).setCellRenderer( new ProgressRenderer() );

        jPanel2.add(jScrollPane2, java.awt.BorderLayout.CENTER);

        statusPopup.getContentPane().add(jPanel2, java.awt.BorderLayout.CENTER);

        jImportBackdrop.setTitle(resourceMap.getString("jImportBackdrop.title")); // NOI18N
        jImportBackdrop.setAlwaysOnTop(true);
        jImportBackdrop.setMinimumSize(new java.awt.Dimension(430, 310));
        jImportBackdrop.setName("jImportBackdrop"); // NOI18N

        jLabelBackdrop1.setBackground(resourceMap.getColor("jLabelBackdrop1.background")); // NOI18N
        jLabelBackdrop1.setBorder(javax.swing.BorderFactory.createLineBorder(new java.awt.Color(0, 0, 0)));
        jLabelBackdrop1.setName("jLabelBackdrop1"); // NOI18N
        jLabelBackdrop1.setOpaque(true);

        jButton3.setAction(actionMap.get("importBackdropCancel")); // NOI18N
        jButton3.setText(resourceMap.getString("jButton3.text")); // NOI18N
        jButton3.setName("jButton3"); // NOI18N

        jButtonBackdropOpen.setAction(actionMap.get("ImportBackdropOpen")); // NOI18N
        jButtonBackdropOpen.setText(resourceMap.getString("jButtonBackdropOpen.text")); // NOI18N
        jButtonBackdropOpen.setName("jButtonBackdropOpen"); // NOI18N
        jButtonBackdropOpen.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                jButtonBackdropOpenActionPerformed(evt);
            }
        });

        jButton5.setText(resourceMap.getString("jButton5.text")); // NOI18N
        jButton5.setName("jButton5"); // NOI18N
        jButton5.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                jButton5ActionPerformed(evt);
            }
        });

        javax.swing.GroupLayout jImportBackdropLayout = new javax.swing.GroupLayout(jImportBackdrop.getContentPane());
        jImportBackdrop.getContentPane().setLayout(jImportBackdropLayout);
        jImportBackdropLayout.setHorizontalGroup(
            jImportBackdropLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jImportBackdropLayout.createSequentialGroup()
                .addContainerGap()
                .addGroup(jImportBackdropLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING, false)
                    .addGroup(jImportBackdropLayout.createSequentialGroup()
                        .addComponent(jButton3)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                        .addComponent(jButtonBackdropOpen)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                        .addComponent(jButton5))
                    .addComponent(jLabelBackdrop1, javax.swing.GroupLayout.PREFERRED_SIZE, 400, javax.swing.GroupLayout.PREFERRED_SIZE))
                .addContainerGap())
        );
        jImportBackdropLayout.setVerticalGroup(
            jImportBackdropLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jImportBackdropLayout.createSequentialGroup()
                .addContainerGap()
                .addComponent(jLabelBackdrop1, javax.swing.GroupLayout.PREFERRED_SIZE, 218, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addGap(18, 18, 18)
                .addGroup(jImportBackdropLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                    .addComponent(jButton3)
                    .addComponent(jButton5)
                    .addComponent(jButtonBackdropOpen))
                .addContainerGap(javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE))
        );

        jJPEGOpen.setCurrentDirectory(new java.io.File("C:\\"));
            jJPEGOpen.setDialogTitle(resourceMap.getString("jJPEGOpen.dialogTitle")); // NOI18N
            jJPEGOpen.setName("jJPEGOpen"); // NOI18N

            jImportPoster.setMinimumSize(new java.awt.Dimension(230, 310));
            jImportPoster.setName("jImportPoster"); // NOI18N

            jLabelPoster1.setBackground(resourceMap.getColor("jLabelPoster1.background")); // NOI18N
            jLabelPoster1.setBorder(javax.swing.BorderFactory.createLineBorder(new java.awt.Color(0, 0, 0)));
            jLabelPoster1.setName("jLabelPoster1"); // NOI18N
            jLabelPoster1.setOpaque(true);

            jButtonPosterCancel.setAction(actionMap.get("importBackdropCancel")); // NOI18N
            jButtonPosterCancel.setText(resourceMap.getString("jButtonPosterCancel.text")); // NOI18N
            jButtonPosterCancel.setName("jButtonPosterCancel"); // NOI18N
            jButtonPosterCancel.addActionListener(new java.awt.event.ActionListener() {
                public void actionPerformed(java.awt.event.ActionEvent evt) {
                    jButtonPosterCancelActionPerformed(evt);
                }
            });

            jButtonPosterOpen.setText(resourceMap.getString("jButtonPosterOpen.text")); // NOI18N
            jButtonPosterOpen.setName("jButtonPosterOpen"); // NOI18N
            jButtonPosterOpen.addActionListener(new java.awt.event.ActionListener() {
                public void actionPerformed(java.awt.event.ActionEvent evt) {
                    jButtonPosterOpenActionPerformed(evt);
                }
            });

            jButtonPosterSave.setText(resourceMap.getString("jButtonPosterSave.text")); // NOI18N
            jButtonPosterSave.setName("jButtonPosterSave"); // NOI18N
            jButtonPosterSave.addActionListener(new java.awt.event.ActionListener() {
                public void actionPerformed(java.awt.event.ActionEvent evt) {
                    jButtonPosterSaveActionPerformed(evt);
                }
            });

            javax.swing.GroupLayout jImportPosterLayout = new javax.swing.GroupLayout(jImportPoster.getContentPane());
            jImportPoster.getContentPane().setLayout(jImportPosterLayout);
            jImportPosterLayout.setHorizontalGroup(
                jImportPosterLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                .addGroup(jImportPosterLayout.createSequentialGroup()
                    .addContainerGap()
                    .addGroup(jImportPosterLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                        .addGroup(jImportPosterLayout.createSequentialGroup()
                            .addComponent(jButtonPosterCancel)
                            .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                            .addComponent(jButtonPosterOpen)
                            .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                            .addComponent(jButtonPosterSave))
                        .addGroup(javax.swing.GroupLayout.Alignment.TRAILING, jImportPosterLayout.createSequentialGroup()
                            .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED, 20, javax.swing.GroupLayout.PREFERRED_SIZE)
                            .addComponent(jLabelPoster1, javax.swing.GroupLayout.PREFERRED_SIZE, 156, javax.swing.GroupLayout.PREFERRED_SIZE)
                            .addGap(21, 21, 21)))
                    .addContainerGap(javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE))
            );
            jImportPosterLayout.setVerticalGroup(
                jImportPosterLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                .addGroup(jImportPosterLayout.createSequentialGroup()
                    .addContainerGap()
                    .addComponent(jLabelPoster1, javax.swing.GroupLayout.PREFERRED_SIZE, 218, javax.swing.GroupLayout.PREFERRED_SIZE)
                    .addGap(11, 11, 11)
                    .addGroup(jImportPosterLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                        .addComponent(jButtonPosterCancel)
                        .addComponent(jButtonPosterOpen)
                        .addComponent(jButtonPosterSave))
                    .addContainerGap(javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE))
            );

            setComponent(mainPanel);
            setMenuBar(menuBar);
            setStatusBar(statusPanel);
        }// </editor-fold>//GEN-END:initComponents

    private void detailsDrawStars(int value) {

        JLabel[] stars = {
            jLabelDetailsStar1,
            jLabelDetailsStar2,
            jLabelDetailsStar3,
            jLabelDetailsStar4,
            jLabelDetailsStar5,
            jLabelDetailsStar6,
            jLabelDetailsStar7,
            jLabelDetailsStar8,
            jLabelDetailsStar9,
            jLabelDetailsStar10, };

        for(int i = 0; i < value; i++)
            stars[i].setIcon(new javax.swing.ImageIcon(getClass().getResource("/Gui/resources/Star.png")));

        for(int i = value; i < 10; i++)
            stars[i].setIcon(new javax.swing.ImageIcon(getClass().getResource("/Gui/resources/NoStar.png")));
    }

    private void detailsDrawPosters(String posterfile, String backdropfile) {
        ImageIcon poster = new ImageIcon(posterfile);
        ImageIcon backdrop = new ImageIcon(backdropfile);
        poster.getImage().flush();
        backdrop.getImage().flush();
        poster = new ImageIcon(posterfile);
        backdrop = new ImageIcon(backdropfile);

        if(poster.getIconWidth() != -1){
            jLabelDetailsPoster.setDoubleBuffered(true);
            jLabelDetailsPoster.setIcon(new ImageIcon(poster.getImage().getScaledInstance(jLabelDetailsPoster.getWidth(), jLabelDetailsPoster.getHeight(), 0)));
        }            
        else {
            jLabelDetailsPoster.setDoubleBuffered(true);
            jLabelDetailsPoster.setIcon(null);
        }

        if(backdrop.getIconWidth() != -1){            
            jLabelDetailsBackdrop.setDoubleBuffered(true);
            jLabelDetailsBackdrop.setIcon(new ImageIcon(backdrop.getImage().getScaledInstance(jLabelDetailsBackdrop.getWidth(), jLabelDetailsBackdrop.getHeight(), 0)));
        }
        else {            
            jLabelDetailsBackdrop.setDoubleBuffered(true);
            jLabelDetailsBackdrop.setIcon(null);
        }
    }

    private final String defaultPoster = "default/defaultposter.jpg";
    private final String defaultBackdrop = "default/defaultbackdrop.jpg";

    private void detailsDrawPosters(String Id){

        String poster = defaultPoster;
        String backdrop = defaultBackdrop;
        if(new File("download/" + Id + "_poster.jpg").exists())
            poster = "download/" + Id + "_poster.jpg";
        else if(new File("converted/" + Id + "_poster.png").exists())
            poster = "converted/" + Id + "_poster.png";

        if(new File("download/" + Id + "_backdrop.jpg").exists())
            backdrop = "download/" + Id + "_backdrop.jpg";
        else if(new File("converted/" + Id + "_backdrop.png").exists())
            backdrop = "converted/" + Id + "_backdrop.png";

        detailsDrawPosters(poster, backdrop);
    }

    @Action
    public void showSelectAlternativeTitelPopup() {
        int row = jTableMovies.getSelectedRow();
        int id = (Integer) jTableMovies.getValueAt(row, 2);

        Database database = (Database)pController.get("Database");
        MediaInfo info = database.getMediaInfoById(id);

        String[] possibilities = new String[info.AlternativesCount + 1];
        possibilities[0] = info.Title + " (" + info.ImdbId + ")";
        for(int i = 0; i < info.AlternativesCount; i++)
            possibilities[i+1] = info.AlternativTitles[i] + " (" + info.AlternativImdbs[i] + ")";

        JComboBox alt = new JComboBox(possibilities);
        ButtonGroup group = new ButtonGroup();
        JRadioButton movie = new JRadioButton("Movie", true);
        JRadioButton tv = new JRadioButton("TV", false);
        group.add (movie);
        group.add (tv);

        Object[] message = {"Select alternativ title:", alt,
                            "TV / Movie:", movie, tv};

        JOptionPane pane = new JOptionPane( message,
            JOptionPane.PLAIN_MESSAGE,
            JOptionPane.OK_CANCEL_OPTION);

        pane.createDialog(null, "Titelmusik").setVisible(true);

        String s = alt.getSelectedItem().toString();

        /*String s = (String)JOptionPane.showInputDialog(
                this.mainPanel,
                "Select alternativ title:\n",
                "Dialog",
                JOptionPane.PLAIN_MESSAGE,
                null,
                possibilities,
                info.Title);*/


        if((s != null) && s.length() > 0)
            jTableMovies.setValueAt(s, row, 2);
    }

    private void detailsRefresh(MediaInfo info) {
        if (info != null) {
            if(info.Title.length() > 0)
                jLabelDetailsTitle.setText(info.Title);
            else
                jLabelDetailsTitle.setText("[S] " + info.SearchString);
            if(info.Tag.length() > 0)
                jLabelDetailsTagline.setText(info.Tag);
            else
                jLabelDetailsTagline.setText("No tagline available.");
            jTextAreaDetailsPlot.setText(info.Plot);
            jTextAreaDetailsPlot.setCaretPosition(0);
            jLabelDetailsYear.setText("[" + info.Year + "]");

            jTextAreaDescription.setText(info.toString());
            jTextAreaDescription.setCaretPosition(0);

            detailsDrawPosters(info.isMovie?info.ImdbId:info.TheTvDbId);
            detailsDrawStars(info.Popularity);
        }
    }

    private void jTableMoviesMouseClicked(java.awt.event.MouseEvent evt) {//GEN-FIRST:event_jTableMoviesMouseClicked

        if (evt.getClickCount() == 1 && evt.getButton() == MouseEvent.BUTTON1) {
            int row = jTableMovies.getSelectedRow();
            int id = (Integer) jTableMovies.getValueAt(row, 3);

            Database database = (Database)pController.get("Database");
            MediaInfo info = database.getMediaInfoById(id);
            
            detailsRefresh(info);
        }
        else if (evt.getClickCount() == 2 && evt.getButton() == MouseEvent.BUTTON1){
            showSelectAlternativeTitelPopup();
        }
    }//GEN-LAST:event_jTableMoviesMouseClicked

    private void jTableMoviesKeyPressed(java.awt.event.KeyEvent evt) {//GEN-FIRST:event_jTableMoviesKeyPressed
        int row = jTableMovies.getSelectedRow();

        if (evt.getKeyCode() == 38 && row > 0) {
            row--;
        } else if (evt.getKeyCode() == 40 && row + 1 < jTableMovies.getRowCount()) {
            row++;
        }

        int id = (Integer) jTableMovies.getValueAt(row, 3);
        Database database = (Database)pController.get("Database");
        MediaInfo info = database.getMediaInfoById(id);

        detailsRefresh(info);
    }//GEN-LAST:event_jTableMoviesKeyPressed

    private void jTableEpisodesMouseClicked(java.awt.event.MouseEvent evt) {//GEN-FIRST:event_jTableEpisodesMouseClicked
        int row = jTableEpisodes.getSelectedRow();
        int id = (Integer) jTableEpisodes.getValueAt(row, 4);

        Database database = (Database)pController.get("Database");
        MediaInfo info = database.getMediaInfoById(id);

        detailsRefresh(info);
    }//GEN-LAST:event_jTableEpisodesMouseClicked

    private void jTableEpisodesKeyPressed(java.awt.event.KeyEvent evt) {//GEN-FIRST:event_jTableEpisodesKeyPressed
        int row = jTableEpisodes.getSelectedRow();

        if (evt.getKeyCode() == 38 && row > 0) {
            row--;
        } else if (evt.getKeyCode() == 40 && row + 1 < jTableEpisodes.getRowCount()) {
            row++;
        }

        int id = (Integer) jTableEpisodes.getValueAt(row, 4);
        Database database = (Database)pController.get("Database");
        MediaInfo info = database.getMediaInfoById(id);

        detailsRefresh(info);
    }//GEN-LAST:event_jTableEpisodesKeyPressed

    private void jTableSeriesMouseClicked(java.awt.event.MouseEvent evt) {//GEN-FIRST:event_jTableSeriesMouseClicked
        int row = jTableSeries.getSelectedRow();
        int id = (Integer) jTableSeries.getValueAt(row, 1);

        Database database = (Database)pController.get("Database");
        MediaInfo info = database.getMediaInfoById(id);

        detailsRefresh(info);

        tablesEpisodesUpdate(id);
    }//GEN-LAST:event_jTableSeriesMouseClicked

    private void jTableSeriesKeyPressed(java.awt.event.KeyEvent evt) {//GEN-FIRST:event_jTableSeriesKeyPressed
        int row = jTableSeries.getSelectedRow();

        if (evt.getKeyCode() == 38 && row > 0) {
            row--;
        } else if (evt.getKeyCode() == 40 && row + 1 < jTableSeries.getRowCount()) {
            row++;
        }

        int id = (Integer) jTableSeries.getValueAt(row, 1);
        Database database = (Database)pController.get("Database");
        MediaInfo info = database.getMediaInfoById(id);

        detailsRefresh(info);
        tablesEpisodesUpdate(id);
    }//GEN-LAST:event_jTableSeriesKeyPressed

    private void jComboBoxBoxinfoItemStateChanged(java.awt.event.ItemEvent evt) {//GEN-FIRST:event_jComboBoxBoxinfoItemStateChanged
        DebugOutput.printl("->");

        pController.set("SelectedBoxInfo", jComboBoxBoxinfo.getSelectedIndex());

        if (jComboBoxBoxinfo == null || jComboBoxBoxinfo.getSelectedItem() == null/* || jComboBoxBoxinfo.getSelectedItem().toString().contains("unknown")*/){
            jButtonUploadToBox.setEnabled(false);
            jButtonDownloadFromBox.setEnabled(false);
            jButtonSync.setEnabled(false);
        }
        else {
            jButtonUploadToBox.setEnabled(true);
            jButtonDownloadFromBox.setEnabled(true);
            jButtonSync.setEnabled(true);
        }

        //this.actionNetworkTransferMO().execute();

        DebugOutput.printl("<-");
    }//GEN-LAST:event_jComboBoxBoxinfoItemStateChanged

    private void jLabelDetailsBackdropMouseClicked(java.awt.event.MouseEvent evt) {//GEN-FIRST:event_jLabelDetailsBackdropMouseClicked

    }//GEN-LAST:event_jLabelDetailsBackdropMouseClicked

    private void jButtonBackdropOpenActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_jButtonBackdropOpenActionPerformed
      
    }//GEN-LAST:event_jButtonBackdropOpenActionPerformed

    private void jButton5ActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_jButton5ActionPerformed
      
    }//GEN-LAST:event_jButton5ActionPerformed

    private void jButtonPosterOpenActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_jButtonPosterOpenActionPerformed
        
    }//GEN-LAST:event_jButtonPosterOpenActionPerformed

    private void jButtonPosterSaveActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_jButtonPosterSaveActionPerformed
       
    }//GEN-LAST:event_jButtonPosterSaveActionPerformed

    private void jButtonPosterCancelActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_jButtonPosterCancelActionPerformed
      
    }//GEN-LAST:event_jButtonPosterCancelActionPerformed

    private void jLabelDetailsPosterMouseClicked(java.awt.event.MouseEvent evt) {//GEN-FIRST:event_jLabelDetailsPosterMouseClicked
        
    }//GEN-LAST:event_jLabelDetailsPosterMouseClicked
    
    public void boxInfosUpdate() {
        DebugOutput.printl("->");
        jComboBoxBoxinfo.removeAllItems();
        BoxInfo[] boxInfos = (BoxInfo[])pController.get("BoxInfos");
        if (boxInfos != null) {
            for (int i = 0; i < boxInfos.length; i++) {
                String vInfo = boxInfos[i].toString();
                jComboBoxBoxinfo.addItem (vInfo);
            }
            pController.set("SelectedBoxInfo", (int)0);
            jComboBoxBoxinfo.setSelectedIndex( 0 );
        } else {
            pController.set("SelectedBoxInfo", (int)-1);
            jComboBoxBoxinfo.setSelectedIndex( -1 );
            //BoxIsConnected = false;
        }

        DebugOutput.printl("<-");
    }

    boolean isUpdating = false;

    public void tablesUpdate() {
        DebugOutput.printl("->");

        Database database = ((Database)pController.get("Database"));
        MediaInfo[] movies = database.getAsArray();

        ((DefaultTableModel) jTableMovies.getModel()).setRowCount(database.getMoviesCount());
        ((DefaultTableModel) jTableEpisodes.getModel()).setRowCount(database.getEpisodesCount());
        ((DefaultTableModel) jTableSeries.getModel()).setRowCount(database.getSeriesCount() + 2);

        int iteratorMovies = 0;
        //int iteratorEpisodes = 0;
        int iteratorSeries = 0;

        isUpdating = true;
        jTableMovies.setEnabled(false);
        jTableSeries.setEnabled(false);
        jTableEpisodes.setEnabled(false);

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
                jTableMovies.setValueAt(String.valueOf(movie.Title), iteratorMovies, 0);
                jTableMovies.setValueAt(String.valueOf(movie.SearchString), iteratorMovies, 1);
                jTableMovies.setValueAt(Integer.valueOf(movie.Year), iteratorMovies, 2);
                jTableMovies.setValueAt(Integer.valueOf(movie.ID), iteratorMovies, 3);
                jTableMovies.setValueAt(Boolean.valueOf(movie.needsUpdate), iteratorMovies, 4);
                iteratorMovies++;
            } else if (movie.isSerie) {
                jTableSeries.setValueAt(String.valueOf(movie.Title), iteratorSeries, 0);
                jTableSeries.setValueAt(Integer.valueOf(movie.ID), iteratorSeries, 1);
                iteratorSeries++;
            }
        }
        tablesEpisodesUpdate(-1);

        jTableMovies.setEnabled(true);
        jTableSeries.setEnabled(true);
        jTableEpisodes.setEnabled(true);

        jTableMovies.getRowSorter().allRowsChanged();
        jTableSeries.getRowSorter().allRowsChanged();
        jTableEpisodes.getRowSorter().allRowsChanged();

        isUpdating = false;

        if (movies.length > 0) detailsRefresh(movies[0]);

        DebugOutput.printl("<-");
    }

    public void tablesEpisodesUpdate(int id) {

        MediaInfo[] movies;
        Database database = (Database)pController.get("Database");

        if (id == -1) {
            movies = database.getMediaInfoEpisodeAsArray();
        } else if (id == -2) {
            movies = database.getMediaInfoEpisodesUnspecified();
        } else {
            MediaInfo series = database.getMediaInfoById(id);
            movies = database.getEpisodeAsArray(series.TheTvDbId);
        }

        ((DefaultTableModel) jTableEpisodes.getModel()).setRowCount(movies.length);

        isUpdating = true;
        jTableEpisodes.setEnabled(false);

        int iteratorEpisodes = 0;
        for (MediaInfo movie : movies) {
            jTableEpisodes.setValueAt(String.valueOf(movie.Title), iteratorEpisodes, 0);
            jTableEpisodes.setValueAt(String.valueOf(movie.SearchString), iteratorEpisodes, 1);
            jTableEpisodes.setValueAt(Integer.valueOf(movie.Season), iteratorEpisodes, 2);
            jTableEpisodes.setValueAt(Integer.valueOf(movie.Episode), iteratorEpisodes, 3);
            jTableEpisodes.setValueAt(Integer.valueOf(movie.ID), iteratorEpisodes, 4);
            jTableEpisodes.setValueAt(Boolean.valueOf(movie.needsUpdate), iteratorEpisodes, 5);

            iteratorEpisodes++;
        }

        jTableEpisodes.setEnabled(true);

        jTableEpisodes.getRowSorter().allRowsChanged();

        isUpdating = false;
    }

    @Action
    public void jMenuItemEditSettingsClicked() {
        JDialog settingsDialog;
        {
            JFrame mainFrame = ValerieApp.getApplication().getMainFrame();
            settingsDialog = new Settings(mainFrame, true, pController);
            settingsDialog.setLocationRelativeTo(mainFrame);
        }
        ValerieApp.getApplication().show(settingsDialog);
    }

    @Action
    public void exportFilelist() {
        Database database = (Database)pController.get("Database");
        MediaInfo[] movies = database.getAsArray();

        try {
            String charset = "UTF-8";
            //String charset = "ISO-8859-1";

            OutputStreamWriter fwMovie = new OutputStreamWriter(new FileOutputStream("export_movies.txt"), charset);
            OutputStreamWriter fwSeries = new OutputStreamWriter(new FileOutputStream("export_series.txt"), charset);

            for (MediaInfo movie : movies) {
                if (movie.isMovie) {
                    fwMovie.append(movie.Path.toString() + "\n");
                } else if (movie.isEpisode) {
                    fwSeries.append(movie.Path.toString() + "\n");
                }
            }
            
            fwMovie.close();
            fwSeries.close();
        } catch (Exception ex) {
            System.out.println(ex.toString());
        }
        
    }

    @Action
    public void checkForUpdate() {

        String cServer = "http://www.duckbox.info/valerie/update.xml";

        String version = "unknown";
        String url = "";

        Document xml = null;
        try {
            xml = new valerie.tools.WebGrabber().getXML(new URL(cServer));
        } catch (Exception ex) {
            System.out.println(ex.toString());
        }

        if (xml == null)
            return;

        List update = ((org.jdom.Element)xml.getRootElement().getChildren("update").get(0)).getChildren();
        for(int i = 0; i < update.size(); i++)
        {
            org.jdom.Element type = (org.jdom.Element) update.get(i);
            if(type.getName().equals("pc"))
            {
                version = type.getChild("version").getText();
                url = type.getChild("url").getText();
            }
        }

        boolean foundUpdate = !getResourceMap().getString("Application.version").equals(version);

        if(foundUpdate) {
            int i = JOptionPane.showConfirmDialog(
                    this.mainPanel,
                    "Update found!\nVersion: " + version + "\n\nDo you want to update?",
                    "Update found!",
                    JOptionPane.YES_NO_OPTION);

                if(i == 0/*TRUE*/) {
                    System.out.println("Updating...");
                    new valerie.tools.WebGrabber().getFile("http://www.duckbox.info/download.php?pv.jar", "pv.jar");
                    String cmd = "java -jar pv.jar -options options.txt";
                    try {
                        File f = new File("options.txt");
                        f.createNewFile();
                        OutputStreamWriter fw = new OutputStreamWriter(new FileOutputStream(f), "UTF-8");

                        String parent = f.getAbsoluteFile().getParent();
                        parent = parent.replaceAll("\\\\", "\\\\\\\\");

                        System.out.println("Target: " + parent);
                        fw.write("INSTALL_PATH=" + parent);
                        fw.close();
                    } catch(Exception ex) {
                        System.out.println(ex.toString());
                    }
                    
                    Process process;
                    int exitval;

                    Restart restart = new Restart();

                    try {
                        process = Runtime.getRuntime().exec(cmd);
                        //process.getErrorStream().close();
                        
                        process.getOutputStream().close();

                        InputStreamReader r = new InputStreamReader(process.getErrorStream());
                        BufferedReader in = new BufferedReader(r);

                        String line;
                        while ((line = in.readLine()) != null) {
                            System.out.print(line);
                        }

                        process.getInputStream().close();
                        process.getErrorStream().close();

                        process.waitFor();
                        exitval = process.exitValue();
                        System.out.printf("update: %d\n",  exitval);
                        
                    } catch(Exception ex) {
                        System.out.println(ex.toString());
                    }

                    restart.restartApplication(this);

                }
        } else {
            JOptionPane.showMessageDialog(this.mainPanel, "Already up to date");
        }

        System.out.println(update.toString());
           
    }

    

    @Action
    public void showConsole() {
        showConsole(true);
    }

    public void showConsole(boolean visible) {
        if(jFrameConsole == null)
            jFrameConsole = new Console(this.getFrame(), false);

        jFrameConsole.setVisible(visible);
    }

    @Action(block = Task.BlockingScope.WINDOW)
    public Task actionDatabaseLoad() {
        return new ActionDatabaseLoadTask(getApplication());
    }

    private class ActionDatabaseLoadTask extends org.jdesktop.application.Task<Object, Void> {
        ActionDatabaseLoadTask(org.jdesktop.application.Application app) {
            // Runs on the EDT.  Copy GUI state that
            // doInBackground() depends on from parameters
            // to ActionDatabaseLoadTask fields, here.
            super(app);

            //this.setUserCanCancel(false);
  

            pController.add(new Notification() {
                @Override
                public void init() {
                    Type = "PROGRESS";
                }

                @Override
                public void callback(Object o) {
                    if(o.getClass().equals(Float.class))
                        setProgress((Float)o);
                    else if(o.getClass().equals(String.class))
                        setMessage((String)o);
                }
            });

            
        }
        @Override protected Object doInBackground() {
            // Your Task's code here.  This method runs
            // on a background thread, so don't reference
            // the Swing GUI from here.
            
            pController.databaseLoad();

            return null;  // return your result
        }
        @Override protected void succeeded(Object result) {
            // Runs on the EDT.  Update the GUI based on
            // the result computed by doInBackground().

            System.out.println("succeeded");
        }

        // inputBlocker: null -> org.jdesktop.application.DefaultInputBlocker@2a2a2ae9
                    // taskService: null -> org.jdesktop.application.TaskService@77d433c1
                    // started: false -> true
                    // state: PENDING -> STARTED
                    // taskService: org.jdesktop.application.TaskService@77d433c1 -> null
                    // done: false -> true
                    // completed: false -> true
        
        @Override
        protected void cancelled() {
            System.out.println("cancelled");
            try {
                Thread.sleep(5000);
            } catch(Exception ex) {

            }
        }
    }

    @Action(block = Task.BlockingScope.WINDOW)
    public Task actionDatabaseSave() {
        return new ActionDatabaseSaveTask(getApplication());
    }

    private class ActionDatabaseSaveTask extends org.jdesktop.application.Task<Object, Void> {
        ActionDatabaseSaveTask(org.jdesktop.application.Application app) {
            // Runs on the EDT.  Copy GUI state that
            // doInBackground() depends on from parameters
            // to ActionDatabaseSaveTask fields, here.
            super(app);

            this.setUserCanCancel(false);

            pController.add(new Notification() {
                @Override
                public void init() {
                    Type = "PROGRESS";
                }

                @Override
                public void callback(Object o) {
                    if(o.getClass().equals(Float.class))
                        setProgress((Float)o);
                    else if(o.getClass().equals(String.class))
                        setMessage((String)o);
                }
            });
        }
        @Override protected Object doInBackground() {
            // Your Task's code here.  This method runs
            // on a background thread, so don't reference
            // the Swing GUI from here.

            pController.databaseSave();

            return null;  // return your result
        }
        @Override protected void succeeded(Object result) {
            // Runs on the EDT.  Update the GUI based on
            // the result computed by doInBackground().
        }
    }

    
    @Action(block = Task.BlockingScope.WINDOW)
    public Task actionNetworkConnect() {
        return new ActionNetworkConnectTask(getApplication());
    }

    private class ActionNetworkConnectTask extends org.jdesktop.application.Task<Object, Void> {
        ActionNetworkConnectTask(org.jdesktop.application.Application app) {
            // Runs on the EDT.  Copy GUI state that
            // doInBackground() depends on from parameters
            // to ActionNetworkConnectTask fields, here.
            super(app);

            this.setUserCanCancel(false);

            pController.add(new Notification() {
                @Override
                public void init() {
                    Type = "PROGRESS";
                }

                @Override
                public void callback(Object o) {
                    if(o.getClass().equals(Float.class))
                        setProgress((Float)o);
                    else if(o.getClass().equals(String.class))
                        setMessage((String)o);
                }
            });
        }
        @Override protected Object doInBackground() {
            // Your Task's code here.  This method runs
            // on a background thread, so don't reference
            // the Swing GUI from here.

            pController.networkConnect();

            return null;  // return your result
        }
        @Override protected void succeeded(Object result) {
            // Runs on the EDT.  Update the GUI based on
            // the result computed by doInBackground().
        }
    }

                @Action(block = Task.BlockingScope.WINDOW)
    public Task actionNetworkTransferMO() {
        return new ActionNetworkTransferMOTask(getApplication());
    }

    private class ActionNetworkTransferMOTask extends org.jdesktop.application.Task<Object, Void> {
        ActionNetworkTransferMOTask(org.jdesktop.application.Application app) {
            // Runs on the EDT.  Copy GUI state that
            // doInBackground() depends on from parameters
            // to ActionNetworkTransferMOTask fields, here.
            super(app);

            this.setUserCanCancel(false);

            pController.add(new Notification() {
                @Override
                public void init() {
                    Type = "PROGRESS";
                }

                @Override
                public void callback(Object o) {
                    if(o.getClass().equals(Float.class))
                        setProgress((Float)o);
                    else if(o.getClass().equals(String.class))
                        setMessage((String)o);
                }
            });
        }
        @Override protected Object doInBackground() {
            // Your Task's code here.  This method runs
            // on a background thread, so don't reference
            // the Swing GUI from here.

            pController.networkTransferMO();

            return null;  // return your result
        }
        @Override protected void succeeded(Object result) {
            // Runs on the EDT.  Update the GUI based on
            // the result computed by doInBackground().
        }
    }

        @Action(block = Task.BlockingScope.WINDOW)
    public Task actionNetworkTransferMT() {
        return new ActionNetworkTransferMTTask(getApplication());
    }

    private class ActionNetworkTransferMTTask extends org.jdesktop.application.Task<Object, Void> {
        ActionNetworkTransferMTTask(org.jdesktop.application.Application app) {
            // Runs on the EDT.  Copy GUI state that
            // doInBackground() depends on from parameters
            // to ActionNetworkTransferMTTask fields, here.
            super(app);

            this.setUserCanCancel(false);

            pController.add(new Notification() {
                @Override
                public void init() {
                    Type = "PROGRESS";
                }

                @Override
                public void callback(Object o) {
                    if(o.getClass().equals(Float.class))
                        setProgress((Float)o);
                    else if(o.getClass().equals(String.class))
                        setMessage((String)o);
                }
            });
        }
        @Override protected Object doInBackground() {
            // Your Task's code here.  This method runs
            // on a background thread, so don't reference
            // the Swing GUI from here.

            pController.networkTransferMT();

            return null;  // return your result
        }
        @Override protected void succeeded(Object result) {
            // Runs on the EDT.  Update the GUI based on
            // the result computed by doInBackground().
        }
    }

                @Action(block = Task.BlockingScope.WINDOW)
    public Task actionNetworkFilesystem() {
        return new ActionNetworkFilesystemTask(getApplication());
    }

    private class ActionNetworkFilesystemTask extends org.jdesktop.application.Task<Object, Void> {
        ActionNetworkFilesystemTask(org.jdesktop.application.Application app) {
            // Runs on the EDT.  Copy GUI state that
            // doInBackground() depends on from parameters
            // to ActionNetworkFilesystemTask fields, here.
            super(app);

            this.setUserCanCancel(false);

            pController.add(new Notification() {
                @Override
                public void init() {
                    Type = "PROGRESS";
                }

                @Override
                public void callback(Object o) {
                    if(o.getClass().equals(Float.class))
                        setProgress((Float)o);
                    else if(o.getClass().equals(String.class))
                        setMessage((String)o);
                }
            });
        }
        @Override protected Object doInBackground() {
            // Your Task's code here.  This method runs
            // on a background thread, so don't reference
            // the Swing GUI from here.

            pController.networkFilesystem();

            return null;  // return your result
        }
        @Override protected void succeeded(Object result) {
            // Runs on the EDT.  Update the GUI based on
            // the result computed by doInBackground().
        }
    }

                @Action(block = Task.BlockingScope.WINDOW)
    public Task actionJobParse() {
        return new ActionJobParseTask(getApplication());
    }

    private class ActionJobParseTask extends org.jdesktop.application.Task<Object, Void> {
        ActionJobParseTask(org.jdesktop.application.Application app) {
            // Runs on the EDT.  Copy GUI state that
            // doInBackground() depends on from parameters
            // to ActionJobParseTask fields, here.
            super(app);

            this.setUserCanCancel(false);

            pController.add(new Notification() {
                @Override
                public void init() {
                    Type = "PROGRESS";
                }

                @Override
                public void callback(Object o) {
                    if(o.getClass().equals(Float.class))
                        setProgress((Float)o);
                    else if(o.getClass().equals(String.class))
                        setMessage((String)o);
                }
            });
        }
        @Override protected Object doInBackground() {
            // Your Task's code here.  This method runs
            // on a background thread, so don't reference
            // the Swing GUI from here.

            pController.jobParse();

            return null;  // return your result
        }
        @Override protected void succeeded(Object result) {
            // Runs on the EDT.  Update the GUI based on
            // the result computed by doInBackground().
        }
    }

                @Action(block = Task.BlockingScope.WINDOW)
    public Task actionJobArts() {
        return new ActionJobArtsTask(getApplication());
    }

    private class ActionJobArtsTask extends org.jdesktop.application.Task<Object, Void> {
        ActionJobArtsTask(org.jdesktop.application.Application app) {
            // Runs on the EDT.  Copy GUI state that
            // doInBackground() depends on from parameters
            // to ActionJobArtsTask fields, here.
            super(app);

            this.setUserCanCancel(false);

            pController.add(new Notification() {
                @Override
                public void init() {
                    Type = "PROGRESS";
                }

                @Override
                public void callback(Object o) {
                    if(o.getClass().equals(Float.class))
                        setProgress((Float)o);
                    else if(o.getClass().equals(String.class))
                        setMessage((String)o);
                }
            });
        }
        @Override protected Object doInBackground() {
            // Your Task's code here.  This method runs
            // on a background thread, so don't reference
            // the Swing GUI from here.

            pController.jobArts();

            return null;  // return your result
        }
        @Override protected void succeeded(Object result) {
            // Runs on the EDT.  Update the GUI based on
            // the result computed by doInBackground().
        }
    }


    
    private static Console jFrameConsole = null;
    // Variables declaration - do not modify//GEN-BEGIN:variables
    private javax.swing.JLabel descLabel;
    private javax.swing.JButton jButton1;
    private javax.swing.JButton jButton3;
    private javax.swing.JButton jButton5;
    private javax.swing.JButton jButtonArt;
    private javax.swing.JButton jButtonBackdropOpen;
    private javax.swing.JButton jButtonConnect;
    private javax.swing.JButton jButtonDownloadFromBox;
    private javax.swing.JButton jButtonParse;
    private javax.swing.JButton jButtonPosterCancel;
    private javax.swing.JButton jButtonPosterOpen;
    private javax.swing.JButton jButtonPosterSave;
    private javax.swing.JButton jButtonSync;
    private javax.swing.JButton jButtonUploadToBox;
    private javax.swing.JComboBox jComboBoxBoxinfo;
    private javax.swing.JFrame jImportBackdrop;
    private javax.swing.JFrame jImportPoster;
    private javax.swing.JFileChooser jJPEGOpen;
    private javax.swing.JLabel jLabelBackdrop1;
    private javax.swing.JLabel jLabelDetailsBackdrop;
    private javax.swing.JLabel jLabelDetailsPlot;
    private javax.swing.JLabel jLabelDetailsPoster;
    private javax.swing.JLabel jLabelDetailsStar1;
    private javax.swing.JLabel jLabelDetailsStar10;
    private javax.swing.JLabel jLabelDetailsStar2;
    private javax.swing.JLabel jLabelDetailsStar3;
    private javax.swing.JLabel jLabelDetailsStar4;
    private javax.swing.JLabel jLabelDetailsStar5;
    private javax.swing.JLabel jLabelDetailsStar6;
    private javax.swing.JLabel jLabelDetailsStar7;
    private javax.swing.JLabel jLabelDetailsStar8;
    private javax.swing.JLabel jLabelDetailsStar9;
    private javax.swing.JLabel jLabelDetailsTagline;
    private javax.swing.JLabel jLabelDetailsTitle;
    private javax.swing.JLabel jLabelDetailsYear;
    private javax.swing.JLabel jLabelPoster1;
    private javax.swing.JMenu jMenu1;
    private javax.swing.JMenu jMenuDebug;
    private javax.swing.JMenuItem jMenuItem1;
    private javax.swing.JMenuItem jMenuItem10;
    private javax.swing.JMenuItem jMenuItem11;
    private javax.swing.JMenuItem jMenuItem2;
    private javax.swing.JMenuItem jMenuItem3;
    private javax.swing.JMenuItem jMenuItem4;
    private javax.swing.JMenuItem jMenuItem5;
    private javax.swing.JMenuItem jMenuItem6;
    private javax.swing.JMenuItem jMenuItem7;
    private javax.swing.JMenuItem jMenuItem8;
    private javax.swing.JMenuItem jMenuItem9;
    private javax.swing.JMenuItem jMenuItemSettings;
    private javax.swing.JMenuItem jMenuItemalternatives;
    private javax.swing.JPanel jPanel2;
    private javax.swing.JPanel jPanelDetails;
    private javax.swing.JPanel jPanelMovies;
    private javax.swing.JPanel jPanelSeries;
    private javax.swing.JScrollPane jScrollPane1;
    private javax.swing.JScrollPane jScrollPane2;
    private javax.swing.JScrollPane jScrollPane3;
    private javax.swing.JScrollPane jScrollPane5;
    private javax.swing.JScrollPane jScrollPane6;
    private javax.swing.JScrollPane jScrollPaneDetailsPlot;
    private javax.swing.JToolBar.Separator jSeparator3;
    private javax.swing.JPopupMenu.Separator jSeparator5;
    private javax.swing.JPopupMenu.Separator jSeparator6;
    private javax.swing.JSplitPane jSplitPane1;
    private javax.swing.JSplitPane jSplitPane2;
    private javax.swing.JTabbedPane jTabbedPane;
    private javax.swing.JTable jTableEpisodes;
    private javax.swing.JTable jTableMovies;
    private javax.swing.JTable jTableSeries;
    private javax.swing.JTable jTableTasks;
    private javax.swing.JTextArea jTextAreaDescription;
    private javax.swing.JTextArea jTextAreaDetailsPlot;
    private javax.swing.JToolBar jToolBar1;
    private javax.swing.JPanel mainPanel;
    private javax.swing.JMenuBar menuBar;
    private javax.swing.JProgressBar progressBar;
    private javax.swing.JLabel statusAnimationLabel;
    private javax.swing.JLabel statusMessageLabel;
    private javax.swing.JPanel statusPanel;
    private javax.swing.JFrame statusPopup;
    private javax.swing.JMenuItem updateMenuItem;
    // End of variables declaration//GEN-END:variables
    private final Timer messageTimer;
    private final Timer busyIconTimer;
    private final Icon idleIcon;
    private final Icon[] busyIcons = new Icon[15];
    private int busyIconIndex = 0;
    private JDialog aboutBox;
    private JDialog importBackdrop;
    private boolean BoxIsConnected = false;
    private MediaInfo BackdropWork;
    private MediaInfo PosterWork;
}
