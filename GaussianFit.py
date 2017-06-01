#!/usr/bin/env python

"""
Copyright (c) UChicago Argonne, LLC. All rights reserved.
See LICENSE file.
"""

# --------------------------------------------------------------------------------------#
from __future__ import unicode_literals
import sys
import numpy as np
import os
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

from scipy.optimize import curve_fit
from scipy import exp
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
from matplotlib.ticker import FormatStrFormatter

class GaussianFitting:

    def __init__ (self, parent=None):
        self.TwoPkGausFitData = []
        self.OnePkFitData = []
        self.readSpec = parent
        self.dockedOpt = self.readSpec.dockedOpt
        self.myMainWindow = self.dockedOpt.myMainWindow
        self.continueGraphingEachFit = True #Boolean to stop on Each fit graphing

    # --------------------------------------------------------------------------------------#
    def TwoPeakFitting(self):
        """Gaussian Fitting for Two Peaks [Updated April 4, 2017]"""
        #try:
        nRow, nCol = self.dockedOpt.fileInfo()

        self.TwoPkGausFitData = zeros((nCol, 12))  # Creats the empty 2D List
        for j in range(nCol):
            col_data = self.dockedOpt.TT[:, j]
            xx = arange(0, len(col_data))
            param = self.twoPkFitting(xx, col_data)
            fit_result = ["%f" % member for member in param[0]]
            fit_error = ["%f" % member for member in param[1]]
            self.TwoPkGausFitData[j, :] = (fit_result[0], fit_error[0], fit_result[1], fit_error[1], fit_result[2],
                                           fit_error[2], fit_result[3], fit_error[3], fit_result[4], fit_error[4],
                                           fit_result[5], fit_error[5])
        #except:
           # QMessageBox.warning(self.myMainWindow, "Warning", "Please make sure to input realistic guesses.\n"
            #                                                        "Reset or reopen the PVvaulue file.")

    def twoPkFitting(self, xx, yy):
        #try:
        mean = sum(xx * yy) / sum(yy)
        sig = np.sqrt(sum(yy * (xx - mean) ** 2)) / sqrt(sum(yy))
        bg0 = (yy[max(xx)] + yy[0]) / 2
        popt, pcov = curve_fit(self.gaus2, xx, yy, p0=[self.twoPeak1Amp, self.twoPeak2Amp, self.twoPeak1Pos, self.twoPeak2Pos,
                                                       self.twoPeak1Wid, self.twoPeak2Wid, bg0])
        perr = np.sqrt(np.diag(pcov))
        self.graphEachFitRawData(xx, yy, popt, 2)
        return popt, perr
       # except TypeError and RuntimeError:
          #   QMessageBox.warning(self.myMainWindow, "Warning", "Please make sure to input realistic guesses.\n"
                                                                    # "Reset or reopen the PVvaulue file.")

    def gaus2(self, x, a1, a2, x01, x02, sigma1, sigma2, background):
        return a1 * exp(-(x - x01) ** 2 / (2 * sigma1 ** 2))\
               + a2 *exp(-(x - x02) ** 2 / (2 * sigma2 ** 2)) + background

    # -------------------------------------------------------------------------------------------------------------#
    def graphEachFitRawData(self, xx, yy, popt, whichPeak):
        """This method graphs the raw data and the fitted data for each column.
        :param xx: bins
        :param yy: raw data column
        :param popt: from the gaussian fit
        """
        if (self.continueGraphingEachFit == True):
            self.mainGraph = QDialog(self.myMainWindow)
            self.mainGraph.resize(600, 600)
            dpi = 100
            fig = Figure((3.0, 3.0), dpi=dpi)
            canvas = FigureCanvas(fig)
            canvas.setParent(self.mainGraph)
            axes = fig.add_subplot(111)

            axes.plot(xx, yy, 'b+:', label='data')
            if(whichPeak == 1):
                axes.plot(xx, self.gaus1(xx, *popt), 'ro:', label='fit')
            elif(whichPeak == 2):
                axes.plot(xx, self.gaus2(xx, *popt), 'ro:', label='fit')
            axes.legend()
            axes.set_title('Gaussian Fit')
            axes.set_xlabel('Bins')
            axes.set_ylabel('Intensity')
            canvas.draw()

            vbox = QVBoxLayout()
            hbox = QHBoxLayout()
            self.skipEachFitGraphButton()
            self.nextFitGraphButton()
            hbox.addWidget(self.skipEachFitGraphBtn)
            hbox.addStretch(1)
            hbox.addWidget(self.nextFitGraphBtn)
            graphNavigationBar = NavigationToolbar(canvas, self.mainGraph)
            vbox.addLayout(hbox)
            vbox.addWidget(graphNavigationBar)
            vbox.addWidget(canvas)
            self.mainGraph.setLayout(vbox)
            self.mainGraph.exec_()

    # ------------------------------------------------------------------------------------#
    def skipEachFitGraphButton(self):
        """Button that allows the user to skip each fit graph, calls on the skipEachFit() method"""
        self.skipEachFitGraphBtn = QPushButton('Skip')
        self.skipEachFitGraphBtn.setStatusTip("Skip the graphing of each fit")
        self.skipEachFitGraphBtn.clicked.connect(self.skipEachFit)

    def nextFitGraphButton(self):
        """Button that shows the next fit graph, calls on nextFitGraph() method"""
        # Button next to the FileNameRdOnly label and LineEdit
        self.nextFitGraphBtn = QPushButton('Next')
        self.nextFitGraphBtn.clicked.connect(self.nextFitGraph)
        self.nextFitGraphBtn.setStatusTip("Graphs the next fit and the original data")

    def nextFitGraph(self):
        """Closes the current fit graph to show the next"""
        self.mainGraph.close()

    def skipEachFit(self):
        """Closes the current fit graph and sets continueGraphingEachFit to false
         so that other graphs are not showed"""
        self.continueGraphingEachFit = False
        self.mainGraph.close()

    # -----------------------------------------------------------------------------------------------------------#
    def OnePeakFitting(self):
        """Gaussian Fit for one Peak [Updated April 11, 2017]"""

        nRow, nCol = self.dockedOpt.fileInfo()

        self.OnePkFitData = zeros((nCol, 6))  # Creates the empty 2D List
        for j in range(nCol):
            col_data = self.dockedOpt.TT[:, j]
            xx = arange(0, len(col_data))
            param = self.OnePkFitting(xx, col_data)
            fit_result = param[0]
            fit_error = param[1]
            self.OnePkFitData[j, :] = (fit_result[0], fit_error[0], fit_result[1], fit_error[1], fit_result[2],
                                    fit_error[2])


    def OnePkFitting(self, xx, yy):
        try:
            mean = sum(xx * yy) / sum(yy)  # note this correction
            sig = np.sqrt(sum(yy * (xx - mean) ** 2)) / sqrt(sum(yy))
            bg0 = (yy[max(xx)] + yy[0]) / 2  # min value of yy
            popt, pcov = curve_fit(self.gaus1, xx, yy, p0=[self.onePeakAmp, self.onePeakPos, self.onePeakWid, bg0])
            perr = np.sqrt(np.diag(pcov))
            self.graphEachFitRawData(xx, yy, popt, 1)
            return popt, perr

        except TypeError and RuntimeError:
            print("Please make sure the fitted data is correct")

    def gaus1(self, x, a, x0, sigma, b):
        return a * exp(-(x - x0) ** 2 / (2 * sigma ** 2)) + b

    # -----------------------------------------------------------------------------------------------------------#
    def GraphUtilGaussianFitGraphs(self, canvas, fig, name, x, y, error, xLabel, yLabel, whichGraph):
        mainGraph = QWidget()

        canvas.setParent(mainGraph)
        axes = fig.add_subplot(111)

        axes.plot(x, y)

        if whichGraph == 'G':
            axes.errorbar(x, y, yerr=error, fmt='o')
        elif whichGraph == 'L':
            axes.plot(x, y, 'go')
            axes.yaxis.set_major_formatter(FormatStrFormatter('%.4f'))

        axes.set_title(name)
        axes.set_xlabel(xLabel)
        axes.set_ylabel(yLabel)
        canvas.draw()

        tab = QWidget()
        tab.setStatusTip(name)
        vbox = QVBoxLayout()
        graphNavigationBar = NavigationToolbar(canvas, mainGraph)
        vbox.addWidget(graphNavigationBar)
        vbox.addWidget(canvas)
        tab.setLayout(vbox)

        self.myMainWindow.savingCanvasTabs(tab, name, canvas, fig)

    # -----------------------------------------------------------------------------------------------------------#
    def graphOnePeakAmplitude(self):
        """This method graphs the Amplitude for peak one"""
        fig = Figure((5.0, 4.0), dpi=100)
        canvas = FigureCanvas(fig)

        x = self.getVoltage()
        y = self.OnePkFitData[:, 0]
        error = self.OnePkFitData[:, 1]
        xLabel = 'Voltage'
        yLabel = 'Intensity'
        name = 'Amplitude (Scan#: ' + str(self.dockedOpt.specDataList.currentRow() + 1) + ')'

        self.GraphUtilGaussianFitGraphs(canvas, fig, name, x, y, error, xLabel, yLabel, 'G')

    # -----------------------------------------------------------------------------------------#
    def graphOnePeakPosition(self):
        """This method graphs the peak position for peak one"""
        fig = Figure((5.0, 4.0), dpi=100)
        canvas = FigureCanvas(fig)

        x = self.getVoltage()
        y = self.OnePkFitData[:, 2]
        error = self.OnePkFitData[:, 3]
        xLabel = 'Voltage'
        yLabel = 'Position'
        name = 'Position (Scan#: ' + str(self.dockedOpt.specDataList.currentRow() + 1) + ')'

        self.GraphUtilGaussianFitGraphs(canvas, fig, name, x, y, error, xLabel, yLabel, 'G')

    # ----------------------------------------------------------------------------------------------------#
    def graphOnePeakWidth(self):
        """This method graphs the Peak width for peak one"""
        fig = Figure((5.0, 4.0), dpi=100)
        canvas = FigureCanvas(fig)

        x = self.getVoltage()
        y = self.OnePkFitData[:, 4]
        error = self.OnePkFitData[:, 5]
        xLabel = 'Voltage'
        yLabel = 'Width'
        name = 'Width (Scan#: ' + str(self.dockedOpt.specDataList.currentRow() + 1) + ')'

        self.GraphUtilGaussianFitGraphs(canvas, fig, name, x, y, error, xLabel, yLabel, 'G')

    # ----------------------------------------------------------------------------------------------------#
    def graphOnePeakAmplitudeXWidth(self):
        """This method graphs the amplitude x width for the first peak"""
        fig = Figure((5.0, 4.0), dpi=100)
        canvas = FigureCanvas(fig)

        x = self.getVoltage()
        yA = self.OnePkFitData[:, 0]
        yW = self.OnePkFitData[:, 4]
        a_err = self.OnePkFitData[:, 1]
        w_err = self.OnePkFitData[:, 5]
        y = yA * yW
        error = ((y * a_err) + (y * w_err)) / y

        xLabel = 'Voltage'
        yLabel = 'A x W'
        name = 'Amplitude X Width (Scan#: ' + str(self.dockedOpt.specDataList.currentRow() + 1) + ')'

        self.GraphUtilGaussianFitGraphs(canvas, fig, name, x, y, error, xLabel, yLabel, 'G')

    # -----------------------------------------------------------------------------------------------------------#
    def graphTwoPeakAmplitude1(self):
        """This method graphs the Amplitude for peak one"""
        fig = Figure((5.0, 4.0), dpi=100)
        canvas = FigureCanvas(fig)

        x = self.getVoltage()
        y = self.TwoPkGausFitData[:, 0]
        error = self.TwoPkGausFitData[:, 1]
        xLabel = 'Voltage'
        yLabel = 'Intensity'
        name = 'Peak #1 Amplitude (Scan#: ' + str(self.dockedOpt.specDataList.currentRow() + 1) + ')'

        self.GraphUtilGaussianFitGraphs(canvas, fig, name, x, y, error, xLabel, yLabel, 'G')

    # -----------------------------------------------------------------------------------------#
    def graphTwoPeakPosition1(self):
        """This method graphs the peak position for peak one"""
        fig = Figure((5.0, 4.0), dpi=100)
        canvas = FigureCanvas(fig)

        x = self.getVoltage()
        y = self.TwoPkGausFitData[:, 4]
        error = self.TwoPkGausFitData[:, 5]
        xLabel = 'Voltage'
        yLabel = 'Position'
        name = 'Peak #1 Position (Scan#: ' + str(self.dockedOpt.specDataList.currentRow() + 1) + ')'

        self.GraphUtilGaussianFitGraphs(canvas, fig, name, x, y, error, xLabel, yLabel, 'G')

    # ----------------------------------------------------------------------------------------------------#
    def graphTwoPeakWidth1(self):
        """This method graphs the Peak width for peak one"""
        fig = Figure((5.0, 4.0), dpi=100)
        canvas = FigureCanvas(fig)

        x = self.getVoltage()
        y = self.TwoPkGausFitData[:, 8]
        error = self.TwoPkGausFitData[:, 9]
        xLabel = 'Voltage'
        yLabel = 'Width'
        name = 'Peak #1 Width (Scan#: ' + str(self.dockedOpt.specDataList.currentRow() + 1) + ')'

        self.GraphUtilGaussianFitGraphs(canvas, fig, name, x, y, error, xLabel, yLabel, 'G')

    # ----------------------------------------------------------------------------------------------------#
    def graphTwoPeakAmplitudeXWidth1(self):
        """This method graphs the amplitude x width for the first peak"""
        fig = Figure((5.0, 4.0), dpi=100)
        canvas = FigureCanvas(fig)

        x = self.getVoltage()
        yA = self.TwoPkGausFitData[:, 0]
        yW = self.TwoPkGausFitData[:, 8]
        a_err = self.TwoPkGausFitData[:, 1]
        w_err = self.TwoPkGausFitData[:, 9]
        y = yA * yW
        error = ((y * a_err) + (y * w_err))/y

        xLabel = 'Voltage'
        yLabel = 'A x W'
        name = 'Peak #1 Amplitude X Width (Scan#: ' + str(self.dockedOpt.specDataList.currentRow() + 1) + ')'

        self.GraphUtilGaussianFitGraphs(canvas, fig, name, x, y, error, xLabel, yLabel, 'G')

    # -----------------------------------------------------------------------------------------------------------#
    def graphTwoPeakAmplitude2(self):
        """This method graphs the Amplitude for peak two"""
        fig = Figure((5.0, 4.0), dpi=100)
        canvas = FigureCanvas(fig)

        x = self.getVoltage()
        y = self.TwoPkGausFitData[:, 2]
        error = self.TwoPkGausFitData[:, 3]
        xLabel = 'Voltage'
        yLabel = 'Intensity'
        name = 'Peak #2 Amplitude (Scan#: ' + str(self.dockedOpt.specDataList.currentRow() + 1) + ')'

        self.GraphUtilGaussianFitGraphs(canvas, fig, name, x, y, error, xLabel, yLabel, 'G')

    # -----------------------------------------------------------------------------------------#
    def graphTwoPeakPosition2(self):
        """This method graphs the peak position for peak two"""
        fig = Figure((5.0, 4.0), dpi=100)
        canvas = FigureCanvas(fig)

        x = self.getVoltage()
        y = self.TwoPkGausFitData[:, 6]
        error = self.TwoPkGausFitData[:, 7]
        xLabel = 'Voltage'
        yLabel = 'Position'
        name = 'Peak #2 Position (Scan#: ' + str(self.dockedOpt.specDataList.currentRow() + 1) + ')'

        self.GraphUtilGaussianFitGraphs(canvas, fig, name, x, y, error, xLabel, yLabel, 'G')

    # ----------------------------------------------------------------------------------------------------#
    def graphTwoPeakWidth2(self):
        """This method graphs the Peak width for peak two"""
        fig = Figure((5.0, 4.0), dpi=100)
        canvas = FigureCanvas(fig)

        x = self.getVoltage()
        y = self.TwoPkGausFitData[:, 10]
        error = self.TwoPkGausFitData[:, 11]
        xLabel = 'Voltage'
        yLabel = 'Width'
        name = 'Peak #2 Width (Scan#: ' + str(self.dockedOpt.specDataList.currentRow() + 1) + ')'

        self.GraphUtilGaussianFitGraphs(canvas, fig, name, x, y, error, xLabel, yLabel, 'G')

    # ----------------------------------------------------------------------------------------------------#
    def graphTwoPeakAmplitudeXWidth2(self):
        """This method graphs the amplitude x width for the second peak"""
        fig = Figure((5.0, 4.0), dpi=100)
        canvas = FigureCanvas(fig)

        x = self.getVoltage()
        yA = self.TwoPkGausFitData[:, 2]
        yW = self.TwoPkGausFitData[:, 10]
        a_err = self.TwoPkGausFitData[:, 3]
        w_err = self.TwoPkGausFitData[:, 11]
        y = yA * yW
        error = ((y * a_err) + (y * w_err)) / y

        xLabel = 'Voltage'
        yLabel = 'A x W'
        name = 'Peak #2 Amplitude X Width (Scan#: ' + str(self.dockedOpt.specDataList.currentRow() + 1) + ')'

        self.GraphUtilGaussianFitGraphs(canvas, fig, name, x, y, error, xLabel, yLabel, 'G')

    # ------------------------------------------------------------------------------------------------------------#
    def getVoltage(self):
        """This method gets the voltage of the bins
        :return: returns the x axis in array x
        """
        x = [] # X array initialized

        # Gets the amplitude
        inF = open(self.dockedOpt.fileName, 'r')
        lines = inF.readlines()
        header = ''
        for (iL, line) in enumerate(lines):
            if line.startswith('#'):
                header = line
        inF.close()
        words = header.split()
        amplWord = words[6]
        ampl = amplWord.split('.')
        amp = float(ampl[0])

        # get the bins
        nRow, bins = self.dockedOpt.fileInfo()

        # Uses the data to find the x axis
        amplStart = amp/2
        points = bins/2
        xDif = amp/points
        xStart = xDif/2
        startX = (-1*amplStart) + xStart
        x.append(startX)
        for j in range(points-1):
            startX = startX + xDif
            x.append(startX)

        x.append(startX)
        for j in range(points-1):
            startX = startX - xDif
            x.append(startX)
        return x


    # -------------------------------------------------------------------------------------------------------------#
    def gausTwoPeakInputDialog(self):
        """Dialog where the user import """
        self.dialogGausFit = QDialog()
        inputForm = QFormLayout()
        buttonLayout = QHBoxLayout()
        spaceLayout = QVBoxLayout()

        spaceLayout.addStretch(1)

        self.twoPeak1AmpSpin = QDoubleSpinBox()
        self.twoPeak1AmpSpin.setMaximum(100000)
        self.twoPeak1PosSpin = QDoubleSpinBox()
        self.twoPeak1WidthSpin = QDoubleSpinBox()

        self.twoPeak2AmpSpin = QDoubleSpinBox()
        self.twoPeak2AmpSpin.setMaximum(100000)
        self.twoPeak2PosSpin = QDoubleSpinBox()
        self.twoPeak2WidthSpin = QDoubleSpinBox()

        ok = QPushButton("Ok")
        cancel = QPushButton("Cancel")

        cancel.clicked.connect(self.dialogGausFit.close)
        ok.clicked.connect(self.returnTwoPeakGausUserInput)
        buttonLayout.addWidget(cancel)
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(ok)

        inputForm.addRow("Peak#1 Amplitude: ", self.twoPeak1AmpSpin)
        inputForm.addRow("Peak#1 Position: ", self.twoPeak1PosSpin)
        inputForm.addRow("Peak#1 Width: ", self.twoPeak1WidthSpin)
        inputForm.addRow("Peak#2 Amplitude: ", self.twoPeak2AmpSpin)
        inputForm.addRow("Peak#2 Position: ", self.twoPeak2PosSpin)
        inputForm.addRow("Peak#2 Width: ", self.twoPeak2WidthSpin)
        inputForm.addRow(spaceLayout)
        inputForm.addRow(buttonLayout)

        self.dialogGausFit.setWindowTitle("Input Guess Data for Fit")
        self.dialogGausFit.setLayout(inputForm)
        self.dialogGausFit.resize(250, 200)
        self.dialogGausFit.show()

    def returnTwoPeakGausUserInput(self):
        """Sets the values of the variables in the method twoPkFitting, that are used as parameters.
        It also sets the Gaussian fit options available"""
        self.twoPeak1Amp = float(self.twoPeak1AmpSpin.value())
        self.twoPeak1Pos = float(self.twoPeak1PosSpin.value())
        self.twoPeak1Wid = float(self.twoPeak1WidthSpin.value())

        self.twoPeak2Amp = float(self.twoPeak2AmpSpin.value())
        self.twoPeak2Pos = float(self.twoPeak2PosSpin.value())
        self.twoPeak2Wid = float(self.twoPeak2WidthSpin.value())

        self.dialogGausFit.close()
        self.TwoPeakFitting()
        self.myMainWindow.LFit.setEnabled(True)

        # Marks that the data has been fitted for one peakm
        self.dockedOpt.twoPeakStat = True
        self.dockedOpt.gausFitStat = True
        self.dockedOpt.GraphingGaussianOptionsTree()

    # -------------------------------------------------------------------------------------------------------------#
    def gausOnePeakInputDialog(self):
        """Dialog where the user inputs guesses about the peak"""
        self.dialogOnePeakGausFit = QDialog()
        inputForm = QFormLayout()
        buttonLayout = QHBoxLayout()
        spaceLayout = QVBoxLayout()

        spaceLayout.addStretch(1)

        self.onePeakAmpSpin = QDoubleSpinBox()
        self.onePeakAmpSpin.setMaximum(100000)
        self.onePeakPosSpin = QDoubleSpinBox()
        self.onePeakWidthSpin = QDoubleSpinBox()

        ok = QPushButton("Ok")
        cancel = QPushButton("Cancel")

        cancel.clicked.connect(self.dialogOnePeakGausFit.close)
        ok.clicked.connect(self.returnOnePeakGausUserInput)
        buttonLayout.addWidget(cancel)
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(ok)

        inputForm.addRow("Peak Amplitude: ", self.onePeakAmpSpin)
        inputForm.addRow("Peak Position: ", self.onePeakPosSpin)
        inputForm.addRow("Peak Width: ", self.onePeakWidthSpin)
        inputForm.addRow(spaceLayout)
        inputForm.addRow(buttonLayout)

        self.dialogOnePeakGausFit.setWindowTitle("Input Guesses")
        self.dialogOnePeakGausFit.setLayout(inputForm)
        self.dialogOnePeakGausFit.resize(200, 110)
        self.dialogOnePeakGausFit.show()

    # -------------------------------------------------------------------------------------------------------------#
    def returnOnePeakGausUserInput(self):
        self.onePeakAmp = float(self.onePeakAmpSpin.value())
        self.onePeakPos = float(self.onePeakPosSpin.value())
        self.onePeakWid = float(self.onePeakWidthSpin.value())

        self.dialogOnePeakGausFit.close()
        self.OnePeakFitting()
        self.myMainWindow.LFit.setEnabled(True)

        # Marks that the data has been fitted for one peak
        self.dockedOpt.onePeakStat = True
        self.dockedOpt.gausFitStat = True
        self.dockedOpt.GraphingGaussianOptionsTree()
    # -------------------------------------------------------------------------------------------------------------#
    def PositionLFit(self, pos, rows):
        l = (1/(((pos/rows)*(self.readSpec.lMax-self.readSpec.lMin)+self.readSpec.lMin)/2))*self.readSpec.lElement
        return l

    # -------------------------------------------------------------------------------------------------------------#
    def doLFit(self):
        """This function
        """
        nRow, nCol = self.dockedOpt.fileInfo()

        if  self.dockedOpt.onePeakStat == True :
            self.LPosData = []
            for i in range(nCol):
                self.LPosData.append(self.PositionLFit(self.OnePkFitData[i, 2], nRow))

        elif self.dockedOpt.twoPeakStat == True:
            self.LPos1Data = []
            self.LPos2Data = []
            # Position 1
            for i in range(nCol):
              self.LPos1Data.append(self.PositionLFit(self.TwoPkGausFitData[i, 4], nCol))
            # Position 2
            for i in range(nCol):
              self.LPos2Data.append(self.PositionLFit(self.TwoPkGausFitData[i, 6], nCol))

    # ----------------------------------------------------------------------------------------------------#
    def graphOnePeakLFitPos(self):
        """This method graphs the L fit position for one peak"""
        fig = Figure((5.0, 4.0), dpi=100)
        canvas = FigureCanvas(fig)

        x = self.getVoltage()
        y = self.LPosData
        xLabel = 'Voltage'
        yLabel = 'L Constant'
        name = 'L Fit - Position (Scan#: ' + str(self.dockedOpt.specDataList.currentRow() + 1) + ')'

        self.GraphUtilGaussianFitGraphs(canvas, fig, name, x, y, None, xLabel, yLabel, 'L')

    # ----------------------------------------------------------------------------------------------------#
    def graphTwoPeakLFitPos1(self):
        """This method graphs the amplitude x width for the first peak"""
        fig = Figure((5.0, 4.0), dpi=100)
        canvas = FigureCanvas(fig)
        x = self.getVoltage()
        y = self.LPos1Data
        print x
        print y
        xLabel = 'Voltage'
        yLabel = 'L Constant'
        name = 'L Fit - Position #1 (Scan#: ' + str(self.dockedOpt.specDataList.currentRow() + 1) + ')'

        self.GraphUtilGaussianFitGraphs(canvas, fig, name, x, y, None, xLabel, yLabel, 'L')

    # ----------------------------------------------------------------------------------------------------#
    def graphTwoPeakLFitPos2(self):
        """This method graphs the amplitude x width for the first peak"""
        fig = Figure((5.0, 4.0), dpi=100)
        canvas = FigureCanvas(fig)

        x = self.getVoltage()
        y = self.LPos2Data
        xLabel = 'Voltage'
        yLabel = 'L Constant'
        name = 'L Fit - Position #2 (Scan#: ' + str(self.dockedOpt.specDataList.currentRow() + 1) + ')'

        self.GraphUtilGaussianFitGraphs(canvas, fig, name, x, y, None, xLabel, yLabel, 'L')

    # -----------------------------------------------------------------------------------------------#
    def percentageChangeLConstantOnePeak(self):
        """This method get the percentage change of the L Constant and graphs it (Try out)"""
        LDataPercentChange = []

        for i in range(0, len(self.LPosData)):
            pctChangeData = ((self.LPosData[i] - self.LPosData[0])/self.LPosData[0]) * 100
            LDataPercentChange.append(pctChangeData)

        fig = Figure((5.0, 4.0), dpi=100)
        canvas = FigureCanvas(fig)

        x = self.getVoltage()
        y = LDataPercentChange
        xLabel = 'Voltage'
        yLabel = '%-Change'
        name = 'L Constant %-Change'

        self.GraphUtilGaussianFitGraphs(canvas, fig, name, x, y, None, xLabel, yLabel, 'L')

    # -----------------------------------------------------------------------------------------------#
    def percentageChangeLConstantPeakOne(self):
        """This method get the percentage change of the L Constant and graphs it (Try out)"""
        LDataPercentChange = []

        for i in range(0, len(self.LPos1Data)):
            pctChangeData = ((self.LPos1Data[i] - self.LPos1Data[0]) / self.LPos1Data[0]) * 100
            LDataPercentChange.append(pctChangeData)

        fig = Figure((5.0, 4.0), dpi=100)
        canvas = FigureCanvas(fig)

        x = self.getVoltage()
        y = LDataPercentChange
        xLabel = 'Voltage'
        yLabel = '%-Change'
        name = 'L Constant %-Change'

        self.GraphUtilGaussianFitGraphs(canvas, fig, name, x, y, None, xLabel, yLabel, 'L')

    # -----------------------------------------------------------------------------------------------#
    def percentageChangeLConstantPeakTwo(self):
        """This method get the percentage change of the L Constant and graphs it (Try out)"""
        LDataPercentChange = []

        for i in range(0, len(self.LPos2Data)):
            pctChangeData = ((self.LPos2Data[i] - self.LPos2Data[0]) / self.LPos2Data[0]) * 100
            LDataPercentChange.append(pctChangeData)

        """Try out for the percentage change of one peak"""
        fig = Figure((5.0, 4.0), dpi=100)
        canvas = FigureCanvas(fig)

        x = self.getVoltage()
        y = LDataPercentChange
        xLabel = 'Voltage'
        yLabel = '%-Change'
        name = 'L Constant %-Change'

        self.GraphUtilGaussianFitGraphs(canvas, fig, name, x, y, None, xLabel, yLabel, 'L')






