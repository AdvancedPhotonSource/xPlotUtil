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

use_pyside = qt_compat.QT_API == qt_compat.QT_API_PYSIDE
if use_pyside:
    from PySide import QtGui, QtCore
else:
    from PyQt4 import QtGui, QtCore


class GraphingUtil (QtGui.QDockWidget):

    def __init__ (self, parent=None):
        super(GraphingUtil, self).__init__(parent)
        self.fileName = None
        self.myMainWindow = parent

 # -----------------------------------------------------------------------------#
    def dockFittingOneOptions(self):
        """Function that creates the dockWidget, Graph Options for fitting one
        """

        self.dockDataGraphing = QtGui.QDockWidget("xPlotting Fitting One", self)
        self.dockDataGraphing.setFloating(False)
        self.dockDataGraphing.setMaximumWidth(320)
        self.dockDataGraphing.setMinimumWidth(320)
        self.dockDataGraphing.setAllowedAreas(QtCore.Qt.RightDockWidgetArea | QtCore.Qt.LeftDockWidgetArea)

        layout = QtGui.QFormLayout()
        FileHLayout = QtGui.QHBoxLayout()
        BtnLayout = QtGui.QHBoxLayout()
        self.dataDocked = QtGui.QWidget()

        self.FileNameRdOnlyBox()
        self.BrowseButton()
        self.GraphFittingOneCheckBox()
        self.GraphFittingOneButton()

        FileHLayout.addWidget(self.fileNameLabel)
        FileHLayout.addWidget(self.rdOnlyFileName)
        FileHLayout.addStretch(1)
        FileHLayout.addWidget(self.BrowseBtn)

        BtnLayout.addStretch(1)
        BtnLayout.addWidget(self.GraphFittingOneBtn)

        layout.addRow(FileHLayout)
        layout.addRow(self.graphCheckBx)
        layout.addRow(BtnLayout)
        self.dataDocked.setLayout(layout)
        self.dockDataGraphing.setWidget(self.dataDocked)

        # Adding the docked widget to the main window
        self.myMainWindow.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dockDataGraphing)


    def GraphFittingOneCheckBox(self):
        """This function contains a group box with check boxes for fitting one"""
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

        self.checkBxAmplitude.stateChanged.connect(self.CheckFittingOneCheckBoxes)
        self.checkBxAmplitudeXWidth.stateChanged.connect(self.CheckFittingOneCheckBoxes)
        self.checkBxPeakWidth.stateChanged.connect(self.CheckFittingOneCheckBoxes)
        self.checkBxPeakPosition.stateChanged.connect(self.CheckFittingOneCheckBoxes)
        self.checkBxGraphAll.stateChanged.connect(self.CheckFittingOneCheckBoxes)

        self.graphCheckBx.setLayout(vbox)

    # ----------------------------------------------------------------------------------------------------------#
    def restoreDockFittingOneOptions(self):
        """This funtion restores the Graphing Options Dock Widget for Fitting One, if it's closed
            uses the GraphingUtilities.py"""
        if self.dockDataGraphing.isVisible() == False:
            self.dockFittingOneOptions()
            if self.fileName is not "" and self.fileName is not None:
                self.rdOnlyFileName.setText(self.fileName)
                self.rdOnlyFileName.setStatusTip(self.fileName)

    # -----------------------------------------------------------------------------------------#
    def GraphDataFittingOne(self):
        """Function that graphs the information from the file and calls on the different methods to graph
        depending on the check boxes the user has chosen. Checks for the fileName not to be empty and
        the path to lead to an actual file. This method is called in the Graphing Utilities file
        """

        self.myMainWindow.fileNm = self.fileName
        if self.fileName is "" or self.fileName is None:
            QtGui.QMessageBox.warning(self, "Error - No File", "There is no data to graph."
                                                               " Make sure a file has been open.")
        else:
            if os.path.isfile(self.fileName) == False:
                QtGui.QMessageBox.warning(self, "Error - No File", "There is no data to graph."
                                                                   " Make sure a file has been open.")
            else:

                if self.checkBxAmplitude.isChecked() and self.checkBxGraphAll.isChecked() == False:
                    self.myMainWindow.graphAmplitude()

                if self.checkBxPeakPosition.isChecked() and self.checkBxGraphAll.isChecked() == False:
                    self.myMainWindow.graphPeakPosition()

                if self.checkBxPeakWidth.isChecked() and self.checkBxGraphAll.isChecked() == False:
                    self.myMainWindow.graphPeakWidth()

                if self.checkBxAmplitudeXWidth.isChecked() and self.checkBxGraphAll.isChecked() == False:
                    self.myMainWindow.graphAmplitudeXWidth()

                if self.checkBxGraphAll.isChecked():
                    self.myMainWindow.graphAll()

        self.checkBxGraphAll.setCheckState(QtCore.Qt.Unchecked)
        self.checkBxAmplitude.setCheckState(QtCore.Qt.Unchecked)
        self.checkBxAmplitudeXWidth.setCheckState(QtCore.Qt.Unchecked)
        self.checkBxPeakPosition.setCheckState(QtCore.Qt.Unchecked)
        self.checkBxPeakWidth.setCheckState(QtCore.Qt.Unchecked)

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
    def openFile(self):
        """This method opens the file """
        openDlg = QtGui.QFileDialog()
        self.fileName = openDlg.getOpenFileName()

        self.rdOnlyFileName.setText(self.fileName)
        self.rdOnlyFileName.setStatusTip(self.fileName)
    # ------------------------------------------------------------------------------------#

    def GraphFittingOneButton(self):
        """Funtion that creates a graph button, connects to the GraphData() method"""
        self.GraphFittingOneBtn = QtGui.QPushButton('Graph', self)
        self.GraphFittingOneBtn.setStatusTip("Graphs the check graphs")
        self.GraphFittingOneBtn.clicked.connect(self.GraphDataFittingOne)


    def BrowseButton(self):
        """Funtion that creates a browse method, connects to the openFile() method"""
        # Button next to the FileNameRdOnly label and LineEdit
        self.BrowseBtn = QtGui.QPushButton('Browse', self)
        self.BrowseBtn.clicked.connect(self.openFile)
        self.BrowseBtn.setStatusTip("Browse and open an existing file")

    # ------------------------------------------------------------------------------------#
    def CheckFittingOneCheckBoxes(self):
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
