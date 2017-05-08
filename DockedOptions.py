#!/usr/bin/env python

"""
Copyright (c) UChicago Argonne, LLC. All rights reserved.
See LICENSE file.

"""

# --------------------------------------------------------------------------------------#
from __future__ import unicode_literals
from pylab import *
from matplotlib.backends import qt_compat
import os
from GaussianFit import GaussianFitting
use_pyside = qt_compat.QT_API == qt_compat.QT_API_PYSIDE
if use_pyside:
    from PySide import QtGui, QtCore
else:
    from PyQt4 import QtGui, QtCore


class DockedOption(QtGui.QDockWidget):

    def __init__ (self, parent=None):
        super(DockedOption, self).__init__(parent)
        self.fileName = None
        self.myMainWindow = parent
        self.gausFit = GaussianFitting(self)
        self.gausFitStat = False
        self.LFitStat = False
        self.dockGaussianFitOptions

 # -----------------------------------------------------------------------------#
    def dockGaussianFitOptions(self):
        """Function that creates the dockWidget, Graph Options for fitting one
        """
        self.dockDataGausFit = QtGui.QDockWidget("Gaussian Fit", self)
        self.dockDataGausFit.setFloating(False)
        self.dockDataGausFit.setMaximumWidth(320)
        self.dockDataGausFit.setMinimumWidth(320)
        self.dockDataGausFit.setAllowedAreas(QtCore.Qt.RightDockWidgetArea | QtCore.Qt.LeftDockWidgetArea)

        layout = QtGui.QFormLayout()
        FileHLayout = QtGui.QHBoxLayout()
        BtnLayout = QtGui.QHBoxLayout()
        self.dataDocked = QtGui.QWidget()

        self.FileNameRdOnlyBox()
        self.GraphFittingOneCheckBox()
        self.GraphFittingOneButton()
        self.GraphAllButton()

        FileHLayout.addWidget(self.fileNameLabel)
        FileHLayout.addWidget(self.rdOnlyFileNameG)
        FileHLayout.addStretch(1)

        BtnLayout.addWidget(self.GraphAllBtn)
        BtnLayout.addStretch(1)
        BtnLayout.addWidget(self.GraphFittingOneBtn)

        layout.addRow(FileHLayout)
        layout.addRow(self.graphCheckBx1)
        layout.addRow(self.graphCheckBx2)
        layout.addRow(BtnLayout)
        self.dataDocked.setLayout(layout)
        self.dockDataGausFit.setWidget(self.dataDocked)

        # Adding the docked widget to the main window
        self.myMainWindow.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dockDataGausFit)
        self.myMainWindow.tabifyDockWidget(self.dockRawData, self.dockDataGausFit)


    def GraphFittingOneCheckBox(self):
        """This function contains a group box with check boxes for fitting one"""
        self.graphCheckBx1 = QtGui.QGroupBox("Peak #1")
        self.graphCheckBx2 = QtGui.QGroupBox("Peak #2")

        self.checkBxAmplitude1 = QtGui.QCheckBox("Amplitude")
        self.checkBxPeakPosition1 = QtGui.QCheckBox("Position")
        self.checkBxPeakWidth1 = QtGui.QCheckBox("Width")
        self.checkBxAmplitudeXWidth1 = QtGui.QCheckBox("Amplitude x Width")
        self.checkBxAmplitude2 = QtGui.QCheckBox("Amplitude")
        self.checkBxPeakPosition2 = QtGui.QCheckBox("Position")
        self.checkBxPeakWidth2 = QtGui.QCheckBox("Width")
        self.checkBxAmplitudeXWidth2  = QtGui.QCheckBox("Amplitude x Width")
        self.checkBxGraphAll = QtGui.QCheckBox("Graph all")

        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.checkBxAmplitude1)
        vbox.addWidget(self.checkBxPeakPosition1)
        vbox.addWidget(self.checkBxPeakWidth1)
        vbox.addWidget(self.checkBxAmplitudeXWidth1)

        vbox2 = QtGui.QVBoxLayout()
        vbox2.addWidget(self.checkBxAmplitude2)
        vbox2.addWidget(self.checkBxPeakPosition2)
        vbox2.addWidget(self.checkBxPeakWidth2)
        vbox2.addWidget(self.checkBxAmplitudeXWidth2)

        self.graphCheckBx1.setLayout(vbox)
        self.graphCheckBx2.setLayout(vbox2)

    # ----------------------------------------------------------------------------------------------------------#
    def restoreDockGaussianFitOptions(self):
        """This funtion restores the Graphing Options Dock Widget for Fitting One, if it's close"""
        if (self.dockDataGausFit.isVisible() == False):
            self.dockGaussianFitOptions()
            if self.fileName is not "" and self.fileName is not None:
                self.rdOnlyFileNameG.setText(self.fileName)
                self.rdOnlyFileNameG.setStatusTip(self.fileName)

    # -----------------------------------------------------------------------------------------#
    def GraphDataGausFit(self):
        """Function that graphs the information from the file and calls on the different methods to graph
        depending on the check boxes the user has chosen. Checks for the fileName not to be empty and
        the path to lead to an actual file. This method is called in the Graphing Utilities file
        """

        if self.fileName is "" or self.fileName is None:
            QtGui.QMessageBox.warning(self, "Error - No File", "There is no data to graph."
                                                               " Make sure a file has been open.")
        else:
            if os.path.isfile(self.fileName) == False:
                QtGui.QMessageBox.warning(self, "Error - No File", "There is no data to graph."
                                                                   " Make sure a file has been open.")
            else:

                if self.checkBxAmplitude1.isChecked():
                    self.gausFit.graphAmplitude1()

                if self.checkBxPeakPosition1.isChecked():
                    self.gausFit.graphPeakPosition1()

                if self.checkBxPeakWidth1.isChecked():
                    self.gausFit.graphPeakWidth1()

                if self.checkBxAmplitudeXWidth1.isChecked():
                    self.gausFit.graphAmplitudeXWidth1()

                if self.checkBxAmplitude2.isChecked():
                    self.gausFit.graphAmplitude2()

                if self.checkBxPeakPosition2.isChecked():
                    self.gausFit.graphPeakPosition2()

                if self.checkBxPeakWidth2.isChecked():
                    self.gausFit.graphPeakWidth2()

                if self.checkBxAmplitudeXWidth2.isChecked():
                    self.gausFit.graphAmplitudeXWidth2()

        self.checkBxAmplitude1.setCheckState(QtCore.Qt.Unchecked)
        self.checkBxAmplitudeXWidth1.setCheckState(QtCore.Qt.Unchecked)
        self.checkBxPeakPosition1.setCheckState(QtCore.Qt.Unchecked)
        self.checkBxPeakWidth1.setCheckState(QtCore.Qt.Unchecked)
        self.checkBxAmplitude2.setCheckState(QtCore.Qt.Unchecked)
        self.checkBxAmplitudeXWidth2.setCheckState(QtCore.Qt.Unchecked)
        self.checkBxPeakPosition2.setCheckState(QtCore.Qt.Unchecked)
        self.checkBxPeakWidth2.setCheckState(QtCore.Qt.Unchecked)

    # ------------------------------------------------------------------------------------#
    def FileNameRdOnlyBox(self):
        """This method contains a QLineEdit and label that display the selected file
            next to the browse button"""
        self.rdOnlyFileName = QtGui.QLineEdit()
        self.rdOnlyFileName.setReadOnly(True)
        self.rdOnlyFileName.setTextMargins(0, 0, 10, 0)
        self.rdOnlyFileName.setFixedWidth(125)

        #For the Gaussioan Fit
        self.rdOnlyFileNameG = QtGui.QLineEdit()
        self.rdOnlyFileNameG.setReadOnly(True)
        self.rdOnlyFileNameG.setTextMargins(0, 0, 10, 0)
        self.rdOnlyFileNameG.setFixedWidth(200)

        # Label
        self.fileNameLabel = QtGui.QLabel()
        self.fileNameLabel.setText("File Name:")

    # ------------------------------------------------------------------------------------#
    def GaussianFittingData(self):
        if (self.gausFitStat == True):
            self.restoreDockGaussianFitOptions()
        else:
            chosePeak = self.PeakDialog()
            if (chosePeak == 'One'):
                self.gausFit.OnePeakFitting(self.fileName)
                self.dockGaussianFitOptions()
            elif (chosePeak == 'Two'):
                self.gausFit.gausInputDialog()


    def PeakDialog(self):
        """Method that asks the user to import """
        peakList = ['One', 'Two']
        text, ok = QtGui.QInputDialog.getItem(self, 'Peak Fit', 'Choose Peak: ', peakList)

        if ok:
            return text

    # ------------------------------------------------------------------------------------#
    def openFile(self):
        """This method opens the file """
        #Sets the fileName rdOnlyBox to blank, if they try to open another file
        self.rdOnlyFileName.setText(" ")
        self.rdOnlyFileName.setStatusTip(" ")
        self.rdOnlyFileNameG.setText(" ")
        self.rdOnlyFileNameG.setStatusTip(" ")

        filters = "Text files (*.txt);;Python files (*.py)"
        selectedFilter = "Any file (*.*);;Text files (*.txt);;Python files (*.py)"
        self.fileName = QtGui.QFileDialog.getOpenFileName(self, "Open File")

        self.rdOnlyFileName.setText(self.fileName)
        self.rdOnlyFileName.setStatusTip(self.fileName)
        self.gausFitStat = False
        self.LFitStat = False

    # ------------------------------------------------------------------------------------#
    def GraphFittingOneButton(self):
        """Funtion that creates a graph button, connects to the GraphDataFittingOne() method"""
        self.GraphFittingOneBtn = QtGui.QPushButton('Graph', self)
        self.GraphFittingOneBtn.setStatusTip("Graphs the check graphs")
        self.GraphFittingOneBtn.clicked.connect(self.GraphDataGausFit)


    def BrowseButton(self):
        """Function that creates a browse method, connects to the openFile() method"""
        # Button next to the FileNameRdOnly label and LineEdit
        self.BrowseBtn = QtGui.QPushButton('Browse', self)
        self.BrowseBtn.clicked.connect(self.openFile)
        self.BrowseBtn.setStatusTip("Browse and open an existing file")

    def GraphRawDataButton(self):
        """Function that creates a graph button, connects to the GraphData() method"""
        self.GraphRawDataBtn = QtGui.QPushButton('Graph', self)
        self.GraphRawDataBtn.setStatusTip("Graphs the checked boxes")
        self.GraphRawDataBtn.clicked.connect(self.GraphRawData)

    def GraphAllButton(self):
        """Function that creates a graph button, the connects to the method that graphs all the graphs"""
        self.GraphAllBtn = QtGui.QPushButton('Graph all', self)
        self.GraphAllBtn.setStatusTip("Graphs all the fitted data graphs")
        self.GraphAllBtn.clicked.connect(self.gausFit.graphAll)

    def GraphLFitButton(self):
        """Function that creates a graph button, connects to the GraphLFit()"""
        self.GraphLFitBtn = QtGui.QPushButton('Graph', self)
        self.GraphLFitBtn.setStatusTip("Graphs the selected L Fit check boxes")
        self.GraphLFitBtn.clicked.connect(self.GraphLFit)

    # --------------------------------------------------------------------------------------------#
    def DockRawDataOptions(self):
        """Function that creates the dockWidget, Graph Options for fitting one
        """
        self.dockRawData = QtGui.QDockWidget("Raw Data", self)
        self.dockRawData.setFloating(False)
        self.dockRawData.setMaximumWidth(320)
        self.dockRawData.setMinimumWidth(320)
        self.dockRawData.setAllowedAreas(QtCore.Qt.RightDockWidgetArea | QtCore.Qt.LeftDockWidgetArea)

        layout = QtGui.QFormLayout()
        FileHLayout = QtGui.QHBoxLayout()
        BtnLayout = QtGui.QHBoxLayout()
        self.dataDockedWidget = QtGui.QWidget()

        self.FileNameRdOnlyBox()
        self.BrowseButton()
        self.GraphRawDataButton()
        self.GraphRawDataCheckBox()

        FileHLayout.addWidget(self.fileNameLabel)
        FileHLayout.addWidget(self.rdOnlyFileName)
        FileHLayout.addStretch(1)
        FileHLayout.addWidget(self.BrowseBtn)

        BtnLayout.addStretch(1)
        BtnLayout.addWidget(self.GraphRawDataBtn)

        layout.addRow(FileHLayout)
        layout.addRow(self.graphCheckBx)
        layout.addRow(BtnLayout)
        self.dataDockedWidget.setLayout(layout)
        self.dockRawData.setWidget(self.dataDockedWidget)

        # Adding the docked widget to the main window
        self.myMainWindow.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dockRawData)
        # Checks to see if the Raw data is being restored when the fitted options have been displayed
        if (self.gausFitStat == True):
            self.myMainWindow.tabifyDockWidget(self.dockRawData, self.dockDataGausFit)

    def GraphRawDataCheckBox(self):
        """This function contains a group box with check boxes for fitting one"""
        self.graphCheckBx = QtGui.QGroupBox("Select Graphs")

        self.checkBxColorGraph = QtGui.QCheckBox("Color Graph")
        self.checkBxLineGraph = QtGui.QCheckBox("Line Graph")

        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.checkBxColorGraph)
        vbox.addWidget(self.checkBxLineGraph)

        self.graphCheckBx.setLayout(vbox)

    # ----------------------------------------------------------------------------------------------------------#
    def restoreRawDataOptions(self):
        """This funtion restores the Graphing Options Dock Widget for Fitting One, if it's closed """
        if self.dockRawData.isVisible() == False:
            self.DockRawDataOptions()
            if self.fileName is not "" and self.fileName is not None:
                self.rdOnlyFileName.setText(self.fileName)
                self.rdOnlyFileName.setStatusTip(self.fileName)

    # ----------------------------------------------------------------------------------------------------------#
    def GraphRawData(self):
        """Function that depending on the check boxes the user has chosen it plots the raw data."""

        self.myMainWindow.fileNm = self.fileName
        if self.fileName is "" or self.fileName is None:
            QtGui.QMessageBox.warning(self, "Error - No File", "There is no data to graph."
                                                               " Make sure a file has been open.")
        else:
            if os.path.isfile(self.fileName) == False:
                QtGui.QMessageBox.warning(self, "Error - No File", "There is no data to graph."
                                                                   " Make sure a file has been open.")
            else:
                if self.checkBxColorGraph.isChecked():
                    self.myMainWindow.PlotColorGraphRawData()

                if self.checkBxLineGraph.isChecked():
                    self.myMainWindow.PlotLineGraphRawData()

        self.checkBxColorGraph.setCheckState(QtCore.Qt.Unchecked)
        self.checkBxLineGraph.setCheckState(QtCore.Qt.Unchecked)

    # ----------------------------------------------------------------------------------------------------------#
    def LFittingData(self):
        if self.fileName is " " or self.fileName == None:
            QtGui.QMessageBox.warning(self, "Error - No File", "There is no data to fit."
                                                               " Make sure a file has been open.")
        else:
            if os.path.isfile(self.fileName) == False:
                QtGui.QMessageBox.warning(self, "Error - No File", "There is no data to fit."
                                                                   " Make sure a file has been open.")
            else:
                self.gausFit.LInputDialog()

    def DockLFitOptions(self):
        """Function that creates the dockWidget, Graph Options for fitting one
        """
        self.dockLFit = QtGui.QDockWidget("L Fit", self)
        self.dockLFit.setFloating(False)
        self.dockLFit.setMaximumWidth(320)
        self.dockLFit.setMinimumWidth(320)
        self.dockLFit.setAllowedAreas(QtCore.Qt.RightDockWidgetArea | QtCore.Qt.LeftDockWidgetArea)

        layout = QtGui.QFormLayout()
        FileHLayout = QtGui.QHBoxLayout()
        BtnLayout = QtGui.QHBoxLayout()
        self.dataDockedWidget = QtGui.QWidget()

        self.FileNameRdOnlyBox()
        self.GraphLFitButton()
        self.GraphLFitCheckBox()

        FileHLayout.addWidget(self.fileNameLabel)
        FileHLayout.addWidget(self.rdOnlyFileNameG)
        FileHLayout.addStretch(1)

        BtnLayout.addStretch(1)
        BtnLayout.addWidget(self.GraphLFitBtn)

        layout.addRow(FileHLayout)
        layout.addRow(self.graphLCheckBx)
        layout.addRow(BtnLayout)
        self.dataDockedWidget.setLayout(layout)
        self.dockLFit.setWidget(self.dataDockedWidget)

        # Adding the docked widget to the main window
        self.myMainWindow.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dockLFit)

        if (self.dockDataGausFit.isVisible() == True):
            self.myMainWindow.tabifyDockWidget(self.dockDataGausFit, self.dockLFit)
        elif (self.dockRawData.isVisible() == True):
            self.myMainWindow.tabifyDockWidget(self.dockRawData, self.dockLFit)

    def GraphLFitCheckBox(self):
        """This function contains a group box with check boxes for fitting one"""
        self.graphLCheckBx = QtGui.QGroupBox("Select Graphs")

        self.checkBxLPos1Graph = QtGui.QCheckBox("Position #1")
        self.checkBxLPos2Graph = QtGui.QCheckBox("Position #2")

        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.checkBxLPos1Graph)
        vbox.addWidget(self.checkBxLPos2Graph)

        self.graphLCheckBx.setLayout(vbox)

    # ----------------------------------------------------------------------------------------------------------#
    def restoreLFitOptions(self):
        """This funtion restores the Graphing Options Dock Widget for Fitting One, if it's closed """
        if self.dockLFit.isVisible() == False:
            self.DockLFitOptions()
            if self.fileName is not "" and self.fileName is not None:
                self.rdOnlyFileNameG.setText(self.fileName)
                self.rdOnlyFileNameG.setStatusTip(self.fileName)

    # ----------------------------------------------------------------------------------------------------------#
    def GraphLFit(self):
        """Function that depending on the check boxes the user has chosen it plots the raw data."""
        if self.checkBxLPos1Graph.isChecked():
            self.gausFit.graphLFitPos1()

        if self.checkBxLPos2Graph.isChecked():
            self.gausFit.graphLFitPos2()

        self.checkBxLPos1Graph.setCheckState(QtCore.Qt.Unchecked)
        self.checkBxLPos2Graph.setCheckState(QtCore.Qt.Unchecked)

    # ------------------------------------------------------------------------------------#
    def LFittingData(self):
        if (self.LFitStat == True):
            self.restoreLFitOptions()
        else:
           self.gausFit.LInputDialog()

