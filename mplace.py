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
# Description:  Main window of the simple GUI for the workflow of generating with MiniZinc and displaying microplate layouts
#
# Authors: Ramiz GINDULLIN (ramiz.gindullin@it.uu.se)
# Version: 1.0
# Last Revision: October 2025
#


import os
import sys
import time
import logging
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from functools import partial
from typing import Tuple
from dataclasses import dataclass

from core.dzn_parser import scan_dzn
from core.io_utils import path_show, extract_csv_text, convert_pharmbio_to_plater, write_csv_file
from core.minizinc_runner import run_model
from config.loader import load_config
from models.constants import PlateDefaults, UI, Messages, WindowConfig, System, FileTypes
from models.dto import AppConfig, DznGenerationResult, MiniZincRunRequest, MiniZincRunResult, CSVConversionRequest
from ui.layout_format_dialog import ask_layout_export_format
from ui.ui_validators import numeric_entry_callback

from ui import window_dzn as wd
from ui import window_visuals as wv

# Configure logging for main application
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mplace.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


# ------------------------------
# Functions
# ------------------------------

def update_csv_path(path: str) -> None:
    """Update CSV file path and display it in the UI.

    Args:
        path: Path to CSV file
    """
    path_show(path, label_csv_loaded)
    csv_file_path.set(path)
    logger.info(f"CSV file path updated: {path}")


def reset_all() -> None:
    """Reset all form fields and UI state to defaults."""
    dzn_file_path.set('')
    csv_file_path.set('')
    num_rows.set(PlateDefaults.ROWS)
    num_cols.set(PlateDefaults.COLS)
    control_names.set(PlateDefaults.CONTROL_NAMES)
    use_compd_flag.set(UI.SELECT_PLAID)
    label_dzn_loaded.config(text=Messages.NO_DZN_LOADED)
    label_csv_loaded.config(text=Messages.NO_CSV_LOADED)
    button_run_minizinc.config(state=tk.DISABLED)
    logger.info("Application state reset to defaults")


def on_dzn_generated(result: DznGenerationResult) -> None:
    """Handle DZN generation completion from WindowGenDZN.

    Args:
        result: DZN generation result data
    """
    # Update main window state with generated DZN data
    dzn_file_path.set(result.file_path)
    num_rows.set(result.rows)
    num_cols.set(result.cols)
    control_names.set(result.control_names)

    # Update UI elements
    path_show(result.file_path, label_dzn_loaded)
    button_run_minizinc.config(state=tk.NORMAL)

    print(
        f"DZN integrated: {result.rows}x{result.cols} plate, controls: {result.control_names}")
    logger.info(
        f"DZN generation result integrated into main window: {result.file_path}")


def generate_dzn() -> None:
    """Show the DZN file generation window."""
    wd.gen_dzn_show()
    logger.debug("DZN generation window opened")


def connect_generate_dzn() -> None:
    """Set up callback for DZN generation completion.

    Establishes clean communication between main and DZN windows.
    """
    wd.set_completion_callback(on_dzn_generated)
    logger.debug("DZN generation callback configured")


def load_dzn() -> None:
    """Load DZN file, extract information, and update UI."""
    path = tk.filedialog.askopenfilename(
        title='open dzn file',
        filetypes=FileTypes.DZN_FILES
    )
    if path != '':
        try:
            path_show(path, label_dzn_loaded)
            dzn_file_path.set(path)

            cols, rows, controls_names_text = scan_dzn(path)
            num_cols.set(cols)
            num_rows.set(rows)
            control_names.set(controls_names_text)

            print(f"Loaded DZN: {rows}x{cols} plate, controls: {controls_names_text}")
            logger.info(f"DZN file loaded successfully: {path}")

            button_run_minizinc.config(state=tk.NORMAL)
        except (FileNotFoundError, ValueError) as e:
            logger.error(f"DZN loading failed: {path}, error: {e}")
            tk.messagebox.showerror("Error", f"Failed to load DZN file: {str(e)}")


def load_csv() -> None:
    """Load CSV file and update UI."""
    path = tk.filedialog.askopenfilename(
        title='open csv file',
        filetypes=FileTypes.CSV_FILES
    )
    if path != '':
        try:
            update_csv_path(path)
            # Count lines for user info
            with open(path, 'r') as f:
                line_count = sum(1 for _ in f) - 1  # Exclude header
            print(f"Loaded CSV: {line_count} layout entries")
            logger.info(f"CSV file loaded: {path}, {line_count} entries")
        except Exception as e:
            logger.error(f"CSV loading failed: {path}, error: {e}")
            tk.messagebox.showerror("Error", f"Failed to load CSV file: {str(e)}")


def run_minizinc() -> None:
    """Launch MiniZinc model and write results to CSV file."""
    if use_compd_flag.get() == True:
        solver_config = compd_mpc_path.get()
        model_file = compd_path.get()
        model_name = Messages.MODEL_OTHER
        print(f"Running {model_name} model...")
        logger.info(f"Starting MiniZinc execution with {model_name} model")
    else:
        solver_config = plaid_mpc_path.get()
        model_file = plaid_path.get()
        model_name = Messages.MODEL_PLAID
        print(f"Running {model_name} model...")
        logger.info(f"Starting MiniZinc execution with {model_name} model")

    # Store original label text to restore on failure
    original_label_text = label_csv_loaded.cget("text")
    label_csv_loaded.config(text='Running the model...')
    time.sleep(System.UI_UPDATE_DELAY)

    try:
        cmd_to_str = run_model(minizinc_path.get(), solver_config,
                               model_file, dzn_file_path.get())
        
        # Extract CSV with improved error handling
        try:
            csv_text = extract_csv_text(cmd_to_str)
            logger.info(f"Successfully extracted {len(csv_text)} CSV lines from solver output")
        except Exception as e:
            logger.error(f"Failed to extract CSV from solver output: {str(e)}")
            label_csv_loaded.config(text='Error extracting layout')
            tk.messagebox.showerror(
                "Layout Extraction Error", 
                "No valid layout data found in solver output.\n\n"
                f"Details: {str(e)}\n\n"
                "Please check that:\n"
                "• The model solved successfully\n" 
                "• The solver produced CSV output with expected headers\n"
                "• The DZN file contains valid experimental data"
            )
            return
            
        label_csv_loaded.config(text='Layout generated. Choose export format...')

        # Ask user for export format with improved error handling
        file_format = ask_layout_export_format(root)
        
        if file_format is None:
            logger.info("User cancelled export format selection - operation aborted")
            label_csv_loaded.config(text=original_label_text)
            return

        # Normalize format string to avoid case/value mismatches
        format_normalized = (file_format or '').lower().strip()
        logger.info(f"User selected export format: '{format_normalized}'")

        saved_paths = []  # Track all saved files
        
        if format_normalized == FileTypes.PHARMBIO.lower().strip():
            # Save PharmBio format (current format)
            default_name = os.path.basename(dzn_file_path.get())[:-4] + ".csv"
            
            path = write_csv_file(csv_text, suggested_filename=default_name)
            if path == -1:
                logger.info("User cancelled PharmBio CSV save")
                label_csv_loaded.config(text=original_label_text)
                return
            elif path == -2:
                logger.error("Failed to write PharmBio CSV file")
                label_csv_loaded.config(text='Error writing file')
                tk.messagebox.showerror("File Write Error", "Failed to save CSV file. Check disk space and permissions.")
                return
            
            saved_paths.append(path)
            print(f"PharmBio CSV saved: {path}")
            logger.info(f"PharmBio format CSV saved successfully: {path}")

        elif format_normalized == FileTypes.PLATER.lower().strip():
            # Convert to PLATER format and save (potentially multiple files)
            try:
                conversion_input = CSVConversionRequest(
                    csv_lines=csv_text,
                    rows=num_rows.get(),
                    cols=num_cols.get()
                )
                
                plater_data_list = convert_pharmbio_to_plater(conversion_input)
                logger.info(f"Converted to PLATER format: {len(plater_data_list)} file(s) to save")
                
                # Save each PLATER CSV file
                for i, plater_csv_content in enumerate(plater_data_list):
                    # Ensure proper CSV line formatting
                    if isinstance(plater_csv_content, str):
                        # If it's a string, split by lines and ensure newlines
                        csv_lines = [line + '\n' if not line.endswith('\n') else line 
                                   for line in plater_csv_content.splitlines()]
                    else:
                        # If it's already a list, use as-is
                        csv_lines = plater_csv_content
                    
                    # Show save dialog with meaningful default filename
                    if len(plater_data_list) == 1:
                        default_name = os.path.basename(dzn_file_path.get())[:-4] + ".csv"
                    else:
                        default_name = os.path.basename(dzn_file_path.get())[:-4] + "_" + str(i+1) + ".csv"
                    
                    path = write_csv_file(csv_lines, suggested_filename=default_name)
                    
                    if path == -1:
                        if i == 0:
                            logger.info("User cancelled PLATER CSV save")
                            label_csv_loaded.config(text=original_label_text)
                            return
                        else:
                            logger.info(f"User cancelled PLATER save on plate {i+1}/{len(plater_data_list)}")
                            break  # Stop saving remaining files
                    elif path == -2:
                        logger.error(f"Failed to write PLATER CSV file {i+1}")
                        label_csv_loaded.config(text='Error writing file')
                        tk.messagebox.showerror(
                            "File Write Error", 
                            f"Failed to save PLATER file {i+1} of {len(plater_data_list)}.\n"
                            "Check disk space and permissions."
                        )
                        return
                    
                    saved_paths.append(path)
                    print(f"PLATER CSV {i+1}/{len(plater_data_list)} saved: {path}")
                    logger.info(f"PLATER format CSV {i+1}/{len(plater_data_list)} saved: {path}")
                
                # Provide user feedback for multi-file saves
                if len(saved_paths) > 1:
                    file_list = '\n'.join(f"• {os.path.basename(p)}" for p in saved_paths)
                    tk.messagebox.showinfo(
                        "PLATER Export Complete",
                        f"Successfully saved {len(saved_paths)} PLATER files:\n\n{file_list}\n\n"
                        "Note: PLATER format uses one file per plate."
                    )
                    logger.info(f"Multi-file PLATER export completed: {len(saved_paths)} files saved")
                
            except Exception as e:
                logger.error(f"PLATER conversion failed: {str(e)}")
                label_csv_loaded.config(text='Error converting to PLATER format')
                tk.messagebox.showerror(
                    "Format Conversion Error",
                    f"Failed to convert layout to PLATER format.\n\n"
                    f"Details: {str(e)}\n\n"
                    "Please report this issue if it persists."
                )
                return
        
        else:
            # Unknown format - shouldn't happen with proper dialog, but defensive programming
            logger.warning(f"Unknown export format selected: '{file_format}' (normalized: '{format_normalized}')")
            tk.messagebox.showerror(
                "Unknown Format",
                f"Unknown export format: '{file_format}'\n\n"
                "Please select either PharmBio or PLATER format."
            )
            label_csv_loaded.config(text=original_label_text)
            return

        # Update UI with primary saved file (first one for multi-file saves)
        if saved_paths:
            primary_path = saved_paths[0]
            update_csv_path(primary_path)
            csv_file_path.set(primary_path)
            
            # Show completion message
            if len(saved_paths) == 1:
                print(f"Layout exported successfully: {os.path.basename(primary_path)}")
            else:
                print(f"Layout exported: {len(saved_paths)} files, primary: {os.path.basename(primary_path)}")
                
            logger.info(f"Export completed: {len(saved_paths)} file(s), primary path set to: {primary_path}")

    except (RuntimeError, FileNotFoundError) as e:
        label_csv_loaded.config(text='MiniZinc execution failed')
        logger.error(f"MiniZinc execution failed: {e}")
        tk.messagebox.showerror(
            "Model Execution Error", 
            f"Failed to run {model_name} model.\n\n"
            f"Details: {str(e)}\n\n"
            "Please check:\n"
            "• MiniZinc is properly installed and configured\n"
            "• The DZN file is valid\n"
            "• The model files are accessible"
        )


def visualize() -> None:
    """Launch visualization window for CSV data."""
    if csv_file_path.get() != '':
        try:
            if use_compd_flag.get():
                model_name = Messages.MODEL_OTHER
            else:
                model_name = Messages.MODEL_PLAID
            figure_name_template = csv_file_path.get()[:-4] + '_' + model_name + '_'
            print(f"Opening visualization for: {csv_file_path.get()}")
            logger.info(
                f"Starting visualization: CSV={csv_file_path.get()}, template={figure_name_template}")

            wv.visualize(csv_file_path.get(), figure_name_template,
                         num_rows.get(), num_cols.get(), control_names.get())
        except Exception as e:
            logger.error(f"Visualization failed: {e}")
            tk.messagebox.showerror("Error", f"Failed to visualize: {str(e)}")


def on_close() -> None:
    """Handle window close event, ensuring all windows are properly destroyed."""
    logger.info("Application shutdown initiated")
    try:
        wd.window.destroy()
    except (AttributeError, tk.TclError):
        # Window might not exist or already be destroyed
        pass
    finally:
        logger.info("Application shutdown completed")
        root.destroy()


if sys.platform.startswith(System.WINDOWS_PLATFORM_PREFIX):
    os.system(System.WINDOWS_CODEPAGE_UTF8)  # Change code page to UTF-8

# Log application startup
logger.info("MPLACE application starting up")

# ------------------------------
# Global variables
# ------------------------------

root: tk.Tk = tk.Tk()
root.title(WindowConfig.TITLE_MAIN)
root.resizable(False, False)

# Close both the root window and WindowGenDZN properly
root.protocol('WM_DELETE_WINDOW', on_close)

dzn_file_path: tk.StringVar = tk.StringVar(root)
csv_file_path: tk.StringVar = tk.StringVar(root)
dzn_file_path.set('')
csv_file_path.set('')

num_cols: tk.StringVar = tk.StringVar(root)
num_rows: tk.StringVar = tk.StringVar(root)
num_cols.set(PlateDefaults.COLS)
num_rows.set(PlateDefaults.ROWS)

control_names: tk.StringVar = tk.StringVar(root)
control_names.set(PlateDefaults.CONTROL_NAMES)

vcmd: Tuple = (root.register(numeric_entry_callback))

use_compd_flag: tk.BooleanVar = tk.BooleanVar(root)
use_compd_flag.set(UI.SELECT_PLAID)

try:
    app_config: AppConfig = load_config()
    print("Configuration loaded successfully")
    logger.info("Configuration loaded from paths.ini")
except FileNotFoundError as e:
    logger.critical(f"Configuration error: {e}")
    tk.messagebox.showerror("Configuration Error", str(e))
    sys.exit(1)

minizinc_path: tk.StringVar = tk.StringVar(root)
plaid_path: tk.StringVar = tk.StringVar(root)
compd_path: tk.StringVar = tk.StringVar(root)
plaid_mpc_path: tk.StringVar = tk.StringVar(root)
compd_mpc_path: tk.StringVar = tk.StringVar(root)

minizinc_path.set(app_config.minizinc_path)
plaid_path.set(app_config.plaid_path)
compd_path.set(app_config.compd_path)
plaid_mpc_path.set(app_config.plaid_mpc_path)
compd_mpc_path.set(app_config.compd_mpc_path)


# ------------------------------
# UI elements and callbacks
# ------------------------------

# Frame 1: DZN file generation/loading
frame_dzn: ttk.LabelFrame = ttk.LabelFrame(root, text=Messages.FRAME_TITLE_DZN)
frame_dzn.pack(expand=True, fill="both", padx=UI.FRAME_PADDING, pady=UI.FRAME_PADDING)
button_generate_dzn: ttk.Button = ttk.Button(
    frame_dzn, width=UI.BUTTON_WIDTH_STANDARD, state=tk.NORMAL, text=Messages.BUTTON_GENERATE_DZN)
button_load_dzn: ttk.Button = ttk.Button(
    frame_dzn, width=UI.BUTTON_WIDTH_STANDARD, state=tk.NORMAL, text=Messages.BUTTON_LOAD_DZN)
label_dzn_loaded: tk.Label = tk.Label(frame_dzn, text=Messages.NO_DZN_LOADED)

frame_dzn.columnconfigure(0, weight=UI.GRID_WEIGHT)
frame_dzn.columnconfigure(1, weight=UI.GRID_WEIGHT)

button_generate_dzn.grid(row=0, column=0, columnspan=1, sticky="ew")
button_load_dzn.grid(row=0, column=1, columnspan=1, sticky="ew")
label_dzn_loaded.grid(row=1, column=0, columnspan=2, sticky="w")

# Frame 2: CSV file generation/loading
frame_csv: ttk.LabelFrame = ttk.LabelFrame(root, text=Messages.FRAME_TITLE_CSV)
frame_csv.pack(expand=True, fill="both", padx=UI.FRAME_PADDING, pady=UI.FRAME_PADDING)
button_run_minizinc: ttk.Button = ttk.Button(
    frame_csv, width=UI.BUTTON_WIDTH_STANDARD, state=tk.DISABLED, text=Messages.BUTTON_RUN_MODEL)
button_load_csv: ttk.Button = ttk.Button(
    frame_csv, width=UI.BUTTON_WIDTH_STANDARD, state=tk.NORMAL, text=Messages.BUTTON_LOAD_CSV)
label_csv_loaded: tk.Label = tk.Label(frame_csv, text=Messages.NO_CSV_LOADED)
radio_plaid: ttk.Radiobutton = ttk.Radiobutton(frame_csv, text=Messages.MODEL_PLAID,
                                               value=UI.SELECT_PLAID, variable=use_compd_flag)
radio_compd: ttk.Radiobutton = ttk.Radiobutton(frame_csv, text=Messages.MODEL_OTHER,
                                               value=UI.SELECT_OTHER, variable=use_compd_flag)

frame_csv.columnconfigure(0, weight=UI.GRID_WEIGHT)
frame_csv.columnconfigure(1, weight=UI.GRID_WEIGHT)

radio_plaid.grid(row=0, column=0, columnspan=1, sticky="")
radio_compd.grid(row=0, column=1, columnspan=1, sticky="")
button_run_minizinc.grid(row=1, column=0, columnspan=1, sticky="ew")
button_load_csv.grid(row=1, column=1, columnspan=1, sticky="ew")
label_csv_loaded.grid(row=2, column=0, columnspan=2, sticky="w")

# Frame 3: Visualization
frame_matplotlib: ttk.LabelFrame = ttk.LabelFrame(root, text=Messages.FRAME_TITLE_VIZ)
frame_matplotlib.pack(expand=True, fill="both",
                      padx=UI.FRAME_PADDING, pady=UI.FRAME_PADDING)
label_rows: tk.Label = tk.Label(frame_matplotlib, text=Messages.LABEL_ROWS)
entry_rows: ttk.Entry = ttk.Entry(frame_matplotlib, textvariable=num_rows, width=UI.ENTRY_WIDTH_NUMERIC,
                                  validate='all', validatecommand=(vcmd, '%P'))
label_cols: tk.Label = tk.Label(frame_matplotlib, text=Messages.LABEL_COLS)
entry_cols: ttk.Entry = ttk.Entry(frame_matplotlib, textvariable=num_cols, width=UI.ENTRY_WIDTH_NUMERIC,
                                  validate='all', validatecommand=(vcmd, '%P'))
button_visualize: ttk.Button = ttk.Button(
    frame_matplotlib, width=UI.BUTTON_WIDTH_STANDARD, state=tk.NORMAL, text=Messages.BUTTON_VISUALIZE)
button_reset_all: ttk.Button = ttk.Button(
    frame_matplotlib, width=UI.BUTTON_WIDTH_STANDARD, text=Messages.BUTTON_RESET)

frame_matplotlib.columnconfigure(0, weight=UI.GRID_WEIGHT)
frame_matplotlib.columnconfigure(1, weight=UI.GRID_WEIGHT)
frame_matplotlib.columnconfigure(2, weight=UI.GRID_WEIGHT)
frame_matplotlib.columnconfigure(3, weight=UI.GRID_WEIGHT)

label_rows.grid(row=0, column=0, columnspan=1, sticky="w")
entry_rows.grid(row=0, column=1, columnspan=1, sticky="w")
label_cols.grid(row=0, column=2, columnspan=1, sticky="w")
entry_cols.grid(row=0, column=3, columnspan=1, sticky="w")
button_visualize.grid(row=1, column=0, columnspan=2, sticky="ew")
button_reset_all.grid(row=1, column=2, columnspan=2, sticky="ew")

# Assign button commands
button_generate_dzn.configure(command=lambda: generate_dzn())
button_load_dzn.configure(command=lambda: load_dzn())
button_run_minizinc.configure(command=lambda: run_minizinc())
button_load_csv.configure(command=lambda: load_csv())
button_visualize.configure(command=lambda: visualize())
button_reset_all.configure(command=lambda: reset_all())

connect_generate_dzn()
reset_all()

logger.info("MPLACE GUI initialized, entering main loop")
root.mainloop()
