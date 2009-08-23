/*
 * ValerieView.java
 */

package valerie;

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
import java.awt.image.BufferedImage;
import java.io.File;
import java.io.FileWriter;
import java.io.Writer;
import java.util.Calendar;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import javax.imageio.ImageIO;
import javax.swing.Icon;
import javax.swing.Timer;
import javax.swing.ImageIcon;
import javax.swing.JDialog;
import javax.swing.JFrame;
import javax.swing.table.DefaultTableModel;
/**
 * The application's main frame.
 */
public class ValerieView extends FrameView {

    valerie.tools.Properties properties = null;

    class UIOutputHandler extends OutputHandler {
        public void print(String s) {
            statusMessageLabel.setText(s);
        }

        public void setWorking(boolean s) {
            jButtonSync.setEnabled(!s);
        }

        public void setProgress(int s) {
            progressBar.setValue(s);
        }
    }

    public ValerieView(SingleFrameApplication app) {
        super(app);

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
                    String text = (String)(evt.getNewValue());
                    statusMessageLabel.setText((text == null) ? "" : text);
                    messageTimer.restart();
                } else if ("progress".equals(propertyName)) {
                    int value = (Integer)(evt.getNewValue());
                    progressBar.setVisible(true);
                    //progressBar.setIndeterminate(false);
                    //progressBar.setValue(value);
                }
            }
        });

        //MY OWN CODE
        properties = new valerie.tools.Properties();
        initPathsTables();
        initFilters();
        Logger.add(new UIOutputHandler());

    }

    private void initFilters() {

        String filter = properties.getPropertyString("FILTER_MOVIES");
        if(filter.length() == 0)
        {
            filter = "mkv|avi|ts|m2ts|vob";
            properties.setProperty("FILTER_MOVIES", filter);
        }
        jTextFieldTypes.setText(filter);

        filter = properties.getPropertyString("FILTER_SERIES");
        if(filter.length() == 0)
        {
            filter = "mkv|avi|ts|m2ts|vob";
            properties.setProperty("FILTER_SERIES", filter);
        }
        jTextFieldTypesSeries.setText(filter);

    }

    private void initPathsTables() {
        String[] pathsMovies = properties.getPropertyString("PATHS_MOVIES").split("\\|");
        ((DefaultTableModel) jTablePaths.getModel()).setRowCount(pathsMovies.length);

        int iteratorMovies = 0;
        for(String pathMovies : pathsMovies) {
                jTablePaths.setValueAt(pathMovies, iteratorMovies, 1);
                jTablePaths.setValueAt(true, iteratorMovies++, 0);
        }


        String[] pathsSeries = properties.getPropertyString("PATHS_SERIES").split("\\|");
        ((DefaultTableModel) jTablePathsSeries.getModel()).setRowCount(pathsSeries.length);

        int iteratorSeries = 0;
        for(String pathSeries : pathsSeries) {
                jTablePathsSeries.setValueAt(pathSeries, iteratorSeries, 1);
                jTablePathsSeries.setValueAt(true, iteratorSeries++, 0);
        }
    }

    private void savePathsTables() {
            String pathsMovies = "";
            for(int i = 0; i < jTablePaths.getRowCount(); i++)
                pathsMovies += jTablePaths.getValueAt(i, 1) + "|";

            properties.setProperty("PATHS_MOVIES", pathsMovies);


            String pathsSeries = "";
            for(int i = 0; i < jTablePathsSeries.getRowCount(); i++)
                pathsSeries += jTablePathsSeries.getValueAt(i, 1) + "|";

            properties.setProperty("PATHS_SERIES", pathsSeries);

            properties.save();
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
        jLabel7 = new javax.swing.JLabel();
        jButtonSync = new javax.swing.JButton();
        jLabel8 = new javax.swing.JLabel();
        jButtonParse = new javax.swing.JButton();
        jLabel9 = new javax.swing.JLabel();
        jButtonArt = new javax.swing.JButton();
        jLabel10 = new javax.swing.JLabel();
        jButtonUpload = new javax.swing.JButton();
        jTabbedPane = new javax.swing.JTabbedPane();
        jPanelMovies = new javax.swing.JPanel();
        jScrollPane1 = new javax.swing.JScrollPane();
        jTableFilelist = new javax.swing.JTable();
        jScrollPane2 = new javax.swing.JScrollPane();
        jTablePaths = new javax.swing.JTable();
        jButtonAdd = new javax.swing.JButton();
        jSeparator1 = new javax.swing.JSeparator();
        jButtonDelete = new javax.swing.JButton();
        jTextFieldTypes = new javax.swing.JTextField();
        jLabel1 = new javax.swing.JLabel();
        jPanelInfosMovies = new javax.swing.JPanel();
        jLabelPosterMovies = new javax.swing.JLabel();
        jLabelBackdropMovies = new javax.swing.JLabel();
        jScrollPane3 = new javax.swing.JScrollPane();
        jTextAreaDescriptionMovies = new javax.swing.JTextArea();
        jPanelSeries = new javax.swing.JPanel();
        jScrollPane4 = new javax.swing.JScrollPane();
        jTablePathsSeries = new javax.swing.JTable();
        jButtonAdd1 = new javax.swing.JButton();
        jButtonDelete1 = new javax.swing.JButton();
        jLabel2 = new javax.swing.JLabel();
        jTextFieldTypesSeries = new javax.swing.JTextField();
        jSeparator2 = new javax.swing.JSeparator();
        jPanelInfos = new javax.swing.JPanel();
        jScrollPane7 = new javax.swing.JScrollPane();
        jTextAreaDescriptionSeries = new javax.swing.JTextArea();
        jLabel3 = new javax.swing.JLabel();
        jLabel4 = new javax.swing.JLabel();
        jLabel5 = new javax.swing.JLabel();
        jLabel6 = new javax.swing.JLabel();
        jPanelTables = new javax.swing.JPanel();
        jScrollPane6 = new javax.swing.JScrollPane();
        jTableSeries = new javax.swing.JTable();
        jScrollPane5 = new javax.swing.JScrollPane();
        jTableFilelistEpisodes = new javax.swing.JTable();
        jLabelConnectionStatus = new javax.swing.JLabel();
        menuBar = new javax.swing.JMenuBar();
        javax.swing.JMenu fileMenu = new javax.swing.JMenu();
        javax.swing.JMenuItem exitMenuItem = new javax.swing.JMenuItem();
        javax.swing.JMenu helpMenu = new javax.swing.JMenu();
        javax.swing.JMenuItem aboutMenuItem = new javax.swing.JMenuItem();
        statusPanel = new javax.swing.JPanel();
        javax.swing.JSeparator statusPanelSeparator = new javax.swing.JSeparator();
        statusMessageLabel = new javax.swing.JLabel();
        statusAnimationLabel = new javax.swing.JLabel();
        progressBar = new javax.swing.JProgressBar();

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

        jLabel7.setIcon(resourceMap.getIcon("jLabel7.icon")); // NOI18N
        jLabel7.setText(resourceMap.getString("jLabel7.text")); // NOI18N
        jLabel7.setName("jLabel7"); // NOI18N
        jToolBar1.add(jLabel7);

        jButtonSync.setAction(actionMap.get("syncFilelist")); // NOI18N
        jButtonSync.setText(resourceMap.getString("jButtonSync.text")); // NOI18N
        jButtonSync.setFocusable(false);
        jButtonSync.setHorizontalTextPosition(javax.swing.SwingConstants.CENTER);
        jButtonSync.setName("jButtonSync"); // NOI18N
        jButtonSync.setVerticalTextPosition(javax.swing.SwingConstants.BOTTOM);
        jToolBar1.add(jButtonSync);

        jLabel8.setIcon(resourceMap.getIcon("jLabel8.icon")); // NOI18N
        jLabel8.setText(resourceMap.getString("jLabel8.text")); // NOI18N
        jLabel8.setName("jLabel8"); // NOI18N
        jToolBar1.add(jLabel8);

        jButtonParse.setAction(actionMap.get("parseFilelist")); // NOI18N
        jButtonParse.setText(resourceMap.getString("jButtonParse.text")); // NOI18N
        jButtonParse.setFocusable(false);
        jButtonParse.setHorizontalTextPosition(javax.swing.SwingConstants.CENTER);
        jButtonParse.setName("jButtonParse"); // NOI18N
        jButtonParse.setVerticalTextPosition(javax.swing.SwingConstants.BOTTOM);
        jToolBar1.add(jButtonParse);

        jLabel9.setIcon(resourceMap.getIcon("jLabel9.icon")); // NOI18N
        jLabel9.setText(resourceMap.getString("jLabel9.text")); // NOI18N
        jLabel9.setName("jLabel9"); // NOI18N
        jToolBar1.add(jLabel9);

        jButtonArt.setAction(actionMap.get("getArt")); // NOI18N
        jButtonArt.setText(resourceMap.getString("jButtonArt.text")); // NOI18N
        jButtonArt.setFocusable(false);
        jButtonArt.setHorizontalTextPosition(javax.swing.SwingConstants.CENTER);
        jButtonArt.setName("jButtonArt"); // NOI18N
        jButtonArt.setVerticalTextPosition(javax.swing.SwingConstants.BOTTOM);
        jToolBar1.add(jButtonArt);

        jLabel10.setIcon(resourceMap.getIcon("jLabel10.icon")); // NOI18N
        jLabel10.setText(resourceMap.getString("jLabel10.text")); // NOI18N
        jLabel10.setName("jLabel10"); // NOI18N
        jToolBar1.add(jLabel10);

        jButtonUpload.setAction(actionMap.get("uploadFiles")); // NOI18N
        jButtonUpload.setText(resourceMap.getString("jButtonUpload.text")); // NOI18N
        jButtonUpload.setFocusable(false);
        jButtonUpload.setHorizontalTextPosition(javax.swing.SwingConstants.CENTER);
        jButtonUpload.setName("jButtonUpload"); // NOI18N
        jButtonUpload.setVerticalTextPosition(javax.swing.SwingConstants.BOTTOM);
        jToolBar1.add(jButtonUpload);

        jTabbedPane.setName("jTabbedPane"); // NOI18N

        jPanelMovies.setName("jPanelMovies"); // NOI18N

        jScrollPane1.setName("jScrollPane1"); // NOI18N

        jTableFilelist.setModel(new javax.swing.table.DefaultTableModel(
            new Object [][] {
                {null, null, null, null, null, null, null}
            },
            new String [] {
                "Filename", "SearchString", "Title", "Year", "ImdbId", "Use", "ID"
            }
        ) {
            Class[] types = new Class [] {
                java.lang.String.class, java.lang.String.class, java.lang.String.class, java.lang.String.class, java.lang.Integer.class, java.lang.Boolean.class, java.lang.String.class
            };
            boolean[] canEdit = new boolean [] {
                false, true, false, false, false, true, false
            };

            public Class getColumnClass(int columnIndex) {
                return types [columnIndex];
            }

            public boolean isCellEditable(int rowIndex, int columnIndex) {
                return canEdit [columnIndex];
            }
        });
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
        jTableFilelist.getColumnModel().getColumn(0).setPreferredWidth(140);
        jTableFilelist.getColumnModel().getColumn(0).setHeaderValue(resourceMap.getString("jTableFilelist.columnModel.title0")); // NOI18N
        jTableFilelist.getColumnModel().getColumn(1).setResizable(false);
        jTableFilelist.getColumnModel().getColumn(1).setHeaderValue(resourceMap.getString("jTableFilelist.columnModel.title3")); // NOI18N
        jTableFilelist.getColumnModel().getColumn(2).setResizable(false);
        jTableFilelist.getColumnModel().getColumn(2).setPreferredWidth(150);
        jTableFilelist.getColumnModel().getColumn(2).setHeaderValue(resourceMap.getString("jTableFilelist.columnModel.title1")); // NOI18N
        jTableFilelist.getColumnModel().getColumn(3).setResizable(false);
        jTableFilelist.getColumnModel().getColumn(3).setPreferredWidth(30);
        jTableFilelist.getColumnModel().getColumn(3).setHeaderValue(resourceMap.getString("jTableFilelist.columnModel.title2")); // NOI18N
        jTableFilelist.getColumnModel().getColumn(4).setResizable(false);
        jTableFilelist.getColumnModel().getColumn(4).setPreferredWidth(40);
        jTableFilelist.getColumnModel().getColumn(4).setHeaderValue(resourceMap.getString("jTableFilelist.columnModel.title4")); // NOI18N
        jTableFilelist.getColumnModel().getColumn(5).setResizable(false);
        jTableFilelist.getColumnModel().getColumn(5).setPreferredWidth(10);
        jTableFilelist.getColumnModel().getColumn(5).setHeaderValue(resourceMap.getString("jTableFilelist.columnModel.title5")); // NOI18N
        jTableFilelist.getColumnModel().getColumn(6).setResizable(false);
        jTableFilelist.getColumnModel().getColumn(6).setPreferredWidth(10);
        jTableFilelist.getColumnModel().getColumn(6).setHeaderValue(resourceMap.getString("jTableFilelist.columnModel.title6")); // NOI18N

        jScrollPane2.setName("jScrollPane2"); // NOI18N

        jTablePaths.setModel(new javax.swing.table.DefaultTableModel(
            new Object [][] {

            },
            new String [] {
                "Enabled", "Path"
            }
        ) {
            Class[] types = new Class [] {
                java.lang.Boolean.class, java.lang.String.class
            };

            public Class getColumnClass(int columnIndex) {
                return types [columnIndex];
            }
        });
        jTablePaths.setName("jTablePaths"); // NOI18N
        jTablePaths.getTableHeader().setReorderingAllowed(false);
        jScrollPane2.setViewportView(jTablePaths);
        jTablePaths.getColumnModel().getColumn(0).setMinWidth(50);
        jTablePaths.getColumnModel().getColumn(0).setPreferredWidth(50);
        jTablePaths.getColumnModel().getColumn(0).setMaxWidth(50);
        jTablePaths.getColumnModel().getColumn(0).setHeaderValue(resourceMap.getString("jTable2.columnModel.title0")); // NOI18N
        jTablePaths.getColumnModel().getColumn(1).setHeaderValue(resourceMap.getString("jTable2.columnModel.title1")); // NOI18N

        jButtonAdd.setAction(actionMap.get("addLine")); // NOI18N
        jButtonAdd.setText(resourceMap.getString("jButtonAdd.text")); // NOI18N
        jButtonAdd.setName("jButtonAdd"); // NOI18N

        jSeparator1.setName("jSeparator1"); // NOI18N

        jButtonDelete.setText(resourceMap.getString("jButtonDelete.text")); // NOI18N
        jButtonDelete.setName("jButtonDelete"); // NOI18N

        jTextFieldTypes.setText(resourceMap.getString("jTextFieldTypes.text")); // NOI18N
        jTextFieldTypes.setName("jTextFieldTypes"); // NOI18N
        jTextFieldTypes.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                jTextFieldTypesActionPerformed(evt);
            }
        });

        jLabel1.setText(resourceMap.getString("jLabel1.text")); // NOI18N
        jLabel1.setName("jLabel1"); // NOI18N

        jPanelInfosMovies.setName("jPanelInfosMovies"); // NOI18N

        jLabelPosterMovies.setText(resourceMap.getString("jLabelPosterMovies.text")); // NOI18N
        jLabelPosterMovies.setBorder(javax.swing.BorderFactory.createLineBorder(new java.awt.Color(0, 0, 0)));
        jLabelPosterMovies.setName("jLabelPosterMovies"); // NOI18N

        jLabelBackdropMovies.setText(resourceMap.getString("jLabelBackdropMovies.text")); // NOI18N
        jLabelBackdropMovies.setBorder(javax.swing.BorderFactory.createLineBorder(new java.awt.Color(0, 0, 0)));
        jLabelBackdropMovies.setName("jLabelBackdropMovies"); // NOI18N

        javax.swing.GroupLayout jPanelInfosMoviesLayout = new javax.swing.GroupLayout(jPanelInfosMovies);
        jPanelInfosMovies.setLayout(jPanelInfosMoviesLayout);
        jPanelInfosMoviesLayout.setHorizontalGroup(
            jPanelInfosMoviesLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanelInfosMoviesLayout.createSequentialGroup()
                .addComponent(jLabelPosterMovies, javax.swing.GroupLayout.PREFERRED_SIZE, 215, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                .addComponent(jLabelBackdropMovies, javax.swing.GroupLayout.DEFAULT_SIZE, 535, Short.MAX_VALUE))
        );
        jPanelInfosMoviesLayout.setVerticalGroup(
            jPanelInfosMoviesLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addComponent(jLabelPosterMovies, javax.swing.GroupLayout.DEFAULT_SIZE, 283, Short.MAX_VALUE)
            .addComponent(jLabelBackdropMovies, javax.swing.GroupLayout.DEFAULT_SIZE, 283, Short.MAX_VALUE)
        );

        jScrollPane3.setName("jScrollPane3"); // NOI18N

        jTextAreaDescriptionMovies.setColumns(20);
        jTextAreaDescriptionMovies.setRows(5);
        jTextAreaDescriptionMovies.setName("jTextAreaDescriptionMovies"); // NOI18N
        jScrollPane3.setViewportView(jTextAreaDescriptionMovies);

        javax.swing.GroupLayout jPanelMoviesLayout = new javax.swing.GroupLayout(jPanelMovies);
        jPanelMovies.setLayout(jPanelMoviesLayout);
        jPanelMoviesLayout.setHorizontalGroup(
            jPanelMoviesLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(javax.swing.GroupLayout.Alignment.TRAILING, jPanelMoviesLayout.createSequentialGroup()
                .addContainerGap()
                .addGroup(jPanelMoviesLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.TRAILING)
                    .addComponent(jScrollPane1, javax.swing.GroupLayout.Alignment.LEADING, javax.swing.GroupLayout.DEFAULT_SIZE, 1130, Short.MAX_VALUE)
                    .addComponent(jSeparator1, javax.swing.GroupLayout.DEFAULT_SIZE, 1130, Short.MAX_VALUE)
                    .addComponent(jScrollPane2, javax.swing.GroupLayout.DEFAULT_SIZE, 1130, Short.MAX_VALUE)
                    .addGroup(jPanelMoviesLayout.createSequentialGroup()
                        .addComponent(jLabel1)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                        .addComponent(jTextFieldTypes, javax.swing.GroupLayout.PREFERRED_SIZE, 192, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED, 781, Short.MAX_VALUE)
                        .addComponent(jButtonDelete)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                        .addComponent(jButtonAdd))
                    .addGroup(javax.swing.GroupLayout.Alignment.LEADING, jPanelMoviesLayout.createSequentialGroup()
                        .addComponent(jScrollPane3, javax.swing.GroupLayout.PREFERRED_SIZE, 364, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                        .addComponent(jPanelInfosMovies, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)))
                .addContainerGap())
        );
        jPanelMoviesLayout.setVerticalGroup(
            jPanelMoviesLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanelMoviesLayout.createSequentialGroup()
                .addContainerGap()
                .addComponent(jScrollPane2, javax.swing.GroupLayout.PREFERRED_SIZE, 69, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addGroup(jPanelMoviesLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addGroup(jPanelMoviesLayout.createSequentialGroup()
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                        .addGroup(jPanelMoviesLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                            .addComponent(jButtonAdd)
                            .addComponent(jButtonDelete)))
                    .addGroup(jPanelMoviesLayout.createSequentialGroup()
                        .addGap(10, 10, 10)
                        .addGroup(jPanelMoviesLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                            .addComponent(jLabel1)
                            .addComponent(jTextFieldTypes, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))))
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addComponent(jSeparator1, javax.swing.GroupLayout.PREFERRED_SIZE, 10, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addGroup(jPanelMoviesLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING, false)
                    .addComponent(jScrollPane3)
                    .addComponent(jPanelInfosMovies, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE))
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addComponent(jScrollPane1, javax.swing.GroupLayout.DEFAULT_SIZE, 314, Short.MAX_VALUE)
                .addContainerGap())
        );

        jTabbedPane.addTab(resourceMap.getString("jPanelMovies.TabConstraints.tabTitle"), jPanelMovies); // NOI18N

        jPanelSeries.setName("jPanelSeries"); // NOI18N
        jPanelSeries.setPreferredSize(new java.awt.Dimension(586, 667));

        jScrollPane4.setName("jScrollPane4"); // NOI18N

        jTablePathsSeries.setModel(new javax.swing.table.DefaultTableModel(
            new Object [][] {

            },
            new String [] {
                "Enabled", "Path"
            }
        ) {
            Class[] types = new Class [] {
                java.lang.Boolean.class, java.lang.String.class
            };

            public Class getColumnClass(int columnIndex) {
                return types [columnIndex];
            }
        });
        jTablePathsSeries.setName("jTablePathsSeries"); // NOI18N
        jTablePathsSeries.getTableHeader().setReorderingAllowed(false);
        jScrollPane4.setViewportView(jTablePathsSeries);
        jTablePathsSeries.getColumnModel().getColumn(0).setMinWidth(50);
        jTablePathsSeries.getColumnModel().getColumn(0).setPreferredWidth(50);
        jTablePathsSeries.getColumnModel().getColumn(0).setMaxWidth(50);
        jTablePathsSeries.getColumnModel().getColumn(0).setHeaderValue(resourceMap.getString("jTable2.columnModel.title0")); // NOI18N
        jTablePathsSeries.getColumnModel().getColumn(1).setHeaderValue(resourceMap.getString("jTable2.columnModel.title1")); // NOI18N

        jButtonAdd1.setAction(actionMap.get("addLine")); // NOI18N
        jButtonAdd1.setText(resourceMap.getString("jButtonAdd1.text")); // NOI18N
        jButtonAdd1.setName("jButtonAdd1"); // NOI18N

        jButtonDelete1.setText(resourceMap.getString("jButtonDelete1.text")); // NOI18N
        jButtonDelete1.setName("jButtonDelete1"); // NOI18N

        jLabel2.setText(resourceMap.getString("jLabel2.text")); // NOI18N
        jLabel2.setName("jLabel2"); // NOI18N

        jTextFieldTypesSeries.setText(resourceMap.getString("jTextFieldTypesSeries.text")); // NOI18N
        jTextFieldTypesSeries.setName("jTextFieldTypesSeries"); // NOI18N
        jTextFieldTypesSeries.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                jTextFieldTypesSeriesActionPerformed(evt);
            }
        });

        jSeparator2.setName("jSeparator2"); // NOI18N

        jPanelInfos.setName("jPanelInfos"); // NOI18N

        jScrollPane7.setName("jScrollPane7"); // NOI18N

        jTextAreaDescriptionSeries.setColumns(20);
        jTextAreaDescriptionSeries.setRows(5);
        jTextAreaDescriptionSeries.setName("jTextAreaDescriptionSeries"); // NOI18N
        jScrollPane7.setViewportView(jTextAreaDescriptionSeries);

        jLabel3.setText(resourceMap.getString("jLabel3.text")); // NOI18N
        jLabel3.setBorder(javax.swing.BorderFactory.createLineBorder(new java.awt.Color(0, 0, 0)));
        jLabel3.setName("jLabel3"); // NOI18N

        jLabel4.setText(resourceMap.getString("jLabel4.text")); // NOI18N
        jLabel4.setBorder(javax.swing.BorderFactory.createLineBorder(new java.awt.Color(0, 0, 0)));
        jLabel4.setName("jLabel4"); // NOI18N

        jLabel5.setText(resourceMap.getString("jLabel5.text")); // NOI18N
        jLabel5.setBorder(javax.swing.BorderFactory.createLineBorder(new java.awt.Color(0, 0, 0)));
        jLabel5.setName("jLabel5"); // NOI18N

        jLabel6.setText(resourceMap.getString("jLabel6.text")); // NOI18N
        jLabel6.setBorder(javax.swing.BorderFactory.createLineBorder(new java.awt.Color(0, 0, 0)));
        jLabel6.setName("jLabel6"); // NOI18N

        javax.swing.GroupLayout jPanelInfosLayout = new javax.swing.GroupLayout(jPanelInfos);
        jPanelInfos.setLayout(jPanelInfosLayout);
        jPanelInfosLayout.setHorizontalGroup(
            jPanelInfosLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanelInfosLayout.createSequentialGroup()
                .addComponent(jScrollPane7, javax.swing.GroupLayout.PREFERRED_SIZE, 383, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                .addGroup(jPanelInfosLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING, false)
                    .addComponent(jLabel6, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                    .addComponent(jLabel5, javax.swing.GroupLayout.PREFERRED_SIZE, 279, javax.swing.GroupLayout.PREFERRED_SIZE))
                .addGap(18, 18, 18)
                .addGroup(jPanelInfosLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.TRAILING)
                    .addComponent(jLabel4, javax.swing.GroupLayout.PREFERRED_SIZE, 199, javax.swing.GroupLayout.PREFERRED_SIZE)
                    .addComponent(jLabel3, javax.swing.GroupLayout.PREFERRED_SIZE, 406, javax.swing.GroupLayout.PREFERRED_SIZE)))
        );
        jPanelInfosLayout.setVerticalGroup(
            jPanelInfosLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanelInfosLayout.createSequentialGroup()
                .addComponent(jLabel3, javax.swing.GroupLayout.PREFERRED_SIZE, 80, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addComponent(jLabel4, javax.swing.GroupLayout.DEFAULT_SIZE, 197, Short.MAX_VALUE))
            .addGroup(jPanelInfosLayout.createSequentialGroup()
                .addComponent(jLabel6, javax.swing.GroupLayout.DEFAULT_SIZE, 112, Short.MAX_VALUE)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addComponent(jLabel5, javax.swing.GroupLayout.PREFERRED_SIZE, 154, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addContainerGap())
            .addGroup(jPanelInfosLayout.createSequentialGroup()
                .addComponent(jScrollPane7, javax.swing.GroupLayout.DEFAULT_SIZE, 272, Short.MAX_VALUE)
                .addContainerGap())
        );

        jPanelTables.setName("jPanelTables"); // NOI18N
        jPanelTables.setPreferredSize(new java.awt.Dimension(1096, 200));

        jScrollPane6.setName("jScrollPane6"); // NOI18N

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

        jScrollPane5.setName("jScrollPane5"); // NOI18N

        jTableFilelistEpisodes.setModel(new javax.swing.table.DefaultTableModel(
            new Object [][] {
                {null, null, null, null, null, null, null, null, null}
            },
            new String [] {
                "Use", "Series", "S", "E", "Filename", "SearchString", "Year", "ImdbId", "ID"
            }
        ) {
            Class[] types = new Class [] {
                java.lang.Boolean.class, java.lang.String.class, java.lang.Integer.class, java.lang.Integer.class, java.lang.String.class, java.lang.String.class, java.lang.String.class, java.lang.Integer.class, java.lang.String.class
            };
            boolean[] canEdit = new boolean [] {
                true, false, false, false, false, true, false, false, false
            };

            public Class getColumnClass(int columnIndex) {
                return types [columnIndex];
            }

            public boolean isCellEditable(int rowIndex, int columnIndex) {
                return canEdit [columnIndex];
            }
        });
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
        jTableFilelistEpisodes.getColumnModel().getColumn(2).setPreferredWidth(15);
        jTableFilelistEpisodes.getColumnModel().getColumn(2).setHeaderValue(resourceMap.getString("jTableFilelistEpisodes.columnModel.title7")); // NOI18N
        jTableFilelistEpisodes.getColumnModel().getColumn(3).setResizable(false);
        jTableFilelistEpisodes.getColumnModel().getColumn(3).setPreferredWidth(15);
        jTableFilelistEpisodes.getColumnModel().getColumn(3).setHeaderValue(resourceMap.getString("jTableFilelistEpisodes.columnModel.title8")); // NOI18N
        jTableFilelistEpisodes.getColumnModel().getColumn(4).setResizable(false);
        jTableFilelistEpisodes.getColumnModel().getColumn(4).setPreferredWidth(140);
        jTableFilelistEpisodes.getColumnModel().getColumn(4).setHeaderValue(resourceMap.getString("jTableFilelist.columnModel.title0")); // NOI18N
        jTableFilelistEpisodes.getColumnModel().getColumn(5).setResizable(false);
        jTableFilelistEpisodes.getColumnModel().getColumn(5).setHeaderValue(resourceMap.getString("jTableFilelist.columnModel.title3")); // NOI18N
        jTableFilelistEpisodes.getColumnModel().getColumn(6).setResizable(false);
        jTableFilelistEpisodes.getColumnModel().getColumn(6).setPreferredWidth(30);
        jTableFilelistEpisodes.getColumnModel().getColumn(6).setHeaderValue(resourceMap.getString("jTableFilelist.columnModel.title2")); // NOI18N
        jTableFilelistEpisodes.getColumnModel().getColumn(7).setResizable(false);
        jTableFilelistEpisodes.getColumnModel().getColumn(7).setPreferredWidth(40);
        jTableFilelistEpisodes.getColumnModel().getColumn(7).setHeaderValue(resourceMap.getString("jTableFilelist.columnModel.title4")); // NOI18N
        jTableFilelistEpisodes.getColumnModel().getColumn(8).setResizable(false);
        jTableFilelistEpisodes.getColumnModel().getColumn(8).setPreferredWidth(10);
        jTableFilelistEpisodes.getColumnModel().getColumn(8).setHeaderValue(resourceMap.getString("jTableFilelistEpisodes.columnModel.title6")); // NOI18N

        javax.swing.GroupLayout jPanelTablesLayout = new javax.swing.GroupLayout(jPanelTables);
        jPanelTables.setLayout(jPanelTablesLayout);
        jPanelTablesLayout.setHorizontalGroup(
            jPanelTablesLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanelTablesLayout.createSequentialGroup()
                .addComponent(jScrollPane6, javax.swing.GroupLayout.PREFERRED_SIZE, 129, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addComponent(jScrollPane5, javax.swing.GroupLayout.DEFAULT_SIZE, 995, Short.MAX_VALUE))
        );
        jPanelTablesLayout.setVerticalGroup(
            jPanelTablesLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addComponent(jScrollPane6, javax.swing.GroupLayout.DEFAULT_SIZE, 303, Short.MAX_VALUE)
            .addComponent(jScrollPane5, javax.swing.GroupLayout.DEFAULT_SIZE, 303, Short.MAX_VALUE)
        );

        javax.swing.GroupLayout jPanelSeriesLayout = new javax.swing.GroupLayout(jPanelSeries);
        jPanelSeries.setLayout(jPanelSeriesLayout);
        jPanelSeriesLayout.setHorizontalGroup(
            jPanelSeriesLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(javax.swing.GroupLayout.Alignment.TRAILING, jPanelSeriesLayout.createSequentialGroup()
                .addGroup(jPanelSeriesLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.TRAILING)
                    .addGroup(javax.swing.GroupLayout.Alignment.LEADING, jPanelSeriesLayout.createSequentialGroup()
                        .addContainerGap()
                        .addComponent(jPanelTables, javax.swing.GroupLayout.DEFAULT_SIZE, 1130, Short.MAX_VALUE))
                    .addComponent(jPanelInfos, javax.swing.GroupLayout.DEFAULT_SIZE, 1140, Short.MAX_VALUE)
                    .addGroup(javax.swing.GroupLayout.Alignment.LEADING, jPanelSeriesLayout.createSequentialGroup()
                        .addGap(20, 20, 20)
                        .addComponent(jLabel2)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                        .addComponent(jTextFieldTypesSeries, javax.swing.GroupLayout.PREFERRED_SIZE, 192, javax.swing.GroupLayout.PREFERRED_SIZE))
                    .addGroup(javax.swing.GroupLayout.Alignment.LEADING, jPanelSeriesLayout.createSequentialGroup()
                        .addContainerGap()
                        .addComponent(jSeparator2, javax.swing.GroupLayout.DEFAULT_SIZE, 1130, Short.MAX_VALUE)))
                .addContainerGap())
            .addGroup(jPanelSeriesLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                .addGroup(jPanelSeriesLayout.createSequentialGroup()
                    .addContainerGap()
                    .addGroup(jPanelSeriesLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                        .addGroup(jPanelSeriesLayout.createSequentialGroup()
                            .addComponent(jScrollPane4, javax.swing.GroupLayout.DEFAULT_SIZE, 1130, Short.MAX_VALUE)
                            .addContainerGap())
                        .addGroup(javax.swing.GroupLayout.Alignment.TRAILING, jPanelSeriesLayout.createSequentialGroup()
                            .addComponent(jButtonDelete1)
                            .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                            .addComponent(jButtonAdd1)
                            .addGap(11, 11, 11)))))
        );
        jPanelSeriesLayout.setVerticalGroup(
            jPanelSeriesLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanelSeriesLayout.createSequentialGroup()
                .addGap(101, 101, 101)
                .addGroup(jPanelSeriesLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                    .addComponent(jLabel2)
                    .addComponent(jTextFieldTypesSeries, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addComponent(jSeparator2, javax.swing.GroupLayout.PREFERRED_SIZE, 10, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addComponent(jPanelInfos, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addComponent(jPanelTables, javax.swing.GroupLayout.DEFAULT_SIZE, 303, Short.MAX_VALUE)
                .addContainerGap())
            .addGroup(jPanelSeriesLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                .addGroup(jPanelSeriesLayout.createSequentialGroup()
                    .addContainerGap()
                    .addComponent(jScrollPane4, javax.swing.GroupLayout.PREFERRED_SIZE, 70, javax.swing.GroupLayout.PREFERRED_SIZE)
                    .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                    .addGroup(jPanelSeriesLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                        .addComponent(jButtonAdd1)
                        .addComponent(jButtonDelete1))
                    .addContainerGap(636, Short.MAX_VALUE)))
        );

        jTabbedPane.addTab(resourceMap.getString("jPanelSeries.TabConstraints.tabTitle"), jPanelSeries); // NOI18N

        jLabelConnectionStatus.setText(resourceMap.getString("jLabelConnectionStatus.text")); // NOI18N
        jLabelConnectionStatus.setName("jLabelConnectionStatus"); // NOI18N

        javax.swing.GroupLayout mainPanelLayout = new javax.swing.GroupLayout(mainPanel);
        mainPanel.setLayout(mainPanelLayout);
        mainPanelLayout.setHorizontalGroup(
            mainPanelLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(mainPanelLayout.createSequentialGroup()
                .addGroup(mainPanelLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addGroup(mainPanelLayout.createSequentialGroup()
                        .addGap(10, 10, 10)
                        .addComponent(jTabbedPane, javax.swing.GroupLayout.DEFAULT_SIZE, 1155, Short.MAX_VALUE))
                    .addGroup(mainPanelLayout.createSequentialGroup()
                        .addComponent(jToolBar1, javax.swing.GroupLayout.DEFAULT_SIZE, 794, Short.MAX_VALUE)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                        .addComponent(jLabelConnectionStatus, javax.swing.GroupLayout.DEFAULT_SIZE, 361, Short.MAX_VALUE)))
                .addContainerGap())
        );
        mainPanelLayout.setVerticalGroup(
            mainPanelLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(mainPanelLayout.createSequentialGroup()
                .addGroup(mainPanelLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.TRAILING)
                    .addComponent(jLabelConnectionStatus, javax.swing.GroupLayout.PREFERRED_SIZE, 25, javax.swing.GroupLayout.PREFERRED_SIZE)
                    .addComponent(jToolBar1, javax.swing.GroupLayout.PREFERRED_SIZE, 25, javax.swing.GroupLayout.PREFERRED_SIZE))
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addComponent(jTabbedPane, javax.swing.GroupLayout.DEFAULT_SIZE, 774, Short.MAX_VALUE)
                .addContainerGap())
        );

        menuBar.setName("menuBar"); // NOI18N

        fileMenu.setText(resourceMap.getString("fileMenu.text")); // NOI18N
        fileMenu.setName("fileMenu"); // NOI18N

        exitMenuItem.setAction(actionMap.get("quit")); // NOI18N
        exitMenuItem.setName("exitMenuItem"); // NOI18N
        fileMenu.add(exitMenuItem);

        menuBar.add(fileMenu);

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
            .addComponent(statusPanelSeparator, javax.swing.GroupLayout.DEFAULT_SIZE, 1175, Short.MAX_VALUE)
            .addGroup(statusPanelLayout.createSequentialGroup()
                .addContainerGap()
                .addComponent(statusMessageLabel)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED, 1155, Short.MAX_VALUE)
                .addComponent(statusAnimationLabel)
                .addContainerGap())
            .addGroup(javax.swing.GroupLayout.Alignment.TRAILING, statusPanelLayout.createSequentialGroup()
                .addContainerGap(868, Short.MAX_VALUE)
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

        setComponent(mainPanel);
        setMenuBar(menuBar);
        setStatusBar(statusPanel);
    }// </editor-fold>//GEN-END:initComponents

    private void jTableFilelistMouseClicked(java.awt.event.MouseEvent evt) {//GEN-FIRST:event_jTableFilelistMouseClicked
        int row = jTableFilelist.getSelectedRow();
        int id = (Integer)jTableFilelist.getValueAt(row, 6);

        MediaInfo info = database.getMediaInfoById(id);

        jTextAreaDescriptionMovies.setText(info.toString());
        ImageIcon poster = new ImageIcon("converted/tt" + info.Imdb + "_poster.png");
        jLabelPosterMovies.getGraphics().drawImage(poster.getImage(), 15, 15, poster.getIconWidth(), poster.getIconHeight(), null);
        jLabelBackdropMovies.getGraphics().drawImage(new ImageIcon("download/tt" + info.Imdb + "_backdrop.jpg").getImage(), 0, 0, jLabelBackdropMovies.getWidth(), jLabelBackdropMovies.getHeight(), null);
    }//GEN-LAST:event_jTableFilelistMouseClicked

    private void jTableFilelistKeyPressed(java.awt.event.KeyEvent evt) {//GEN-FIRST:event_jTableFilelistKeyPressed
        int row = jTableFilelist.getSelectedRow();

        if(evt.getKeyCode() == 38 && row > 0)
            row--;
        else if(evt.getKeyCode() == 40 && row <= jTableFilelist.getRowCount())
            row++;

        int id = (Integer)jTableFilelist.getValueAt(row, 6);

        MediaInfo info = database.getMediaInfoById(id);

        jTextAreaDescriptionMovies.setText(info.toString());
        //jLabelPoster.setIcon(new ImageIcon(info.Imdb + "_poster.jpg"));
        ImageIcon poster = new ImageIcon("converted/tt" + info.Imdb + "_poster.png");
        jLabelPosterMovies.getGraphics().drawImage(poster.getImage(), 15, 15, poster.getIconWidth(), poster.getIconHeight(), null);
        jLabelBackdropMovies.getGraphics().drawImage(new ImageIcon("download/tt" + info.Imdb + "_backdrop.jpg").getImage(), 0, 0, jLabelBackdropMovies.getWidth(), jLabelBackdropMovies.getHeight(), null);
    }//GEN-LAST:event_jTableFilelistKeyPressed

    private void jTableFilelistEpisodesMouseClicked(java.awt.event.MouseEvent evt) {//GEN-FIRST:event_jTableFilelistEpisodesMouseClicked
        int row = jTableFilelistEpisodes.getSelectedRow();
        int id = (Integer)jTableFilelistEpisodes.getValueAt(row, 8);

        MediaInfo info = database.getMediaInfoById(id);

        jTextAreaDescriptionSeries.setText(info.toString());
    }//GEN-LAST:event_jTableFilelistEpisodesMouseClicked

    private void jTableFilelistEpisodesKeyPressed(java.awt.event.KeyEvent evt) {//GEN-FIRST:event_jTableFilelistEpisodesKeyPressed
        int row = jTableFilelistEpisodes.getSelectedRow();

        if(evt.getKeyCode() == 38 && row > 0)
            row--;
        else if(evt.getKeyCode() == 40 && row <= jTableFilelistEpisodes.getRowCount())
            row++;

        int id = (Integer)jTableFilelistEpisodes.getValueAt(row, 8);
        MediaInfo info = database.getMediaInfoById(id);
        jTextAreaDescriptionSeries.setText(info.toString());
    }//GEN-LAST:event_jTableFilelistEpisodesKeyPressed

    private void jTableSeriesMouseClicked(java.awt.event.MouseEvent evt) {//GEN-FIRST:event_jTableSeriesMouseClicked
        int row = jTableSeries.getSelectedRow();
        int id = (Integer)jTableSeries.getValueAt(row, 1);

        MediaInfo info = database.getMediaInfoById(id);

        jTextAreaDescriptionSeries.setText(info.toString());
    }//GEN-LAST:event_jTableSeriesMouseClicked

    private void jTableSeriesKeyPressed(java.awt.event.KeyEvent evt) {//GEN-FIRST:event_jTableSeriesKeyPressed
        int row = jTableSeries.getSelectedRow();

        if(evt.getKeyCode() == 38 && row > 0)
            row--;
        else if(evt.getKeyCode() == 40 && row <= jTableSeries.getRowCount())
            row++;

        int id = (Integer)jTableFilelistEpisodes.getValueAt(row, 1);
        MediaInfo info = database.getMediaInfoById(id);
        jTextAreaDescriptionSeries.setText(info.toString());
    }//GEN-LAST:event_jTableSeriesKeyPressed

    private void jTextFieldTypesActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_jTextFieldTypesActionPerformed
        properties.setProperty("FILTER_MOVIES", jTextFieldTypes.getText());
    }//GEN-LAST:event_jTextFieldTypesActionPerformed

    private void jTextFieldTypesSeriesActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_jTextFieldTypesSeriesActionPerformed
        properties.setProperty("FILTER_SERIES", jTextFieldTypesSeries.getText());
    }//GEN-LAST:event_jTextFieldTypesSeriesActionPerformed

    MediaInfoDB database = new MediaInfoDB();

    public void updateTables() {
        MediaInfo[] movies = database.getMediaInfo();

        ((DefaultTableModel) jTableFilelist.getModel()).setRowCount(database.getMediaInfoMoviesCount());
        ((DefaultTableModel) jTableFilelistEpisodes.getModel()).setRowCount(database.getMediaInfoEpisodesCount());
        ((DefaultTableModel) jTableSeries.getModel()).setRowCount(database.getMediaInfoSeriesCount());

        int iteratorMovies = 0;
        int iteratorEpisodes = 0;
        int iteratorSeries = 0;
        for(MediaInfo movie : movies) {
            if(movie.isMovie) {
                jTableFilelist.setValueAt(movie.Filename, iteratorMovies, 0);
                jTableFilelist.setValueAt(movie.SearchString, iteratorMovies, 1);
                jTableFilelist.setValueAt(movie.Title, iteratorMovies, 2);
                jTableFilelist.setValueAt(movie.Year, iteratorMovies, 3);
                jTableFilelist.setValueAt(movie.Imdb, iteratorMovies, 4);
                jTableFilelist.setValueAt(!movie.Ignoring, iteratorMovies, 5);
                jTableFilelist.setValueAt(movie.ID, iteratorMovies, 6);
                iteratorMovies++;
            }
            else if(movie.isEpisode) {
                jTableFilelistEpisodes.setValueAt(!movie.Ignoring, iteratorEpisodes, 0);
                jTableFilelistEpisodes.setValueAt(movie.Title, iteratorEpisodes, 1);
                jTableFilelistEpisodes.setValueAt(movie.Season, iteratorEpisodes, 2);
                jTableFilelistEpisodes.setValueAt(movie.Episode, iteratorEpisodes, 3);
                jTableFilelistEpisodes.setValueAt(movie.Filename, iteratorEpisodes, 4);
                jTableFilelistEpisodes.setValueAt(movie.SearchString, iteratorEpisodes, 5);
                jTableFilelistEpisodes.setValueAt(movie.Year, iteratorEpisodes, 6);
                jTableFilelistEpisodes.setValueAt(movie.Imdb, iteratorEpisodes, 7);
                jTableFilelistEpisodes.setValueAt(movie.ID, iteratorEpisodes, 8);
                iteratorEpisodes++;
            }
            else if(movie.isSeries) {
                jTableSeries.setValueAt(movie.Title, iteratorSeries, 0);
                jTableSeries.setValueAt(movie.ID, iteratorSeries, 1);
                iteratorSeries++;
            }
        }

        //create db file
        try {
            Writer fwMovie = new FileWriter( "db/moviedb.txt" );
            Writer fwSeries = new FileWriter( "db/seriesdb.txt" );

            File episodes = new File("db/episodes");
            if(episodes.exists()) {
                for(File episode : episodes.listFiles())
                    episode.delete();
            }

            episodes.mkdir();

            //Writer fwEpisode = new FileWriter( "db/episodedb.txt" );
            fwMovie.write("Created on " + Calendar.getInstance().getTime() + "\n");
            fwSeries.write("Created on " + Calendar.getInstance().getTime() + "\n");
            //fwEpisode.write("Created on " + Calendar.getInstance().getTime() + "\n");
            for(MediaInfo movie : movies) {
                if(!movie.Ignoring) {
                    if(movie.isMovie)
                        fwMovie.append(movie.toString());
                    else if(movie.isSeries)
                        fwSeries.append(movie.toString());
                    else if(movie.isEpisode) {
                        Writer fwEpisode = new FileWriter("db/episodes/" + movie.TheTvDb + ".txt", true);
                        fwEpisode.append(movie.toString());
                        fwEpisode.close();
                    }
                }
            }
            fwMovie.close();
            fwSeries.close();
        } catch(Exception ex) {
            System.out.println(ex.toString());
        }
    }

    @Action
    public Task syncFilelist() {

        savePathsTables();

        return new SyncFilelistTask(getApplication());
    }

    private class SyncFilelistTask extends org.jdesktop.application.Task<Object, Void> {
        SyncFilelistTask(org.jdesktop.application.Application app) {
            // Runs on the EDT.  Copy GUI state that
            // doInBackground() depends on from parameters
            // to SyncFilelistTask fields, here.
            super(app);
            //Thread t1 = new Thread( new syncFilelistThread() );
            //t1.start();
        }
        @Override protected Object doInBackground() {
            // Your Task's code here.  This method runs
            // on a background thread, so don't reference
            // the Swing GUI from here.

            //clear database
            database.clear();

            Logger.setWorking(true);
            Logger.setProgress(0);

            searchMovies();
            searchSeries();

            Logger.print("Finished");
            Logger.setWorking(false);
            Logger.setProgress(0);

            return null;  // return your result
        }
        @Override protected void succeeded(Object result) {
            // Runs on the EDT.  Update the GUI based on
            // the result computed by doInBackground().

            updateTables();
        }

        private void searchMovies()
        {
            DefaultTableModel dModel = (DefaultTableModel) jTablePaths.getModel();

            for(int row = 0; row < dModel.getRowCount(); row++)
            {
                if(Boolean.parseBoolean(String.valueOf(dModel.getValueAt(row, 0))) == false)
                    continue;

                String[] entries = new valerie.tools.Network().sendCMD(boxInfo.IpAddress, "find \"" + dModel.getValueAt(row, 1) + "\" -type f\n");

                for(int i = 0; i < entries.length; i++)
                {
                    Float progress = (float)i * 100;
                    progress /= entries.length;

                    Logger.setProgress(progress.intValue());

                    MediaInfo movie = new MediaInfo(entries[i]);

                    Pattern pFileFilter = Pattern.compile(".*(" +  properties.getPropertyString("FILTER_MOVIES") + ")$");
                    Matcher mFileFilter = pFileFilter.matcher(movie.Filename);
                    if(!mFileFilter.matches())
                        continue;

                    movie.isMovie = true;

                    Logger.print(movie.Filename + " : Parsing");

                    //FileFilter
                    Pattern p = Pattern.compile("tt\\d{7}");
                    Matcher m = p.matcher(movie.Filename);
                    if(m.find())
                        System.out.printf("Imdb found: %d", Integer.valueOf(m.group()));

                    String[][] replacements = new String[][] {
                        new String[] {"[.]", " "},
                        new String[] {"_", " "},
                        new String[] {"tt\\d{7}", ""},
                        new String[] {"(\\b(dth|vc1|ac3d|dl|extcut|mkv|nhd|576p|720p|1080p|1080i|dircut|directors cut|dvdrip|dvdscreener|dvdscr|avchd|wmv|ntsc|pal|mpeg|dsr|hd|r5|dvd|dvdr|dvd5|dvd9|bd5|bd9|dts|ac3|bluray|blu-ray|hdtv|pdtv|stv|hddvd|xvid|divx|x264|dxva|m2ts|(?-i)FESTIVAL|LIMITED|WS|FS|PROPER|REPACK|RERIP|REAL|RETAIL|EXTENDED|REMASTERED|UNRATED|CHRONO|THEATRICAL|DC|SE|UNCUT|INTERNAL|DUBBED|SUBBED)\\b([-].+?$)?)", ""},
                    };
                    String filtered = movie.Filename.toLowerCase();
                    for(int iter = 0; iter < replacements.length; iter++)
                        filtered = filtered.replaceAll(replacements[iter][0].toLowerCase(), replacements[iter][1]);

                    filtered = filtered.trim();
                    filtered = filtered.replaceAll("\\s+", " ");

                    String[] parts = filtered.split(" ");
                    for(int possibleYearPosition = 0; possibleYearPosition < 3 && possibleYearPosition < parts.length; possibleYearPosition++)
                    {
                        if(parts[parts.length - 1 - possibleYearPosition].matches("\\d{4}"))
                        {
                             System.out.printf("Year found: %s", parts[parts.length - 1 - possibleYearPosition]);
                             movie.Year = Integer.valueOf(parts[parts.length - 1 - possibleYearPosition]);
                             filtered = filtered.substring(0, filtered.length()-5);

                             break;
                        }
                    }

                    filtered = filtered.trim();

                    //Idee bei grossklein wechsel leerzeichen einfügen, auch bei buchstabe auf zahlen wechsel
                    for (int i2 = 0; i2 + 1 < filtered.length(); i2++)
                    {
                        String p1 = filtered.substring(i2, i2+1);
                        String p2 = filtered.substring(i2+1, i2+2);

                        if(     (p1.matches("[a-zA-Z]") && p2.matches("\\d")) ||
                                (p1.matches("\\d") && p2.matches("[a-zA-Z]")))
                        {
                            filtered = filtered.substring(0, i2+1) + " " + filtered.substring(i2+1, filtered.length());
                        }
                    }

                    //Idee alles was nach dem Erscheinungsjahr kommt wegwerfen, mögliche Fehlerquelle wenn bestandteil des Filmes ist.
                    if(movie.Year > 1950 && movie.Year < 2020)
                        filtered = filtered.split(String.valueOf(movie.Year))[0];

                    //Sometimes the release groups insert their name in front of the title, so letzs check if the frist word contains a '-'
                    String firstWord = "";
                    String[] spaceSplit = filtered.split(" ", 2);
                    if(spaceSplit.length == 2)
                        firstWord = spaceSplit[0];
                    else
                        firstWord = filtered;

                    String[] minusSplit = firstWord.split("-", 2);
                    if(minusSplit.length == 2)
                        filtered = minusSplit[1] + (spaceSplit.length==2?" " + spaceSplit[1]:"");

                    movie.SearchString = filtered;

                    database.addMediaInfo(movie);

                    Logger.print(movie.Filename + " : Using \"" + movie.SearchString +"\" to get title");
                }
            }
        }

        private void searchSeries()
        {
            DefaultTableModel dModel = (DefaultTableModel) jTablePathsSeries.getModel();

            for(int row = 0; row < dModel.getRowCount(); row++)
            {
                if(Boolean.parseBoolean(String.valueOf(dModel.getValueAt(row, 0))) == false)
                    continue;

                String[] entries = new valerie.tools.Network().sendCMD(boxInfo.IpAddress, "find \"" + dModel.getValueAt(row, 1) + "\" -type f\n");

                for(int i = 0; i < entries.length; i++) {
                    Float progress = (float)i * 100;
                    progress /= entries.length;

                    Logger.setProgress(progress.intValue());

                    MediaInfo movie = new MediaInfo(entries[i]);

                    //FileFilter
                    Pattern pFileFilter = Pattern.compile(".*(" + properties.getPropertyString("FILTER_SERIES") + ")$");
                    Matcher mFileFilter = pFileFilter.matcher(movie.Filename);
                    if(!mFileFilter.matches()) {
                        continue;
                    }

                    movie.isEpisode = true;

                    Logger.print(movie.Filename + " : Parsing");

                    Pattern p = Pattern.compile("tt\\d{7}");
                    Matcher m = p.matcher(movie.Filename);
                    if(m.find())
                        System.out.printf("Imdb found: %d", Integer.valueOf(m.group()));

                    String[][] replacements = new String[][] {
                        new String[] {"[.]", " "},
                        new String[] {"_", " "},
                        new String[] {"tt\\d{7}", ""},
                        new String[] {"(\\b(dth|vc1|ac3d|dl|extcut|mkv|nhd|576p|720p|1080p|1080i|dircut|directors cut|dvdrip|dvdscreener|dvdscr|avchd|wmv|ntsc|pal|mpeg|dsr|hd|r5|dvd|dvdr|dvd5|dvd9|bd5|bd9|dts|ac3|bluray|blu-ray|hdtv|pdtv|stv|hddvd|xvid|divx|x264|dxva|(?-i)FESTIVAL|LIMITED|WS|FS|PROPER|REPACK|RERIP|REAL|RETAIL|EXTENDED|REMASTERED|UNRATED|CHRONO|THEATRICAL|DC|SE|UNCUT|INTERNAL|DUBBED|SUBBED)\\b([-].+?$)?)", ""},
                    };
                    String filtered = movie.Filename.toLowerCase();
                    for(int iter = 0; iter < replacements.length; iter++)
                        filtered = filtered.replaceAll(replacements[iter][0].toLowerCase(), replacements[iter][1]);

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
                    if(spaceSplit.length == 2)
                        firstWord = spaceSplit[0];
                    else
                        firstWord = SeriesName;

                    String[] minusSplit = firstWord.split("-", 2);
                    if(minusSplit.length == 2) {
                        SeriesName = minusSplit[1] + (spaceSplit.length==2?" " + spaceSplit[1]:"");
                    }

                    {
                        Pattern pSeasonEpisode = Pattern.compile(" s\\d+e\\d+");
                        Matcher mSeasonEpisode = pSeasonEpisode.matcher(filtered);
                        if(mSeasonEpisode.find()) {
                            String sSeasonEpisode = mSeasonEpisode.group().trim();

                            Matcher mSeason = Pattern.compile("s\\d+").matcher(sSeasonEpisode);
                            mSeason.find();
                            movie.Season = Integer.valueOf(mSeason.group().substring(1));

                            Matcher mEpisode = Pattern.compile("e\\d+").matcher(sSeasonEpisode);
                            mEpisode.find();
                            movie.Episode = Integer.valueOf(mEpisode.group().substring(1));
                        }
                    }

                    if(movie.Season == 0&& movie.Episode == 0){
                        Pattern pSeasonEpisode = Pattern.compile(" \\d+x\\d+");
                        Matcher mSeasonEpisode = pSeasonEpisode.matcher(filtered);
                        if(mSeasonEpisode.find()) {
                            String sSeasonEpisode = mSeasonEpisode.group().trim();

                            Matcher mSeason = Pattern.compile("\\d+x").matcher(sSeasonEpisode);
                            if(mSeason.find())
                                movie.Season = Integer.valueOf(mSeason.group().substring(0, mSeason.group().length()-1));

                            Matcher mEpisode = Pattern.compile("x\\d+").matcher(sSeasonEpisode);
                            if(mEpisode.find())
                                movie.Episode = Integer.valueOf(mEpisode.group().substring(1));
                        }
                    }

                    //Sometimes the Season and Episode info is like this 812 for Season: 8 Episode: 12
                    if(movie.Season == 0&& movie.Episode == 0) {
                        String[] sSeasonEpisodeA = SeriesName.split(" ");
                        SeriesName = "";
                        for(int iteratorSeasonEpisodeA = 0; iteratorSeasonEpisodeA < sSeasonEpisodeA.length; iteratorSeasonEpisodeA++) {
                            String sSeasonEpisode = sSeasonEpisodeA[iteratorSeasonEpisodeA];

                            Pattern pSeasonEpisode = Pattern.compile("\\d+");
                            Matcher mSeasonEpisode = pSeasonEpisode.matcher(sSeasonEpisode);
                            if(mSeasonEpisode.matches()) {
                                int iSeasonEpisode = Integer.valueOf(mSeasonEpisode.group());
                                if(iSeasonEpisode > 100 && iSeasonEpisode < 2400) {
                                    movie.Season = iSeasonEpisode / 100;
                                    movie.Episode = iSeasonEpisode % 100;

                                    break;
                                }
                            } else
                                SeriesName += sSeasonEpisode + " ";
                        }
                    }

                    movie.SearchString = SeriesName.trim();

                    Logger.print(movie.Filename + " : Using \"" + movie.SearchString +"\" to get title");

                    database.addMediaInfo(movie);
                }
            }
        }
    }

    @Action
    public void addLine() {
        DefaultTableModel dModel = (DefaultTableModel) jTablePathsSeries.getModel();
        dModel.setRowCount(dModel.getRowCount() + 1);
        dModel.setValueAt(false, dModel.getRowCount()-1, 0);
    }

    @Action
    public void connectNetwork() {

        boxInfo = new valerie.tools.BoxInfoParser().parse(new valerie.tools.Network().sendBroadcast());
        jLabelConnectionStatus.setText(boxInfo.toShortString());
    }

    @Action
    public Task parseFilelist() {
        return new ParseFilelistTask(getApplication());
    }

    private class ParseFilelistTask extends org.jdesktop.application.Task<Object, Void> {
        ParseFilelistTask(org.jdesktop.application.Application app) {
            // Runs on the EDT.  Copy GUI state that
            // doInBackground() depends on from parameters
            // to ParseFilelistTask fields, here.
            super(app);
        }
        @Override protected Object doInBackground() {
            // Your Task's code here.  This method runs
            // on a background thread, so don't reference
            // the Swing GUI from here.

            Logger.setWorking(true);
            Logger.setProgress(0);

            getMediaInfo();

            Logger.print("Finished");
            Logger.setWorking(false);
            Logger.setProgress(0);

            return null;  // return your result
        }
        @Override protected void succeeded(Object result) {
            // Runs on the EDT.  Update the GUI based on
            // the result computed by doInBackground().

            updateTables();
        }

        private void getMediaInfo() {
            //Befor getting the MediaInfo lets refresh the SearchString as the user could have changed this.

            for(int row = 0; row < jTableFilelist.getRowCount(); row++)
                database.getMediaInfoById(Integer.decode(jTableFilelist.getValueAt(row, 6).toString())).SearchString = jTableFilelist.getValueAt(row, 1).toString();

            //The easysiest way would be to delete the content of the database an readd everthing
            MediaInfo[] movies = database.getMediaInfo();

            database.clear();

            for(int i = 0; i < movies.length; i++) {
                Float progress = (float)i * 100;
                progress /= movies.length;
                Logger.setProgress(progress.intValue());

                MediaInfo movie = movies[i];

                Logger.print(movie.Filename + " : Using \"" + movie.SearchString +"\" to get title");

                if(movie.SearchString.length() == 0)
                    continue;

                if(movie.isMovie)
                    getMediaInfoMovie(movie);
                else if(movie.isEpisode)
                    getMediaInfoSeries(movie);

                Logger.print(movie.Filename + " : Got title \"" + movie.Title +"\".");

                movie.Ignoring = false;
            }
        }

         private void getMediaInfoMovie(MediaInfo movie) {

            movie.DataProvider = new valerie.provider.Imdb();
            movie.ArtProvider = new valerie.provider.theMovieDb();

            movie.getDataByTitle();

            if(movie.Title.length() > 0)
                movie.Ignoring = false;

            database.addMediaInfo(movie);
         }

        private void getMediaInfoSeries(MediaInfo movie) {

            movie.DataProvider = new valerie.provider.theTvDb();
            movie.ArtProvider = new valerie.provider.theTvDb();

            MediaInfo Series;

            if(database.getMediaInfoForSeries(movie.SearchString) == null) {
                Series = movie.clone();
                Series.isSeries = true;
                Series.isEpisode = false;
                Series.getDataByTitle();
                Series.Filename = "";

                if(Series.Title.length() > 0) {
                    Series.Ignoring = false;

                     if(database.getMediaInfoForSeries(Series.TheTvDb) == null)
                        database.addMediaInfo(Series);
                }
            } else
                Series = database.getMediaInfoForSeries(movie.SearchString);

            MediaInfo Episode = null;

            if(Series != null) {
                Episode = Series.clone();
                Episode.isSeries = false;
                Episode.isEpisode = true;
                Episode.Filename = movie.Filename;
                Episode.Path = movie.Path;
                Episode.Season = movie.Season;
                Episode.Episode = movie.Episode;

            } else return;

            Episode.getDataByTitle();


            Episode.ArtProvider = Episode.DataProvider;

            if(Episode.Title.length() > 0)
                Episode.Ignoring = false;

            database.addMediaInfo(Episode);
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
        @Override protected Object doInBackground() {
            // Your Task's code here.  This method runs
            // on a background thread, so don't reference
            // the Swing GUI from here.

            new valerie.tools.Network().sendFile(boxInfo.IpAddress, "db/moviedb.txt", "/hdd/valerie");
            new valerie.tools.Network().sendFile(boxInfo.IpAddress, "db/seriesdb.txt", "/hdd/valerie");

            File episodes = new File("db/episodes");
            if (!(episodes.exists())) {
              Logger.print("No such Folder \"db/episodes\"!");
            }
            else {
              String[] entries = episodes.list();

              for (int i = 0; i < entries.length; ++i) {
                  new valerie.tools.Network().sendFile(boxInfo.IpAddress, "db/episodes/" + entries[i], "/hdd/valerie/episodes");
              }
            }

            File folder = new File("converted");
            if (!(folder.exists())) {
              Logger.print("No such Folder \"converted\"!");
            }
            else {
              String[] entries = folder.list();

              for (int i = 0; i < entries.length; ++i) {
                  new valerie.tools.Network().sendFile(boxInfo.IpAddress, "converted/" + entries[i], "/hdd/valerie/media");
              }
            }


            return null;  // return your result
        }
        @Override protected void succeeded(Object result) {
            // Runs on the EDT.  Update the GUI based on
            // the result computed by doInBackground().
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
        @Override protected Object doInBackground() {
            // Your Task's code here.  This method runs
            // on a background thread, so don't reference
            // the Swing GUI from here.

            Logger.setWorking(true);
            Logger.setProgress(0);

            MediaInfo[] movies = database.getMediaInfo();

            int moviesSize = movies.length;
            int moviesIterator = 0;

            for(MediaInfo movie : movies) {
                 Logger.setProgress((moviesIterator++*100)/moviesSize);
                if(movie.isMovie)
                    getMediaArtMovie(movie);
                if(movie.isSeries)
                    getMediaArtSeries(movie);
            }

            Logger.print("Finished");
            Logger.setWorking(false);
            Logger.setProgress(0);

            return null;  // return your result
        }
        @Override protected void succeeded(Object result) {
            // Runs on the EDT.  Update the GUI based on
            // the result computed by doInBackground().
        }

        private void getMediaArtMovie(MediaInfo movie) {
            Logger.print(movie.Filename + " : Got title \"" + movie.Title +"\". Downloading posters");

            movie.ArtProvider.getArtById(movie);

            if(movie.Poster.length() > 0) {
                File checkIfFileAlreadyExists = new File( "download/tt" + movie.Imdb + "_poster.jpg" );
                if(checkIfFileAlreadyExists != null && checkIfFileAlreadyExists.exists()) {
                } else {
                    new valerie.tools.webgrabber().getFile(movie.Poster, "download/tt" + movie.Imdb + "_poster.jpg");
                }

                if(checkIfFileAlreadyExists != null && checkIfFileAlreadyExists.exists()) {
                    File checkIfFilePNGalreadyExists = new File( "converted/tt" + movie.Imdb + "_poster.png" );
                    if(checkIfFilePNGalreadyExists == null || !checkIfFilePNGalreadyExists.exists())
                        try {
                            BufferedImage image = ImageIO.read(checkIfFileAlreadyExists);
                            Image scaled = image.getScaledInstance(156, 214, Image.SCALE_SMOOTH );

                            BufferedImage bi = new BufferedImage(
                                156,
                                214,
                                BufferedImage.TYPE_INT_RGB
                            );
                            Graphics g = bi.getGraphics();
                            g.drawImage(scaled, 0, 0, null);

                            ImageIO.write( bi, "png", checkIfFilePNGalreadyExists );

                            new pngquant().exec("converted\\tt" + movie.Imdb + "_poster.png", "converted\\tt" + movie.Imdb + "_poster.png");

                        } catch(Exception ex) {
                            System.out.println(ex.toString());
                        }
                }
            }

            Logger.print(movie.Filename + " : Got title \"" + movie.Title +"\". Downloading and Converting backdrops");

            if(movie.Backdrop.length() > 0) {
                File downloaded = new File( "download/tt" + movie.Imdb + "_backdrop.jpg" );

                //Check if already downloaded
                if(downloaded == null || !downloaded.exists()) {
                   new valerie.tools.webgrabber().getFile(movie.Backdrop, "download/tt" + movie.Imdb + "_backdrop.jpg");
                }


                if(downloaded != null && downloaded.exists()) {
                    File converted = new File( "converted/tt" + movie.Imdb + "_backdrop.m1v" );

                    //check if file already converted
                    if(converted == null || !converted.exists())
                        new mencoder().exec("download/tt" + movie.Imdb + "_backdrop.jpg", "converted/tt" + movie.Imdb + "_backdrop.m1v");
                }
            }

            database.addMediaInfo(movie);
        }


        private void getMediaArtSeries(MediaInfo movie) {
            Logger.print(movie.Filename + " : Got title \"" + movie.Title +"\". Downloading posters");

            movie.ArtProvider.getArtById(movie);

            if(movie.Poster.length() > 0) {
                File checkIfFileAlreadyExists = new File( "download/" + movie.TheTvDb + "_poster.jpg" );
                if(checkIfFileAlreadyExists != null && checkIfFileAlreadyExists.exists()) {
                } else {
                    new valerie.tools.webgrabber().getFile(movie.Poster, "download/" + movie.TheTvDb + "_poster.jpg");
                }

                if(checkIfFileAlreadyExists != null && checkIfFileAlreadyExists.exists()) {
                    File checkIfFilePNGalreadyExists = new File( "converted/" + movie.TheTvDb + "_poster.png" );
                    if(checkIfFilePNGalreadyExists == null || !checkIfFilePNGalreadyExists.exists())
                        try {
                            BufferedImage image = ImageIO.read(checkIfFileAlreadyExists);
                            Image scaled = image.getScaledInstance(156, 214, Image.SCALE_SMOOTH );

                            BufferedImage bi = new BufferedImage(
                                156,
                                214,
                                BufferedImage.TYPE_INT_RGB
                            );
                            Graphics g = bi.getGraphics();
                            g.drawImage(scaled, 0, 0, null);

                            ImageIO.write( bi, "png", checkIfFilePNGalreadyExists );

                            new pngquant().exec("converted\\" + movie.TheTvDb + "_poster.png", "converted\\" + movie.TheTvDb + "_poster.png");

                        } catch(Exception ex) {
                            System.out.println(ex.toString());
                        }
                }
            }

            Logger.print(movie.Filename + " : Got title \"" + movie.Title +"\". Downloading and Converting backdrops");

            if(movie.Backdrop.length() > 0) {
                File checkIfFileJPEGAlreadyExists = new File( "download/" + movie.TheTvDb + "_backdrop.jpg" );
                if(checkIfFileJPEGAlreadyExists != null && checkIfFileJPEGAlreadyExists.exists()) {
                }
                else {
                   new valerie.tools.webgrabber().getFile(movie.Backdrop, "download/" + movie.TheTvDb + "_backdrop.jpg");
                }

                if(checkIfFileJPEGAlreadyExists != null && checkIfFileJPEGAlreadyExists.exists()) {
                    File checkIfFileMVIlreadyExists = new File( "converted/" + movie.TheTvDb + "_backdrop.m1v" );
                    if(checkIfFileMVIlreadyExists == null || !checkIfFileMVIlreadyExists.exists())
                        new mencoder().exec("download/" + movie.TheTvDb + "_backdrop.jpg", "converted/" + movie.TheTvDb + "_backdrop.m1v");
                }
            }

            database.addMediaInfo(movie);
        }
    }





    private valerie.tools.BoxInfo boxInfo;

    // Variables declaration - do not modify//GEN-BEGIN:variables
    private javax.swing.JButton jButtonAdd;
    private javax.swing.JButton jButtonAdd1;
    private javax.swing.JButton jButtonArt;
    private javax.swing.JButton jButtonConnect;
    private javax.swing.JButton jButtonDelete;
    private javax.swing.JButton jButtonDelete1;
    private javax.swing.JButton jButtonParse;
    private javax.swing.JButton jButtonSync;
    private javax.swing.JButton jButtonUpload;
    private javax.swing.JLabel jLabel1;
    private javax.swing.JLabel jLabel10;
    private javax.swing.JLabel jLabel2;
    private javax.swing.JLabel jLabel3;
    private javax.swing.JLabel jLabel4;
    private javax.swing.JLabel jLabel5;
    private javax.swing.JLabel jLabel6;
    private javax.swing.JLabel jLabel7;
    private javax.swing.JLabel jLabel8;
    private javax.swing.JLabel jLabel9;
    private javax.swing.JLabel jLabelBackdropMovies;
    private javax.swing.JLabel jLabelConnectionStatus;
    private javax.swing.JLabel jLabelPosterMovies;
    private javax.swing.JPanel jPanelInfos;
    private javax.swing.JPanel jPanelInfosMovies;
    private javax.swing.JPanel jPanelMovies;
    private javax.swing.JPanel jPanelSeries;
    private javax.swing.JPanel jPanelTables;
    private javax.swing.JScrollPane jScrollPane1;
    private javax.swing.JScrollPane jScrollPane2;
    private javax.swing.JScrollPane jScrollPane3;
    private javax.swing.JScrollPane jScrollPane4;
    private javax.swing.JScrollPane jScrollPane5;
    private javax.swing.JScrollPane jScrollPane6;
    private javax.swing.JScrollPane jScrollPane7;
    private javax.swing.JSeparator jSeparator1;
    private javax.swing.JSeparator jSeparator2;
    private javax.swing.JTabbedPane jTabbedPane;
    private javax.swing.JTable jTableFilelist;
    private javax.swing.JTable jTableFilelistEpisodes;
    private javax.swing.JTable jTablePaths;
    private javax.swing.JTable jTablePathsSeries;
    private javax.swing.JTable jTableSeries;
    private javax.swing.JTextArea jTextAreaDescriptionMovies;
    private javax.swing.JTextArea jTextAreaDescriptionSeries;
    private javax.swing.JTextField jTextFieldTypes;
    private javax.swing.JTextField jTextFieldTypesSeries;
    private javax.swing.JToolBar jToolBar1;
    private javax.swing.JPanel mainPanel;
    private javax.swing.JMenuBar menuBar;
    private javax.swing.JProgressBar progressBar;
    private javax.swing.JLabel statusAnimationLabel;
    private javax.swing.JLabel statusMessageLabel;
    private javax.swing.JPanel statusPanel;
    // End of variables declaration//GEN-END:variables

    private final Timer messageTimer;
    private final Timer busyIconTimer;
    private final Icon idleIcon;
    private final Icon[] busyIcons = new Icon[15];
    private int busyIconIndex = 0;

    private JDialog aboutBox;
}
