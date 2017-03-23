#!/usr/bin/env python

"""
Copyright (c) UChicago Argonne, LLC. All rights reserved.
See LICENSE file.
"""

from __future__ import unicode_literals
import sys
import os
import numpy as np
from pylab import *
from matplotlib.backends import qt_compat

use_pyside = qt_compat.QT_API == qt_compat.QT_API_PYSIDE
if use_pyside:
    from PySide import QtGui, QtCore
else:
    from PyQt4 import QtGui, QtCore

import matplotlib.pyplot as plt
matplotlib.use('Qt4Agg')

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4 import NavigationToolbar2QT as NavigationToolbar
import gc

class MainWindow (QtGui.QMainWindow):

    def __init__ (self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.setGeometry(50, 50, 800, 700)
        self.setMinimumSize(800, 700)
        self.setWindowTitle("xPlot Util")
        self.setWindowIcon(QtGui.QIcon('Icons/Graph.png'))
        self.fileName = None
        self.canvasArray = []
        self.figArray = []

        self.SetupComponents()
        self.windowTabs()
        self.dockGraphingOptions()
        self.CheckGraphCheckBoxes()
        self.setCentralWidget(self.tabWidget)

    # -----------------------------------------------------------------------------#
    def dockGraphingOptions(self):
        """Function that creates the dockWidget, Graph Options"""

        self.dockDataGraphing = QtGui.QDockWidget("xPlot Options", self)
        self.dockDataGraphing.setFloating(False)
        self.dockDataGraphing.setMaximumWidth(300)
        self.dockDataGraphing.setAllowedAreas(QtCore.Qt.RightDockWidgetArea | QtCore.Qt.LeftDockWidgetArea)

        layout = QtGui.QFormLayout()
        FileHLayout = QtGui.QHBoxLayout()
        BtnLayout = QtGui.QHBoxLayout()
        self.dataDocked = QtGui.QWidget()

        self.FileNameRdOnlyBox()
        self.BrowseButton()
        self.GraphButton()
        self.GraphingCheckBox()

        FileHLayout.addWidget(self.fileNameLabel)
        FileHLayout.addWidget(self.rdOnlyFileName)
        FileHLayout.addWidget(self.BrowseBtn)
        FileHLayout.addStretch(1)

        BtnLayout.addStretch(1)
        BtnLayout.addWidget(self.GraphBtn)

        layout.addRow(FileHLayout)
        layout.addRow(self.graphCheckBx)
        layout.addRow(BtnLayout)
        self.dataDocked.setLayout(layout)
        self.dockDataGraphing.setWidget(self.dataDocked)

        # Adding the docked widget to the main window
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dockDataGraphing)

    def restoreDockGraphingOptions(self):
        """This funtion restores the Graphing Options Dock Widget, if it closed"""
        if self.dockDataGraphing.isVisible() == False:
            self.dockGraphingOptions()

    # ------------------------------------------------------------------------------------#
    def windowTabs(self):
        """This function creates the central widget QTabWidget and creates the Data tab"""
        self.tabWidget = QtGui.QTabWidget()
        self.tabBar = QtGui.QTabBar()

        self.tabWidget.setTabsClosable(True)
        self.tabWidget.tabCloseRequested.connect(self.closeTab)


    def closeTab(self, tabIndex):
        """This method closes the tab and closes the canvas. A garbage collector is used
        to collect the left memory.
        :param tabIndex: is the index of the tab
        """
        self.figArray[tabIndex].clear()
        self.figArray.pop(tabIndex)
        self.canvasArray[tabIndex].renderer.clear()
        del self.canvasArray[tabIndex].renderer
        self.canvasArray[tabIndex].mpl_disconnect(self.canvasArray[tabIndex].scroll_pick_id)
        self.canvasArray[tabIndex].mpl_disconnect(self.canvasArray[tabIndex].button_pick_id)
        self.canvasArray[tabIndex].close()
        self.canvasArray.pop(tabIndex)
        gc.collect()

        self.tabWidget.removeTab(tabIndex)

    # ------------------------------------------------------------------------------------#
    def FileNameRdOnlyBox(self):
        """This method contains a QLineEdit and label that display the selected file
            next to the browse button"""
        self.rdOnlyFileName = QtGui.QLineEdit()
        self.rdOnlyFileName.setReadOnly(True)
        self.rdOnlyFileName.setTextMargins(0, 0, 10, 0)
        self.rdOnlyFileName.setFixedWidth(125)

        self.fileNameLabel = QtGui.QLabel()
        self.fileNameLabel.setText("File Name:")

    # ------------------------------------------------------------------------------------#
    def GraphButton(self):
        """Funtion that creates a graph button, connects to the GraphData() method"""
        self.GraphBtn = QtGui.QPushButton('Graph', self)
        self.GraphBtn.clicked.connect(self.GraphData)
        self.GraphBtn.setStatusTip("Graphs the check graphs")

    def BrowseButton(self):
        """Funtion that creates a browse method, connects to the openFile() method"""
        # Button next to the FileNameRdOnly label and LineEdit
        self.BrowseBtn = QtGui.QPushButton('Browse', self)
        self.BrowseBtn.clicked.connect(self.openFile)
        self.BrowseBtn.setStatusTip("Browse and open an existing file")
    # ------------------------------------------------------------------------------------#

    def SetupComponents(self):
        """ Function to setup status bar and menu bar
        """
        self.myStatusBar = QtGui.QStatusBar()
        self.setStatusBar(self.myStatusBar)
        self.myStatusBar.showMessage('Ready', 30000)

        self.CreateActions()
        self.CreateMenus()
        self.fileMenu.addAction(self.openAction)
        self.fileMenu.addAction(self.graphingOptionsAction)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAction)
        self.graphMenu.addAction(self.graphAmplitudeAction)
        self.graphMenu.addAction(self.graphPeakPositionAction)
        self.graphMenu.addAction(self.graphPeakWidthAction)
        self.graphMenu.addAction(self.graphAmplitudeXWidthAction)
        self.graphMenu.addSeparator()
        self.graphMenu.addAction(self.graphAllAction)
        self.helpMenu.addSeparator()  
        self.helpMenu.addAction(self.aboutAction)

    def CreateActions(self):
        """Function that creates the actions used in the menu bar"""
        self.openAction = QtGui.QAction(QtGui.QIcon('openFolder.png'), '&Open',
                                        self, shortcut=QtGui.QKeySequence.Open,
                                        statusTip="Open an existing file",
                                        triggered=self.openFile)
        self.exitAction = QtGui.QAction(QtGui.QIcon('exit.png'), 'E&xit',
                                        self, shortcut="Ctrl+Q",
                                        statusTip="Exit the Application",
                                        triggered=self.exitFile)
        self.graphingOptionsAction = QtGui.QAction('Graphing Options',
                                                   self, statusTip="Dock the graphing options",
                                                   triggered=self.restoreDockGraphingOptions)
        self.graphAmplitudeAction = QtGui.QAction('Amplitude',
                                            self, statusTip="Graphs the amplitude",
                                            triggered=self.graphAmplitude)
        self.graphPeakPositionAction = QtGui.QAction('Peak Position',
                                               self, statusTip="Graphs the peak position",
                                                     triggered=self.graphPeakPosition)
        self.graphPeakWidthAction = QtGui.QAction('Peak &Width',
                                            self, shortcut="Ctrl+W", statusTip="Graphs the peak width",
                                                  triggered=self.graphPeakWidth)
        self.graphAmplitudeXWidthAction = QtGui.QAction('Amplitude X Width',
                                                  self, statusTip="Graphs the amplitude X width",
                                                        triggered=self.graphAmplitudeXWidth)
        self.graphAllAction = QtGui.QAction('Graph all',
                                      self, statusTip="Graphs all the graphs",
                                            triggered=self.graphAll)
        self.aboutAction = QtGui.QAction(QtGui.QIcon('about.png'), 'A&bout',
                                         self, shortcut="Ctrl+B", statusTip="Displays info about the graph program",
                                         triggered=self.aboutHelp)

    def CreateMenus(self):
        """This is where I initialize the menu bar and create the menus"""
        self.mainMenu = self.menuBar()
        self.fileMenu = self.mainMenu.addMenu("File")
        self.graphMenu = self.mainMenu.addMenu("Graph")
        self.helpMenu = self.mainMenu.addMenu("Help")
    # ---------------------------------------------------------------------------------------------#

    def openFile(self):
        """This method opens the file """
        openDlg = QtGui.QFileDialog()
        self.fileName = openDlg.getOpenFileName()

        self.rdOnlyFileName.setText(self.fileName)
        self.rdOnlyFileName.setStatusTip(self.fileName)

    def exitFile(self):
        response = self.msgApp("Exiting Form", "Would you like to exit the form")

        if response == "Y":
            self.close()
        else:
            pass

    def msgApp(self, title, msg):
        userInfo = QtGui.QMessageBox.question(self, title, msg, QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)

        if userInfo == QtGui.QMessageBox.Yes:
            return "Y"
        if userInfo == QtGui.QMessageBox.No:
            return "N"

    def aboutHelp(self):
        QtGui.QMessageBox.about(self, "About Data Graphing",
                          "Open a file and select the graphs you want to graph, "
                          "then click to graph the graphs. If you close down the "
                          "graphing options you can click on the ")

    # -----------------------------------------------------------------------------------------#
    def GraphingCheckBox(self):
        """This function contains a group box with check boxes"""
        self.graphCheckBx = QtGui.QGroupBox("Select graphs")

        self.checkBxAmplitude = QtGui.QCheckBox("Amplitude")
        self.checkBxPeakPosition = QtGui.QCheckBox("Peak position")
        self.checkBxPeakWidth = QtGui.QCheckBox("Peak width")
        self.checkBxAmplitudeXWidth = QtGui.QCheckBox("Amplitude x Width")
        self.checkBxGraphAll = QtGui.QCheckBox("Graph all")

        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.checkBxAmplitude)
        vbox.addWidget(self.checkBxPeakPosition)
        vbox.addWidget(self.checkBxPeakWidth)
        vbox.addWidget(self.checkBxAmplitudeXWidth)
        vbox.addWidget(self.checkBxGraphAll)

        self.checkBxAmplitude.stateChanged.connect(self.CheckGraphCheckBoxes)
        self.checkBxAmplitudeXWidth.stateChanged.connect(self.CheckGraphCheckBoxes)
        self.checkBxPeakWidth.stateChanged.connect(self.CheckGraphCheckBoxes)
        self.checkBxPeakPosition.stateChanged.connect(self.CheckGraphCheckBoxes)
        self.checkBxGraphAll.stateChanged.connect(self.CheckGraphCheckBoxes)

        self.graphCheckBx.setLayout(vbox)
    # -----------------------------------------------------------------------------------------#

    def CheckGraphCheckBoxes(self):
        """This function contains different conditions for the check boxes in data tab"""
        # Checks Graph all and unchecks the rest, if all are selected
        if self.checkBxGraphAll.isChecked() is False and self.checkBxPeakPosition.isEnabled() is False \
                and self.checkBxAmplitude.isEnabled() is False and self.checkBxPeakWidth.isEnabled() is False \
                and self.checkBxAmplitudeXWidth.isEnabled() is False:
            self.checkBxPeakPosition.setCheckState(QtCore.Qt.Unchecked)
            self.checkBxAmplitude.setCheckState(QtCore.Qt.Unchecked)
            self.checkBxPeakWidth.setCheckState(QtCore.Qt.Unchecked)
            self.checkBxAmplitudeXWidth.setCheckState(QtCore.Qt.Unchecked)
            self.checkBxPeakPosition.setEnabled(True)
            self.checkBxAmplitude.setEnabled(True)
            self.checkBxPeakWidth.setEnabled(True)
            self.checkBxAmplitudeXWidth.setEnabled(True)

        # Checks and disables other boxes when Graph all is checked
        if self.checkBxGraphAll.isChecked():
            self.checkBxPeakPosition.setCheckState(QtCore.Qt.Checked)
            self.checkBxAmplitude.setCheckState(QtCore.Qt.Checked)
            self.checkBxPeakWidth.setCheckState(QtCore.Qt.Checked)
            self.checkBxAmplitudeXWidth.setCheckState(QtCore.Qt.Checked)
            self.checkBxPeakPosition.setEnabled(False)
            self.checkBxAmplitude.setEnabled(False)
            self.checkBxPeakWidth.setEnabled(False)
            self.checkBxAmplitudeXWidth.setEnabled(False)

        # Checks Graph all if all other boxes are checked
        if self.checkBxAmplitude.isChecked() and self.checkBxPeakPosition.isChecked() \
                and self.checkBxPeakWidth.isChecked() and self.checkBxAmplitudeXWidth.isChecked():
            self.checkBxGraphAll.setChecked(True)
    # -----------------------------------------------------------------------------------------#
    def graphAmplitude(self):
        """This method graphs the Amplitude graph"""
        if self.fileName is not None:
            if os.path.isfile(self.fileName):
                mainGraph = QtGui.QWidget()

                dpi = 100
                fig = Figure((5.0, 4.0), dpi=dpi)
                canvas = FigureCanvas(fig)
                canvas.setParent(mainGraph)

                data = np.loadtxt(open(self.fileName))
                axes = fig.add_subplot(111)

                yy0 = data[:, 0]
                yy_err0 = data[:, 1]
                xx = [-7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 7, 6, 5, 4, 3, 2, 1, 0, -1, -2, -3, -4, -5, -6,
                      -7]
                axes.plot(xx, yy0)
                axes.errorbar(xx, yy0, yerr=yy_err0, fmt='o')
                axes.set_title('Amplitude')
                canvas.draw()

                tab = QtGui.QWidget()
                tab.setStatusTip("Amplitude graph")
                vbox = QtGui.QVBoxLayout()
                graphNavigationBar = NavigationToolbar(canvas, self)
                vbox.addWidget(graphNavigationBar)
                vbox.addWidget(canvas)
                tab.setLayout(vbox)

                self.tabWidget.addTab(tab, "Amplitude")

                self.canvasArray.append(canvas)
                self.figArray.append(fig)


    # -----------------------------------------------------------------------------------------#
    def graphPeakPosition(self):
        """This method graphs the Peak and position graph"""
        if self.fileName is not None:
            if os.path.isfile(self.fileName):
                mainGraph = QtGui.QWidget()

                dpi = 100
                fig = Figure((5.0, 4.0), dpi=dpi)
                canvas = FigureCanvas(fig)
                canvas.setParent(mainGraph)

                data = np.loadtxt(open(self.fileName))
                axes = fig.add_subplot(111)

                xx = [-7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 7, 6, 5, 4, 3, 2, 1, 0, -1, -2, -3, -4, -5, -6,
                      -7]
                yy1 = data[:, 2]
                yy_err1 = data[:, 3]
                axes.plot(xx, yy1)
                axes.errorbar(xx, yy1, yerr=yy_err1, fmt='o')
                axes.set_title('Peak Position')
                canvas.draw()

                tab = QtGui.QWidget()
                tab.setStatusTip("Peak position graph")

                vbox = QtGui.QVBoxLayout()
                graphNavigationBar = NavigationToolbar(canvas, self)
                vbox.addWidget(graphNavigationBar)
                vbox.addWidget(canvas)
                tab.setLayout(vbox)

                self.tabWidget.addTab(tab, "Peak Position")


                self.canvasArray.append(canvas)
                self.figArray.append(fig)

    # ----------------------------------------------------------------------------------------------------#
    def graphPeakWidth(self):
        """This method graphs the Peak width graph"""
        if self.fileName is not None:
            if os.path.isfile(self.fileName):
                mainGraph = QtGui.QWidget()

                dpi = 100
                fig = Figure((5.0, 4.0), dpi=dpi)
                canvas = FigureCanvas(fig)
                canvas.setParent(mainGraph)

                data = np.loadtxt(open(self.fileName))
                axes = fig.add_subplot(111)

                xx = [-7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 7, 6, 5, 4, 3, 2, 1, 0, -1, -2, -3, -4, -5, -6,
                      -7]
                yy2 = data[:, 4]
                yy_err2 = data[:, 5]
                axes.plot(xx, yy2)
                axes.errorbar(xx, yy2, yerr=yy_err2, fmt='o')
                axes.set_title('Peak Width')
                canvas.draw()

                tab = QtGui.QWidget()
                tab.setStatusTip("Peak width graph")
                vbox = QtGui.QVBoxLayout()
                graphNavigationBar = NavigationToolbar(canvas, self)
                vbox.addWidget(graphNavigationBar)
                vbox.addWidget(canvas)
                tab.setLayout(vbox)
                self.tabWidget.addTab(tab, "Peak Width")

                self.canvasArray.append(canvas)
                self.figArray.append(fig)

    # ----------------------------------------------------------------------------------------------------#
    def graphAmplitudeXWidth(self):
        """This method graphs the amplitude x width graph"""
        if self.fileName is not None:
            if os.path.isfile(self.fileName):
                mainGraph = QtGui.QWidget()

                dpi = 100
                fig = Figure((5.0, 4.0), dpi=dpi)
                canvas = FigureCanvas(fig)
                canvas.setParent(mainGraph)

                data = np.loadtxt(open(self.fileName))
                axes = fig.add_subplot(111)

                xx = [-7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 7, 6, 5, 4, 3, 2, 1, 0, -1, -2, -3, -4, -5, -6,
                      -7]
                yy2 = data[:, 4]
                yy0 = data[:, 0]
                yy3 = yy0 * yy2
                axes.plot(xx, yy3)
                axes.plot(xx, yy3, 'go')
                axes.set_title('Amplitude Times Width')
                canvas.draw()

                tab = QtGui.QWidget()
                tab.setStatusTip("Amplitude times width graph")
                vbox = QtGui.QVBoxLayout()
                graphNavigationBar = NavigationToolbar(canvas, self)
                vbox.addWidget(graphNavigationBar)
                vbox.addWidget(canvas)
                tab.setLayout(vbox)
                self.tabWidget.addTab(tab, "Amplitude Times Width")

                self.canvasArray.append(canvas)
                self.figArray.append(fig)

    # ------------------------------------------------------------------------------------------------------------#
    def graphAll(self):
        """Fuction graphs all the graphs. Makes sure the fileName is not empty
            and that the path leads to a file
        """
        if self.fileName is not None:
            if os.path.isfile(self.fileName):
                self.graphAmplitude()
                self.graphPeakPosition()
                self.graphPeakWidth()
                self.graphAmplitudeXWidth()

    # -----------------------------------------------------------------------------------------#
    def GraphData(self):
        """Function that graphs the information from the file and codes on the different method to graph
        depending on the check boxes the user has chosen. Checks for the fileName not to be empty and
        the path to lead to a file.
        """
        if self.fileName is "" or self.fileName is None:
            QtGui.QMessageBox.warning(self, "Error - No File", "There is no data to graph."
                                                      " Make sure a file has been open.")
        else:
            if os.path.isfile(self.fileName) == False:
                QtGui.QMessageBox.warning(self, "Error - No File", "There is no data to graph."
                                                                   " Make sure a file has been open.")
            else:

                if self.checkBxAmplitude.isChecked() and self.checkBxGraphAll.isChecked() == False:
                    self.graphAmplitude()

                if self.checkBxPeakPosition.isChecked() and self.checkBxGraphAll.isChecked() == False:
                    self.graphPeakPosition()

                if self.checkBxPeakWidth.isChecked() and self.checkBxGraphAll.isChecked() == False:
                    self.graphPeakWidth()

                if self.checkBxAmplitudeXWidth.isChecked() and self.checkBxGraphAll.isChecked() == False:
                    self.graphAmplitudeXWidth()

                if self.checkBxGraphAll.isChecked():
                   self.graphAll()

        self.checkBxGraphAll.setCheckState(QtCore.Qt.Unchecked)
        self.checkBxAmplitude.setCheckState(QtCore.Qt.Unchecked)
        self.checkBxAmplitudeXWidth.setCheckState(QtCore.Qt.Unchecked)
        self.checkBxPeakPosition.setCheckState(QtCore.Qt.Unchecked)
        self.checkBxPeakWidth.setCheckState(QtCore.Qt.Unchecked)

def main():
    """Main method"""
    app = QtGui.QApplication(sys.argv)
    myMainWindow = MainWindow()
    myMainWindow.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()