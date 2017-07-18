#!/usr/bin/env python

"""
Copyright (c) UChicago Argonne, LLC. All rights reserved.
See LICENSE file.

#C In some methods LFit or L refer to the Lattice Constant not RLU

"""
# ---------------------------------------------------------------------------------------------------------------------#
from __future__ import unicode_literals

from PyQt5.QtWidgets import *
from lmfit.models import LorentzianModel, GaussianModel, LinearModel, VoigtModel
from lmfit import Parameters
from pylab import *
# ---------------------------------------------------------------------------------------------------------------------#


class LorentzianFitting:
    """Contains Lorentzian and Voigt fit functions.
    """

    def __init__ (self, parent=None):
        self.algebraExp = parent
        self.gausFit = self.algebraExp.gausFit
        self.dockedOpt = self.algebraExp.dockedOpt
        self.readSpec = self.algebraExp.readSpec
        self.myMainWindow = self.algebraExp.myMainWindow

    def WhichPeakLorentzianFit(self):

        if self.dockedOpt.FileError() == False and self.dockedOpt.fitStat == False:
            chosePeak = self.dockedOpt.PeakDialog()
            if (chosePeak == 'One'):
                self.OnePeakLorentzianFit()
            elif (chosePeak == 'Two'):
                self.TwoPeakLorentzianFit()

    def OnePeakLorentzianFit(self):
        error = self.onePeakLorentzianFit()

        if error == False:
            self.dockedOpt.onePeakStat = True
            self.dockedOpt.fitStat = True
            self.dockedOpt.GraphingFitOptionsTree("L")

    def onePeakLorentzianFit(self):
        try:
            nRow, nCol = self.dockedOpt.fileInfo()

            self.gausFit.binFitData = zeros((nRow, 0))
            self.gausFit.OnePkFitData = zeros((nCol, 6))  # Creates the empty 2D List
            for j in range(nCol):
                yy = self.dockedOpt.TT[:, j]
                xx = arange(0, len(yy))

                x1 = xx[0]
                x2 = xx[-1]
                y1 = yy[0]
                y2 = yy[-1]
                m = (y2 - y1) / (x2 - x1)
                b = y2 - m * x2

                mod = LorentzianModel()
                pars = mod.guess(yy, x=xx)
                mod = mod + LinearModel()
                pars.add('intercept', value=b, vary=True)
                pars.add('slope', value=m, vary=True)
                out = mod.fit(yy, pars, x=xx, slope=m)

                self.gausFit.OnePkFitData[j, :] = (out.best_values['amplitude'], 0, out.best_values['center'], 0,
                                                   out.best_values['sigma'], 0)

                # Saves fitted data of each fit
                fitData = out.best_fit
                binFit = np.reshape(fitData, (len(fitData), 1))
                self.gausFit.binFitData = np.concatenate((self.gausFit.binFitData, binFit), axis=1)

                if self.gausFit.continueGraphingEachFit == True:
                    self.gausFit.graphEachFitRawData(xx, yy, out.best_fit, 'L')

            return False
        except:
            return True

    def TwoPeakLorentzianFit(self):
        error = self.twoPeakLorentzianFit()

        if error == False:
            self.dockedOpt.twoPeakStat = True
            self.dockedOpt.fitStat = True
            self.dockedOpt.GraphingFitOptionsTree("L")

    def twoPeakLorentzianFit(self):
        try:
            nRow, nCol = self.dockedOpt.fileInfo()

            self.gausFit.binFitData = zeros((nRow, 0))
            self.gausFit.TwoPkGausFitData = zeros((nCol, 12))  # Creates the empty 2D List
            for j in range(nCol):
                yy1 = []
                yy2 = []
                yy = self.dockedOpt.TT[:, j]
                i = 0
                for y in yy:
                    if i < len(yy)/2:
                        yy1.append(y)
                    else:
                        yy2.append(y)
                    i += 1

                xx = arange(0, len(yy))
                xx1 = arange(0, len(yy)/2)
                xx2 = arange(len(yy)/2, len(yy))

                x1 = xx[0]
                x2 = xx[-1]
                y1 = yy[0]
                y2 = yy[-1]
                m = (y2 - y1) / (x2 - x1)
                b = y2 - m * x2

                mod1 = LorentzianModel(prefix='p1_')
                mod2 = LorentzianModel(prefix='p2_')

                pars1 = mod1.guess(yy1, x=xx1)
                pars2 = mod2.guess(yy2, x=xx2)
                mod = mod1 + mod2 + LinearModel()
                pars = pars1 + pars2

                pars.add('intercept', value=b, vary=True)
                pars.add('slope', value=m, vary=True)
                out = mod.fit(yy, pars, x=xx, slope=m)

                self.gausFit.TwoPkGausFitData[j, :] = (out.best_values['p1_amplitude'], 0, out.best_values['p1_center'],
                                                       0, out.best_values['p1_sigma'], 0,
                                                       out.best_values['p1_amplitude'], 0, out.best_values['p1_center'],
                                                       0, out.best_values['p1_sigma'], 0)

                # Saves fitted data of each fit
                fitData = out.best_fit
                binFit = np.reshape(fitData, (len(fitData), 1))
                self.gausFit.binFitData = np.concatenate((self.gausFit.binFitData, binFit), axis=1)

                if self.gausFit.continueGraphingEachFit == True:
                    self.gausFit.graphEachFitRawData(xx, yy, out.best_fit, 'L')

            return False
        except:
            return True

    def WhichPeakVoigtFit(self):

        if self.dockedOpt.FileError() == False and self.dockedOpt.fitStat == False:
            chosePeak = self.dockedOpt.PeakDialog()
            if (chosePeak == 'One'):
                self.OnePeakVoigtFit()
            elif (chosePeak == 'Two'):
                self.TwoPeakVoigtFit()

    def OnePeakVoigtFit(self):
        error = self.onePeakVoigtFit()

        if error == False:
            self.dockedOpt.onePeakStat = True
            self.dockedOpt.fitStat = True
            self.dockedOpt.GraphingFitOptionsTree("V")

    def onePeakVoigtFit(self):
        try:
            nRow, nCol = self.dockedOpt.fileInfo()

            self.gausFit.binFitData = zeros((nRow, 0))
            self.gausFit.OnePkFitData = zeros((nCol, 6))  # Creates the empty 2D List
            for j in range(nCol):
                yy = self.dockedOpt.TT[:, j]
                xx = arange(0, len(yy))

                x1 = xx[0]
                x2 = xx[-1]
                y1 = yy[0]
                y2 = yy[-1]
                m = (y2 - y1) / (x2 - x1)
                b = y2 - m * x2

                mod = VoigtModel()
                # print mod.param_names
                pars = mod.guess(yy, x=xx)
                mod = mod + LinearModel()
                pars.add('intercept', value=b, vary=True)
                pars.add('slope', value=m, vary=True)
                out = mod.fit(yy, pars, x=xx, slope=m)

                self.gausFit.OnePkFitData[j, :] = (out.best_values['amplitude'], 0, out.best_values['center'], 0,
                                           out.best_values['sigma'], 0)

                # Saves fitted data of each fit
                fitData = out.best_fit
                binFit = np.reshape(fitData, (len(fitData), 1))
                self.gausFit.binFitData = np.concatenate((self.gausFit.binFitData, binFit), axis=1)

                if self.gausFit.continueGraphingEachFit == True:
                    self.gausFit.graphEachFitRawData(xx, yy, out.best_fit, 'V')

            return False
        except:
            QMessageBox.warning(self.myMainWindow, "Error", "Please make sure the guesses are realistic when fitting.")
            return True

    def TwoPeakVoigtFit(self):
        error = self.twoPeakVoigtFit()

        if error == False:
            self.dockedOpt.twoPeakStat = True
            self.dockedOpt.fitStat = True
            self.dockedOpt.GraphingFitOptionsTree("V")

    def twoPeakVoigtFit(self):
        try:
            nRow, nCol = self.dockedOpt.fileInfo()

            self.gausFit.binFitData = zeros((nRow, 0))
            self.gausFit.TwoPkGausFitData = zeros((nCol, 12))  # Creates the empty 2D List
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

                print "m ", m
                print 'b ', b

                mod1 = VoigtModel(prefix='p1_')
                mod2 = VoigtModel(prefix='p2_')

                pars1 = mod1.guess(yy1, x=xx1)
                pars2 = mod2.guess(yy2, x=xx2)
                mod = mod1 + mod2 + LinearModel()
                pars = pars1 + pars2

                pars.add('intercept', value=b)
                pars.add('slope', value=m, vary=False)
                print pars
                out = mod.fit(yy, pars, x=xx)

                print out.best_values

                self.gausFit.TwoPkGausFitData[j, :] = (out.best_values['p1_amplitude'], 0, out.best_values['p1_center'],
                                                       0, out.best_values['p1_sigma'], 0,
                                                       out.best_values['p1_amplitude'], 0, out.best_values['p1_center'],
                                                       0, out.best_values['p1_sigma'], 0)

                # Saves fitted data of each fit
                fitData = out.best_fit
                binFit = np.reshape(fitData, (len(fitData), 1))
                self.gausFit.binFitData = np.concatenate((self.gausFit.binFitData, binFit), axis=1)

                if self.gausFit.continueGraphingEachFit == True:
                    self.gausFit.graphEachFitRawData(xx, yy, out.best_fit, 'V')

            return False
        except:
            QMessageBox.warning(self.myMainWindow, "Error", "Please make sure the guesses are realistic when fitting.")
            return True


