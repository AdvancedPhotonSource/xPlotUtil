===================================
xPlot Util Version 0.0.1 06/12/2017
===================================

The program provides an interface for the the user to fit, graph and normalize its data. The GUI is built using PyQT5,
creating an interactive GUI for the user to fit and graphs those fits. First the user must open a spec file, the scans
will load on the docked widget on the right of the window. The user will then select a scan by double clicking on it.
This will allow the user to open the file with the specific data for the scan. This enables the user to graph the raw
data, as well as do a Gaussian fit, normalize the data or do a Lattice fit. The program allows the user to graph the
data obtained from both the Gaussian and Lattice fit, as well as to create a report from those fits.

Getting Started
---------------
- The first step to building an environment to run xPlot Util is downloading Anaconda. Install the version that utilizes
Python 2.7. For further instructions on how to download Anaconda visit https://www.continuum.io/downloads
- Once Anaconda has been installed on your machine, through the terminal either using pip or conda. Please install the
following modules:
    - pyqt 5.6.0
    - matplotlib 2.0.2
    - numpy 1.13.0
    - pyside 1.2.0
    - spec2nexus 2017.522.1
    - future 0.16.0
    - scipy 0.19.0

Built With
----------
- PyQt5/PySide - Creates the framework for the GUI.
- matplotlib - Creates frame work for the graphs.
- spec2nexus - Reads spec file.

Installation
------------
To download xPlot Util use the git clone command by using HTTPS or SSH, which I have provided below:
    - SSH - git@github.com:AdvancedPhotonSource/xPlotUtil.git
    - HTTPS - https://github.com/AdvancedPhotonSource/xPlotUtil.git

Author(s)
-------
Phaulo C. Escalante - CO-OP Student Technical at Argonne National Laboratory

License
-------
Copyright (c) UChicago Argonne, LLC. All rights reserved.
See LICENSE file.






