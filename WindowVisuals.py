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



import matplotlib as mpl
from matplotlib import pyplot
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,NavigationToolbar2Tk)

import numpy as np

import tkinter as tk
from tkinter import ttk, VERTICAL, RIGHT, Y, LEFT, BOTH

import ast

from utility import transform_coordinate, read_csv_file, transform_concentrations_to_alphas, to_int_if_possible


# main function that loads the csv file, analyzes it, splits it into separate layouts and passes it to draw_plates(**kwargs),
# and, lastly, draws first 5 material concentration scales
def draw_plates(parent, figure_name_template, text_array, m = 16, n = 24, control_names = []):
    layouts_dict = {}
    concentrations_list = {}
    for line in text_array:
        array = line.strip().split(',')
        if array[0] in layouts_dict:
            layouts_dict[array[0]].append(array[1:])
        else:
            layouts_dict[array[0]] = [array[1:]]

        if array[2] in concentrations_list:
            if to_int_if_possible(array[3]) not in concentrations_list[array[2]]:
                concentrations_list[array[2]].append(to_int_if_possible(array[3]))
            else:
                None
        else:
            concentrations_list[array[2]] = [to_int_if_possible(array[3])]
    for material in concentrations_list:
        concentrations_list[material] = sorted(concentrations_list[material])

    #prng = np.random.RandomState(100)
    colormap = pyplot.get_cmap('tab20')
    color = 0
    material_colors = {}
    for material in sorted(concentrations_list.keys()):
        material_colors[material] = np.array(colormap(color)[:3])
        color += 1
        if color >= 20:
            color = 0
    
    tab_control = ttk.Notebook(parent)
    for layout in layouts_dict:
        draw_plate(tab_control,figure_name_template,layout,layouts_dict[layout],material_colors,concentrations_list,m,n,control_names)
    tab_control.grid(row = 1, column = 0, padx = 10, pady = 2)
    
    tab_control2 = ttk.Frame(parent, width = 400)
    canvas_right = tk.Canvas(tab_control2, width = 400, height = 600)
    canvas_right.pack(side="left", fill="both", expand=True)
    
    scrollbar = ttk.Scrollbar(tab_control2, orient="vertical", command=canvas_right.yview)
    scrollbar.pack(side="right", fill="y")
    
    canvas_right.configure(yscrollcommand=scrollbar.set)
    scrollable_frame = ttk.Frame(canvas_right)
    
    scrollable_frame.bind("<Configure>", lambda event: update_scroll_region(event, canvas_right))
    
    i = 0
    for material in material_colors:
        i += 1
        material_color = material_colors[material]
        concentration_material = concentrations_list[material]
        draw_material_scale(scrollable_frame, material, material_color, concentration_material)
    
    canvas_right.create_window((0, 0), window=scrollable_frame, anchor="nw")
    
    tab_control2.grid(row = 1, column = 1, padx = 10, pady = 2)

def update_scroll_region(event, canvas):
    canvas.configure(scrollregion=canvas.bbox("all"))

 
# draws a microplate layout
# note that if concentrations_list is not empty, then the wells containing a material with a name from a list, will be depicted as a circle
# otherwise a material will be depicted as a square
def draw_plate(parent,figure_name_template,layout,layout_array, material_colors, concentrations_list,
               m = 16, n = 24, control_names = []):
    fig1 = pyplot.figure()
    
    if n > m:
        m,n = n,m
        is_switch = True
    else:
        is_switch = False
    pyplot.xlim(0, m)
    pyplot.ylim(0, n)

    pyplot.grid(True)
    pyplot.xticks(np.arange(0, m, 1))
    pyplot.yticks(np.arange(0, n, 1))
    pyplot.axis('scaled')

    materials = {}
    # line = ['D03', 'ctrl1', '1', 'ctrl1_1'], e.g.
    for line in layout_array:
        if line[1] in materials:
            materials[line[1]].append([line[0]] + line[1:])
        else:
            materials[line[1]] = [[line[0]] + line[1:]]

    for material in materials:
        if material in control_names:
            marker = 'o'
        else:
            marker = 's'

        alpha_values = transform_concentrations_to_alphas(concentrations_list[material])

        x_coords = []
        y_coords = []
        alphas = []
        for well in materials[material]:
            if is_switch:
                [y, x] = transform_coordinate(well[0])
            else:
                [x, y] = transform_coordinate(well[0])
            x_coords.append(x+0.5)
            y_coords.append(y+0.5)
            alphas.append(alpha_values[to_int_if_possible(well[2])])
        pyplot.scatter(x_coords, y_coords, marker=marker, c = material_colors[material], s = 80, edgecolor='black', alpha=alphas)
    
    pyplot.savefig(figure_name_template + layout + '.png')
    
    tab = ttk.Frame(parent)
    canvas = FigureCanvasTkAgg(fig1, master = tab)
    canvas.draw()
    canvas.get_tk_widget().pack()
    parent.add(tab, text = layout)
    
        
# draw a scale representing different concentration of a material
def draw_material_scale(parent, material_name, color, concentrations):
    # Create alpha values from 0.3 to 1
    alphas_dict =  transform_concentrations_to_alphas(concentrations)

    alphas = [alphas_dict[x] for x in alphas_dict]

    rgba_colors = np.zeros((1, len(concentrations), 4))
    rgba_colors[:, :, 0] = color[0]
    rgba_colors[:, :, 1] = color[1]
    rgba_colors[:, :, 2] = color[2]
    rgba_colors[:, :, 3] = alphas # Set alpha for the alpha channel

    fig1 = pyplot.figure(figsize=(4, 2))
    pyplot.imshow(rgba_colors, extent=[0, len(concentrations), 0, 1])

    pyplot.title(material_name)
    pyplot.xlabel('Concentrations')
    x_ticks = np.linspace(1, len(concentrations), len(concentrations))
    x_labels = [str(i) for i in alphas_dict]
    pyplot.xticks(x_ticks, x_labels)
    pyplot.yticks([]) # Hide y-axis ticks as it's a 1D spectrum
    
    pyplot.axis('tight')
    
    tab2 = ttk.Frame(parent)
    canvas = FigureCanvasTkAgg(fig1, master = tab2)
    canvas.draw()
    canvas.get_tk_widget().pack(padx = 2, pady = 2)
    tab2.pack(fill="both", expand=True)
    
# main window of a visuzliation.
def visualize(file_path, figure_name_template, rows, cols, control_names = '[]'):
    window = tk.Tk()
    quit_button = ttk.Button(window, text = 'close window')
    quit_button.grid(row = 0, column = 0, columnspan = 2)
    quit_button.configure(  command = lambda: [pyplot.close('all'), window.destroy()])
    window.title("Visualize GUI")
    window.overrideredirect(True) # disable your window to be closed by regular means
    
    try:
        draw_plates(window, figure_name_template, read_csv_file(file_path), m = int(rows), n = int(cols),
                    control_names = ast.literal_eval(control_names))
        window.geometry('+%d+%d'%(10,10))
    except:
        # if error, write down the csv file to help the troubleshooting
        print(read_csv_file(file_path))
        window.destroy()