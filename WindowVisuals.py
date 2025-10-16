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
# Description:  GUI for displaying microplate layouts
#
# Authors: Ramiz GINDULLIN (ramiz.gindullin@it.uu.se)
# Version: 1.0
# Last Revision: October 2025
#


import matplotlib as mpl
from matplotlib import pyplot
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import numpy as np

import tkinter as tk
from tkinter import ttk, VERTICAL, RIGHT, Y, LEFT, BOTH

import ast
from typing import List, Dict, Sequence, Union

from utility import transform_coordinate, read_csv_file, transform_concentrations_to_alphas, to_number_if_possible

# Cache colormap at module level for performance optimization
COLORMAP_TAB20 = pyplot.get_cmap('tab20')


def draw_plates(parent: tk.Widget, figure_name_template: str, text_array: Sequence[str], 
                num_rows: int = 16, num_cols: int = 24, control_names: Sequence[str] = ()) -> None:
    """Load CSV data, analyze it, split into layouts, and draw plates with material scales.
    
    Args:
        parent: Parent tkinter widget
        figure_name_template: Template for saved figure names
        text_array: List of CSV lines to process
        num_rows: Number of rows in microplate
        num_cols: Number of columns in microplate  
        control_names: List of control material names
    """
    layouts_dict: Dict[str, List[List[str]]] = {}
    concentrations_list: Dict[str, List[Union[str, float, int]]] = {}
    
    for line in text_array:
        if line == '\n':  # happens on Windows machines
            continue
        array = line.strip().split(',')
        if array[0] in layouts_dict:
            layouts_dict[array[0]].append(array[1:])
        else:
            layouts_dict[array[0]] = [array[1:]]

        if array[2] in concentrations_list:
            if to_number_if_possible(array[3]) not in concentrations_list[array[2]]:
                concentrations_list[array[2]].append(to_number_if_possible(array[3]))
        else:
            concentrations_list[array[2]] = [to_number_if_possible(array[3])]
            
    # Sort concentrations for each material
    for material in concentrations_list:
        try:
            concentrations_list[material] = sorted(concentrations_list[material])
        except TypeError:
            # Handle mixed types by converting to strings and sorting
            concentrations_list[material] = [str(x) for x in concentrations_list[material]]
            concentrations_list[material] = sorted(concentrations_list[material])

    # Generate colors for materials using cached tab20 colormap
    color_index = 0
    material_colors: Dict[str, np.ndarray] = {}
    for material in sorted(concentrations_list.keys()):
        material_colors[material] = np.array(COLORMAP_TAB20(color_index)[:3])
        color_index += 1
        if color_index >= 20:
            color_index = 0

    # Create main plate visualization tabs
    tab_control = ttk.Notebook(parent)
    for layout in layouts_dict:
        draw_plate(tab_control, figure_name_template, layout,
                   layouts_dict[layout], material_colors, concentrations_list, 
                   num_rows, num_cols, control_names)
    tab_control.grid(row=0, column=0, padx=10, pady=2)

    # Create scrollable material scale panel
    tab_control2 = ttk.Frame(parent, width=400)
    canvas_right = tk.Canvas(tab_control2, width=400, height=500)
    canvas_right.pack(side="left", fill="both", expand=True)

    scrollbar = ttk.Scrollbar(tab_control2, orient="vertical",
                              command=canvas_right.yview)
    scrollbar.pack(side="right", fill="y")

    canvas_right.configure(yscrollcommand=scrollbar.set)
    scrollable_frame = ttk.Frame(canvas_right)

    scrollable_frame.bind(
        "<Configure>", lambda event: update_scroll_region(event, canvas_right))

    # Draw material concentration scales
    for material in material_colors:
        material_color = material_colors[material]
        concentration_material = concentrations_list[material]
        draw_material_scale(scrollable_frame, material,
                            material_color, concentration_material)

    canvas_right.create_window((0, 0), window=scrollable_frame, anchor="nw")
    tab_control2.grid(row=0, column=1, padx=10, pady=2)


def update_scroll_region(event: tk.Event, canvas: tk.Canvas) -> None:
    """Update canvas scroll region when content changes.
    
    Args:
        event: Tkinter event object
        canvas: Canvas widget to update
    """
    canvas.configure(scrollregion=canvas.bbox("all"))


def draw_plate(parent: ttk.Notebook, figure_name_template: str, layout: str, layout_array: Sequence[Sequence[str]],
               material_colors: Dict[str, np.ndarray], concentrations_list: Dict[str, Sequence[Union[str, float, int]]],
               num_rows: int = 16, num_cols: int = 24, control_names: Sequence[str] = ()) -> None:
    """Draw a single microplate layout visualization.
    
    Args:
        parent: Parent tkinter widget
        figure_name_template: Template for saved figure name
        layout: Layout identifier/name
        layout_array: Array of layout data
        material_colors: Dictionary mapping materials to colors
        concentrations_list: Dictionary of material concentrations
        num_rows: Number of rows in microplate
        num_cols: Number of columns in microplate
        control_names: List of control material names (shown as circles)
    """
    # Create figure
    fig = Figure()
    try:
        ax = fig.add_subplot(111)

        # Ensure consistent orientation (wider dimension is horizontal)
        if num_cols > num_rows:
            num_rows, num_cols = num_cols, num_rows
            is_switched = True
        else:
            is_switched = False

        ax.grid(True)
        ax.set_xticks(np.arange(0, num_rows + 1, 1))
        ax.set_yticks(np.arange(0, num_cols + 1, 1))
        ax.set_aspect('equal')

        # Group wells by material
        materials: Dict[str, List[List[str]]] = {}
        for line in layout_array:
            if line[1] in materials:
                materials[line[1]].append([line[0]] + line[1:])
            else:
                materials[line[1]] = [[line[0]] + line[1:]]

        # Plot each material
        for material in materials:
            # Use circles for controls, squares for other materials
            if material in control_names:
                marker = 'o'
            else:
                marker = 's'

            alpha_values = transform_concentrations_to_alphas(concentrations_list[material])

            x_coords: List[float] = []
            y_coords: List[float] = []
            alphas: List[float] = []
            
            for well in materials[material]:
                if is_switched:
                    [y_coord, x_coord] = transform_coordinate(well[0])
                else:
                    [x_coord, y_coord] = transform_coordinate(well[0])
                x_coords.append(x_coord + 0.5)
                y_coords.append(y_coord + 0.5)
                
                try:
                    alphas.append(alpha_values[to_number_if_possible(well[2])])
                except (KeyError, IndexError):
                    # Handle missing concentration data gracefully
                    alphas.append(alpha_values[well[2]])

            colors = [material_colors[material] for i in range(len(x_coords))]
            ax.scatter(x_coords, y_coords, marker=marker, c=colors, s=80,
                       edgecolor='black', alpha=alphas)

        ax.set_xlim(0, num_rows)
        ax.set_ylim(0, num_cols)

        # Save figure before embedding
        fig.savefig(figure_name_template + layout + '.png')

        # Create tab and canvas
        tab = ttk.Frame(parent)
        canvas = FigureCanvasTkAgg(fig, master=tab)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        parent.add(tab, text=layout)

        # Store canvas reference for cleanup
        tab.canvas_ref = canvas

    except Exception:
        # Ensure figure resources are freed if plotting fails
        try:
            pyplot.close(fig)
        except Exception:
            pass
        raise


def draw_material_scale(parent: tk.Widget, material_name: str, color: np.ndarray, 
                        concentrations: Sequence[Union[str, float, int]]) -> None:
    """Draw a concentration scale for a specific material.
    
    Args:
        parent: Parent tkinter widget
        material_name: Name of the material
        color: RGB color array for the material
        concentrations: List of concentration values
    """
    # Create alpha values from 0.3 to 1
    alphas_dict = transform_concentrations_to_alphas(concentrations)
    alphas = [alphas_dict[x] for x in alphas_dict]

    rgba_colors = np.zeros((1, len(concentrations), 4))
    rgba_colors[:, :, 0] = color[0]
    rgba_colors[:, :, 1] = color[1]
    rgba_colors[:, :, 2] = color[2]
    rgba_colors[:, :, 3] = alphas  # Set alpha for the alpha channel

    # Create Figure
    fig = Figure(figsize=(4, 2))
    try:
        ax = fig.add_subplot(111)

        ax.imshow(rgba_colors, extent=[0, len(concentrations), 0, 1], aspect='auto')
        ax.set_title(material_name)

        x_ticks = np.linspace(0, len(concentrations), len(concentrations))
        x_labels = [str(i) for i in alphas_dict]
        ax.set_xticks(x_ticks)
        ax.set_xticklabels(x_labels)
        ax.set_yticks([])  # Hide y-axis ticks as it's a 1D spectrum

        tab2 = ttk.Frame(parent)
        canvas = FigureCanvasTkAgg(fig, master=tab2)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        tab2.pack(fill="both", expand=True, padx=1, pady=5)

        # Store canvas reference for cleanup
        tab2.canvas_ref = canvas

    except Exception:
        # Ensure figure resources are freed if scale creation fails
        try:
            pyplot.close(fig)
        except Exception:
            pass
        raise


def visualize(file_path: str, figure_name_template: str, rows: str, cols: str, 
              control_names: str = '[]') -> None:
    """Main visualization window for microplate layouts.
    
    Args:
        file_path: Path to CSV data file
        figure_name_template: Template for saved figure names
        rows: Number of rows as string
        cols: Number of columns as string
        control_names: JSON string of control names (default: '[]')
    """
    def cleanup_and_close() -> None:
        """Properly cleanup all matplotlib resources before closing."""
        try:
            # Find and cleanup all canvas references
            cleanup_canvas_widgets(window)
            pyplot.close('all')  # Close any remaining pyplot figures
        except Exception as e:
            print(f"Warning during cleanup: {e}")
        finally:
            window.destroy()

    window: tk.Tk = tk.Tk()
    window.title("Visualize GUI")
    window.protocol('WM_DELETE_WINDOW', cleanup_and_close)  # Handle window X button

    try:
        draw_plates(window, figure_name_template, read_csv_file(file_path),
                    num_rows=int(rows), num_cols=int(cols), 
                    control_names=ast.literal_eval(control_names))
        window.geometry('+%d+%d' % (10, 10))
        window.mainloop()
    except Exception as e:
        print(read_csv_file(file_path))
        print(f"Error in visualization: {e}")
        cleanup_and_close()


def cleanup_canvas_widgets(widget: tk.Misc) -> None:
    """Recursively cleanup matplotlib canvases in widget tree.
    
    Args:
        widget: Root widget to start cleanup from
    """
    if hasattr(widget, 'canvas_ref'):
        try:
            canvas = widget.canvas_ref
            fig = canvas.figure
            canvas.get_tk_widget().destroy()
            # Close the figure explicitly to free memory from backend
            pyplot.close(fig)
            del canvas
        except (AttributeError, tk.TclError):
            # Canvas might already be destroyed
            pass

    # Recursively check children
    try:
        for child in widget.winfo_children():
            cleanup_canvas_widgets(child)
    except (AttributeError, tk.TclError):
        # Widget might be destroyed during iteration
        pass