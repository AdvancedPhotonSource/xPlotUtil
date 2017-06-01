#!/usr/bin/env python

"""
Copyright (c) UChicago Argonne, LLC. All rights reserved.
See LICENSE file.

"""

# --------------------------------------------------------------------------------------#
from __future__ import unicode_literals
from pylab import *
from matplotlib.backends import qt_compat
from GaussianFit import GaussianFitting
import os
from pathlib2 import Path
from GaussianFit import GaussianFitting
use_pyside = qt_compat.QT_API == qt_compat.QT_API_PYSIDE
if use_pyside:
    from PySide.QtGui import *
    from PySide.QtCore import *
else:
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import *

from spec2nexus.spec import SpecDataFile
# --------------------------------------------------------------------------------------#

class ReadSpec:

    def __init__ (self, parent=None):
        self.dockedOpt = parent
        self.myMainWindow = self.dockedOpt.myMainWindow
        self.gausFit = GaussianFitting(self)
        self.specFileOpened = False
        self.specFileName = None

        # L information
        self.L = []
        self.lElement = 0
        self.lMax = 0
        self.lMin = 0

    def loadScans(self, scans):
        self.scans = scans
        scanKeys = self.scans.keys()

        scanKeys.sort(key=int)  # Sorts the scans in alphabetical order
        for scan in scanKeys:
            PValue = 'PVvalue #' + str(scans[scan].scanNum)
            self.dockedOpt.specDataList.addItem(PValue)

    def currentScan(self):
        scan = str(self.dockedOpt.specDataList.currentRow() + 1)
        self.currentRow = self.dockedOpt.specDataList.currentRow()
        self.dockedOpt.openFile()

        # Making sure the file of the PVvalue has been opened
        try:
            if os.path.isfile(self.dockedOpt.fileName):
                # Getting the L information for the particular PVValue
                L = self.scans[scan].data["L"]
                self.lMin = L[0]
                self.lMax = L[-1]
                k = self.scans[scan].G["G1"].split(" ")
                self.lElement = float(k[2])
                self.getRLU()
        except TypeError or RuntimeError or KeyError:
            print("Please make sure the PVValue file has L the information on the file.")

    # ------------------------------------------------------------------------------------#
    def openSpecFile(self):
        if self.specFileOpened == False:
            self.openSpecDialog()
        elif self.specFileOpened == True:
            response = self.dockedOpt.msgApp("Open New Spec File", "Would you like to open a new spec file?")
            if response == "Y":
                self.openSpecDialog()

    def openSpecDialog(self):
        """This method allows the user to open the spec file """
        try:
            filters = "Spec files (*.spec);;Python files (*.py)"
            selectedFilter = "Spec files (*.spec);;Python files (*.py)"
            self.specFileName, self.specFileFilter = QFileDialog.getOpenFileName(self.myMainWindow, "Open Spec File", filters, selectedFilter)
            self.dockedOpt.mainOptions.close()
            self.dockedOpt.DockMainOptions()
            self.myMainWindow.LFit.setEnabled(False)

            # Makes sure a file has been opened
            if os.path.isfile(self.specFileName):
                self.gausFitStat = False
                self.LFitStat = False
                self.dockedOpt.rdOnlyFileName.setText(self.specFileName)
                self.dockedOpt.rdOnlyFileName.setStatusTip(self.specFileName)
                self.specFile = SpecDataFile(self.specFileName)
                self.loadScans(self.specFile.scans)
                self.specFileOpened = True
                self.dockedOpt.fileOpened = False
                self.continueGraphingEachFit = True
        except:
            print("Please make sure the PVValue file has L the information on the file.")


    def getRLU(self):
        nRow, nCol = self.dockedOpt.fileInfo()  # nRows = points || nCol = bins
        if nRow != 0:
            adjustment = (self.lMax - self.lMin)/nRow
            self.L = []
            self.L.append(self.lMin)
            RLU = self.lMin
            count = 1
            while count < nRow:
                RLU += adjustment
                self.L.append(round(RLU, 3))
                count += 1



