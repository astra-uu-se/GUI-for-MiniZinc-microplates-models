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
# Description: Constants for the MPLACE application
#
# Authors: Ramiz GINDULLIN (ramiz.gindullin@it.uu.se)
# Version: 1.0
# Last Revision: October 2025
#


"""
Constants module for MPLACE application.

This module centralizes all magic numbers, default values, and string constants
used throughout the application to improve maintainability and consistency.
"""


class PlateDefaults:
    """Default values for microplate configurations."""
    ROWS = '16'
    COLS = '24'
    EMPTY_EDGE_SIZE = '0'
    CORNER_EMPTY_WELLS = '0'
    CELL_LINES = '1'
    CONTROL_NAMES = '[]'
    
    # Numeric versions for calculations
    ROWS_INT = 16
    COLS_INT = 24


class UI:
    """User interface layout constants."""
    # Widget dimensions
    BUTTON_WIDTH_STANDARD = 13
    ENTRY_WIDTH_NUMERIC = 6
    ENTRY_WIDTH_MATERIALS = 33
    
    # Padding and spacing
    FRAME_PADDING = 10
    GRID_PADDING = 3
    SMALL_PADDING = 2
    WIDGET_SPACING = 1
    WIDGET_SPACING_LARGE = 5
    
    # Grid weights
    GRID_WEIGHT = 1
    
    # Model selection
    SELECT_PLAID = False
    SELECT_OTHER = True


class Visualization:
    """Constants for visualization components."""
    # Panel dimensions
    MATERIAL_PANEL_WIDTH = 400
    MATERIAL_PANEL_HEIGHT = 500
    
    # Plot settings
    WELL_COORDINATE_OFFSET = 0.5
    SCATTER_MARKER_SIZE = 80
    
    # Figure dimensions
    SCALE_FIGURE_WIDTH = 4
    SCALE_FIGURE_HEIGHT = 2
    
    # Alpha transparency range
    ALPHA_MIN = 0.3
    ALPHA_MAX = 1.0


class Performance:
    """Performance-related constants."""
    COORDINATE_CACHE_SIZE = 2048
    COLORMAP_COLOR_LIMIT = 20


class PathsIni:
    """Configuration file parsing constants."""
    # Configuration keys and prefixes
    MINIZINC_PREFIX = 'minizinc_path = '
    PLAID_PREFIX = 'plaid_path = '
    COMPD_PREFIX = 'compd_path = '
    PLAID_MPC_PREFIX = 'plaid_mpc_path = '
    COMPD_MPC_PREFIX = 'compd_mpc_path = '
    
    # Calculated offsets
    MINIZINC_OFFSET = len(MINIZINC_PREFIX)
    PLAID_OFFSET = len(PLAID_PREFIX)
    COMPD_OFFSET = len(COMPD_PREFIX)
    PLAID_MPC_OFFSET = len(PLAID_MPC_PREFIX)
    COMPD_MPC_OFFSET = len(COMPD_MPC_PREFIX)


class Messages:
    """User interface messages and labels."""
    # Status messages
    NO_DZN_LOADED = 'No *.dzn file is loaded'
    NO_CSV_LOADED = 'No *.csv file is loaded'
    
    # Dialog titles and labels
    FRAME_TITLE_DZN = 'Step 1 - Generate OR load the *.dzn file:'
    FRAME_TITLE_CSV = 'Step 2 - Generate OR load the layout (*.csv):'
    FRAME_TITLE_VIZ = 'Step 3 - Visualize the layout (*.csv):'
    
    BUTTON_GENERATE_DZN = 'Generate *.dzn file'
    BUTTON_LOAD_DZN = 'Load *.dzn file'
    BUTTON_RUN_MODEL = 'Run a model'
    BUTTON_LOAD_CSV = 'Load *.csv file'
    BUTTON_VISUALIZE = 'Visualize *.csv'
    BUTTON_RESET = 'Reset all'
    BUTTON_CLOSE = 'close window'
    
    # Label texts
    LABEL_ROWS = 'nb rows:'
    LABEL_COLS = 'nb cols:'
    
    # Model types
    MODEL_PLAID = 'PLAID'
    MODEL_COMPD = 'COMPD'
    MODEL_OTHER = 'Other'


class WindowConfig:
    """Window positioning and titles."""
    # Window titles
    TITLE_MAIN = "MPLACE"
    TITLE_DZN_GENERATOR = "Generate *.dzn file"
    TITLE_VISUALIZER = "Visualize GUI"
    
    # Window positions (x, y offsets)
    DZN_WINDOW_X = 30
    DZN_WINDOW_Y = 30
    VIZ_WINDOW_X = 10
    VIZ_WINDOW_Y = 10


class MaterialDefaults:
    """Default material configurations for DZN generation."""
    # Default compound dictionary
    DEFAULT_DRUGS = "{'Drug1': [5,'0.1', '0.3'], 'Drug2': [5, '1']}"
    
    # Default control dictionary  
    DEFAULT_CONTROLS = "{'pos': [10, '100']}"


class FileTypes:
    """File type constants for dialogs."""
    DZN_FILES = [('dzn files', '*.dzn')]
    CSV_FILES = [('csv files', '*.csv')]


class Validation:
    """Input validation constants."""
    MATERIAL_NAME_MAX_LENGTH = 100
    PATH_DISPLAY_MAX_LENGTH = 20
    PATH_TRUNCATION_PREFIX = '...'


class System:
    """System-related constants."""
    # Platform detection
    WINDOWS_PLATFORM_PREFIX = 'win'
    
    # Encoding
    WINDOWS_CODEPAGE_UTF8 = 'chcp 65001'
    
    # Time delays
    UI_UPDATE_DELAY = 0.25  # seconds