#!/usr/bin/env python

"""
Copyright (c) UChicago Argonne, LLC. All rights reserved.
See LICENSE file.
"""
# ---------------------------------------------------------------------------------------------------------------------#
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
# ---------------------------------------------------------------------------------------------------------------------#

class AlgebraicExpress:
    """
    """
    def __init__ (self, parent=None):
        self.gausFit = parent
        self.dockedOpt = self.gausFit.dockedOpt
        self.readSpec = self.gausFit.readSpec
        self.myMainWindow = self.gausFit.myMainWindow


    def singularValueDecomposition(self):
        self.U = []
        self.S = []
        self.V = []

        self.U, self.S, self.V = svd(self.dockedOpt.TT)
        print len(self.S)

    def PlotAlgebraicExpGraph(self, name, x, y, xLabel, yLabel):
        """Generic plotting method that plots depending on which graph the user has selected.
        :param canvas: canvas for widget
        :param fig: figure for graph
        :param name: name of tab
        :param x: x-values
        :param y: y-values
        :param error: error values for gaussian fit graphs
        :param xLabel: x-axis label
        :param yLabel: y-axis label
        """
        mainGraph = QWidget()
        fig = Figure((5.0, 4.0), dpi=100)
        canvas = FigureCanvas(fig)

        canvas.setParent(mainGraph)
        axes = fig.add_subplot(221)

        axes.plot(x, y)

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

    def PlotAlgebraicExpGraphs(self, title, name1, x, y1, xLabel, yLabel1, y2, name2, yLabel2, y3, name3, yLabel3):
        mainGraph = QWidget()
        fig = Figure((5.0, 4.0), dpi=100)
        canvas = FigureCanvas(fig)

        canvas.setParent(mainGraph)
        axes = fig.add_subplot(221)
        ax = fig.add_subplot(222)
        axe = fig.add_subplot(223)

        axes.set_title(name1)
        axes.set_xlabel(xLabel)
        axes.set_ylabel(yLabel1)
        axes.plot(x, y1)

        ax.set_title(name2)
        ax.set_xlabel(xLabel)
        ax.set_ylabel(yLabel2)
        ax.plot(x, y2)

        axe.set_title(name3)
        axe.set_xlabel(xLabel)
        axe.set_ylabel(yLabel3)
        axe.plot(x, y3)

        fig.tight_layout()
        canvas.draw()

        tab = QWidget()
        tab.setStatusTip(title)
        vbox = QVBoxLayout()
        graphNavigationBar = NavigationToolbar(canvas, mainGraph)
        vbox.addWidget(graphNavigationBar)
        vbox.addWidget(canvas)
        tab.setLayout(vbox)

        self.myMainWindow.savingCanvasTabs(tab, title, canvas, fig)

    def plotTh2ThExp(self):
        self.singularValueDecomposition()
        title = '\u03B82\u03B8 (Scan#: ' + str(self.dockedOpt.specDataList.currentRow() + 1) + ')'

        name1 = "\u03B82\u03B8"
        x = self.readSpec.L
        y1 = -self.U[:, 0]
        xLabel = "RLU"
        yLabel1 = "TH2TH"

        name2 = "\u03B82\u03B8'"
        y2 = self.U[:, 1]
        yLabel2 = "Counts"

        name3 = "\u03B82\u03B8''"
        y3 = self.U[:, 3]
        yLabel3 = "Counts"
        self.PlotAlgebraicExpGraphs(title, name1, x, y1, xLabel, yLabel1, y2, name2, yLabel2, y3, name3, yLabel3)

    def weightingExp(self):
        self.singularValueDecomposition()
        title = 'Weighting (Scan#: ' + str(self.dockedOpt.specDataList.currentRow() + 1) + ')'

        name1 = "Weighting 1"
        x = self.gausFit.getVoltage()
        y1 = -self.V[0]
        xLabel = "Voltage"
        yLabel1 = "Weighting 1"

        name2 = "Weighting 2"
        y2 = self.V[1]
        yLabel2 = "Weighting 2"

        name3 = "Weighting 3"
        y3 = self.V[2]
        yLabel3 = "Weighting 3"
        self.PlotAlgebraicExpGraphs(title, name1, x, y1, xLabel, yLabel1, y2, name2, yLabel2, y3, name3, yLabel3)

    def plotSingleValueIndex(self):
        """Needs some work. Not working properly yet"""
        self.singularValueDecomposition()
        name = 'Singular Value Index (Scan#: ' + str(self.dockedOpt.specDataList.currentRow() + 1) + ')'
        x = self.readSpec.L
        y = log(self.S)
        xLabel = "RLU"
        yLabel = "TH2TH"
        self.PlotAlgebraicExpGraph(name, x, y, xLabel, yLabel)


