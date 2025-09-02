# GUI-for-MiniZinc-microplates-models
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
A simple GUI to streamline the workflow for using MiniZinc models, which generate microplate layouts. Specifically, it is aimed to be compatible with PLAID ( https://github.com/pharmbio/plaid ) and COMPD (to be published).


## Requirements

The tool is developed in Python 3.12.6, and it requires the installation of `numpy` (version 2.1.1 was used) and `matplotlib` (version 3.10.6 was used) libraries.

Earlier versions of Python and the libraries are likely to work, but it is not guaranteed.

The GUI elements are developed by using the `tkinter` library. It is lightweight and is a Python standard library, though it is somewhat rigid compared to alternatives, such as PyQt6. Thus, there are some limitations on what is possible to accomplish (e.g. due to not being able to scroll the tabs, we only show color gradients for a small number of materials).

## Description

This tool allows a user to:

  - load a selected `*.dzn` file (an input data file, it is an optional step)
  - load a selected `*.csv` file (a microplate layout file, i.e. the results of executing the model)
  - launch MiniZinc, which will take the loaded input file and a selected model file (PLAID or COMPD)
  - visualize the loaded (or generated) layout `*.csv` file in a separate window, where every material (control or drug compound) is represented as a square. The visualization can be enhanced by also loading `*.dzn` file (this enables representing the controls as circles)

A functionality for the future:

  - a separate window to help the user generate the `*.dzn` file

It should be noted that due to some limitations of `tkinter`


## Before launch

  1. Install Python (3.12+ recommended) with `numpy` (2.1+ recommended) and `matplotlib` (3.10+ recommended) libraries.
  2. Download [PLAID](https://github.com/pharmbio/plaid) and/or COMPD model files (`*.mzn`) and copy them to a desired location. The link to COMPD will be available at a later date
  3. Install [MiniZinc](https://www.minizinc.org/)
  4. Configure paths to MiniZinc, PLAID and/or COMPD model files in the `paths.ini` file
  5. Launch `main.py` (e.g. by using the command `python3 main.py`)

## Credits

The project is developed by [Ramiz Gindullin](https://orcid.org/0000-0003-4947-9641)

## License
COMPD has an Apache 2.0 LICENSE. The COMPD team accepts no responsibility or liability for the use of COMPD or any direct or indirect damages arising out of its use.
