#!/usr/bin/env python

"""
Copyright (c) UChicago Argonne, LLC. All rights reserved.
See LICENSE file.
"""
# --------------------------------------------------------------------------------------#
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
from DockedOptions import DockedOption
from GaussianFit import GaussianFitting
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4 import NavigationToolbar2QT as NavigationToolbar
import gc
import ntpath
# --------------------------------------------------------------------------------------#

class MainWindow (QtGui.QMainWindow):

    def __init__ (self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.setGeometry(50, 50, 1000, 800)
        self.setMinimumSize(800, 700)
        self.setWindowTitle("xPlot Util")
        self.setWindowIcon(QtGui.QIcon('Icons/Graph.png'))
        self.dockedOpt = DockedOption(parent = self)
        self.canvasArray = []
        self.figArray = []
        self.TT = [[]]

        self.SetupComponents()
        self.windowTabs()
        self.dockedOpt.DockRawDataOptions()
        self.setCentralWidget(self.tabWidget)
        self.setTabPosition(QtCore.Qt.RightDockWidgetArea | QtCore.Qt.LeftDockWidgetArea, QtGui.QTabWidget.North)

    # ---------------------------------------------------------------------------------------------#
    def windowTabs(self):
        """This function creates the central widget QTabWidget and creates the Data tab"""
        self.tabWidget = QtGui.QTabWidget()

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

    # -------------------------------------------------------------------------------------#
    def SetupComponents(self):
        """ Function to setup status bar and menu bar
        """
        self.myStatusBar = QtGui.QStatusBar()
        self.setStatusBar(self.myStatusBar)
        self.myStatusBar.showMessage('Ready', 30000)

        self.CreateActions()
        self.CreateMenus()
        self.fileMenu.addAction(self.openAction)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAction)
        self.graphMenu.addAction(self.graphRawData)
        self.graphMenu.addAction(self.GaussianFit)
        self.graphMenu.addAction(self.LFit)
        self.LFit.setEnabled(False)
        self.helpMenu.addSeparator()  
        self.helpMenu.addAction(self.aboutAction)

    def CreateActions(self):
        """Function that creates the actions used in the menu bar"""
        self.openAction = QtGui.QAction(QtGui.QIcon('openFolder.png'), '&Open',
                                        self, shortcut=QtGui.QKeySequence.Open,
                                        statusTip="Open an existing file",
                                        triggered=self.dockedOpt.openFile)
        self.exitAction = QtGui.QAction(QtGui.QIcon('exit.png'), 'E&xit',
                                        self, shortcut="Ctrl+Q",
                                        statusTip="Exit the Application",
                                        triggered=self.exitFile)
        self.GaussianFit= QtGui.QAction('Gaussian Fit',
                                                   self, statusTip="Dock the graphing options",
                                                   triggered= self.dockedOpt.GaussianFittingData)
        self.graphRawData= QtGui.QAction('Raw Data',
                                            self, statusTip="Plots different graphs for the raw data",
                                             triggered= self.dockedOpt.restoreRawDataOptions)
        self.LFit = QtGui.QAction('L Fit',
                                          self, statusTip="Fits the data to the L fit",
                                          triggered= self.dockedOpt.LFittingData)
        self.aboutAction = QtGui.QAction(QtGui.QIcon('about.png'), 'A&bout',
                                         self, shortcut="Ctrl+B", statusTip="Displays info about the graph program",
                                         triggered=self.aboutHelp)

    def CreateMenus(self):
        """This is where I initialize the menu bar and create the menus"""
        self.mainMenu = self.menuBar()
        self.fileMenu = self.mainMenu.addMenu("File")
        self.graphMenu = self.mainMenu.addMenu("xPlot")
        self.helpMenu = self.mainMenu.addMenu("Help")
    # ---------------------------------------------------------------------------------------------#
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
        QtGui.QMessageBox.about(self, "About xPlot Util",
                          "Open a file and graph the raw data or click on the xPlot tab\n "
                          "to fit the data. Also under xPlot you can restore the Graphing options "
                          "if you close them.")

    # ---------------------------------------------------------------------------------------------------#
    def PlotColorGraphRawData(self):
        """This function uses the raw data to plot a color graph of the data
        """
        mainGraph = QtGui.QWidget()
        fN = str(self.dockedOpt.fileName)
        dpi = 100
        fig = Figure((3.0, 3.0), dpi=dpi)
        canvas = FigureCanvas(fig)
        canvas.setParent(mainGraph)
        axes = fig.add_subplot(111)

        title0 = 'file:' + ntpath.basename(fN)
        # read file header
        inF = open(self.dockedOpt.fileName, 'r')
        lines = inF.readlines()
        header = ''
        for (iL, line) in enumerate(lines):
            if line.startswith('#'):
                header = line
        inF.close()
        data = np.loadtxt(open(self.dockedOpt.fileName))
        words = header.split()
        ampl = ''
        if len(words) > 6:
            ampl = words[6]
        line1 = '[-' + str(ampl) + '] --> [0] --> [+' + str(ampl) + '] --> [0] --> [-' + str(ampl) + '] '
        title0 = title0 + '\n' + header
        nRow = data.shape[0]  # Gets the number of rows
        nCol = data.shape[1]  # Gets the number of columns
        x = 0
        for f in range(nCol):
            if (np.mean(data[:, f]) == 0):
                pass
            else:
                x += 1
        nCol = x

        self.TT = np.zeros((nRow, nCol))
        for i in range(nCol):
            self.TT[:, i] = data[:, i]

        tMax = np.max(self.TT)
        tMin = np.min(self.TT)
        z = np.linspace(tMin, tMax, endpoint=True)
        YY = range(nCol)
        XX = range(nRow)

        axes.contourf(YY, XX, self.TT, z)
        fig.colorbar(axes.contourf(YY, XX, self.TT, z))
        axes.set_title(title0)
        axes.set_xlabel('array_index (voltage:' + line1 + ')')
        axes.set_ylabel('spec_pnt: L')
        canvas.draw()

        tab = QtGui.QWidget()
        tab.setStatusTip("Raw Data")
        vbox = QtGui.QVBoxLayout()
        graphNavigationBar = NavigationToolbar(canvas, self)
        vbox.addWidget(graphNavigationBar)
        vbox.addWidget(canvas)
        tab.setLayout(vbox)
        self.tabWidget.addTab(tab, "Raw Data")
        self.tabWidget.setCurrentWidget(tab)

        self.canvasArray.append(canvas)
        self.figArray.append(fig)

    # ----------------------------------------------------------------------------------------------#
    def PlotLineGraphRawData(self):
        """This method graphs the raw data into line graphs"""
        mainGraph = QtGui.QWidget()

        dpi = 100
        fig = Figure((3.0, 3.0), dpi=dpi)
        canvas = FigureCanvas(fig)
        canvas.setParent(mainGraph)
        axes = fig.add_subplot(111)

        data = np.loadtxt(open(self.dockedOpt.fileName))

        nRow = data.shape[0]  # Gets the number of rows
        nCol = data.shape[1]  # Gets the number of columns
        x = 0
        for f in range(nCol):
            if (np.mean(data[:, f]) == 0):
                pass
            else:
                x += 1
        nCol = x

        self.TT = np.zeros((nRow, nCol))
        for i in range(nCol):
            self.TT[:, i] = data[:, i]

        xx = arange(0, nRow)

        for j in range(nCol):
            yy = self.TT[:, j]
            axes.plot(xx, yy)

        axes.set_title('Fit for Time Constant')
        axes.set_xlabel('Bins')
        axes.set_ylabel('Intensity')
        canvas.draw()

        tab = QtGui.QWidget()
        tab.setStatusTip("Line Graph of Raw Data")
        vbox = QtGui.QVBoxLayout()
        graphNavigationBar = NavigationToolbar(canvas, self)
        vbox.addWidget(graphNavigationBar)
        vbox.addWidget(canvas)
        tab.setLayout(vbox)
        self.tabWidget.addTab(tab, "Line Graph Raw Data")
        self.tabWidget.setCurrentWidget(tab)

        self.canvasArray.append(canvas)
        self.figArray.append(fig)


def main():
    """Main method"""
    app = QtGui.QApplication(sys.argv)
    myMainWindow = MainWindow()
    myMainWindow.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()