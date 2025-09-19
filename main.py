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
# Last Revision: September 2025
#


import time
import tkinter as tk
from tkinter import ttk
from functools import partial

import utility as ut

import WindowVisuals as wv
import WindowGenDZN  as wd


#------------------------------
# Functions
#------------------------------
# we name the csv-file based on the name of the dzn-file
def update_csv_path(path):
    ut.path_show(path, label_csv_loaded)
    csv_file_path.set(path)

def reset_all():
    dzn_file_path.set('')
    csv_file_path.set('')
    num_rows.set('16')
    num_cols.set('24')
    control_names.set("[]")
    use_compd_flag.set('PLAID')
    label_dzn_loaded.config(text = 'No *.dzn file is loaded')
    label_csv_loaded.config(text = 'No *.csv file is loaded')
    button_run_mzn.config(state = tk.DISABLED)

def gen_dzn():
    wd.gen_dzn_show()

# is used to ensure seamless two-way transfer of data between the main window and the generate dzn-file window
def connect_gen_dzn():
    wd.path_main = dzn_file_path
    wd.label_main = label_dzn_loaded
    wd.button_main = button_run_mzn
    wd.num_rows_main = num_rows
    wd.num_cols_main = num_cols
    wd.control_names = control_names
    
    

# select the dzn-file, extract the relevant information, display it to the user
def load_dzn():
    path = tk.filedialog.askopenfilename(
        title = 'open dzn file',
        filetypes = [ ('dzn files','*.dzn') ]
    )
    if path != '':
        ut.path_show(path, label_dzn_loaded)
        dzn_file_path.set(path)
        
        cols, rows, controls_names_text = ut.scan_dzn(path)
        num_cols.set(cols)
        num_rows.set(rows)
        control_names.set(controls_names_text)
    
        button_run_mzn.config(state = tk.NORMAL)

# select the csv-file, extract the relevant information, display it to the user
def load_csv():
    path = tk.filedialog.askopenfilename(
        title = 'open csv file',
        filetypes = [ ('csv files','*.csv') ]
    )
    if path != '':
        update_csv_path(path)

# launch MiniZinc model, write the results in the csv-file
def run_minizinc():
    if use_compd_flag.get() == 'COMPD':
        solver_config = compd_mpc_path.get()
        model_file = compd_path.get()
    else:
        solver_config = plaid_mpc_path.get()
        model_file = plaid_path.get()
    
    label_csv_loaded.config(text = 'Running the model...')
    time.sleep(0.25)
    cmd_to_str = ut.run_cmd(minizinc_path.get(), solver_config, model_file, dzn_file_path.get())
    label_csv_loaded.config(text = 'Done...')
    
    path = dzn_file_path.get()[:-3] + 'csv'
    
    csv_file = open(path, 'w')
    csv_text = ut.extract_csv_text(cmd_to_str)
    csv_file.writelines(csv_text)
    csv_file.close()
    
    update_csv_path(path)
    csv_file_path.set(path)

def visualize():
    if csv_file_path.get() != '':
        figure_name_template = csv_file_path.get()[:-3] + '_' + use_compd_flag.get() + '_'
        wv.visualize(csv_file_path.get(), figure_name_template, num_rows.get(), num_cols.get(), control_names.get())

def on_close():
    wd.window.destroy()
    root.destroy()
    

#------------------------------
# Global variables
#------------------------------

root = tk.Tk()
root.title("GUI for displaying microplates")
root.resizable(False, False)

root.protocol('WM_DELETE_WINDOW', on_close) # to close both the root window and WindowGenDZN

dzn_file_path = tk.StringVar(root)
csv_file_path = tk.StringVar(root)
dzn_file_path.set('')
csv_file_path.set('')

num_cols = tk.StringVar(root)
num_rows = tk.StringVar(root)
num_cols.set('16')
num_rows.set('24')

control_names = tk.StringVar(root)
control_names.set('[]')

vcmd = (root.register(ut.callback))

use_compd_flag = tk.StringVar(root)
use_compd_flag.set('PLAID')

minizinc_path_s, plaid_path_s, compd_path_s, plaid_mpc_path_s, compd_mpc_path_s = ut.read_paths_ini_file()

minizinc_path = tk.StringVar(root)
plaid_path = tk.StringVar(root)
compd_path = tk.StringVar(root)
plaid_mpc_path = tk.StringVar(root)
compd_mpc_path = tk.StringVar(root)

minizinc_path.set(minizinc_path_s)
plaid_path.set(plaid_path_s)
compd_path.set(compd_path_s)
plaid_mpc_path.set(plaid_mpc_path_s)
compd_mpc_path.set(compd_mpc_path_s)



#------------------------------
# UI elements and callbacks
#------------------------------

# frame 1:
frame_dzn = ttk.LabelFrame(root, text = 'Step 0 - Generate or load the *.dzn file (optional):')
frame_dzn.pack(expand=True, fill="both", padx=10, pady=10)
button_gen_dzn   = ttk.Button(frame_dzn, state = tk.NORMAL, text = 'Generate *.dzn file')
button_load_dzn  = ttk.Button(frame_dzn, state = tk.NORMAL, text = 'Load *.dzn file')
label_dzn_loaded = tk.Label(frame_dzn,  text = 'No *.dzn file is loaded')

frame_dzn.columnconfigure(0, weight=1)
frame_dzn.columnconfigure(1, weight=1)

button_gen_dzn.grid(row=0,column=0,columnspan=1,sticky="ew")
button_load_dzn.grid(row=0,column=1,columnspan=1,sticky="ew")
label_dzn_loaded.grid(row=1,column=0,columnspan=2,sticky="w")

# frame 2:
frame_csv = ttk.LabelFrame(root, text = 'Step 1 - Generate or load the layout (*.csv):')
frame_csv.pack(expand=True, fill="both", padx=10, pady=10)
button_run_mzn   = ttk.Button(frame_csv,  state = tk.DISABLED, text = 'Run a model')
button_load_csv  = ttk.Button(frame_csv,  state = tk.NORMAL, text = 'Load *.csv file')
label_csv_loaded = tk.Label(frame_csv,  text = 'No *.csv file is loaded')
radio_plaid = ttk.Radiobutton(frame_csv, text = 'PLAID', value='PLAID', variable=use_compd_flag)
radio_compd = ttk.Radiobutton(frame_csv, text = 'Other', value='COMPD', variable=use_compd_flag)

frame_csv.columnconfigure(0, weight=1)
frame_csv.columnconfigure(1, weight=1)

radio_plaid.grid(row=0,column=0,columnspan=1,sticky="")
radio_compd.grid(row=0,column=1,columnspan=1,sticky="")
button_run_mzn.grid(row=1,column=0,columnspan=1,sticky="ew")
button_load_csv.grid(row=1,column=1,columnspan=1,sticky="ew")
label_csv_loaded.grid(row=2,column=0,columnspan=2,sticky="w")

# frame 3:
frame_mpl = ttk.LabelFrame(root,  text = 'Step 2 - Visualize the layout (*.csv):')
frame_mpl.pack(expand=True, fill="both", padx=10, pady=10)
label_rows = tk.Label(frame_mpl, text = 'nb rows:')
entry_rows = ttk.Entry(frame_mpl, textvariable = num_rows, width = 6,
                       validate = 'all', validatecommand = (vcmd, '%P'))
label_cols = tk.Label(frame_mpl, text = 'nb cols:')
entry_cols = ttk.Entry(frame_mpl, textvariable = num_cols, width = 6,
                       validate = 'all', validatecommand = (vcmd, '%P'))
button_visualize = ttk.Button(frame_mpl,  state = tk.NORMAL, text = 'Visualize *.csv')
button_reset_all = ttk.Button(frame_mpl,  text = 'Reset')

frame_mpl.columnconfigure(0, weight=1)
frame_mpl.columnconfigure(1, weight=1)
frame_mpl.columnconfigure(2, weight=1)
frame_mpl.columnconfigure(3, weight=1)

label_rows.grid(row=0,column=0,columnspan=1,sticky="w")
entry_rows.grid(row=0,column=1,columnspan=1,sticky="w")
label_cols.grid(row=0,column=2,columnspan=1,sticky="w")
entry_cols.grid(row=0,column=3,columnspan=1,sticky="w")
button_visualize.grid(row=1,column=0,columnspan=2,sticky="ew")
button_reset_all.grid(row=1,column=2,columnspan=2,sticky="ew")

# assign button commands
button_gen_dzn.configure(  command = lambda: gen_dzn())
button_load_dzn.configure( command = lambda: load_dzn())
button_run_mzn.configure(  command = lambda: run_minizinc())
button_load_csv.configure( command = lambda: load_csv())
button_visualize.configure(command = lambda: visualize())
button_reset_all.configure(command = lambda: reset_all())

connect_gen_dzn()
reset_all()

root.mainloop()