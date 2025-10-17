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
# Description:  Various supplementary utilities related to reading the config file
#
# Authors: Ramiz GINDULLIN (ramiz.gindullin@it.uu.se)
# Version: 1.0
# Last Revision: October 2025
#


import os
import logging

from typing import Tuple

from models.constants import Performance, Validation, PathsIni, Visualization


logger = logging.getLogger(__name__)


def load_paths_config() -> Tuple[str, str, str, str, str]:
    """Read and parse paths.ini configuration file.
    
    Returns:
        Tuple of (minizinc_path, plaid_path, compd_path, plaid_mpc_path, compd_mpc_path)
        
    Raises:
        FileNotFoundError: If paths.ini file cannot be read
    """
    logger.debug("Loading configuration from paths.ini")
    try:
        with open('config/paths.ini', 'r') as file:
            paths_array = file.readlines()
    except (FileNotFoundError, IOError) as e:
        logger.error(f"Cannot read paths.ini file: {e}")
        raise FileNotFoundError("Could not read paths.ini file. Please ensure it exists and is readable.") from e
    
    # Initialize variables with defaults
    minizinc_path = plaid_path = compd_path = plaid_mpc_path = compd_mpc_path = ""
    
    for line in paths_array:
        line_clean = line.strip()
        if line_clean.startswith(PathsIni.MINIZINC_PREFIX):
            minizinc_path = line_clean[PathsIni.MINIZINC_OFFSET:].strip('"\'')
        elif line_clean.startswith(PathsIni.PLAID_PREFIX):
            plaid_path = line_clean[PathsIni.PLAID_OFFSET:].strip('"\'')
        elif line_clean.startswith(PathsIni.COMPD_PREFIX):
            compd_path = line_clean[PathsIni.COMPD_OFFSET:].strip('"\'')
        elif line_clean.startswith(PathsIni.PLAID_MPC_PREFIX):
            plaid_mpc_path = line_clean[PathsIni.PLAID_MPC_OFFSET:].strip('"\'')
        elif line_clean.startswith(PathsIni.COMPD_MPC_PREFIX):
            compd_mpc_path = line_clean[PathsIni.COMPD_MPC_OFFSET:].strip('"\'')
    
    logger.info("Configuration loaded successfully from paths.ini")
    return minizinc_path, plaid_path, compd_path, plaid_mpc_path, compd_mpc_path


