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
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from functools import partial
from typing import Tuple

import utility as ut

import WindowVisuals as wv
import WindowGenDZN as wd


# ------------------------------
# Functions
# ------------------------------

def update_csv_path(path: str) -> None:
    """Update CSV file path and display it in the UI.
    
    Args:
        path: Path to CSV file
    """
    ut.path_show(path, label_csv_loaded)
    csv_file_path.set(path)


def reset_all() -> None:
    """Reset all form fields and UI state to defaults."""
    dzn_file_path.set('')
    csv_file_path.set('')
    num_rows.set('16')
    num_cols.set('24')
    control_names.set("[]")
    use_compd_flag.set('PLAID')
    label_dzn_loaded.config(text='No *.dzn file is loaded')
    label_csv_loaded.config(text='No *.csv file is loaded')
    button_run_minizinc.config(state=tk.DISABLED)


def generate_dzn() -> None:
    """Show the DZN file generation window."""
    wd.gen_dzn_show()


def connect_generate_dzn() -> None:
    """Connect main window variables to DZN generation window.
    
    Ensures seamless two-way transfer of data between windows.
    """
    wd.path_main = dzn_file_path
    wd.label_main = label_dzn_loaded
    wd.button_main = button_run_minizinc
    wd.num_rows_main = num_rows
    wd.num_cols_main = num_cols
    wd.control_names = control_names


def load_dzn() -> None:
    """Load DZN file, extract information, and update UI."""
    path = tk.filedialog.askopenfilename(
        title='open dzn file',
        filetypes=[('dzn files', '*.dzn')]
    )
    if path != '':
        try:
            ut.path_show(path, label_dzn_loaded)
            dzn_file_path.set(path)

            cols, rows, controls_names_text = ut.scan_dzn(path)
            num_cols.set(cols)
            num_rows.set(rows)
            control_names.set(controls_names_text)

            button_run_minizinc.config(state=tk.NORMAL)
        except (FileNotFoundError, ValueError) as e:
            tk.messagebox.showerror("Error", f"Failed to load DZN file: {str(e)}")


def load_csv() -> None:
    """Load CSV file and update UI."""
    path = tk.filedialog.askopenfilename(
        title='open csv file',
        filetypes=[('csv files', '*.csv')]
    )
    if path != '':
        try:
            update_csv_path(path)
        except Exception as e:
            tk.messagebox.showerror("Error", f"Failed to load CSV file: {str(e)}")


def run_minizinc() -> None:
    """Launch MiniZinc model and write results to CSV file."""
    if use_compd_flag.get() == 'COMPD':
        solver_config = compd_mpc_path.get()
        model_file = compd_path.get()
    else:
        solver_config = plaid_mpc_path.get()
        model_file = plaid_path.get()

    # Store original label text to restore on failure
    original_label_text = label_csv_loaded.cget("text")
    label_csv_loaded.config(text='Running the model...')
    time.sleep(0.25)
    
    try:
        cmd_to_str = ut.run_cmd(minizinc_path.get(), solver_config,
                                model_file, dzn_file_path.get())
        label_csv_loaded.config(text='Done...')

        path = tk.filedialog.asksaveasfilename(
            defaultextension=".csv", filetypes=[('csv files', '*.csv')])

        print(path)

        if path is None or path == '':
            # User cancelled - restore original state
            label_csv_loaded.config(text=original_label_text)
            return

        # Use context manager for file writing
        try:
            with open(path, 'w') as csv_file:
                csv_text = ut.extract_csv_text(cmd_to_str)
                csv_file.writelines(csv_text)
        except (IOError, OSError) as e:
            tk.messagebox.showerror("Error", f"Failed to write CSV file: {str(e)}")
            label_csv_loaded.config(text='Error writing file')
            return

        update_csv_path(path)
        csv_file_path.set(path)
        
    except (RuntimeError, FileNotFoundError) as e:
        label_csv_loaded.config(text='Error occurred')
        tk.messagebox.showerror("Error", f"Failed to run MiniZinc: {str(e)}")


def visualize() -> None:
    """Launch visualization window for CSV data."""
    if csv_file_path.get() != '':
        try:
            figure_name_template = csv_file_path.get()[:-3] + '_' + use_compd_flag.get() + '_'
            wv.visualize(csv_file_path.get(), figure_name_template,
                         num_rows.get(), num_cols.get(), control_names.get())
        except Exception as e:
            tk.messagebox.showerror("Error", f"Failed to visualize: {str(e)}")


def on_close() -> None:
    """Handle window close event, ensuring all windows are properly destroyed."""
    try:
        wd.window.destroy()
    except (AttributeError, tk.TclError):
        # Window might not exist or already be destroyed
        pass
    finally:
        root.destroy()


if sys.platform.startswith('win'):
    os.system('chcp 65001')  # Change code page to UTF-8

# ------------------------------
# Global variables
# ------------------------------

root: tk.Tk = tk.Tk()
root.title("MPLACE")
root.resizable(False, False)

# Close both the root window and WindowGenDZN properly
root.protocol('WM_DELETE_WINDOW', on_close)

dzn_file_path: tk.StringVar = tk.StringVar(root)
csv_file_path: tk.StringVar = tk.StringVar(root)
dzn_file_path.set('')
csv_file_path.set('')

num_cols: tk.StringVar = tk.StringVar(root)
num_rows: tk.StringVar = tk.StringVar(root)
num_cols.set('16')
num_rows.set('24')

control_names: tk.StringVar = tk.StringVar(root)
control_names.set('[]')

vcmd: Tuple = (root.register(ut.callback))

use_compd_flag: tk.StringVar = tk.StringVar(root)
use_compd_flag.set('PLAID')

try:
    minizinc_path_s, plaid_path_s, compd_path_s, plaid_mpc_path_s, compd_mpc_path_s = ut.read_paths_ini_file()
except FileNotFoundError as e:
    tk.messagebox.showerror("Configuration Error", str(e))
    sys.exit(1)

minizinc_path: tk.StringVar = tk.StringVar(root)
plaid_path: tk.StringVar = tk.StringVar(root)
compd_path: tk.StringVar = tk.StringVar(root)
plaid_mpc_path: tk.StringVar = tk.StringVar(root)
compd_mpc_path: tk.StringVar = tk.StringVar(root)

minizinc_path.set(minizinc_path_s)
plaid_path.set(plaid_path_s)
compd_path.set(compd_path_s)
plaid_mpc_path.set(plaid_mpc_path_s)
compd_mpc_path.set(compd_mpc_path_s)


# ------------------------------
# UI elements and callbacks
# ------------------------------

# Frame 1: DZN file generation/loading
frame_dzn: ttk.LabelFrame = ttk.LabelFrame(root, text='Step 1 - Generate OR load the *.dzn file:')
frame_dzn.pack(expand=True, fill="both", padx=10, pady=10)
button_generate_dzn: ttk.Button = ttk.Button(
    frame_dzn, width=13, state=tk.NORMAL, text='Generate *.dzn file')
button_load_dzn: ttk.Button = ttk.Button(
    frame_dzn, width=13, state=tk.NORMAL, text='Load *.dzn file')
label_dzn_loaded: tk.Label = tk.Label(frame_dzn, text='No *.dzn file is loaded')

frame_dzn.columnconfigure(0, weight=1)
frame_dzn.columnconfigure(1, weight=1)

button_generate_dzn.grid(row=0, column=0, columnspan=1, sticky="ew")
button_load_dzn.grid(row=0, column=1, columnspan=1, sticky="ew")
label_dzn_loaded.grid(row=1, column=0, columnspan=2, sticky="w")

# Frame 2: CSV file generation/loading
frame_csv: ttk.LabelFrame = ttk.LabelFrame(root, text='Step 2 - Generate OR load the layout (*.csv):')
frame_csv.pack(expand=True, fill="both", padx=10, pady=10)
button_run_minizinc: ttk.Button = ttk.Button(frame_csv, width=13, state=tk.DISABLED, text='Run a model')
button_load_csv: ttk.Button = ttk.Button(
    frame_csv, width=13, state=tk.NORMAL, text='Load *.csv file')
label_csv_loaded: tk.Label = tk.Label(frame_csv, text='No *.csv file is loaded')
radio_plaid: ttk.Radiobutton = ttk.Radiobutton(frame_csv, text='PLAID',
                              value='PLAID', variable=use_compd_flag)
radio_compd: ttk.Radiobutton = ttk.Radiobutton(frame_csv, text='Other',
                              value='COMPD', variable=use_compd_flag)

frame_csv.columnconfigure(0, weight=1)
frame_csv.columnconfigure(1, weight=1)

radio_plaid.grid(row=0, column=0, columnspan=1, sticky="")
radio_compd.grid(row=0, column=1, columnspan=1, sticky="")
button_run_minizinc.grid(row=1, column=0, columnspan=1, sticky="ew")
button_load_csv.grid(row=1, column=1, columnspan=1, sticky="ew")
label_csv_loaded.grid(row=2, column=0, columnspan=2, sticky="w")

# Frame 3: Visualization
frame_matplotlib: ttk.LabelFrame = ttk.LabelFrame(root, text='Step 3 - Visualize the layout (*.csv):')
frame_matplotlib.pack(expand=True, fill="both", padx=10, pady=10)
label_rows: tk.Label = tk.Label(frame_matplotlib, text='nb rows:')
entry_rows: ttk.Entry = ttk.Entry(frame_matplotlib, textvariable=num_rows, width=6,
                       validate='all', validatecommand=(vcmd, '%P'))
label_cols: tk.Label = tk.Label(frame_matplotlib, text='nb cols:')
entry_cols: ttk.Entry = ttk.Entry(frame_matplotlib, textvariable=num_cols, width=6,
                       validate='all', validatecommand=(vcmd, '%P'))
button_visualize: ttk.Button = ttk.Button(
    frame_matplotlib, width=13, state=tk.NORMAL, text='Visualize *.csv')
button_reset_all: ttk.Button = ttk.Button(frame_matplotlib, width=13, text='Reset all')

frame_matplotlib.columnconfigure(0, weight=1)
frame_matplotlib.columnconfigure(1, weight=1)
frame_matplotlib.columnconfigure(2, weight=1)
frame_matplotlib.columnconfigure(3, weight=1)

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

root.mainloop()