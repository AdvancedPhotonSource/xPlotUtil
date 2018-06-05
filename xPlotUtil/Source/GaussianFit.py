#!/usr/bin/env python

"""
Copyright (c) UChicago Argonne, LLC. All rights reserved.
See LICENSE file.

#C In some methods LFit or L refer to the Lattice Constant not RLU

"""
# ---------------------------------------------------------------------------------------------------------------------#
from __future__ import unicode_literals

from PyQt5.QtWidgets import *
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from lmfit.models import LorentzianModel, GaussianModel, LinearModel, VoigtModel

from pylab import *
import numpy as np


from xPlotUtil.Source.AlgebraicExpressions import AlgebraicExpress


# ---------------------------------------------------------------------------------------------------------------------#

class GaussianFitting:
    """Contains Gaussian fit and lattice fit.
    """

    def __init__ (self, parent=None):
        self.TwoPkGausFitData = []
        self.OnePkFitData = []
        self.LPosPrcChangeData = []
        self.LPos1PrcChangeData = []
        self.LPos2PrcChangeData = []
        self.readSpec = parent
        self.dockedOpt = self.readSpec.dockedOpt
        self.myMainWindow = self.dockedOpt.myMainWindow
        self.algebraExp = AlgebraicExpress(parent=self)
        self.lorentFit = self.algebraExp.lorentFit
        self.continueGraphingEachFit = True  # Boolean to stop Each fit graphing

    # --------------------------------Gaussian Fit---------------------------------------------------------------------#
    def OnePeakGaussianFit(self):
        """Calls on the gaussian fit function for one peak and saves fitted data in array.
        """
        error = self.onePeakGaussianFit()

        if error is False:
            self.dockedOpt.onePeakStat = True
            self.dockedOpt.fitStat = True
            self.dockedOpt.GraphingFitOptionsTree("G")


    def onePeakGaussianFit(self):
        """Gaussian Fit for one Peak.
        :param xx: x-value
        :param yy: y-values
        :return: fitted data and error
        """
        try:
            nRow, nCol = self.dockedOpt.fileInfo()

            self.binFitData = zeros((nRow, 0))
            self.OnePkFitData = zeros((nCol, 6))  # Creates the empty 2D List
            QMessageBox.warning(self.myMainWindow, "Hi", "Hola")
            for j in range(nCol):
                yy = self.dockedOpt.TT[:, j]
                xx = arange(0, len(yy))

                x1 = xx[0]
                x2 = xx[-1]
                y1 = yy[0]
                y2 = yy[-1]
                m = (y2 - y1) / (x2 - x1)
                b = y2 - m * x2

                mod = GaussianModel()
                pars = mod.guess(yy, x=xx)
                mod = mod + LinearModel()
                pars.add('intercept', value=b, vary=True)
                pars.add('slope', value=m, vary=True)
                out = mod.fit(yy, pars, x=xx)


                self.OnePkFitData[j, :] = (out.best_values['amplitude'], 0, out.best_values['center'], 0,
                                                   out.best_values['sigma'], 0)

                # Saves fitted data of each fit
                fitData = out.best_fit
                binFit = np.reshape(fitData, (len(fitData), 1))
                self.binFitData = np.concatenate((self.binFitData, binFit), axis=1)

                if self.continueGraphingEachFit == True:
                    self.graphEachFitRawData(xx, yy, out.best_fit, 'G')

            return False
        except:
            QMessageBox.warning(self.myMainWindow, "Error", "Please make sure the guesses are realistic when fitting.")
            return True

    def TwoPeakGaussianFit(self):
        try:
            error = self.twoPeakGaussianFit()

            if error == False:
                self.dockedOpt.twoPeakStat = True
                self.dockedOpt.fitStat = True
                self.dockedOpt.GraphingFitOptionsTree("G")
        except Exception as ex:
            QMessageBox.warning(self.myMainWindow, "Error", "Please make sure the guesses are realistic when fitting."
                                                            "\n\nException: " + str(ex))

    def twoPeakGaussianFit(self):
        try:
            nRow, nCol = self.dockedOpt.fileInfo()

            self.binFitData = zeros((nRow, 0))
            self.TwoPkGausFitData = zeros((nCol, 12))  # Creates the empty 2D List
            for j in range(nCol):
                yy1 = []
                yy2 = []
                yy = self.dockedOpt.TT[:, j]
                i = 0
                for y in yy:
                    if i < len(yy) / 2:
                        yy1.append(y)
                    else:
                        yy2.append(y)
                    i += 1

                xx = arange(0, len(yy))
                xx1 = arange(0, len(yy) / 2)
                xx2 = arange(len(yy) / 2, len(yy))
                x1 = xx[0]
                x2 = xx[-1]
                y1 = yy[0]
                y2 = yy[-1]
                m = (y2 - y1) / (x2 - x1)
                b = y2 - m * x2

                mod1 = GaussianModel(prefix='p1_')

                mod2 = GaussianModel(prefix='p2_')

                pars1 = mod1.guess(yy1, x=xx1)
                pars2 = mod2.guess(yy2, x=xx2)

                mod = mod1 + mod2 + LinearModel()
                pars = pars1 + pars2

                pars.add('intercept', value=b, vary=True)
                pars.add('slope', value=m, vary=True)
                out = mod.fit(yy, pars, x=xx, slope=m)
                QMessageBox.warning(self.myMainWindow, "Hi", "About to start fitting")

                self.TwoPkGausFitData[j, :] = (out.best_values['p1_amplitude'], 0, out.best_values['p1_center'],
                                                       0, out.best_values['p1_sigma'], 0,
                                                       out.best_values['p2_amplitude'], 0, out.best_values['p2_center'],
                                                       0, out.best_values['p2_sigma'], 0)

                # Saves fitted data of each fit
                fitData = out.best_fit
                binFit = np.reshape(fitData, (len(fitData), 1))
                self.binFitData = np.concatenate((self.binFitData, binFit), axis=1)

                if self.continueGraphingEachFit == True:
                    self.graphEachFitRawData(xx, yy, out.best_fit, 'G')

            return False
        except Exception as ex:
            QMessageBox.warning(self.myMainWindow, "Error", "Please make sure the guesses are realistic when fitting."
                                                            "\n\nException: " + str(ex))
            return True

    def graphEachFitRawData(self, xx, yy, fitData, whichFit):
        """This method graphs the raw data and the fitted data for each column.
        :param xx: bins
        :param yy: raw data column
        :param popt: from the gaussian fit
        :param whichPeak: number of peaks
        """
        try:
            self.mainGraph = QDialog(self.myMainWindow)
            self.mainGraph.resize(600, 600)
            dpi = 100
            fig = Figure((3.0, 3.0), dpi=dpi)
            canvas = FigureCanvas(fig)
            canvas.setParent(self.mainGraph)
            axes = fig.add_subplot(111)

            axes.plot(xx, yy, 'b+:', label='data')
            if whichFit == 'G':
                axes.plot(xx, fitData, 'ro:', label='fit')
                axes.set_title('Gaussian Fit')
            elif whichFit == 'L':
                axes.plot(xx, fitData, 'ro:', label='fit')
                axes.set_title("Lorentzian Fit")
            elif whichFit == 'V':
                axes.plot(xx, fitData, 'ro:', label='fit')
                axes.set_title("Voigt Fit")

            axes.legend()
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
        except Exception as e:
            QMessageBox.warning(self.myMainWindow, "Error", "Please make sure the guesses are realistic when fitting. \n\n" + str(e))

    def skipEachFitGraphButton(self):
        """Button that allows the user to skip each fit graph.
        """
        self.skipEachFitGraphBtn = QPushButton('Skip')
        self.skipEachFitGraphBtn.setStatusTip("Skip the graphing of each fit")
        self.skipEachFitGraphBtn.clicked.connect(self.skipEachFit)

    def nextFitGraphButton(self):
        """Button that shows the next fit graph.
        """
        self.nextFitGraphBtn = QPushButton('Next')
        self.nextFitGraphBtn.clicked.connect(self.nextFitGraph)
        self.nextFitGraphBtn.setStatusTip("Graphs the next fit and the original data")

    def nextFitGraph(self):
        """Closes the current fit graph to show the next.
        """
        self.mainGraph.close()

    def skipEachFit(self):
        """Closes the current fit graph and sets continueGraphingEachFit to false
         so that other graphs are not showed.
         """
        self.continueGraphingEachFit = False
        self.mainGraph.close()

    def GraphUtilGaussianFitGraphs(self, name, x, y, error, xLabel, yLabel, whichGraph):
        """Generic plotting method that plots depending on which graph is being plotted.
        :param canvas: canvas for widget
        :param fig: figure for graph
        :param name: name of tab
        :param x: x-values
        :param y: y-values
        :param error: error values for gaussian fit graphs
        :param xLabel: x-axis label
        :param yLabel: y-axis label
        :param whichGraph: char that represents either gaussian or lattice fit
        """
        mainGraph = QWidget()
        fig = Figure((5.0, 4.0), dpi=100)
        canvas = FigureCanvas(fig)

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

    def graphOnePeakAmplitude(self):
        """This method graphs the Amplitude for one peak.
        """
        x = self.getVoltage()
        y = self.OnePkFitData[:, 0]
        error = self.OnePkFitData[:, 1]
        xLabel = 'Voltage'
        yLabel = 'Intensity'
        name = 'Amplitude (Scan#: ' + self.readSpec.scan + ')'

        self.GraphUtilGaussianFitGraphs(name, x, y, error, xLabel, yLabel, 'G')

    def graphOnePeakPosition(self):
        """This method graphs the peak position for one peak.
        """
        x = self.getVoltage()
        y = self.OnePkFitData[:, 2]
        error = self.OnePkFitData[:, 3]
        xLabel = 'Voltage'
        yLabel = 'Position'
        name = 'Position (Scan#: ' + self.readSpec.scan + ')'

        self.GraphUtilGaussianFitGraphs(name, x, y, error, xLabel, yLabel, 'G')

    def graphOnePeakWidth(self):
        """This method graphs the Peak width for one peak.
        """
        x = self.getVoltage()
        y = self.OnePkFitData[:, 4]
        error = self.OnePkFitData[:, 5]
        xLabel = 'Voltage'
        yLabel = 'Width'
        name = 'Width (Scan#: ' + self.readSpec.scan + ')'

        self.GraphUtilGaussianFitGraphs(name, x, y, error, xLabel, yLabel, 'G')

    def graphOnePeakAmplitudeXWidth(self):
        """This method graphs the amplitude x width for one peak.
        """
        x = self.getVoltage()
        yA = self.OnePkFitData[:, 0]
        yW = self.OnePkFitData[:, 4]
        a_err = self.OnePkFitData[:, 1]
        w_err = self.OnePkFitData[:, 5]
        y = yA * yW
        error = ((y * a_err) + (y * w_err)) / y

        xLabel = 'Voltage'
        yLabel = 'A x W'
        name = 'Amplitude X Width (Scan#: ' + self.readSpec.scan + ')'

        self.GraphUtilGaussianFitGraphs(name, x, y, error, xLabel, yLabel, 'G')

    def graphTwoPeakAmplitude1(self):
        """This method graphs the peak one amplitude for two peak.
        """
        x = self.getVoltage()
        y = self.TwoPkGausFitData[:, 0]
        error = self.TwoPkGausFitData[:, 1]
        xLabel = 'Voltage'
        yLabel = 'Intensity'
        name = 'Peak #1 Amplitude (Scan#: ' + self.readSpec.scan + ')'

        self.GraphUtilGaussianFitGraphs(name, x, y, error, xLabel, yLabel, 'G')

    def graphTwoPeakPosition1(self):
        """This method graphs the peak one position for two peak.
        """
        x = self.getVoltage()
        y = self.TwoPkGausFitData[:, 2]
        error = self.TwoPkGausFitData[:, 3]
        xLabel = 'Voltage'
        yLabel = 'Position'
        name = 'Peak #1 Position (Scan#: ' + self.readSpec.scan + ')'

        self.GraphUtilGaussianFitGraphs(name, x, y, error, xLabel, yLabel, 'G')

    def graphTwoPeakWidth1(self):
        """This method graphs the peak one width for two peak.
        """
        x = self.getVoltage()
        y = self.TwoPkGausFitData[:, 4]
        error = self.TwoPkGausFitData[:, 5]
        xLabel = 'Voltage'
        yLabel = 'Width'
        name = 'Peak #1 Width (Scan#: ' + self.readSpec.scan + ')'

        self.GraphUtilGaussianFitGraphs(name, x, y, error, xLabel, yLabel, 'G')

    def graphTwoPeakAmplitudeXWidth1(self):
        """This method graphs the peak one amplitude x width for two peak.
        """
        x = self.getVoltage()
        yA = self.TwoPkGausFitData[:, 0]
        yW = self.TwoPkGausFitData[:, 4]
        a_err = self.TwoPkGausFitData[:, 1]
        w_err = self.TwoPkGausFitData[:, 5]
        y = yA * yW
        error = ((y * a_err) + (y * w_err))/y

        xLabel = 'Voltage'
        yLabel = 'A x W'
        name = 'Peak #1 Amplitude X Width (Scan#: ' + self.readSpec.scan + ')'

        self.GraphUtilGaussianFitGraphs(name, x, y, error, xLabel, yLabel, 'G')

    def graphTwoPeakAmplitude2(self):
        """This method graphs the peak two Amplitude for two peak.
        """
        x = self.getVoltage()
        y = self.TwoPkGausFitData[:, 6]
        error = self.TwoPkGausFitData[:, 7]
        xLabel = 'Voltage'
        yLabel = 'Intensity'
        name = 'Peak #2 Amplitude (Scan#: ' + self.readSpec.scan + ')'

        self.GraphUtilGaussianFitGraphs(
            name, x, y, error, xLabel, yLabel, 'G')

    def graphTwoPeakPosition2(self):
        """This method graphs the peak two position for two peak.
        """
        x = self.getVoltage()
        y = self.TwoPkGausFitData[:, 8]
        error = self.TwoPkGausFitData[:, 9]
        xLabel = 'Voltage'
        yLabel = 'Position'
        name = 'Peak #2 Position (Scan#: ' + self.readSpec.scan + ')'

        self.GraphUtilGaussianFitGraphs(name, x, y, error, xLabel, yLabel, 'G')

    def graphTwoPeakWidth2(self):
        """This method graphs the peak two width for two peak.
        """
        x = self.getVoltage()
        y = self.TwoPkGausFitData[:, 10]
        error = self.TwoPkGausFitData[:, 11]
        xLabel = 'Voltage'
        yLabel = 'Width'
        name = 'Peak #2 Width (Scan#: ' + self.readSpec.scan + ')'

        self.GraphUtilGaussianFitGraphs(name, x, y, error, xLabel, yLabel, 'G')

    def graphTwoPeakAmplitudeXWidth2(self):
        """This method graphs the peak two amplitude x width for the two peak.
        """
        x = self.getVoltage()
        yA = self.TwoPkGausFitData[:, 6]
        yW = self.TwoPkGausFitData[:, 10]
        a_err = self.TwoPkGausFitData[:, 7]
        w_err = self.TwoPkGausFitData[:, 11]
        y = yA * yW
        error = ((y * a_err) + (y * w_err)) / y

        xLabel = 'Voltage'
        yLabel = 'A x W'
        name = 'Peak #2 Amplitude X Width (Scan#: ' + self.readSpec.scan + ')'

        self.GraphUtilGaussianFitGraphs(name, x, y, error, xLabel, yLabel, 'G')

    def getVoltage(self):
        """This method gets the voltage of the bins.
        :return: the voltage
        """
        try:
            x = [] # X array initialized
            PVInfo = {}

            # Gets the amplitude
            inF = open(self.dockedOpt.fileName, 'r')
            lines = inF.readlines()
            header = ''
            for (iL, line) in enumerate(lines):
                if line.startswith('#'):
                    header = line
                    break
            inF.close()
            headerParts = header.split('(')
            titles = headerParts[1].split(',')
            values = headerParts[2].split(',')

            for i in range(len(titles)):
                if i == (len(titles) - 1):
                    lastT = titles[i].split(')')
                    lastV = values[i].split(')')
                    PVInfo.update({str(lastT[0].strip()): float(lastV[0])})
                else:
                    PVInfo.update({str(titles[i].strip()): float(values[i])})
            bins = PVInfo['N_bins']
            amp = PVInfo['amplitude']

            print ("Amplitude: ", amp)

            print ("Bins: ",  bins)

            # Uses the data to find the x axis
            ampStart = 0
            rate = (amp/2)/(bins/4)

        
            for j in range(int(bins/4)):
                ampStart = ampStart + rate
                x.append(ampStart)

            for j in range(int(bins/2)):
                ampStart = ampStart - rate
                x.append(ampStart)

            for j in range(int(bins / 4)):
                ampStart = ampStart + rate
                x.append(ampStart)

            return x
        except Exception as e:
            QMessageBox.warning(self.myMainWindow, "Error", "Unable to detect voltage. Please make sure the PVvalue "
                                                            "contains the voltage in the comments.\n\n"
                                                            "Exception: " + str(e))
    # -----------------------------------------Lattice Fit-------------------------------------------------------------#
    def PositionLFit(self, pos, rows):
        """This method calculates the lattice based on the passed paramaters.
        :param pos: position of the peak
        :param rows: number of total points
        """
        l = (1/(((pos/rows)*(self.readSpec.lMax-self.readSpec.lMin)+self.readSpec.lMin)/2))*self.readSpec.lElement
        return l

    def doLFit(self):
        """This function stores the lattice in arrays depending on the peak.
        """
        try:
            nRow, nCol = self.dockedOpt.fileInfo()

            if  self.dockedOpt.onePeakStat == True :
                self.LPosData = []  # L Constant for One Peak
                for i in range(nCol):
                    self.LPosData.append(self.PositionLFit(self.OnePkFitData[i, 2], nRow))

            elif self.dockedOpt.twoPeakStat == True:
                self.LPos1Data = []  # L Constant for Two Peak [#1]
                self.LPos2Data = []  # L Constant for Two Peak [#2]
                # Position 1
                for i in range(nCol):
                  self.LPos1Data.append(self.PositionLFit(self.TwoPkGausFitData[i, 4], nCol))
                # Position 2
                for i in range(nCol):
                  self.LPos2Data.append(self.PositionLFit(self.TwoPkGausFitData[i, 6], nCol))
        except:
            QMessageBox.warning(self.myMainWindow, "Error", "Please make sure the gaussian fit was done correctly.")

    def graphOnePeakLFitPos(self):
        """This method graphs the Lattice fit position for one peak.
        """
        x = self.getVoltage()
        y = self.LPosData
        xLabel = 'Voltage'
        yLabel = 'L Constant (\u00c5)'
        name = 'Lattice - Position (Scan#: ' + self.readSpec.scan + ')'

        self.GraphUtilGaussianFitGraphs(name, x, y, None, xLabel, yLabel, 'L')

    def graphTwoPeakLFitPos1(self):
        """This method graphs the peak one Lattice fit position for two peak.
        """
        x = self.getVoltage()
        y = self.LPos1Data
        xLabel = 'Voltage'
        yLabel = 'L Constant'
        name = 'Lattice - Position #1 (Scan#: ' + self.readSpec.scan + ')'

        self.GraphUtilGaussianFitGraphs(name, x, y, None, xLabel, yLabel, 'L')

    def graphTwoPeakLFitPos2(self):
        """This method graphs the peak two Lattice fit position for two peak.
        """
        x = self.getVoltage()
        y = self.LPos2Data
        xLabel = 'Voltage'
        yLabel = 'L Constant'
        name = 'Lattice - Position #2 (Scan#: ' + self.readSpec.scan + ')'

        self.GraphUtilGaussianFitGraphs(name, x, y, None, xLabel, yLabel, 'L')

    def doLFitPercentChange(self):
        """This function finds the percentage change of the lattice, depending on the peak.
        """
        try:
            self.LPosPrcChangeData = []

            if self.dockedOpt.onePeakStat == True:
                for i in range(0, len(self.LPosData)):
                    pctChangeData = ((self.LPosData[i] - self.LPosData[0]) / self.LPosData[0]) * 100
                    self.LPosPrcChangeData.append(pctChangeData)

            elif self.dockedOpt.twoPeakStat == True:
                self.LPos1PrcChangeData = []
                self.LPos2PrcChangeData = []
                for i in range(0, len(self.LPos1Data)):
                    pctChangeData = ((self.LPos1Data[i] - self.LPos1Data[0]) / self.LPos1Data[0]) * 100
                    self.LPos1PrcChangeData.append(pctChangeData)

                for i in range(0, len(self.LPos2Data)):
                    pctChangeData = ((self.LPos2Data[i] - self.LPos2Data[0]) / self.LPos2Data[0]) * 100
                    self.LPos2PrcChangeData.append(pctChangeData)
        except:
            QMessageBox.warning(self.myMainWindow, "Error", "Something went wrong while doing the percentage change"
                                                            "lattice fit. Make sure the lattice fit was "
                                                            "done correctly.")

    def percentageChangeLConstantOnePeak(self):
        """This method graphs the lattice %-change for one peak.
        """
        x = self.getVoltage()
        y = self.LPosPrcChangeData
        xLabel = 'Voltage'
        yLabel = '%-Change'
        name = 'Lattice %-Change (Scan#: ' + self.readSpec.scan + ')'

        self.GraphUtilGaussianFitGraphs(name, x, y, None, xLabel, yLabel, 'L')

    def percentageChangeLConstantPeakOne(self):
        """This method graphs the peak one lattice %-change for two peak.
         """
        x = self.getVoltage()
        y = self.LPos1PrcChangeData
        xLabel = 'Voltage'
        yLabel = '%-Change'
        name = 'Lattice %-Change #1 (Scan#: ' + self.readSpec.scan + ')'

        self.GraphUtilGaussianFitGraphs(name, x, y, None, xLabel, yLabel, 'L')

    def percentageChangeLConstantPeakTwo(self):
        """This method graphs the peak two lattice %-change for two peak.
        """
        x = self.getVoltage()
        y = self.LPos2PrcChangeData
        xLabel = 'Voltage'
        yLabel = '%-Change'
        name = 'Lattice %-Change #2 (Scan#: ' + self.readSpec.scan + ')'

        self.GraphUtilGaussianFitGraphs(name, x, y, None, xLabel, yLabel, 'L')

    def EachFitDataReport(self):
        try:
            if self.dockedOpt.fitStat == True:
                selectedFilters = ".txt"
                reportFile, reportFileFilter = QFileDialog.getSaveFileName(self.myMainWindow, "Save Report", None, selectedFilters)

                if reportFile != "":
                    reportFile += reportFileFilter
                    _, nCol = self.dockedOpt.fileInfo()
                    header = "#Bin "

                    i = 1
                    while i <= nCol:
                        header += str(i)+" "
                        i += 1

                    scanNum = self.readSpec.scan
                    comment = "#C PVvalue #" + scanNum + "\n"
                    if self.dockedOpt.onePeakStat == True:
                        np.savetxt(reportFile, self.binFitData, fmt=str('%f'), header=header, comments=comment)
                    elif self.dockedOpt.twoPeakStat == True:
                        np.savetxt(reportFile, self.binFitData, fmt=str('%-14.6f'), delimiter=" ", header=header, comments=comment)
        except:
            QMessageBox.warning(self.myMainWindow, "Error", "Make sure the gaussian fit was done properly, before "
                                                            "exporting the report again.")





