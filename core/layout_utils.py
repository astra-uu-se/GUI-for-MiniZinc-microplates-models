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
# Description:  Various supplementary utilities related to visualization of layouts
#
# Authors: Ramiz GINDULLIN (ramiz.gindullin@it.uu.se)
# Version: 1.0
# Last Revision: October 2025
#

import logging

from functools import lru_cache
from typing import List, Sequence, Union, Dict

from models.constants import Alphabet, Performance, Visualization


# Configure logging for utility module
logger = logging.getLogger(__name__)


@lru_cache(maxsize=Performance.COORDINATE_CACHE_SIZE)
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
        if symbol in Alphabet.LETTERS_CAPITAL:
            row += Alphabet.LETTERS_CAPITAL.index(symbol)
        elif symbol in Alphabet.LETTERS_LOWERCASE:
            row = Alphabet.LETTERS_LOWERCASE.index(symbol) + (row + 1) * len(Alphabet.LETTERS_LOWERCASE)
        else:
            col = int(well[i:]) - 1
            logger.debug(f"Coordinate transform: {well} -> [{row}, {col}]")
            return [row, col]


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
    min_alpha = Visualization.ALPHA_MIN
    max_alpha = Visualization.ALPHA_MAX
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


