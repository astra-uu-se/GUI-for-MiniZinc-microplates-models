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
# Description:  GUI for generating MiniZinc files for PLAID and other similar models
#
# Authors: Ramiz GINDULLIN (ramiz.gindullin@it.uu.se)
# Version: 1.0
# Last Revision: September 2025
#



import tkinter as tk
from tkinter import ttk, VERTICAL, RIGHT, Y, LEFT, BOTH, SOLID

import ast
import re

import utility as ut

def generate_dzn_file():
    #Step 0 - validate input data
    if num_cols.get() == '' or num_rows.get() == '' or size_empty_edge.get() == '' or size_corner_empty_wells.get() == '' or horizontal_cell_lines.get() == '' or vertical_cell_lines.get() == '' or drgs.get() == '' or ctrs.get() == '':
        error_message = 'At least one of the entries is empty'
        print(error_message)
        tk.messagebox.showerror("Invalid input", error_message)
        return
    
    try:
        compounds = ast.literal_eval(drgs.get())
    except:
        error_message = 'Error: the list of drugs has an invalid format:\n' + drgs.get()[:50]+'\n'
        print(error_message)
        tk.messagebox.showerror("Invalid input", error_message)
        return
        
    try:
        controls = ast.literal_eval(ctrs.get())
    except:
        error_message = 'Error: the list of controls has an invalid format:\n' + ctrs.get()[:50]+'\n'
        print(error_message)
        tk.messagebox.showerror("Invalid input", error_message)
        return
    
    #Step 1 - do the conversion, get the string
    
    dzn_txt = ''
    
    #1: write basic values
    dzn_txt += 'num_rows = ' + num_rows.get() + ';\n'
    dzn_txt += 'num_cols = ' + num_cols.get() + ';\n\n'
    
    if inner_empty_edge.get() == False:  # no printing for PLAID
        dzn_txt += 'inner_empty_edge_input = ' + str(inner_empty_edge.get()).lower() + ';\n'
    dzn_txt += 'size_empty_edge = ' + size_empty_edge.get() + ';\n'
    dzn_txt += 'size_corner_empty_wells = ' + size_corner_empty_wells.get() + ';\n\n'
    
    dzn_txt += 'horizontal_cell_lines = ' + horizontal_cell_lines.get() + ';\n'
    dzn_txt += 'vertical_cell_lines = ' + vertical_cell_lines.get() + ';\n\n'
    
    dzn_txt += 'allow_empty_wells = ' + str(flag_allow_empty_wells.get()).lower() + ';\n'
    dzn_txt += 'concentrations_on_different_rows = ' + str(flag_concentrations_on_different_rows.get()).lower() + ';\n'
    dzn_txt += 'concentrations_on_different_columns = ' + str(flag_concentrations_on_different_columns.get()).lower() + ';\n'
    dzn_txt += 'replicates_on_different_plates = ' + str(flag_replicates_on_different_plates.get()).lower() + ';\n'
    dzn_txt += 'replicates_on_same_plate = ' + str(flag_replicates_on_same_plate.get()).lower() + ';\n\n'
    
    nb_compounds = 0
    compound_concentrations = []
    compound_names = []
    compound_replicates = []
    
    for drug in compounds:
        nb_compounds += 1
        compound_names.append(str(drug))
        compound_replicates.append(compounds[drug][0])
        compounds[drug] = [str(x) for x in compounds[drug][1:]]
        compound_concentrations.append(len(compounds[drug]))
    
    dzn_txt += 'compounds = ' + str(nb_compounds) + ';\n'
    dzn_txt += 'compound_concentrations = ' + str(compound_concentrations) + ';\n'
    dzn_txt += 'compound_names = ' + str(compound_names) + ';\n'
    dzn_txt += 'compound_replicates = ' + str(compound_replicates) + ';\n'
    dzn_txt += 'compound_concentration_names = \n['
    drug1 = True
    for drug in compounds:
        if drug1:
            drug1 = False
        else:
            dzn_txt += ' '
        dzn_txt += '| ' + str(compounds[drug])[1:-1]
        for i in range(len(compounds[drug]),max(compound_concentrations)):
            dzn_txt += ", ''"
        dzn_txt += '\n'
    dzn_txt += '|];\n'
    dzn_txt += 'compound_concentration_indicators = [];\n\n'
    
    dzn_txt += 'combinations = 	0;\ncombination_names = [];\ncombination_concentration_names = [];\ncombination_concentrations = 0;\n\n'

    nb_controls = 0
    control_concentrations = []
    control_names_str = []
    control_replicates = []
    
    for control in controls:
        nb_controls += 1
        control_names_str.append(str(control))
        control_replicates.append(controls[control][0])
        controls[control] = [str(x) for x in controls[control][1:]]
        control_concentrations.append(len(controls[control]))
    
    dzn_txt += 'num_controls = ' + str(nb_controls) + ';\n'
    dzn_txt += 'control_concentrations = ' + str(control_concentrations) + ';\n'
    dzn_txt += 'control_names = ' + str(control_names_str) + ';\n'
    dzn_txt += 'control_replicates = ' + str(control_replicates) + ';\n'
    dzn_txt += 'control_concentration_names = \n['
    control1 = True
    for control in controls:
        if control1:
            control1 = False
        else:
            dzn_txt += ' '
        dzn_txt += '| ' + str(controls[control])[1:-1]
        for i in range(len(controls[control]),max(control_concentrations)):
            dzn_txt += ", ''"
        dzn_txt += '\n'
    dzn_txt += '|];\n\n'

    dzn_txt = dzn_txt.replace("'",'"')
    print(dzn_txt)
    
    #Step 2 - save the results
    path = tk.filedialog.asksaveasfilename(defaultextension=".dzn", filetypes = [('dzn files','*.dzn') ])
    
    print(path)
    
    if path == None: # asksaveasfile return `None` if dialog is closed with "cancel".
        return
    if path == '': # asksaveasfile return `None` if dialog is closed with "cancel".
        return
    
    dzn_file = open(path, "w")
    dzn_file.write(dzn_txt)
    dzn_file.close()
    
    path_main.set(path)
    
    num_rows_main.set(num_rows.get())
    num_cols_main.set(num_cols.get())
    ut.path_show(path, label_main)
    button_main.config(state = tk.NORMAL)
    control_names.set(str(control_names_str))
    
    window.withdraw()

def reset_dzn():
    flag_allow_empty_wells.set(True)
    flag_concentrations_on_different_rows.set(True)
    flag_concentrations_on_different_columns.set(True)
    flag_replicates_on_different_plates.set(False)
    flag_replicates_on_same_plate.set(False)
    
    num_rows.set('16')
    num_cols.set('24')
    
    inner_empty_edge.set(True)
    size_empty_edge.set('0')
    size_corner_empty_wells.set('0')
    horizontal_cell_lines.set('1')
    vertical_cell_lines.set('1')

    drgs.set("{'Drug1': [5,'0.1', '0.3'], 'Drug2': [5, '0.1', '0.5', '1']}")
    ctrs.set("{'pos': [10, '100'], 'neg': [10, '100'], 'DMSO': [20, '100']}")


def gen_dzn_show():
    window.deiconify()

def check_replicates_on_different_plates():
    if flag_replicates_on_different_plates.get() == True:
        flag_replicates_on_same_plate.set(False)

def check_replicates_on_same_plate():
    if flag_replicates_on_same_plate.get() == True:
        flag_replicates_on_different_plates.set(False)



#------main window--------
window = tk.Tk()
window.title("Generate *.dzn file")
window.resizable(False, False)
window.geometry('+%d+%d'%(30,30))
window.protocol('WM_DELETE_WINDOW', window.withdraw)
window.withdraw()



#------variables----

# for imports:
path_main = tk.StringVar()
label_main = tk.Label()
button_main = ttk.Button()
control_names = tk.StringVar()
num_rows_main = tk.StringVar()
num_cols_main = tk.StringVar()

# locals:
vcmd = (window.register(ut.callback))

flag_allow_empty_wells = tk.BooleanVar()
flag_concentrations_on_different_rows = tk.BooleanVar()
flag_concentrations_on_different_columns = tk.BooleanVar()
flag_replicates_on_different_plates = tk.BooleanVar()
flag_replicates_on_same_plate = tk.BooleanVar()

num_rows = tk.StringVar(window)
num_cols = tk.StringVar(window)

inner_empty_edge = tk.BooleanVar()
size_empty_edge = tk.StringVar(window)
size_corner_empty_wells = tk.StringVar(window)
horizontal_cell_lines = tk.StringVar(window)
vertical_cell_lines = tk.StringVar(window)

drgs = tk.StringVar(window)
ctrs = tk.StringVar(window)

    

#------UI elements----

#frames
frame_flags      = ttk.LabelFrame(window, text = 'Main properties:')
frame_dimentions = ttk.LabelFrame(window, text = 'Plate dimentions:')
frame_layout     = ttk.LabelFrame(window, text = 'Layout properties:')
frame_materials  = ttk.LabelFrame(window, text = 'Materials:')
button_visualize = ttk.Button(window,  state = tk.NORMAL, text = 'Generate *.dzn file')

#flags
label_flag_allow_empty_wells                   = tk.Label(frame_flags, text = 'Allow empty wells')
label_flag_concentrations_on_different_rows    = tk.Label(frame_flags, text = 'Replicates on different rows')
label_flag_concentrations_on_different_columns = tk.Label(frame_flags, text = 'Replicates on different columns')
label_flag_replicates_on_different_plates      = tk.Label(frame_flags, text = 'Replicates on different plates')
label_flag_replicates_on_same_plate            = tk.Label(frame_flags, text = 'Replicates on the same plate')

check_flag_allow_empty_wells = ttk.Checkbutton(frame_flags, variable=flag_allow_empty_wells, onvalue = True, offvalue = False)
check_flag_concentrations_on_different_rows = ttk.Checkbutton(frame_flags, variable=flag_concentrations_on_different_rows, onvalue = True, offvalue = False)
check_flag_concentrations_on_different_columns = ttk.Checkbutton(frame_flags, variable=flag_concentrations_on_different_columns, onvalue = True, offvalue = False)
check_flag_replicates_on_different_plates = ttk.Checkbutton(frame_flags, variable=flag_replicates_on_different_plates, onvalue = True, offvalue = False)
check_flag_replicates_on_same_plate = ttk.Checkbutton(frame_flags, variable=flag_replicates_on_same_plate, onvalue = True, offvalue = False)

#dimentions
label_rows = tk.Label(frame_dimentions, text = 'Number of rows')
label_cols = tk.Label(frame_dimentions, text = 'Number of columns')

entry_rows = ttk.Entry(frame_dimentions, textvariable = num_rows, width = 6,
                           validate = 'all', validatecommand = (vcmd, '%P'))
entry_cols = ttk.Entry(frame_dimentions, textvariable = num_cols, width = 6,
                           validate = 'all', validatecommand = (vcmd, '%P'))

#layout
label_inner_empty_edge      = tk.Label(frame_layout, text = 'Inner edge')
label_size_empty_edge       = tk.Label(frame_layout, text = 'Empty edge size')
label_corner_empty_wells    = tk.Label(frame_layout, text = 'Empty corner size')
label_horizontal_cell_lines = tk.Label(frame_layout, text = 'Number of horizontal lines')
label_vertical_cell_lines   = tk.Label(frame_layout, text = 'Number of vertical lines')

check_inner_empty_edge = ttk.Checkbutton(frame_layout, variable=inner_empty_edge, onvalue = True, offvalue = False)
entry_size_empty_edge = ttk.Entry(frame_layout, textvariable = size_empty_edge, width = 6,
                           validate = 'all', validatecommand = (vcmd, '%P'))
entry_corner_empty_wells = ttk.Entry(frame_layout, textvariable = size_corner_empty_wells, width = 6,
                           validate = 'all', validatecommand = (vcmd, '%P'))
entry_horizontal_cell_lines = ttk.Entry(frame_layout, textvariable = horizontal_cell_lines, width = 6,
                           validate = 'all', validatecommand = (vcmd, '%P'))
entry_vertical_cell_lines = ttk.Entry(frame_layout, textvariable = vertical_cell_lines, width = 6,
                           validate = 'all', validatecommand = (vcmd, '%P'))

#materials
label_drgs = tk.Label(frame_materials, text = 'List of compounds \nwith concentrations')
label_ctrs = tk.Label(frame_materials, text = 'List of controls \nwith concentrations:')
entry_drgs = ttk.Entry(frame_materials, textvariable = drgs, width = 33)
entry_ctrs = ttk.Entry(frame_materials, textvariable = ctrs, width = 33)
help_drgs = tk.Label(frame_materials, text = '?', relief = 'raised')
help_ctrs = tk.Label(frame_materials, text = '?', relief = 'raised')



#-----UI placement----
#frame_flags.pack(expand=True, fill="both", padx=10, pady=10)
#frame_dimentions.pack(expand=True, fill="both", padx=10, pady=10)
#frame_layout.pack(expand=True, fill="both", padx=10, pady=10)
#frame_materials.pack(expand=True, fill="both", padx=10, pady=10)
#button_visualize.pack()
frame_flags.grid(     row=0,column=0,rowspan=2,columnspan=1,sticky="nw", padx=3, pady=3)
frame_dimentions.grid(row=0,column=1,rowspan=1,columnspan=1,sticky="nw", padx=3, pady=3)
frame_layout.grid(    row=1,column=1,rowspan=1,columnspan=1,sticky="nw", padx=3, pady=3)
frame_materials.grid( row=2,column=0,rowspan=1,columnspan=2,sticky="w",  padx=3, pady=3)
button_visualize.grid(row=3,column=0,rowspan=1,columnspan=2,sticky="ew", padx=3, pady=3)



label_flag_allow_empty_wells.grid(                  row=0,column=0,columnspan=1,sticky="w")
label_flag_concentrations_on_different_rows.grid(   row=1,column=0,columnspan=1,sticky="w")
label_flag_concentrations_on_different_columns.grid(row=2,column=0,columnspan=1,sticky="w")
label_flag_replicates_on_different_plates.grid(     row=3,column=0,columnspan=1,sticky="w")
label_flag_replicates_on_same_plate.grid(           row=4,column=0,columnspan=1,sticky="w")
check_flag_allow_empty_wells.grid(                  row=0,column=1,columnspan=1,sticky="w")
check_flag_concentrations_on_different_rows.grid(   row=1,column=1,columnspan=1,sticky="w")
check_flag_concentrations_on_different_columns.grid(row=2,column=1,columnspan=1,sticky="w")
check_flag_replicates_on_different_plates.grid(     row=3,column=1,columnspan=1,sticky="w")
check_flag_replicates_on_same_plate.grid(           row=4,column=1,columnspan=1,sticky="w")

label_rows.grid(row=0,column=0,columnspan=1,sticky="w")
entry_rows.grid(row=0,column=1,columnspan=1,sticky="w")
label_cols.grid(row=1,column=0,columnspan=1,sticky="w")
entry_cols.grid(row=1,column=1,columnspan=1,sticky="w")


label_inner_empty_edge.grid(     row=0,column=0,columnspan=1,sticky="w")
label_size_empty_edge.grid(      row=1,column=0,columnspan=1,sticky="w")
label_corner_empty_wells.grid(   row=2,column=0,columnspan=1,sticky="w")
label_horizontal_cell_lines.grid(row=3,column=0,columnspan=1,sticky="w")
label_vertical_cell_lines.grid(  row=4,column=0,columnspan=1,sticky="w")
check_inner_empty_edge.grid(     row=0,column=1,columnspan=1,sticky="w")
entry_size_empty_edge.grid(      row=1,column=1,columnspan=1,sticky="w")
entry_corner_empty_wells.grid(   row=2,column=1,columnspan=1,sticky="w")
entry_horizontal_cell_lines.grid(row=3,column=1,columnspan=1,sticky="w")
entry_vertical_cell_lines.grid(  row=4,column=1,columnspan=1,sticky="w")

label_drgs.grid(row=0,column=0,columnspan=1,sticky="w")
label_ctrs.grid(row=1,column=0,columnspan=1,sticky="w")
entry_drgs.grid(row=0,column=1,columnspan=1,sticky="w")
entry_ctrs.grid(row=1,column=1,columnspan=1,sticky="w")
help_drgs.grid( row=0,column=2,columnspan=1,sticky="w")
help_ctrs.grid( row=1,column=2,columnspan=1,sticky="w")


#----UI events and functions----
ut.CreateToolTip(label_flag_allow_empty_wells,                   text = 'If enabled, the model will check if there are any empty wells within a plate line.\nIf yes, the model will fail.\nIf disabled, then no such check is performed, i.e. a plate line can have empty wells within it.')
ut.CreateToolTip(label_flag_concentrations_on_different_rows,    text = 'If enabled, the model will try to force replicates of each drug to be placed on different rows.\nIf there are too many replicates, no such attempt will be made.\nIf the number of replicates per drug is small enough, it will also try to ensure that this drug placement is enforced across multiple plates.\nNOTE: if the model is unsatisfiable try to disable this option')
ut.CreateToolTip(label_flag_concentrations_on_different_columns, text = 'If enabled, the model will try to force replicates of each drug to be placed on different columns.\nIf there are too many replicates, no such attempt will be made.\nIf the number of replicates per drug is small enough, it will also try to ensure that this drug placement is enforced across multiple plates.\nNOTE: if the model is unsatisfiable try to disable this option')
ut.CreateToolTip(label_flag_replicates_on_different_plates,      text = 'If enabled, replicates of a drug can be placed on different microplates.')
ut.CreateToolTip(label_flag_replicates_on_same_plate,            text = 'If enabled, all replicates of a single drug must be placed on the same microplate.')

ut.CreateToolTip(label_rows, text = 'Enter the number of rows of the microplate')
ut.CreateToolTip(label_cols, text = 'Enter the number of columns of the microplate')

ut.CreateToolTip(label_inner_empty_edge,      text = 'When set to True, each plate line will have an edge of empty wells.\nWhen False, the whole plate will have an outer edge, but not each individual plate line.\nSee Figure 2 of COMPD article.')
ut.CreateToolTip(label_size_empty_edge,       text = 'How thick the empty edge is. The number must be no less than 0')
ut.CreateToolTip(label_corner_empty_wells,    text = 'The size of a corner filled with empty wells only. IGNORED by PLAID. The number must be no less than 0')
ut.CreateToolTip(label_horizontal_cell_lines, text = 'How many horizontal plate lines is required? No less than 1')
ut.CreateToolTip(label_vertical_cell_lines,   text = 'How many vertical plate lines is required? No less than 1')

ut.CreateToolTip(help_drgs, text = "List all the materials and their concentrations.\nWe use the format of Python dictionaries: {'Drug1': [5,'Concentration 1', 'Concentration 2'], 'Drug2': [10, '0.1', '0.5, '10']},\nwhich means that we will have:\n - Drug1 in concentrations 'Concentration 1' and 'Concentration 2' (5 replicates each) and\n - Drug2 in concentrations 0.1, 0.5 and 10 (10 replicates each).\nI recommend to write down the list of materials in the spreadsheet `Convert the compounds and controls.xlsx`,\navailable at https://github.com/astra-uu-se/COMPD, and then copy generated text here")
ut.CreateToolTip(help_ctrs, text = "List all the controls and their concentrations.\nWe use the same format as the list of materials.\nAs an illustration, here is another example, for controls:\n   {'Control1': [5,'Concentration 1', 'Concentration 2'], 'Control2': [10, '100'], 'Control3': [3, '100']},\nwhere we have three different controls.\nAs you can see, the dictionary format allows us to use various number of drugs/controls,\nwhere each drug/control can have its own number of replicates and/or the list concentrations")

check_flag_replicates_on_different_plates.configure(command = lambda:check_replicates_on_different_plates())
check_flag_replicates_on_same_plate.configure(command = lambda: check_replicates_on_same_plate())
button_visualize.configure(command = lambda: generate_dzn_file())

reset_dzn()