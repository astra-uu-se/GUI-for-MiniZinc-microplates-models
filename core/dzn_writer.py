# Copyright 2025 Ramiz Gindullin.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Description:  DZN text generation logic
#
# Authors: Ramiz GINDULLIN (ramiz.gindullin@it.uu.se)
# Version: 1.0
# Last Revision: October 2025
#


import logging
from typing import Dict, List


logger = logging.getLogger(__name__)


def build_dzn_text(
    num_rows: str,
    num_cols: str,
    inner_empty_edge: bool,
    size_empty_edge: str,
    size_corner_empty_wells: str,
    horizontal_cell_lines: str,
    vertical_cell_lines: str,
    flag_allow_empty_wells: bool,
    flag_concentrations_on_different_rows: bool,
    flag_concentrations_on_different_columns: bool,
    flag_replicates_on_different_plates: bool,
    flag_replicates_on_same_plate: bool,
    compounds_dict: Dict[str, List],
    controls_dict: Dict[str, List],
) -> str:
    """
    Construct a detailed DZN (Data Specification File) string representing the layout and parameters
    for a MiniZinc optimization model, based on the provided user-defined input parameters and data.

    This method generates the textual content of a .dzn file, which encodes various configuration
    settings and experimental parameters for the layout generation problem. It produces a string
    formatted according to MiniZinc's data syntax, including arrays and variable assignments.

    Parameters
    ----------
    num_rows : str
        The number of rows in the plate layout, as a string (e.g., '8' for an 8x12 plate).
    num_cols : str
        The number of columns in the plate layout, as a string (e.g., '12' for an 8x12 plate).
    inner_empty_edge : bool
        Whether to allow inner empty edges within the layout, affecting layout padding.
    size_empty_edge : str
        The size or distance of the empty edge around the plate layout.
    size_corner_empty_wells : str
        The size or spacing of empty wells at the corners.
    horizontal_cell_lines : str
        Configuration string defining whether horizontal cell lines are present.
    vertical_cell_lines : str
        Configuration string defining whether vertical cell lines are present.
    flag_allow_empty_wells : bool
        Whether empty wells are permitted in the layout.
    flag_concentrations_on_different_rows : bool
        Whether concentrations can vary across different rows.
    flag_concentrations_on_different_columns : bool
        Whether concentrations can vary across different columns.
    flag_replicates_on_different_plates : bool
        Whether replicates are allowed on different plates.
    flag_replicates_on_same_plate : bool
        Whether replicates are allowed within the same plate.
    compounds_dict : dict
        Dictionary where keys are compound names and values are lists containing
        replicate count, concentration, and other properties, e.g.,
        {'DrugA': [3, '0.1'], 'DrugB': [2, '0.5']}.
    controls_dict : dict
        Similar structure as compounds_dict, but for control samples, e.g.,
        {'pos': [2, '100'], 'neg': [2, '0']}.

    Returns
    -------
    str
        The generated DZN file content as a string. It contains all the variable assignments
        and array data structured for MiniZinc, with proper syntax. Quotes within string data are
        replaced with double quotes for safety. This string can be written directly to a .dzn file.

    Notes
    -----
    - This method mimics the exact string formatting and layout as the original UI code, ensuring
      consistent output for testing and reproducibility.
    - Arrays are formatted with spacing and brackets, matching MiniZinc conventions.
    - Boolean flags are converted to lowercase ('true'/'false') as per MiniZinc.
    - The method is designed for internal use; assumes all inputs are pre-validated.
    - No file I/O occurs here; the string should be saved externally by caller.

    Example
    -------
    >>> dzn_text = builder.build_dzn_text(
    ...     num_rows='8',
    ...     num_cols='12',
    ...     inner_empty_edge=False,
    ...     size_empty_edge='1',
    ...     size_corner_empty_wells='2',
    ...     horizontal_cell_lines='true',
    ...     vertical_cell_lines='true',
    ...     flag_allow_empty_wells=True,
    ...     flag_concentrations_on_different_rows=False,
    ...     flag_concentrations_on_different_columns=False,
    ...     flag_replicates_on_different_plates=True,
    ...     flag_replicates_on_same_plate=True,
    ...     compounds_dict={'DrugA': [3, '0.1'], 'DrugB': [2, '0.5']},
    ...     controls_dict={'pos': [2, '100'], 'neg': [2, '0']}
    ... )
    """

    # Start constructing DZN
    compounds = compounds_dict
    control_compounds = controls_dict
    
    dzn_txt = ''

    # Write basic values
    dzn_txt += 'num_rows = ' + num_rows + ';\n'
    dzn_txt += 'num_cols = ' + num_cols + ';\n\n'

    if inner_empty_edge == False:  # no printing for PLAID
        dzn_txt += 'inner_empty_edge_input = ' + str(inner_empty_edge).lower() + ';\n'
    dzn_txt += 'size_empty_edge = ' + size_empty_edge + ';\n'
    dzn_txt += 'size_corner_empty_wells = ' + size_corner_empty_wells + ';\n\n'

    dzn_txt += 'horizontal_cell_lines = ' + horizontal_cell_lines + ';\n'
    dzn_txt += 'vertical_cell_lines = ' + vertical_cell_lines + ';\n\n'

    dzn_txt += 'allow_empty_wells = ' + str(flag_allow_empty_wells).lower() + ';\n'
    dzn_txt += 'concentrations_on_different_rows = ' + str(flag_concentrations_on_different_rows).lower() + ';\n'
    dzn_txt += 'concentrations_on_different_columns = ' + str(flag_concentrations_on_different_columns).lower() + ';\n'
    dzn_txt += 'replicates_on_different_plates = ' + str(flag_replicates_on_different_plates).lower() + ';\n'
    dzn_txt += 'replicates_on_same_plate = ' + str(flag_replicates_on_same_plate).lower() + ';\n\n'

    # Process compounds data
    nb_compounds = 0
    compound_concentrations: List[int] = []
    compound_names: List[str] = []
    compound_replicates: List[int] = []

    for drug in compounds:
        nb_compounds += 1
        compound_names.append(str(drug))
        compound_replicates.append(compounds[drug][0])
        compounds[drug] = [str(x) for x in compounds[drug][1:]]
        compound_concentrations.append(len(compounds[drug]))

    dzn_txt += 'compounds = ' + str(nb_compounds) + ';\n'
    dzn_txt += 'compound_concentrations = ' + str(compound_concentrations) + ';\n'
    dzn_txt += 'compound_names = ' + str(compound_names) + ';\n'
    dzn_txt += 'compound_replicates = ' + str(compound_replicates) + ';\n'
    dzn_txt += 'compound_concentration_names = \n['
    
    drug1 = True
    for drug in compounds:
        if drug1:
            drug1 = False
        else:
            dzn_txt += ' '
        dzn_txt += '| ' + str(compounds[drug])[1:-1]
        for i in range(len(compounds[drug]), max(compound_concentrations)):
            dzn_txt += ", ''"
        dzn_txt += '\n'
    dzn_txt += '|];\n'
    dzn_txt += 'compound_concentration_indicators = [];\n\n'

    dzn_txt += 'combinations = 	0;\ncombination_names = [];\ncombination_concentration_names = [];\ncombination_concentrations = 0;\n\n'

    # Process controls data
    nb_controls = 0
    control_concentrations: List[int] = []
    control_names_str: List[str] = []
    control_replicates: List[int] = []

    for control in control_compounds:
        nb_controls += 1
        control_names_str.append(str(control))
        control_replicates.append(control_compounds[control][0])
        control_compounds[control] = [str(x) for x in control_compounds[control][1:]]
        control_concentrations.append(len(control_compounds[control]))

    dzn_txt += 'num_controls = ' + str(nb_controls) + ';\n'
    dzn_txt += 'control_concentrations = ' + str(control_concentrations) + ';\n'
    dzn_txt += 'control_names = ' + str(control_names_str) + ';\n'
    dzn_txt += 'control_replicates = ' + str(control_replicates) + ';\n'
    dzn_txt += 'control_concentration_names = \n['
    
    control1 = True
    for control in control_compounds:
        if control1:
            control1 = False
        else:
            dzn_txt += ' '
        dzn_txt += '| ' + str(control_compounds[control])[1:-1]
        for i in range(len(control_compounds[control]), max(control_concentrations)):
            dzn_txt += ", ''"
        dzn_txt += '\n'
    dzn_txt += '|];\n\n'

    dzn_txt = dzn_txt.replace("'", '"')
    
    logger.debug(f"DZN content generated: {len(dzn_txt)} characters")
    return dzn_txt, control_names_str
