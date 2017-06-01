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
    from PySide.QtGui import *
    from PySide.QtCore import *
else:
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import *

import matplotlib.pyplot as plt
from DockedOptions import DockedOption
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
import gc
import ntpath
# --------------------------------------------------------------------------------------#

class MainWindow (QMainWindow):

    def __init__ (self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.setGeometry(50, 50, 1000, 800)
        self.setMinimumSize(800, 700)
        self.setWindowTitle("xPlot Util")
        self.setWindowIcon(QIcon('Icons/Graph.png'))
        self.dockedOpt = DockedOption(parent = self)
        self.gausFit = self.dockedOpt.gausFit
        self.readSpec = self.dockedOpt.readSpec
        self.canvasArray = []
        self.figArray = []

        self.SetupComponents()
        self.windowTabs()
        # self.dockedOpt.DockRawDataOptions() #Starts with the raw data options
        self.dockedOpt.DockMainOptions()
        self.setCentralWidget(self.tabWidget)
        self.setTabPosition(Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea, QTabWidget.North)

    # ---------------------------------------------------------------------------------------------#
    def windowTabs(self):
        """This function creates the central widget QTabWidget and creates the Data tab"""
        self.tabWidget = QTabWidget()

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
        self.myStatusBar = QStatusBar()
        self.setStatusBar(self.myStatusBar)
        self.myStatusBar.showMessage('Ready', 30000)

        self.CreateActions()
        self.CreateMenus()
        self.fileMenu.addAction(self.openAction)
        self.fileMenu.addAction(self.resetAction)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAction)
        self.graphMenu.addAction(self.mainOptionsAction)
        self.graphMenu.addAction(self.GaussianFitAction)
        self.graphMenu.addAction(self.LFit)
        self.graphMenu.addSeparator()
        self.graphMenu.addAction(self.reportAction)
        self.helpMenu.addSeparator()  
        self.helpMenu.addAction(self.aboutAction)

        # Setting L Fit to not enabled until the Gaussian Fit is complete
        self.LFit.setEnabled(False)

    def CreateActions(self):
        """Function that creates the actions used in the menu bar"""
        self.openAction = QAction(QIcon('openFolder.png'), '&Open',
                                        self, shortcut=QKeySequence.Open,
                                        statusTip="Open an existing file",
                                        triggered=self.readSpec.openSpecFile)
        self.exitAction = QAction(QIcon('exit.png'), 'E&xit',
                                        self, shortcut="Ctrl+Q",
                                        statusTip="Exit the Application",
                                        triggered=self.exitFile)
        self.resetAction = QAction('Reset', self, statusTip="Resets xPlot Util",
                                  triggered=self.dockedOpt.resetxPlot)
        self.reportAction = QAction('Report', self, statusTip="Create a report of the data",
                                         triggered=self.ReportDialog)
        self.mainOptionsAction = QAction('Main Options', self, statusTip="Main options for xPlot Util",
                                             triggered=self.dockedOpt.restoreMainOptions)
        self.GaussianFitAction= QAction('Gaussian Fit',self, statusTip="Dock the graphing options" ,
                                        triggered=self.dockedOpt.WhichPeakGaussianFit)
        self.LFit = QAction('L Fit', self, statusTip="Fits the data to the L fit",
                                  triggered =self.dockedOpt.GraphingLOptionsTree)
        self.aboutAction = QAction(QIcon('about.png'), 'A&bout',
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
        response = self.dockedOpt.msgApp("Exiting Form", "Would you like to exit the form")

        if response == "Y":
            self.close()
        else:
            pass

    def aboutHelp(self):
        QMessageBox.about(self, "About xPlot Util",
                          "Click on the browse button to select and open a spec file.\n"
                          "Choose a PVValue and under xPlot in the menu bar you can click\n on the fits. "
                          "Once you've clicked on the fit, checkboxes will apear that\n will enable you "
                          "to graph")

    # ---------------------------------------------------------------------------------------------------#
    def savingCanvasTabs(self,tab, name, canvas, fig):
        self.tabWidget.addTab(tab, name)
        self.tabWidget.setCurrentWidget(tab)

        self.canvasArray.append(canvas)
        self.figArray.append(fig)

    # ---------------------------------------------------------------------------------------------------#
    def PlotColorGraphRawData(self):
        """This function uses the raw data to plot a color graph of the data
        """
        mainGraph = QWidget()
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
        words = header.split()
        ampl = ''
        if len(words) > 6:
            ampl = words[6]
        line1 = '[-' + str(ampl) + '] --> [0] --> [+' + str(ampl) + '] --> [0] --> [-' + str(ampl) + '] '

        nRow, nCol = self.dockedOpt.fileInfo()

        tMax = np.max(self.dockedOpt.TT)
        tMin = np.min(self.dockedOpt.TT)
        z = np.linspace(tMin, tMax, endpoint=True)
        YY = range(nCol)
        if self.readSpec.lMax - self.readSpec.lMin == 0:
            XX = range(len(self.readSpec.L))
            axes.set_ylabel('Points in Bins')
        else:
            XX = self.readSpec.L
            axes.set_ylabel('RLU (Reciprocal Lattice Unit)')
        axes.contourf(YY, XX, self.dockedOpt.TT, z)
        fig.colorbar(axes.contourf(YY, XX, self.dockedOpt.TT, z))
        axes.set_title(title0)
        axes.set_xlabel('array_index (voltage:' + line1 + ')')
        canvas.draw()

        tab = QWidget()
        tab.setStatusTip("Raw Data")
        vbox = QVBoxLayout()
        graphNavigationBar = NavigationToolbar(canvas, self)
        vbox.addWidget(graphNavigationBar)
        vbox.addWidget(canvas)
        tab.setLayout(vbox)
        name = 'Color Graph Raw Data'

        self.savingCanvasTabs(tab, name, canvas, fig)

    # ----------------------------------------------------------------------------------------------#
    def GraphUtilRawDataLineGraphs(self, canvas, fig, gTitle, xLabel, yLabel, statTip, tabName, whichGraph):
        mainGraph = QWidget()

        canvas.setParent(mainGraph)
        axes = fig.add_subplot(111)

        nRow, nCol = self.dockedOpt.fileInfo()

        if whichGraph == 'B':
            xx = range(nRow)
        elif whichGraph == 'L':
            xx = self.readSpec.L

        for j in range(nCol):
            yy = self.dockedOpt.TT[:, j]
            axes.plot(xx, yy)

        axes.set_title(gTitle)
        axes.set_xlabel(xLabel)
        axes.set_ylabel(yLabel)
        canvas.draw()

        tab = QWidget()
        tab.setStatusTip(statTip)
        vbox = QVBoxLayout()
        graphNavigationBar = NavigationToolbar(canvas, self)
        vbox.addWidget(graphNavigationBar)
        vbox.addWidget(canvas)
        tab.setLayout(vbox)

        self.savingCanvasTabs(tab, tabName, canvas, fig)

    # ----------------------------------------------------------------------------------------------#
    def PlotLineGraphRawDataRLU(self):
        """This method graphs the raw data into a line graph wiith RLU as x-axis"""
        fig = Figure((3.0, 3.0), dpi=100)
        canvas = FigureCanvas(fig)

        gTitle = 'Raw Data in L Constant (Scan#: ' + str(self.dockedOpt.specDataList.currentRow() + 1) + ')'
        xLabel = 'RLU (Reciprocal Lattice Unit)'
        yLabel = 'Intensity'
        statTip = 'Raw Data in RLU (Reciprocal Lattice Unit)'
        tabName = 'Raw Data RLU'

        self.GraphUtilRawDataLineGraphs(canvas, fig, gTitle, xLabel, yLabel, statTip, tabName, 'L')

    # ----------------------------------------------------------------------------------------------#
    def PlotLineGraphRawDataBins(self):
        """This method graphs the raw data into a line graph into bins"""
        fig = Figure((3.0, 3.0), dpi=100)
        canvas = FigureCanvas(fig)

        gTitle = 'Raw Data in Bins (Scan#: ' + str(self.dockedOpt.specDataList.currentRow() + 1) + ')'
        xLabel = 'Bins'
        yLabel = 'Intensity'
        statTip = 'Raw Data in Bins'
        tabName = 'Raw Data Bins'

        self.GraphUtilRawDataLineGraphs(canvas, fig, gTitle, xLabel, yLabel, statTip, tabName, 'B')

    # -----------------------------Creating Report-----------------------------------------------------------#
    def ReportButton(self):
        """This button creates a report"""
        self.reportBtn = QPushButton('Report', self)
        self.reportBtn.setStatusTip("Creates a report of the chosen data.")
        self.reportBtn.clicked.connect(self.CreateReport)

    # -------------------------------------------------------------------------------------------------------#
    def CancelReportButton(self):
        """This button cancels the creation of a report"""
        self.cancelReportBtn = QPushButton('Cancel', self)
        self.cancelReportBtn.setStatusTip("Cancels the creation of the report.")
        self.cancelReportBtn.clicked.connect(self.reportDialog.close)

    # ------------------------------------------------------------------------------------------------------#
    def CreateReport(self):
        self.reportDialog.close()
        self.ReportSaveDialog()
        if self.reportFile != "":
            self.WrittingReport()

    # ------------------------------------------------------------------------------------------------------#
    def ReportSaveDialog(self):
        filters = "All files (*.*);;Text files (*txt);;Python files (*.py)"
        selectedFilters = "Text files (*txt);;Python files (*.py)"
        self.reportFile, self.reportFileFilter = QFileDialog.getSaveFileName(self, "Save Report", "", selectedFilters)
    # ------------------------------------------------------------------------------------------------------#
    def ReportDialog(self):
        self.reportDialog = QDialog(self)
        vBox = QVBoxLayout()
        buttonLayout = QHBoxLayout()

        self.ReportCheckBox()
        self.CancelReportButton()
        self.ReportButton()

        buttonLayout.addWidget(self.cancelReportBtn)
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(self.reportBtn)

        vBox.addWidget(self.reportGroupBx)
        vBox.addLayout(buttonLayout)

        self.reportDialog.setWindowTitle("Create Final Report")
        self.reportDialog.setLayout(vBox)
        self.reportDialog.exec_()

    # -----------------------------------------------------------------------------------------#
    def ReportCheckBox(self):
        """This function contains a group box with check boxes"""
        self.reportGroupBx = QGroupBox("Select the data")

        self.reportCbGausFit = QCheckBox("Gaussian Fit")
        self.reportCbLFit = QCheckBox("L Fit")
        self.reportCbGausFit.setEnabled(False)
        self.reportCbLFit.setEnabled(False)

        if self.dockedOpt.gausFitStat == True:
            self.reportCbGausFit.setEnabled(True)
        if self.dockedOpt.LFitStat == True:
            self.reportCbLFit.setEnabled(True)

        vbox = QVBoxLayout()
        vbox.addWidget(self.reportCbGausFit)
        vbox.addWidget(self.reportCbLFit)

        self.reportGroupBx.setLayout(vbox)

    def WrittingReport(self):
        """This method writes the data to the report file, calling on the appropriate methods.
        """
        _, nCol = self.dockedOpt.fileInfo()
        reportData = np.zeros((nCol, 0))
        header = "#H "
        scanNum = str(self.dockedOpt.specDataList.currentRow() + 1)
        comment = "#C PVvalue #" + scanNum + "\n"

        if self.reportCbGausFit.isChecked():
            if self.dockedOpt.onePeakStat == True:
                header += "Amp Err Position Err Width Err "
                reportData = np.concatenate((reportData, self.gausFit.OnePkFitData), axis=1)
            if self.dockedOpt.twoPeakStat == True:
                header += "Amp Err Amp Err Pos Err Pos Err Wid Err Wid Err "
                reportData = np.concatenate((reportData, self.gausFit.TwoPkGausFitData), axis=1)

        if self.reportCbLFit.isChecked():
            if self.dockedOpt.onePeakStat == True:
                header += "L "
                # Reshapes the array so that it can be append
                L = np.reshape(self.gausFit.LPosData, (len(self.gausFit.LPosData), 1))  # Enables array to be appended
                reportData = np.concatenate((reportData, L), axis=1)
            if self.dockedOpt.twoPeakStat == True:
                header += "L1 L2 "
                L1 = np.reshape(self.gausFit.LPos1Data, (len(self.gausFit.LPos1Data), 1))  # Reshapes to append
                L2 = np.reshape(self.gausFit.LPos2Data, (len(self.gausFit.LPos2Data), 1))  # Reshapes to append
                print len(L1)
                print len(L2)
                print len(reportData)

                reportData = np.concatenate((reportData, L1, L2), axis=1)

        # Writes to sheet
        np.savetxt(self.reportFile, reportData, fmt=str('%f'), header=header, comments=comment)


def main():
    """Main method"""
    app = QApplication(sys.argv)
    myMainWindow = MainWindow()
    myMainWindow.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()