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
# Description:  Various supplementary utilities related to I/O operations
#
# Authors: Ramiz GINDULLIN (ramiz.gindullin@it.uu.se)
# Version: 1.0
# Last Revision: October 2025
#


import os
import logging

import tkinter as tk

from typing import List, Union, Tuple

from core.layout_utils import transform_index, transform_coordinate, find_all_plates_concentrations
from models.constants import Performance, Alphabet, Validation, PathsIni, Visualization, FileTypes, PlaterFormat
from models.dto import CSVConversionRequest


logger = logging.getLogger(__name__)


def write_csv_file(csv_text: List[str]) -> Union[int,str]:
    path = tk.filedialog.asksaveasfilename(
        defaultextension=".csv", filetypes=FileTypes.CSV_FILES)

    print(f"Saving results to: {path}")
    logger.info(f"User selected CSV save path: {path}")

    if path is None or path == '':
        # User cancelled - restore original state
        logger.info("User cancelled CSV save - operation aborted")
        return -1

    # Use context manager for file writing
    try:
        with open(path, 'w') as csv_file:
            # Clean csv_text and ensure that there are always new line breaks
            csv_text = [x.strip() + '\n' for x in csv_text]
            
            # Write the cleaned text into the file
            csv_file.writelines(csv_text)
        
        print(f"CSV saved successfully: {path}")
        logger.info(f"CSV file saved: {path}, {len(csv_text)} lines")
    except (IOError, OSError) as e:
        logger.error(f"CSV write failed: {path}, error: {e}")
        tk.messagebox.showerror("Error", f"Failed to write CSV file: {str(e)}")
        return -2
    
    return path

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
        
        layout_text_array = convert_to_pharmbio_format(layout_text_array)
        
        line_count = len(layout_text_array) - 1  # Exclude header
        logger.info(f"CSV file loaded: {file_path}, {line_count} data lines")
        return layout_text_array[1:]  # Remove header
    except (FileNotFoundError, IOError) as e:
        logger.error(f"Failed to read CSV file: {file_path}, error: {e}")
        raise FileNotFoundError(f"Could not read CSV file: {file_path}") from e
    

def convert_to_pharmbio_format(layout_text_array: List[str]) -> List[str]:
    """Verifies that the uploaded data is in the PharmBio format.
    If it is in the Plater format, the function will convert it into PharmBio format
    
    Args:
        List of lines from CSV file (with header)
        
    Returns:
        List of lines from CSV file (excluding header)
        
    Raises:
        FileNotFoundError: If file cannot be read
    """
    header = layout_text_array[0].strip().split(',')
    
    if len(header) == 6 and [x.strip() for x in header] == ['plateID', 'well', 'cmpdname', 'CONCuM', 'cmpdnum', 'VOLuL']:
        logger.info(f"CSV file (PharmBio format) is recognized")
        return layout_text_array
    else:
        # For simplicity, currently we assume that we can only load a Plater formatted file
        # We also assume that the file in the Plater format will always have 2 matrices: Drugs and Concentrations
        try:
            rows, cols, drugs_matrix, concentrations_matrix = scan_csv_plater_matrices(layout_text_array)
            logger.info(f"CSV file (Plater format) is recognized and parsed")
            
            plater_layout_text_array = []
            
            for i in range(rows):
                for j in range(1,cols):
                    if drugs_matrix[i][j] != '':
                        plater_layout_text_array.append(''.join(['plate_1',
                                                                 ',',
                                                                 drugs_matrix[i][0] + "{:02d}".format(j),
                                                                 ',',
                                                                 drugs_matrix[i][j],
                                                                 ',',
                                                                 concentrations_matrix[i][j],
                                                                 ',',
                                                                 drugs_matrix[i][j] + '_' + concentrations_matrix[i][j],
                                                                 ]))
            
            return plater_layout_text_array
            
        except Exception as e:
            logger.error(f"File could not be read in Plater format, error: {e}")
            tk.messagebox.showerror("Error", f"Failed to load CSV file (Plater format): {str(e)}")
            return
        
def scan_csv_plater_matrices(layout_text_array: List[str]) -> Tuple[int, int, List[str],List[str]]:
    """Scans the CSV file (Plater format) and extracts the layout information about the placement
    of drugs and compounds
    
    Args:
        List of lines from CSV file (with header)
        
    Returns:
        Dimensions of the extracted layout (number of rows and columns)
        Lists of lines corresponding to drug and concentrations
        
    Raises:
        FileNotFoundError: If file cannot be read
    """
    drugs_matrix: List[str] = []
    concentrations_matrix: List[str] = []
    
    cols = len(layout_text_array[0].split(','))
    
    is_drugs = False
    is_concentrations = False
    done_drugs = False
    done_concentrations = False
    matrix_count = 0
    
    for line in layout_text_array:
        if line.strip() == '':
            continue
        elif line == '\n':  # happens on Windows machines (to be tested)
            continue
        
        elements = line.strip().split(',')
        
        if len(elements) != cols:
            raise Exception(f'CSV Plater file has formatting issues (number of column for line {line} is not equal to {cols})')
        
        if is_drugs and elements == ['' for _ in range(cols)]:
            is_drugs = False
            done_drugs = True
        
        if is_concentrations and elements == ['' for _ in range(cols)]:
            is_concentrations = False
            done_concentrations = True
        
        if elements[0] == PlaterFormat.DRUGS_LABEL:
            is_drugs = True
            matrix_count += 1
            e = 'drugs'
        elif is_drugs:
            drugs_matrix.append(elements)
            
        if elements[0] == PlaterFormat.CONCENTRATIONS_LABEL:
            is_concentrations = True
            matrix_count += 1
            e = 'concentrations'
        elif is_concentrations:
            concentrations_matrix.append(elements)
            
        if elements[0] == PlaterFormat.DRUGS_LABEL or elements[0] == PlaterFormat.CONCENTRATIONS_LABEL:
            for i in range(1,cols):
                if elements[i] != str(i):
                    raise Exception(f'CSV Plater file has formatting issues (header line for {e} has incorrect order of columns)')
    
    # When reached EOF
    if is_drugs:
        done_drugs = True
    if is_concentrations:
        done_concentrations = True
    
    # Data verification:
    if matrix_count < 2 or not done_drugs or not done_concentrations:
        raise Exception(f'CSV Plater file has formatting issues (no layout matrix for drugs or concentrations)')
    if matrix_count > 2:
        raise Exception(f'CSV Plater file has formatting issues (too many layout matrices for drugs/concentrations)')
    
    rows = len(drugs_matrix)
    if rows != len(concentrations_matrix):
        print('Drugs:')
        for line in drugs_matrix:
            print(line)
        print('Concentrations:')
        for line in concentrations_matrix:
            print(line)
        raise Exception(f'Drug and concentration layouts of Plater file have mismatched number of rows: {rows} and {len(concentrations_matrix)}')
    
    return rows, cols, drugs_matrix, concentrations_matrix


def path_show(path: str, label_object: tk.Label) -> None:
    """Display truncated path in label widget.
    
    Args:
        path: File path to display
        label_object: Tkinter label widget to update
    """
    if len(path) >= Validation.PATH_DISPLAY_MAX_LENGTH:
        prefix = Validation.PATH_TRUNCATION_PREFIX
    else:
        prefix = ''
    display_text = 'File loaded: ' + prefix + path[-Validation.PATH_DISPLAY_MAX_LENGTH:]
    label_object.config(text=display_text)
    logger.debug(f"UI updated with path: {display_text}")


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
        if lines[i] == '=====UNSATISFIABLE=====':
            raise Exception('The model is unsatisfiable (no layout can not be constructed).\nRecommendation: change the input data to make the solution less restrictive')
        if lines[i] == 'plateID,well,cmpdname,CONCuM,cmpdnum,VOLuL':
            s = i
        if lines[i][:17] == 'criteria function' or lines[i][:1] == '%' or lines[i] == '----------' or lines[i] == 'finished':
            if e <= s:
                e = i
    
    extracted_lines = [line+'\n' for line in lines[s:e]]
    logger.debug(f"Extracted {len(extracted_lines)} CSV lines from MiniZinc output")
    return extracted_lines


def convert_pharmbio_to_plater(input_data: CSVConversionRequest) -> str:
    """Convert CSV-formatted text from PharmBio format to Plater format
    
    Args:
        input_data: CSVConversionRequest() object containing all input data
        
    Returns:
        List of CSV lines compatible with Plater R-package
    """
    rows = int(input_data.rows)
    cols = int(input_data.cols)
    lines = input_data.csv_lines[1:]
    
    plates, _ = find_all_plates_concentrations(lines)
    
    if len(plates) > 1:
        tk.messagebox.showinfo("Information",f"There are {len(plates)} plates. For each plate there will be a corresponding save file dialogue.")
    logger.info(f"Generated {len(plates)} plates to convert and save.")
    
    return [convert_pharmbio_to_plater_plate(CSVConversionRequest(csv_lines=plates[plate],
                                                                  rows=rows,
                                                                  cols=cols)) for plate in plates]


def convert_pharmbio_to_plater_plate(input_data: CSVConversionRequest) -> str:
    """Convert CSV-formatted text from PharmBio format to Plater format
    
    Args:
        input_data: CSVConversionRequest() object containing all input data
        
    Returns:
        List of CSV lines compatible with Plater R-package
    """
    rows = int(input_data.rows)
    cols = int(input_data.cols)
    lines = input_data.csv_lines
    
    drugs_matrix = [['' for j in range(cols+1)] for i in range(rows+1)]
    concentration_matrix = [['0' for j in range(cols+1)] for i in range(rows+1)]
    
    drugs_matrix[0][0] = PlaterFormat.DRUGS_LABEL
    concentration_matrix[0][0] = PlaterFormat.CONCENTRATIONS_LABEL
    
    for i in range(rows):
        drugs_matrix[i+1][0] = transform_index(i)
        concentration_matrix[i+1][0] = transform_index(i)
    
    for i in range(1,cols+1):
        drugs_matrix[0][i] = str(i)
        concentration_matrix[0][i] = str(i)
    
    for line in lines:
        x,y = transform_coordinate(line[0])
        drugs_matrix[x+1][y+1] = line[1]
        concentration_matrix[x+1][y+1] = line[2]
        
    text: str = plater_matrix_to_string(drugs_matrix)
    text += ''.join([',' for _ in range(cols)]) + '\n'
    text += plater_matrix_to_string(concentration_matrix)
    
    return text    


def plater_matrix_to_string(matrix):
    """Convert plater matrix into a string to write
    """
    text: str = ''
    for line in matrix:
        for element in line[:-1]:
            text += element + ','
        text += line[-1] + '\n'
    return text