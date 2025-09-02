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
# Description:  A simple GUI for MiniZinc microplates models
#
# Authors: Ramiz GINDULLIN (ramiz.gindullin@it.uu.se)
# Version: 1.0
# Last Revision: September 2025
#


import os
import os.path
import subprocess
import sys
import re
import numpy as np

letters_capital = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
letters_inline  = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]

# transform coordinates from a standard csv-file. i.e. `A1` will become (1,1) coordinate
def transform_coordinate(well):
    row = 0
    for i in range(len(well)):
        symbol = well[i]
        if symbol in letters_capital:
            row += letters_capital.index(symbol)
        elif symbol in letters_inline:
            row = letters_inline.index(symbol) + (row + 1) * len(letters_inline)
        else:
            col = int(well[i:]) - 1
            return [row, col]

# load the csv file as a list of lines (except header)
def read_csv_file(file_path):
    file = open(file_path, 'r')
    layout_text_array = file.readlines()
    #print(layout_text_array[0:10])
    layout_text_array = layout_text_array[1:]
    file.close()
    return layout_text_array

# scan the dzn file and extract the number of rows, columns and the list of control names
def scan_dzn(file_path):
    rows_str = 'num_rows' # > num_rows = 16; %% height
    cols_str = 'num_cols' # > num_cols = 24; %% width
    ctrs_str = 'control_names'
    
    file = open(file_path, 'r')
    dzn_text = file.read()
    file.close()
    
    dzn_text = re.sub(r"[\n\t\s]*", "", dzn_text) # remove spaces, tabs and newlines to ensure a more robust scan
    
    rows = retrieve_dzn_param(dzn_text,rows_str)
    cols = retrieve_dzn_param(dzn_text,cols_str)
    ctrs = retrieve_dzn_param(dzn_text,ctrs_str)
    
    if rows.isnumeric() & cols.isnumeric():
        return cols, rows, str(parse_control_string(ctrs))
    else:
        print(text)
        raise Exception('Corrupt dzn file')
    
# a helper function that scans the dzn file for a specific parameter
def retrieve_dzn_param(text,param_string):
    param_string += '='
    pos = text.find(param_string)
    
    if pos == -1:
        raise Exception('Can not find dzn parameter (' + param_string + ')')
        sys.exit('Corrupt dzn file')
    
    pos += len(param_string)
    param_res = text[pos:text.find(';',pos)]
    
    return param_res

# if we have 1  concentration then there is only one alpha-channel value: [1]
# if we have 2  concentration then there are 2: [0.3, 1]
# if we have 3+ concentration then there we get a list: [0.3, ..., 1] with eaually spaced values
def transform_concentrations_to_alphas(concentration_list):
    min_alpha = 0.3
    max_alpha = 1
    num_alpha = len(concentration_list)
    if num_alpha == 1:
        return {concentration_list[0]: 1}
    alphas = {}
    for i in range(len(concentration_list)):
        alphas[concentration_list[i]] = min([1,min_alpha + (max_alpha - min_alpha) * i / (num_alpha - 1)])
    return alphas

# self-explanatory
def to_int_if_possible(value):
    try:
        return int(value)
    except:
        return value

# extract relevant information from the ini file
def read_paths_ini_file():
    file = open('paths.ini','r')
    paths_array = file.readlines()
    for line in paths_array:
        line_clean = line.strip()
        if line_clean[:16] == 'minizinc_path = ':
            minizinc_path = line_clean[17:-1]
        if line_clean[:13] == 'plaid_path = ':
            plaid_path    = line_clean[14:-1]
        if line_clean[:13] == 'compd_path = ':
            compd_path    = line_clean[14:-1]
        if line_clean[:17] == 'plaid_mpc_path = ':
            plaid_mpc_path    = line_clean[18:-1]
        if line_clean[:17] == 'compd_mpc_path = ':
            compd_mpc_path    = line_clean[18:-1]
    file.close()
    return minizinc_path, plaid_path, compd_path, plaid_mpc_path, compd_mpc_path

# launch minizinc and solve the problem instance
def run_cmd(minizinc_path, solver_config, model_file, data_file):
    cmd = minizinc_path + ' --param-file-no-push ' + solver_config + ' ' + model_file  + ' ' + data_file
    process = subprocess.Popen([cmd], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #retval = process.wait()
    output, _ = process.communicate()
    output = output.decode('utf-8').strip()
    process.kill()
    return output

# extract the layout from the Minizinc output
def extract_csv_text(text):
    s, e = 0, 0
    lines = text.split('\n')
    for i in range(len(lines)):
        if lines[i] == 'plateID,well,cmpdname,CONCuM,cmpdnum,VOLuL':
            s = i
        if lines[i][:17] == 'criteria function' or lines[i][:1] == '%' or lines[i] == '----------' or lines[i] == 'finished':
            if e <= s:
                e = i
    return [line + '\n' for line in lines[s:e]]




# INPORTANT: This function is generated by Google Gemini
def parse_control_string(control_string):
  """
  Transforms a string with a generalized format like ...(REDACTED)...
  into a list of strings, such as `['Neg1', 'Neg2', 'badctrl3', ..., 'badctrl16', 'ctrl1', ..., 'ctrl8', 'DMSO']`.
  The function handles sections with explicit names and sections with ranged patterns, separated by '++'.
  It also suppresses any SyntaxWarning related to escape sequences by using raw strings in regex patterns and docstrings.

  Args:
    control_string: The input string.

  Returns:
    A list of unique control names.
  """
  sections = control_string.split('++')
  all_control_names = []

  for section in sections:
    if "|iin" in section:
      # Ranged pattern section - using raw string to suppress SyntaxWarning
      match = re.search(r'\["(.*?)\\\(i\)\"\|iin(\d+)\.\.(\d+)\]', section)
      if match:
        prefix = match.group(1)
        start = int(match.group(2))
        end = int(match.group(3))
        for i in range(start, end + 1):
          all_control_names.append(f'{prefix}{i}')
    else:
      # Explicit names section
      names = re.findall(r'"(.*?)"', section)
      all_control_names.extend(names)

  unique_control_names = list(set(all_control_names))
  return unique_control_names