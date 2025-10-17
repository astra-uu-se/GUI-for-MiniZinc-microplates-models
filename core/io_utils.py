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

from typing import List

from models.constants import Performance, Validation, PathsIni, Visualization


logger = logging.getLogger(__name__)


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

