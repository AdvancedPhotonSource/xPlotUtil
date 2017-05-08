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
    from PySide import QtGui, QtCore
else:
    from PyQt4 import QtGui, QtCore
from scipy.optimize import curve_fit
from scipy import exp
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4 import NavigationToolbar2QT as NavigationToolbar
from matplotlib.ticker import FormatStrFormatter

class GaussianFitting:

    def __init__ (self, parent=None):
        self.TwoPkFitData = [0][0]
        self.dockedOpt = parent
        self.myMainWindow = self.dockedOpt.myMainWindow
        self.continueGraphingEachFit = True #Boolean to stop on Each fit graphing

    # --------------------------------------------------------------------------------------#
    def TwoPeakFitting(self, filename):
        """Gaussian Fitting for Two Peaks [Updated April 4, 2017]"""
        data = np.loadtxt(open(filename))
        nRow = data.shape[0]  # Number of rows
        nCol = data.shape[1]  # Number of columns
        x = 0
        for f in range(nCol):
            if (np.mean(data[:, f]) == 0):
                pass
            else:
                x += 1
        nCol = x  # Gets the number of columns with data in them
        TT = np.zeros((nRow, nCol))
        for i in range(nCol):
            TT[:, i] = data[:, i]

        self.PkFitData = zeros((nCol, 12))  # Creats the empty 2D List

        for j in range(nCol):
            col_data = data[:, j]
            xx = arange(0, len(col_data))
            param = self.twoPkFitting(xx, col_data)
            fit_result = param[0]
            fit_error = param[1]
            self.PkFitData[j, :] = (fit_result[0], fit_error[0], fit_result[1], fit_error[1], fit_result[2],
                                    fit_error[2], fit_result[3], fit_error[3], fit_result[4], fit_error[4],
                                    fit_result[5], fit_error[5])
        print(self.PkFitData)


    def twoPkFitting(self, xx, yy):
        mean = sum(xx * yy) / sum(yy)
        sigma = np.sqrt(sum(yy * (xx - mean) ** 2)) / sqrt(sum(yy))
        bg0 = min(yy)  # min value of yy
        popt, pcov = curve_fit(self.gaus2, xx, yy, p0=[self.peak1Amp, self.peak2Amp, self.peak1Pos, self.peak2Pos,
                                                       self.peak1Wid, self.peak2Wid, bg0])
        perr = np.sqrt(np.diag(pcov))
        self.graphEachFitRawData(xx, yy, popt)
        return popt, perr

    def gaus2(self, x, a1, a2, x01, x02, sigma1, sigma2, background):
        return a1 * exp(-(x - x01) ** 2 / (2 * sigma1 ** 2))\
               + a2 *exp(-(x - x02) ** 2 / (2 * sigma2 ** 2)) + background
    # -------------------------------------------------------------------------------------------------------------#
    def graphEachFitRawData(self, xx, yy, popt):
        """
        This method graphs the raw data and the fitted data.
        :param xx: bins
        :param yy: raw data column
        :param popt: from the gaussian fit
        :return:
        """
        if (self.continueGraphingEachFit == True):
            self.mainGraph = QtGui.QDialog(self.myMainWindow)
            self.mainGraph.resize(600, 600)
            dpi = 100
            fig = Figure((3.0, 3.0), dpi=dpi)
            canvas = FigureCanvas(fig)
            canvas.setParent(self.mainGraph)
            axes = fig.add_subplot(111)

            axes.plot(xx, yy, 'b+:', label='data')
            axes.plot(xx, self.gaus2(xx, *popt), 'ro:', label='fit')
            axes.legend()
            axes.set_title('Gaussian Fit')
            axes.set_xlabel('Bins')
            axes.set_ylabel('Intensity')
            canvas.draw()

            vbox = QtGui.QVBoxLayout()
            hbox = QtGui.QHBoxLayout()
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
        self.skipEachFitGraphBtn = QtGui.QPushButton('Skip')
        self.skipEachFitGraphBtn.setStatusTip("Skip the graphing of each fit")
        self.skipEachFitGraphBtn.clicked.connect(self.skipEachFit)

    def nextFitGraphButton(self):
        """Button that shows the next fit graph, calls on nextFitGraph() method"""
        # Button next to the FileNameRdOnly label and LineEdit
        self.nextFitGraphBtn = QtGui.QPushButton('Next')
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
    def OnePeakFitting(self, filename):
        """Gaussian Fit for one Peak [Updated April 11, 2017]"""
        data = np.loadtxt(open(filename))
        nRow = data.shape[0]  # num of points, 76
        nCol = data.shape[1]  # size of array from epics, 100
        x = 0
        for f in range(nCol):
            if (np.mean(data[:, f]) == 0):
                pass
            else:
                x += 1
        nCol = x  # Gets the number of columns

        TT = np.zeros((nRow, nCol))
        for i in range(nCol):
            TT[:, i] = data[:, i]

        self.PkFitData = zeros((nCol, 6))  # Creates the empty 2D List
        for j in range(nCol):
            col_data = data[:, j]
            xx = arange(0, len(col_data))
            param = self.OnePkFitting(xx, col_data)
            fit_result = param[0]
            fit_error = param[1]
            self.PkFitData[j, :] =(fit_result[0], fit_error[0], fit_result[1], fit_error[1], fit_result[2],
                                             fit_error[2])
        print(self.PkFitData)


    def OnePkFitting(self, xx, yy):
        n = len(xx)  # the number of data
        mean = sum(xx * yy) / sum(yy)  # note this correction
        #    #sigma = sum(y*(x-mean)**2)/n        #note this correction
        sigma = np.sqrt(sum(yy * (xx - mean) ** 2)) / sqrt(sum(yy))
        popt, pcov = curve_fit(self.gaus1, xx, yy, p0=[1000, mean, sigma, 1, 100])
        perr = np.sqrt(np.diag(pcov))
        return popt, perr


    def gaus1(self, x, a, x0, sigma, a0, b):
        return a * exp(-(x - x0) ** 2 / (2 * sigma ** 2)) + a0 * x + b

    # -----------------------------------------------------------------------------------------------------------#
    def graphAmplitude1(self):
        """This method graphs the Amplitude for peak one"""

        mainGraph = QtGui.QWidget()

        dpi = 100
        fig = Figure((5.0, 4.0), dpi=dpi)
        canvas = FigureCanvas(fig)
        canvas.setParent(mainGraph)

        axes = fig.add_subplot(111)

        yy0 = self.PkFitData[:, 0]
        yy_err0 = self.PkFitData[:, 1]
        xx = self.getXAxis(self.dockedOpt.fileName)

        axes.plot(xx, yy0)
        axes.set_ylabel('Intensity')
        axes.set_xlabel('Voltage')
        axes.errorbar(xx, yy0, yerr=yy_err0, fmt='o')
        axes.set_title('Peak #1 Amplitude')
        canvas.draw()

        tab = QtGui.QWidget()
        tab.setStatusTip("Peak #1 Amplitude")
        vbox = QtGui.QVBoxLayout()
        graphNavigationBar = NavigationToolbar(canvas, mainGraph)
        vbox.addWidget(graphNavigationBar)
        vbox.addWidget(canvas)
        tab.setLayout(vbox)

        self.myMainWindow.tabWidget.addTab(tab, "Peak #1 Amplitude")
        self.myMainWindow.tabWidget.setCurrentWidget(tab)

        self.myMainWindow.canvasArray.append(canvas)
        self.myMainWindow.figArray.append(fig)
    # -----------------------------------------------------------------------------------------#

    def graphPeakPosition1(self):
        """This method graphs the peak position for peak one"""

        mainGraph = QtGui.QWidget()

        dpi = 100
        fig = Figure((5.0, 4.0), dpi=dpi)
        canvas = FigureCanvas(fig)
        canvas.setParent(mainGraph)

        axes = fig.add_subplot(111)

        xx = self.getXAxis(self.dockedOpt.fileName)
        yy1 = self.PkFitData[:, 4]
        yy_err1 = self.PkFitData[:, 5]
        axes.plot(xx, yy1)
        axes.set_ylabel('Position')
        axes.set_xlabel('Voltage')
        axes.errorbar(xx, yy1, yerr=yy_err1, fmt='o')
        axes.set_title('Peak #1 Position')
        canvas.draw()

        tab = QtGui.QWidget()
        tab.setStatusTip("Peak #1 Position")

        vbox = QtGui.QVBoxLayout()
        graphNavigationBar = NavigationToolbar(canvas, mainGraph)
        vbox.addWidget(graphNavigationBar)
        vbox.addWidget(canvas)
        tab.setLayout(vbox)

        self.myMainWindow.tabWidget.addTab(tab, "Peak #1 Position")
        self.myMainWindow.tabWidget.setCurrentWidget(tab)

        self.myMainWindow.canvasArray.append(canvas)
        self.myMainWindow.figArray.append(fig)

    # ----------------------------------------------------------------------------------------------------#

    def graphPeakWidth1(self):
        """This method graphs the Peak width for peak one"""

        mainGraph = QtGui.QWidget()

        dpi = 100
        fig = Figure((5.0, 4.0), dpi=dpi)
        canvas = FigureCanvas(fig)
        canvas.setParent(mainGraph)

        axes = fig.add_subplot(111)

        xx = self.getXAxis(self.dockedOpt.fileName)
        yy2 = self.PkFitData[:, 8]
        yy_err2 = self.PkFitData[:, 9]
        axes.plot(xx, yy2)
        axes.set_ylabel('Width')
        axes.set_xlabel('Voltage')
        axes.errorbar(xx, yy2, yerr=yy_err2, fmt='o')
        axes.set_title('Peak #1 Width')
        canvas.draw()

        tab = QtGui.QWidget()
        tab.setStatusTip("Peak #1 Width")
        vbox = QtGui.QVBoxLayout()
        graphNavigationBar = NavigationToolbar(canvas, mainGraph)
        vbox.addWidget(graphNavigationBar)
        vbox.addWidget(canvas)
        tab.setLayout(vbox)
        self.dockedOpt.myMainWindow.tabWidget.addTab(tab, "Peak #1 Width")
        self.dockedOpt.myMainWindow.tabWidget.setCurrentWidget(tab)

        self.dockedOpt.myMainWindow.canvasArray.append(canvas)
        self.dockedOpt.myMainWindow.figArray.append(fig)

    # ----------------------------------------------------------------------------------------------------#
    def graphAmplitudeXWidth1(self):
        """This method graphs the amplitude x width for the first peak"""

        mainGraph = QtGui.QWidget()

        dpi = 100
        fig = Figure((5.0, 4.0), dpi=dpi)
        canvas = FigureCanvas(fig)
        canvas.setParent(mainGraph)
        axes = fig.add_subplot(111)

        xx = self.getXAxis(self.dockedOpt.fileName)
        yy2 = self.PkFitData[:, 8]
        yy0 = self.PkFitData[:, 0]
        yy3 = yy0 * yy2
        axes.plot(xx, yy3)
        axes.set_ylabel('A x W')
        axes.set_xlabel('Voltage')
        axes.plot(xx, yy3, 'go')
        axes.set_title('Peak #1 Amplitude X Width')
        canvas.draw()

        tab = QtGui.QWidget()
        tab.setStatusTip("Peak #1 Amplitude X Width")
        vbox = QtGui.QVBoxLayout()
        graphNavigationBar = NavigationToolbar(canvas, mainGraph)
        vbox.addWidget(graphNavigationBar)
        vbox.addWidget(canvas)
        tab.setLayout(vbox)
        self.dockedOpt.myMainWindow.tabWidget.addTab(tab, "Peak #1 Amplitude X Width")
        self.dockedOpt.myMainWindow.tabWidget.setCurrentWidget(tab)

        self.dockedOpt.myMainWindow.canvasArray.append(canvas)
        self.dockedOpt.myMainWindow.figArray.append(fig)

    # -----------------------------------------------------------------------------------------------------------#
    def graphAmplitude2(self):
        """This method graphs the Amplitude for peak one"""

        mainGraph = QtGui.QWidget()

        dpi = 100
        fig = Figure((5.0, 4.0), dpi=dpi)
        canvas = FigureCanvas(fig)
        canvas.setParent(mainGraph)

        axes = fig.add_subplot(111)

        yy0 = self.PkFitData[:, 2]
        yy_err0 = self.PkFitData[:, 3]
        xx = self.getXAxis(self.dockedOpt.fileName)

        axes.plot(xx, yy0)
        axes.set_xlabel('Voltage')
        axes.set_ylabel('Intensity')
        axes.errorbar(xx, yy0, yerr=yy_err0, fmt='o')
        axes.set_title('Peak #2 Amplitude')
        canvas.draw()

        tab = QtGui.QWidget()
        tab.setStatusTip("Peak #2 Amplitude")
        vbox = QtGui.QVBoxLayout()
        graphNavigationBar = NavigationToolbar(canvas, mainGraph)
        vbox.addWidget(graphNavigationBar)
        vbox.addWidget(canvas)
        tab.setLayout(vbox)

        self.myMainWindow.tabWidget.addTab(tab, "Peak #2 Amplitude")
        self.myMainWindow.tabWidget.setCurrentWidget(tab)

        self.myMainWindow.canvasArray.append(canvas)
        self.myMainWindow.figArray.append(fig)
    # -----------------------------------------------------------------------------------------#

    def graphPeakPosition2(self):
        """This method graphs the peak position for peak one"""

        mainGraph = QtGui.QWidget()

        dpi = 100
        fig = Figure((5.0, 4.0), dpi=dpi)
        canvas = FigureCanvas(fig)
        canvas.setParent(mainGraph)

        axes = fig.add_subplot(111)

        xx = self.getXAxis(self.dockedOpt.fileName)
        yy1 = self.PkFitData[:, 6]
        yy_err1 = self.PkFitData[:, 7]
        axes.plot(xx, yy1)
        axes.set_xlabel('Voltage')
        axes.set_ylabel('Position')
        axes.errorbar(xx, yy1, yerr=yy_err1, fmt='o')
        axes.set_title('Peak #1 Position')
        canvas.draw()

        tab = QtGui.QWidget()
        tab.setStatusTip("Peak #1 Position")

        vbox = QtGui.QVBoxLayout()
        graphNavigationBar = NavigationToolbar(canvas, mainGraph)
        vbox.addWidget(graphNavigationBar)
        vbox.addWidget(canvas)
        tab.setLayout(vbox)

        self.myMainWindow.tabWidget.addTab(tab, "Peak #2 Position")
        self.myMainWindow.tabWidget.setCurrentWidget(tab)

        self.myMainWindow.canvasArray.append(canvas)
        self.myMainWindow.figArray.append(fig)

    # ----------------------------------------------------------------------------------------------------#

    def graphPeakWidth2(self):
        """This method graphs the Peak width for peak one"""

        mainGraph = QtGui.QWidget()

        dpi = 100
        fig = Figure((5.0, 4.0), dpi=dpi)
        canvas = FigureCanvas(fig)
        canvas.setParent(mainGraph)

        axes = fig.add_subplot(111)

        xx = self.getXAxis(self.dockedOpt.fileName)
        yy2 = self.PkFitData[:, 10]
        yy_err2 = self.PkFitData[:, 11]
        axes.plot(xx, yy2)
        axes.set_xlabel('Voltage')
        axes.set_ylabel('Width')
        axes.errorbar(xx, yy2, yerr=yy_err2, fmt='o')
        axes.set_title('Peak #2 Width')
        canvas.draw()

        tab = QtGui.QWidget()
        tab.setStatusTip("Peak #2 Width")
        vbox = QtGui.QVBoxLayout()
        graphNavigationBar = NavigationToolbar(canvas, mainGraph)
        vbox.addWidget(graphNavigationBar)
        vbox.addWidget(canvas)
        tab.setLayout(vbox)
        self.dockedOpt.myMainWindow.tabWidget.addTab(tab, "Peak #2 Width")
        self.dockedOpt.myMainWindow.tabWidget.setCurrentWidget(tab)

        self.dockedOpt.myMainWindow.canvasArray.append(canvas)
        self.dockedOpt.myMainWindow.figArray.append(fig)

    # ----------------------------------------------------------------------------------------------------#
    def graphAmplitudeXWidth2(self):
        """This method graphs the amplitude x width for the first peak"""

        mainGraph = QtGui.QWidget()

        dpi = 100
        fig = Figure((5.0, 4.0), dpi=dpi)
        canvas = FigureCanvas(fig)
        canvas.setParent(mainGraph)
        axes = fig.add_subplot(111)

        xx = self.getXAxis(self.dockedOpt.fileName)
        yy2 = self.PkFitData[:, 10]
        yy0 = self.PkFitData[:, 2]
        yy3 = yy0 * yy2
        axes.plot(xx, yy3)
        axes.set_xlabel('Voltage')
        axes.set_ylabel('A x W')
        axes.plot(xx, yy3, 'go')
        axes.set_title('Peak #2 Amplitude X Width')
        canvas.draw()

        tab = QtGui.QWidget()
        tab.setStatusTip("Peak #2 Amplitude X Width")
        vbox = QtGui.QVBoxLayout()
        graphNavigationBar = NavigationToolbar(canvas, mainGraph)
        vbox.addWidget(graphNavigationBar)
        vbox.addWidget(canvas)
        tab.setLayout(vbox)
        self.dockedOpt.myMainWindow.tabWidget.addTab(tab, "Peak #2 Amplitude X Width")
        self.dockedOpt.myMainWindow.tabWidget.setCurrentWidget(tab)

        self.dockedOpt.myMainWindow.canvasArray.append(canvas)
        self.dockedOpt.myMainWindow.figArray.append(fig)

    # ------------------------------------------------------------------------------------------------------------#
    def getXAxis(self, fileName):
        x = []
        # Gets the amplitude
        inF = open(fileName, 'r')
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
        data = np.loadtxt(open(fileName))
        nCol = data.shape[1]  # Number of columns
        c = 0
        for f in range(nCol):
            if (np.mean(data[:, f]) == 0):
                break
            else:
                c += 1
        bins = c  # Gets the number of bins

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

    #-------------------------------------------------------------------------------------------------------------#
    def graphAll(self):
        """Fuction graphs all the graphs. Makes sure the fileName is not empty
            and that the path leads to a file
        """
        self.graphAmplitude1()
        self.graphPeakPosition1()
        self.graphPeakWidth1()
        self.graphAmplitudeXWidth1()
        self.graphAmplitude2()
        self.graphPeakPosition2()
        self.graphPeakWidth2()
        self.graphAmplitudeXWidth2()
    # -------------------------------------------------------------------------------------------------------------#
    def gausInputDialog(self):
        """Dialog where the user import """
        self.dialogGausFit = QtGui.QDialog()
        inputForm = QtGui.QFormLayout()
        buttonLayout = QtGui.QHBoxLayout()
        spaceLayout = QtGui.QVBoxLayout()

        spaceLayout.addStretch(1)

        self.peak1AmpSpin = QtGui.QDoubleSpinBox()
        self.peak1AmpSpin.setMaximum(100000)
        self.peak1PosSpin = QtGui.QDoubleSpinBox()
        self.peak1WidthSpin = QtGui.QDoubleSpinBox()

        self.peak2AmpSpin = QtGui.QDoubleSpinBox()
        self.peak2AmpSpin.setMaximum(100000)
        self.peak2PosSpin = QtGui.QDoubleSpinBox()
        self.peak2WidthSpin = QtGui.QDoubleSpinBox()

        ok = QtGui.QPushButton("Ok")
        cancel = QtGui.QPushButton("Cancel")

        cancel.clicked.connect(self.dialogGausFit.close)
        ok.clicked.connect(self.returnGausUserInput)
        buttonLayout.addWidget(cancel)
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(ok)

        inputForm.addRow("Peak#1 Amplitude: ", self.peak1AmpSpin)
        inputForm.addRow("Peak#1 Position: ", self.peak1PosSpin)
        inputForm.addRow("Peak#1 Width: ", self.peak1WidthSpin)
        inputForm.addRow("Peak#2 Amplitude: ", self.peak2AmpSpin)
        inputForm.addRow("Peak#2 Position: ", self.peak2PosSpin)
        inputForm.addRow("Peak#2 Width: ", self.peak2WidthSpin)
        inputForm.addRow(spaceLayout)
        inputForm.addRow(buttonLayout)

        self.dialogGausFit.setWindowTitle("Input Guess Data for Fit")
        self.dialogGausFit.setLayout(inputForm)
        self.dialogGausFit.resize(250, 200)
        self.dialogGausFit.show()

    def returnGausUserInput(self):
        """Sets the values of the variables in the method twoPkFitting, that are used as parameters.
        It also sets the Gaussian fit options available"""
        self.peak1Amp = float(self.peak1AmpSpin.value())
        self.peak1Pos = float(self.peak1PosSpin.value())
        self.peak1Wid = float(self.peak1WidthSpin.value())

        self.peak2Amp = float(self.peak2AmpSpin.value())
        self.peak2Pos = float(self.peak2PosSpin.value())
        self.peak2Wid = float(self.peak2WidthSpin.value())

        self.dialogGausFit.close()
        self.TwoPeakFitting(self.dockedOpt.fileName)
        self.dockedOpt.dockGaussianFitOptions()
        self.dockedOpt.rdOnlyFileNameG.setText(self.dockedOpt.fileName)
        self.dockedOpt.rdOnlyFileNameG.setStatusTip(self.dockedOpt.fileName)
        self.myMainWindow.LFit.setEnabled(True)

        # Marks the data has been fitted
        self.dockedOpt.gausFitStat = True

    # -------------------------------------------------------------------------------------------------------------#
    def LInputDialog(self):
        """Dialog where the user import """
        self.dialogLFit = QtGui.QDialog()
        inputForm = QtGui.QFormLayout()
        buttonLayout = QtGui.QHBoxLayout()
        spaceLayout = QtGui.QVBoxLayout()

        spaceLayout.addStretch(1)

        self.maxLSpin = QtGui.QDoubleSpinBox()
        self.maxLSpin.setDecimals(4)
        self.maxLSpin.setMaximum(100000)
        self.minLSpin = QtGui.QDoubleSpinBox()
        self.lElementSpin = QtGui.QDoubleSpinBox()
        self.lElementSpin.setDecimals(4)

        ok = QtGui.QPushButton("Ok")
        cancel = QtGui.QPushButton("Cancel")

        cancel.clicked.connect(self.dialogLFit.close)
        ok.clicked.connect(self.doLFit)
        buttonLayout.addWidget(cancel)
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(ok)

        inputForm.addRow("Max L: ", self.maxLSpin)
        inputForm.addRow("Min L: ", self.minLSpin)
        inputForm.addRow("L Element: ", self.lElementSpin)
        inputForm.addRow(spaceLayout)
        inputForm.addRow(buttonLayout)

        self.dialogLFit.setWindowTitle("Input Data for L Fit")
        self.dialogLFit.setLayout(inputForm)
        self.dialogLFit.resize(200, 150)
        self.dialogLFit.exec_()

    # -------------------------------------------------------------------------------------------------------------#
    """This is where the methods used for the L Fit begin"""
    def PositionLFit(self, pos, rows):
        l = (1/(((pos/rows)*(self.maxL-self.minL)+self.minL)/2))*self.elementL
        return l


    # -------------------------------------------------------------------------------------------------------------#
    def doLFit(self):
        self.dialogLFit.close()
        self.maxL = float(self.maxLSpin.value())
        self.minL = float(self.minLSpin.value())
        self.elementL = float(self.lElementSpin.value())

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

        self.LPos1Data = []
        self.LPos2Data = []

        # Position 1
        for i in range(nRow-1):
          self.LPos1Data.append(self.PositionLFit(self.PkFitData[i, 4], nRow))

        # Position 2
        for i in range(nRow - 1):
          self.LPos2Data.append(self.PositionLFit(self.PkFitData[i, 6], nRow))

        self.dockedOpt.DockLFitOptions()
        self.dockedOpt.rdOnlyFileNameG.setText(self.dockedOpt.fileName)
        self.dockedOpt.rdOnlyFileNameG.setStatusTip(self.dockedOpt.fileName)
        # Marks that the data has been fitted
        self.dockedOpt.LFitStat = True

    # ----------------------------------------------------------------------------------------------------#
    def graphLFitPos1(self):
        """This method graphs the amplitude x width for the first peak"""

        mainGraph = QtGui.QWidget()

        dpi = 100
        fig = Figure((5.0, 4.0), dpi=dpi)
        canvas = FigureCanvas(fig)
        canvas.setParent(mainGraph)
        axes = fig.add_subplot(111)

        xx = self.getXAxis(self.dockedOpt.fileName)
        yy = self.LPos1Data
        axes.plot(xx, yy)
        axes.plot(xx, yy, 'go')
        axes.set_title('L Fit - Position #1')
        axes.set_xlabel('Voltage')
        axes.set_ylabel('L R U')
        axes.yaxis.set_major_formatter(FormatStrFormatter('%.4f'))
        canvas.draw()

        tab = QtGui.QWidget()
        tab.setStatusTip("L Fit - Position #1")
        vbox = QtGui.QVBoxLayout()
        graphNavigationBar = NavigationToolbar(canvas, mainGraph)
        vbox.addWidget(graphNavigationBar)
        vbox.addWidget(canvas)
        tab.setLayout(vbox)
        self.dockedOpt.myMainWindow.tabWidget.addTab(tab, "L Fit - Position #1")
        self.dockedOpt.myMainWindow.tabWidget.setCurrentWidget(tab)

        self.dockedOpt.myMainWindow.canvasArray.append(canvas)
        self.dockedOpt.myMainWindow.figArray.append(fig)

    # ----------------------------------------------------------------------------------------------------#
    def graphLFitPos2(self):
        """This method graphs the amplitude x width for the first peak"""

        mainGraph = QtGui.QWidget()

        dpi = 100
        fig = Figure((5.0, 4.0), dpi=dpi)
        canvas = FigureCanvas(fig)
        canvas.setParent(mainGraph)
        axes = fig.add_subplot(111)

        xx = self.getXAxis(self.dockedOpt.fileName)
        yy = self.LPos2Data
        axes.plot(xx, yy)
        axes.plot(xx, yy, 'go')
        axes.set_xlabel('Voltage')
        axes.set_ylabel('L R U')
        axes.set_title('L Fit - Position #2')
        axes.yaxis.set_major_formatter(FormatStrFormatter('%.4f'))
        canvas.draw()

        tab = QtGui.QWidget()
        tab.setStatusTip("L Fit - Position #2")
        vbox = QtGui.QVBoxLayout()
        graphNavigationBar = NavigationToolbar(canvas, mainGraph)
        vbox.addWidget(graphNavigationBar)
        vbox.addWidget(canvas)
        tab.setLayout(vbox)
        self.dockedOpt.myMainWindow.tabWidget.addTab(tab, "L Fit - Position #2")
        self.dockedOpt.myMainWindow.tabWidget.setCurrentWidget(tab)

        self.dockedOpt.myMainWindow.canvasArray.append(canvas)
        self.dockedOpt.myMainWindow.figArray.append(fig)





