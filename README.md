# GUI-for-MiniZinc-microplates-models
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

A simple GUI to streamline the workflow for using MiniZinc models, which generate microplate layouts. Specifically, it is designed to be compatible with PLAID (https://github.com/pharmbio/plaid) and other future projects.


## Requirements

The tool is developed in Python 3.12.6, and it requires the installation of `numpy` (version 2.1.1 was used) and `matplotlib` (version 3.10.6 was used) libraries.

Earlier versions of Python and the libraries are likely to work, but it is not guaranteed.

The GUI elements are developed by using the `tkinter` library. It is lightweight and is a Python standard library, though it is somewhat rigid compared to alternatives, such as PyQt6. Thus, there are some limitations on what is possible to accomplish

## Description

This tool allows a user to:

  - generate and save a `*.dzn` file with a GUI in a separate window (similar to [PLAID web-page](https://plaid.pharmb.io/))
  - load an existing `*.dzn` file (an input data file, it is an optional step)
  - load an existing `*.csv` file (a microplate layout file, i.e. the results of executing the model)
  - launch MiniZinc, which will take the loaded input file and a selected model file (PLAID or another one)
  - visualize the loaded (or generated) layout `*.csv` file in a separate window, where every material (control or drug compound) is represented as a square. The visualization can be enhanced by also loading `*.dzn` file (this enables representing the controls as circles). Note that it automatically saves the figures as `*.png` files

Future plans:

  - using a colormap with a larger number (at least 50) of distinct colors

Limitations:
  - for simplicity of development, it is not possible to select custom names and locations for saved `*.csv` and `*.png` files. We use the name and location of the `*.dzn` file
  - the project currently uses the `tab20` colormap, i.e. 20 distinct colors, meaning that the project repeats the same colors when the number of materials is larger than 20


## Before launch

  1. Install Python (3.12+ recommended) with `numpy` (2.1+ recommended) and `matplotlib` (3.10+ recommended) libraries
  2. Download [PLAID](https://github.com/pharmbio/plaid) and/or other model files (`*.mzn`) and copy them to a desired location
  3. Install [MiniZinc](https://www.minizinc.org/)
  4. Configure paths to MiniZinc, PLAID and/or another model files in the `paths.ini` file
  5. (optional) Update solver configuration files for PLAID and/or another model (by default, `plaid_default.mpc` and `compd_default.mpc`, respectively) if you want to switch a solver or change the number of threads used by the solver. You can create additional solver configuration files as well (e.g. if you want to try different settings). Additional notes:
     
       - PLAID can only work with GeCode
       - Non-PLAID layout quality might depend on the timeout, i.e. if you are unsatisfied with a solution, you can try to increase the timeout from 180s to e.g. 300s
         
  7. Launch `main.py` (e.g. by using the command `python3 main.py`)

## Notes about generating the model file

If an option to generate a `*.dzn` file is selected, then the user must fill in fields listing all the compounds and all their concentrations.

We use the format of Python dictionaries of `{'Material1': [number_of_replicates1, 'Concentration11',...], 'Material2': [number_of_replicates2, 'Concentration21',...], ...}`

Example 1: `{'Drug1': [5, 'Concentration 1', 'Concentration 2'], 'Drug2': [10, '0.1', '0.5, '10']}`, which means that we will have:
  - `Drug1` in concentrations `Concentration 1` and `Concentration 2` (5 replicates each) and
  - `Drug2` in concentrations `0.1`, `0.5` and `10` (10 replicates each).

Example 2: `{'Control1': [5, 'Concentration 1', 'Concentration 2'], 'Control2': [10, '100'], 'Control3': [3, '100']},` where we have three types of controls:
  - `Control1` in concentrations `Concentration 1` and `Concentration 2` (5 replicates each),
  - `Control2` in concentration `100` (10 replicates), and
  - `Control3` in concentration `100` (10 replicates).

As you can see, the dictionary format allows us to use various number of drugs/controls, where each drug/control can have its own number of replicates and/or the list concentrations. The idea is to have a simple but flexible format for the user to use no matter the configuration of materials and concentrations.

I recommend to write down the list of materials in a separate editor and then copy it in the entry field.

## Credits

The project is developed by [Ramiz Gindullin](https://orcid.org/0000-0003-4947-9641)

## License
The project has an Apache 2.0 LICENSE. The author accepts no responsibility or liability for the use of the project or any direct or indirect damages arising out of its use.
