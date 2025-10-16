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
# Description:  Various supplementary utilities for the simple GUI for MiniZinc microplates models
#
# Authors: Ramiz GINDULLIN (ramiz.gindullin@it.uu.se)
# Version: 1.0
# Last Revision: October 2025
#


import os
import os.path
import subprocess
import sys
import ast
import re
import time
import logging
from functools import lru_cache
import numpy as np
import tkinter as tk
from typing import List, Dict, Tuple, Union, Sequence

# Configure logging for utility module
logger = logging.getLogger(__name__)

# Constants for coordinate transformation
LETTERS_CAPITAL: List[str] = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K",
                              "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
LETTERS_LOWERCASE: List[str] = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k",
                                "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]


@lru_cache(maxsize=2048)
def transform_coordinate(well: str) -> List[int]:
    """Transform coordinates from standard csv-file format.
    
    Args:
        well: Well coordinate (e.g., 'A1', 'B3')
        
    Returns:
        List of [row, col] coordinates (0-indexed)
        
    Example:
        transform_coordinate('A1') returns [0, 0]
        transform_coordinate('B3') returns [1, 2]
    
    Note:
        This function is cached for performance when processing repeated well coordinates.
    """
    row = 0
    for i in range(len(well)):
        symbol = well[i]
        if symbol in LETTERS_CAPITAL:
            row += LETTERS_CAPITAL.index(symbol)
        elif symbol in LETTERS_LOWERCASE:
            row = LETTERS_LOWERCASE.index(symbol) + (row + 1) * len(LETTERS_LOWERCASE)
        else:
            col = int(well[i:]) - 1
            logger.debug(f"Coordinate transform: {well} -> [{row}, {col}]")
            return [row, col]


def read_csv_file(file_path: str) -> List[str]:
    """Read CSV file and return all lines except header.
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        List of lines from CSV file (excluding header)
        
    Raises:
        FileNotFoundError: If file cannot be read
    """
    try:
        with open(file_path, 'r') as file:
            layout_text_array = file.readlines()
        line_count = len(layout_text_array) - 1  # Exclude header
        logger.info(f"CSV file loaded: {file_path}, {line_count} data lines")
        return layout_text_array[1:]  # Remove header
    except (FileNotFoundError, IOError) as e:
        logger.error(f"Failed to read CSV file: {file_path}, error: {e}")
        raise FileNotFoundError(f"Could not read CSV file: {file_path}") from e


def scan_dzn(file_path: str) -> Tuple[str, str, str]:
    """Scan DZN file and extract parameters.
    
    Args:
        file_path: Path to the DZN file
        
    Returns:
        Tuple of (cols, rows, control_names)
        
    Raises:
        FileNotFoundError: If file cannot be read
        ValueError: If DZN file is corrupted or invalid
    """
    rows_str = 'num_rows'  # > num_rows = 16; %% height
    cols_str = 'num_cols'  # > num_cols = 24; %% width
    ctrs_str = 'control_names'
    nb_ctrs_str = 'num_controls'

    logger.debug(f"Scanning DZN file: {file_path}")
    
    try:
        with open(file_path, 'r') as file:
            dzn_text = file.read()
    except (FileNotFoundError, IOError) as e:
        logger.error(f"Cannot read DZN file: {file_path}, error: {e}")
        raise FileNotFoundError(f"Could not read DZN file: {file_path}") from e

    # Remove spaces, tabs and newlines to ensure a more robust scan
    dzn_text = re.sub(r"[\n\t\s]*", "", dzn_text)

    rows = retrieve_dzn_param(dzn_text, rows_str)
    cols = retrieve_dzn_param(dzn_text, cols_str)
    ctrs = retrieve_dzn_param(dzn_text, ctrs_str)
    nb_ctrs = retrieve_dzn_param(dzn_text, nb_ctrs_str)

    ctrs = ctrs.replace(nb_ctrs_str, nb_ctrs)

    if rows.isnumeric() and cols.isnumeric():
        controls = str(parse_control_string(ctrs))
        logger.info(f"DZN parsed: {cols}x{rows} plate, controls: {controls}")
        return cols, rows, controls
    else:
        logger.error(f"Invalid DZN file - non-numeric dimensions: rows={rows}, cols={cols}")
        raise ValueError('Corrupt dzn file - invalid numeric values')


def retrieve_dzn_param(text: str, param_string: str) -> str:
    """Extract parameter value from DZN text.
    
    Args:
        text: DZN file content as string
        param_string: Parameter name to search for
        
    Returns:
        Parameter value as string
        
    Raises:
        ValueError: If parameter not found in text
    """
    param_string += '='
    pos = text.find(param_string)

    if pos == -1:
        logger.error(f"DZN parameter not found: {param_string}")
        raise ValueError(f'Cannot find dzn parameter ({param_string})')

    pos += len(param_string)
    param_res = text[pos:text.find(';', pos)]
    logger.debug(f"DZN parameter extracted: {param_string[:-1]} = {param_res}")

    return param_res


def transform_concentrations_to_alphas(concentration_list: Sequence[Union[str, float, int]]) -> Dict[Union[str, float, int], float]:
    """Transform concentration list to alpha values for visualization.
    
    Args:
        concentration_list: List of concentration values
        
    Returns:
        Dictionary mapping concentrations to alpha values (0.3 to 1.0)
        
    Examples:
        - Single concentration: returns {concentration: 1.0}
        - Multiple concentrations: returns evenly spaced alpha values
    """
    min_alpha = 0.3
    max_alpha = 1
    num_alpha = len(concentration_list)
    if num_alpha == 1:
        return {concentration_list[0]: 1}
    alphas = {}
    for i in range(len(concentration_list)):
        alphas[concentration_list[i]] = min(
            [1, min_alpha + (max_alpha - min_alpha) * i / (num_alpha - 1)])
    logger.debug(f"Alpha mapping generated for {num_alpha} concentrations")
    return alphas


def to_number_if_possible(value: str) -> Union[int, float, str]:
    """Convert string to number if possible, otherwise return original value.
    
    Args:
        value: String value to convert
        
    Returns:
        Integer, float, or original string value
    """
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value


def read_paths_ini_file() -> Tuple[str, str, str, str, str]:
    """Read and parse paths.ini configuration file.
    
    Returns:
        Tuple of (minizinc_path, plaid_path, compd_path, plaid_mpc_path, compd_mpc_path)
        
    Raises:
        FileNotFoundError: If paths.ini file cannot be read
    """
    logger.debug("Loading configuration from paths.ini")
    try:
        with open('paths.ini', 'r') as file:
            paths_array = file.readlines()
    except (FileNotFoundError, IOError) as e:
        logger.error(f"Cannot read paths.ini file: {e}")
        raise FileNotFoundError("Could not read paths.ini file. Please ensure it exists and is readable.") from e
    
    # Initialize variables with defaults
    minizinc_path = plaid_path = compd_path = plaid_mpc_path = compd_mpc_path = ""
    
    for line in paths_array:
        line_clean = line.strip()
        if line_clean.startswith('minizinc_path = '):
            minizinc_path = line_clean[16:].strip('"\'')
        elif line_clean.startswith('plaid_path = '):
            plaid_path = line_clean[13:].strip('"\'')
        elif line_clean.startswith('compd_path = '):
            compd_path = line_clean[13:].strip('"\'')
        elif line_clean.startswith('plaid_mpc_path = '):
            plaid_mpc_path = line_clean[17:].strip('"\'')
        elif line_clean.startswith('compd_mpc_path = '):
            compd_mpc_path = line_clean[17:].strip('"\'')
    
    logger.info("Configuration loaded successfully from paths.ini")
    return minizinc_path, plaid_path, compd_path, plaid_mpc_path, compd_mpc_path


def run_cmd(minizinc_path: str, solver_config: str, model_file: str, data_file: str) -> str:
    """Execute MiniZinc command and return output.
    
    Args:
        minizinc_path: Path to MiniZinc executable
        solver_config: Solver configuration file path
        model_file: Model file path (.mzn)
        data_file: Data file path (.dzn)
        
    Returns:
        Command output as string
        
    Raises:
        RuntimeError: If MiniZinc command execution fails
    """
    if sys.platform.startswith('win'):
        cmd = [minizinc_path, solver_config, model_file, data_file]
    else:
        cmd = [minizinc_path + ' --param-file-no-push ' +
               solver_config + ' ' + model_file + ' ' + data_file]
    
    print('command:', cmd)
    logger.info(f"Executing MiniZinc: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    
    start_time = time.time()
    
    try:
        process = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, errors = process.communicate()
        output = output.decode('utf-8').strip()
        errors = errors.decode('utf-8').strip()
        process.kill()
    except (subprocess.SubprocessError, OSError) as e:
        logger.error(f"MiniZinc execution failed: {e}")
        raise RuntimeError(f"Failed to execute MiniZinc command: {e}") from e

    elapsed = time.time() - start_time
    
    if errors:
        print(errors)  # User sees warnings/errors
        logger.warning(f"MiniZinc stderr: {errors}")
    if output:
        print(output)  # User sees output
        logger.debug(f"MiniZinc stdout: {output}")

    print(f'MiniZinc completed in {elapsed:.1f} seconds')
    logger.info(f"MiniZinc execution completed in {elapsed:.1f} seconds")

    return output


def extract_csv_text(text: str) -> List[str]:
    """Extract CSV content from MiniZinc output.
    
    Args:
        text: MiniZinc output text
        
    Returns:
        List of CSV lines extracted from output
    """
    s, e = 0, 0
    lines = text.split('\n')
    for i in range(len(lines)):
        if lines[i] == 'plateID,well,cmpdname,CONCuM,cmpdnum,VOLuL':
            s = i
        if lines[i][:17] == 'criteria function' or lines[i][:1] == '%' or lines[i] == '----------' or lines[i] == 'finished':
            if e <= s:
                e = i
    
    extracted_lines = [line + '\n' for line in lines[s:e]]
    logger.debug(f"Extracted {len(extracted_lines)} CSV lines from MiniZinc output")
    return extracted_lines


def parse_control_string(control_string: str) -> str:
    """Parse control string and generate control names.
    
    Args:
        control_string: String containing control definitions
        
    Returns:
        Stringified list of parsed control names, or '[]' if parsing fails.
        Use ast.literal_eval() to convert back to a Python list.
    """
    control_names = []
    logger.debug(f"Parsing control string: {control_string[:50]}...")
    
    for section in control_string.split('++'):
        if section.find('..') == -1:
            try:
                control_names.extend(ast.literal_eval(section))
            except (ValueError, SyntaxError):
                logger.warning(f"Failed to parse control section: {section}")
                return '[]'
        else:
            try:
                section = section[1:-1]

                pos_index_s = section.find('\\(')
                pos_index_e = section.find(')', pos_index_s)

                index_str = section[pos_index_s + 2:pos_index_e]

                pos_iin = section.find('|' + index_str + 'in')
                pos_nii = pos_iin + len(index_str) + 3
                pos_dot = section.find('..')

                i_start = int(section[pos_nii:pos_dot])
                i_end = int(section[pos_dot + 2:])

                for i in range(i_start, i_end + 1):
                    control_names.append(
                        section[1:pos_index_s] + str(i) + section[pos_index_e + 1:pos_iin-1])
            except (ValueError, IndexError):
                logger.warning(f"Failed to parse complex control section: {section}")
                return '[]'
    
    logger.debug(f"Parsed {len(control_names)} control names")
    return str(control_names)


def callback(P: str) -> bool:
    """Validation callback for numeric input.
    
    Args:
        P: Input string to validate
        
    Returns:
        True if input is valid (digits or empty), False otherwise
    """
    return str.isdigit(P) or P == ""


def path_show(path: str, label_object: tk.Label) -> None:
    """Display truncated path in label widget.
    
    Args:
        path: File path to display
        label_object: Tkinter label widget to update
    """
    if len(path) >= 20:
        prefix = '...'
    else:
        prefix = ''
    display_text = 'File loaded: ' + prefix + path[-20:]
    label_object.config(text=display_text)
    logger.debug(f"UI updated with path: {display_text}")


class ToolTip(object):
    """Tooltip widget for displaying help text on hover.
    
    Source: squareRoot17, https://stackoverflow.com/questions/20399243/display-message-when-hovering-over-something-with-mouse-cursor-in-python
    """
    
    def __init__(self, widget: tk.Widget) -> None:
        """Initialize tooltip for widget.
        
        Args:
            widget: Tkinter widget to attach tooltip to
        """
        self.widget = widget
        self.tipwindow: tk.Toplevel = None
        self.id: str = None
        self.x: int = 0
        self.y: int = 0

    def showtip(self, text: str) -> None:
        """Display text in tooltip window.
        
        Args:
            text: Text to display in tooltip
        """
        self.text = text
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 5
        y = y + cy + self.widget.winfo_rooty() + 5
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background="#ffffe0", fg="black", relief=tk.SOLID, borderwidth=1,
                         font=("tahoma", "12", "normal"))
        label.pack(ipadx=1)

    def hidetip(self) -> None:
        """Hide the tooltip window."""
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()


def CreateToolTip(widget: tk.Widget, text: str) -> None:
    """Create a tooltip for the given widget.
    
    Args:
        widget: Tkinter widget to attach tooltip to
        text: Help text to display on hover
    """
    toolTip = ToolTip(widget)

    def enter(event):
        toolTip.showtip(text)

    def leave(event):
        toolTip.hidetip()
    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)