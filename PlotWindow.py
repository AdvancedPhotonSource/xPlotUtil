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
from GraphingUtilities import GraphingUtil
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4 import NavigationToolbar2QT as NavigationToolbar
import gc
# --------------------------------------------------------------------------------------#

class MainWindow (QtGui.QMainWindow):

    def __init__ (self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.setGeometry(50, 50, 1000, 700)
        self.setMinimumSize(800, 700)
        self.setWindowTitle("xPlot Util")
        self.setWindowIcon(QtGui.QIcon('Icons/Graph.png'))
        self.grphUtil = GraphingUtil(parent = self)
        self.fileNm = self.grphUtil.fileName
        self.canvasArray = []
        self.figArray = []


        self.SetupComponents()
        self.windowTabs()
        self.grphUtil.dockFittingOneOptions()
        self.setCentralWidget(self.tabWidget)


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
        self.graphMenu.addAction(self.graphingFittingOne)

        self.helpMenu.addSeparator()  
        self.helpMenu.addAction(self.aboutAction)

    def CreateActions(self):
        """Function that creates the actions used in the menu bar"""
        self.openAction = QtGui.QAction(QtGui.QIcon('openFolder.png'), '&Open',
                                        self, shortcut=QtGui.QKeySequence.Open,
                                        statusTip="Open an existing file",
                                        triggered=self.grphUtil.openFile)
        self.exitAction = QtGui.QAction(QtGui.QIcon('exit.png'), 'E&xit',
                                        self, shortcut="Ctrl+Q",
                                        statusTip="Exit the Application",
                                        triggered=self.exitFile)
        self.graphingFittingOne= QtGui.QAction('Fitting One',
                                                   self, statusTip="Dock the graphing options",
                                                   triggered= self.grphUtil.restoreDockFittingOneOptions)
        self.graphRawData= QtGui.QAction('Raw Data',
                                            self, statusTip="Plots different graphs for the raw data")
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

    # ----------------------------------------------------------------------------------------------------------#
    def graphAmplitude(self):
        """This method graphs the Amplitude graph"""

        mainGraph = QtGui.QWidget()

        dpi = 100
        fig = Figure((5.0, 4.0), dpi=dpi)
        canvas = FigureCanvas(fig)
        canvas.setParent(mainGraph)

        data = np.loadtxt(open(self.fileNm))
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

        mainGraph = QtGui.QWidget()

        dpi = 100
        fig = Figure((5.0, 4.0), dpi=dpi)
        canvas = FigureCanvas(fig)
        canvas.setParent(mainGraph)

        data = np.loadtxt(open(self.fileNm))
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

        mainGraph = QtGui.QWidget()

        dpi = 100
        fig = Figure((5.0, 4.0), dpi=dpi)
        canvas = FigureCanvas(fig)
        canvas.setParent(mainGraph)

        data = np.loadtxt(open(self.fileNm))
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

        mainGraph = QtGui.QWidget()

        dpi = 100
        fig = Figure((5.0, 4.0), dpi=dpi)
        canvas = FigureCanvas(fig)
        canvas.setParent(mainGraph)

        data = np.loadtxt(open(self.fileNm))
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

        self.graphAmplitude()
        self.graphPeakPosition()
        self.graphPeakWidth()
        self.graphAmplitudeXWidth()

    # ---------------------------------------------------------------------------------------------------#
    def  GraphRawData(self):
        self.PlotColorGraphRawData()

    def PlotColorGraphRawData(self):
        """This function uses the raw data to plot a color graph of the data
        """
        if self.fileNm is not None:
            if os.path.isfile(self.fileNm):
                mainGraph = QtGui.QWidget()

                dpi = 100
                fig = Figure((3.0, 3.0), dpi=dpi)
                canvas = FigureCanvas(fig)
                canvas.setParent(mainGraph)
                axes = fig.add_subplot(111)

                print(self.fileNm)
                title0 = 'file:'
                # read file header
                inF = open(self.fileNm, 'r')
                lines = inF.readlines()
                header = ''
                for (iL, line) in enumerate(lines):
                    if line.startswith('#'):
                        header = line
                inF.close()
                data = np.loadtxt(open(self.fileNm))
                #    print data.shape, header
                words = header.split()
                ampl = ''
                if len(words) > 6:
                    ampl = words[6]
                # line1 = '[0] --> [-' +str(ampl) + '] --> [0] --> [+'+str(ampl) + '] --> [0]'
                line1 = '[-' + str(ampl) + '] --> [0] --> [+' + str(ampl) + '] --> [0] --> [-' + str(ampl) + '] '
                title0 = title0 + '\n' + header  # + '\t' + line1
                nRow = data.shape[0]  # Gets the number of rows
                nCol = data.shape[1]  # Gets the number of columns
                x = 0
                for f in range(nCol):
                    if (np.mean(data[:, f]) == 0):
                        pass
                    else:
                        x += 1
                nCol = x

                TT = np.zeros((nRow, nCol))
                for i in range(nCol):
                    TT[:, i] = data[:, i]

                tMax = np.max(TT)
                tMin = np.min(TT)

                z = np.linspace(tMin, tMax, endpoint=True)
                YY = range(nCol)
                XX = range(nRow)

                axes.contourf(YY, XX, TT, z)
                fig.colorbar(axes.contourf(YY, XX, TT, z))
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