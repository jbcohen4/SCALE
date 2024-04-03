import tkinter as tk
from tkinter import LabelFrame, StringVar, OptionMenu, ttk, filedialog

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import pandas as pd

import backend
import exe_tools

from constants import DROPDOWN_MAPPING
INFINITY = float('inf') 


# Create Window for GUI
root = tk.Tk()

# Set title of the window
root.title("Radiation on BJT explorer")

# Set dimensions of the window
root.geometry("800x750")

# Set the background color of the root window

root.configure(bg="cadetBlue4")


# Adding frames for parts and specifications
def create_frame(row, column, text, width=2, height=2):
    frame = LabelFrame(root, text=text, padx=10, pady=10, borderwidth=2, relief="solid", width=width, height=height)
    frame.grid(row=row, column=column, padx=10, pady=10, columnspan=width, rowspan=height, sticky="ewns")

    return frame

# Validation function to allow only numerical values
def validate_numerical(value):
    if value == '':
        return True
    try:
        float(value)
        return True
    except ValueError:
        return False



def draw_graph():
    global plot_data
    # get data from user
    Selected_Part = var1.get()
    Selected_Specification = var2.get()
    Voltage = textbox_dataset_vcc.get()
    Temperature = textbox_temp.get() # at the moment, the backend can't use this
    Fluence_Min = textbox_fluences_min.get()
    Fluence_Max = textbox_fluences_max.get()
    
    # validate data and put in default values as needed
    Voltage = 5.0 if Voltage == "" else float(Voltage)
    Fluence_Min = -INFINITY if Fluence_Min == "" else float(Fluence_Min) * 10 ** 11
    Fluence_Max = +INFINITY if Fluence_Max == "" else float(Fluence_Max) * 10 ** 13

    data = backend.generate_data(Selected_Part, Selected_Specification, Voltage, Fluence_Min, Fluence_Max)

    plot_data = pd.DataFrame.from_dict(data, orient='index').transpose()
    print(plot_data)
    (x_axis_name, x_axis_data), (y_axis_name, y_axis_data) = data.items()
    xs = np.array(x_axis_data)
    ys = np.array(y_axis_data)


    
    graph_frame = create_frame(2, 0, "Graph", width=6, height=4)
    Chart_title = "Line Chart"

    fig, ax = plt.subplots()
    ax.plot(xs, ys)
    ax.set_xscale('log') # Set the x-axis to log scale
    ax.set_xlabel(x_axis_name)
    ax.set_ylabel(y_axis_name)
    ax.set_title(Chart_title)
    plt.subplots_adjust(left=0.2)

    # Embedding the plot in the Tkinter window
    canvas = FigureCanvasTkAgg(fig, master=graph_frame)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.grid(row=0, column=0, sticky="nsew")
    graph_frame.update_idletasks()

# Clear function 
def clear_function():
    textbox_dataset_vcc.delete(0, tk.END)
    textbox_temp.delete(0, tk.END)
    textbox_fluences_min.delete(0, tk.END)
    textbox_fluences_max.delete(0, tk.END)
    print("Clear all the fields")

    # Find and destroy the existing graph frame
    for widget in root.winfo_children():
        if isinstance(widget, LabelFrame) and widget.cget("text") == "Graph":
            widget.destroy()

# function to save the plot data to CSV file
def save_plot_data():
    global plot_data
    if not plot_data.empty:
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Save the plot data as CSV"
        )
        if filepath:
            plot_data.to_csv(filepath, index=False)
            print(f'Plot data saved to {filepath}')
        else:
            print('No file selected')
    else:
        print('No data to save')


# Frame 1
frame1 = create_frame(0, 0, "", width=2, height=2)

label_Parts = tk.Label(frame1, text="Parts:", padx=5, pady=5, font="Arial 10 bold")
label_Parts.grid(row=0, column=0, sticky="e")

# Dropdown Parts
options_part = list(DROPDOWN_MAPPING.keys())
var1 = StringVar()
var1.set(options_part[0])
dropdown_part = OptionMenu(frame1, var1, *options_part)
dropdown_part.grid(row=0, column=1, sticky="w", padx=5, pady=5)
dropdown_part.config(bg="white")

label_Specifications = tk.Label(frame1, text="Specifications:", padx=5, pady=5, font="Arial 9 bold")
label_Specifications.grid(row=1, column=0, sticky="e")

# Dropdown Specifications
selected_part = options_part[0]
options_specifications = DROPDOWN_MAPPING[selected_part]
var2 = StringVar()
var2.set(options_specifications[0])
dropdown_specifications = OptionMenu(frame1, var2, *options_specifications)
dropdown_specifications.grid(row=1, column=1, sticky="w", padx=5, pady=5)
dropdown_specifications.config(bg="white")

# Function to update Specifications Dropdown based on Part Dropdown selection
def update_dropdown_specifications(*args):
    selected_part = var1.get()
    options_specifications = DROPDOWN_MAPPING[selected_part]
    dropdown_specifications['menu'].delete(0, 'end') 
    for spec in options_specifications:
        dropdown_specifications['menu'].add_command(label=spec, command=tk._setit(var2, spec))
    var2.set(options_specifications[0])  # Set default value for var2

# Trace changes in Dropdown 1 and update Dropdown 2 accordingly
var1.trace_add('write', update_dropdown_specifications)

label_dataset = tk.Label(frame1, text="Dataset:", padx=5, pady=5, font="Arial 9 bold")
label_dataset.grid(row=2, column=0, sticky="we")

label_dataset_vcc = tk.Label(frame1, text="VCC(0~25,step-1):", padx=5, pady=5, font="Arial 9 bold")
label_dataset_vcc.grid(row=3, column=0, sticky="e")

# Text Entry for Dataset with border and padding
validate_dataset_vcc = (root.register(validate_numerical), '%P')
textbox_dataset_vcc = ttk.Entry(frame1, style="TEntry", validate="key", validatecommand=validate_dataset_vcc)
textbox_dataset_vcc.grid(row=3, column=1, sticky="w")

# Frame 2
frame2 = create_frame(0, 2, "", width=2, height=2)

label_temp = tk.Label(frame2, text="Temperature (C):", padx=5, pady=5, font="Arial 9 bold")
label_temp.grid(row=0, column=0, sticky="e")

# Text Entry for Temperature with border and padding
validate_temp = (root.register(validate_numerical), '%P')
textbox_temp = ttk.Entry(frame2, style="TEntry", validate="key", validatecommand=validate_temp)
textbox_temp.grid(row=0, column=1, sticky="w")

label_fluences_min = tk.Label(frame2, text="Fluences Min(n/cm^2):", padx=5, pady=5, font="Arial 9 bold")
label_fluences_min.grid(row=1, column=0, sticky="e")

# Text Entry for Fluences Min with border and padding
validate_fluences_min = (root.register(validate_numerical), '%P')
textbox_fluences_min = ttk.Entry(frame2, style="TEntry", validate="key", validatecommand=validate_fluences_min)
textbox_fluences_min.grid(row=1, column=1, sticky="w")
label_fluences_range1 = tk.Label(frame2, text="e^11", padx=5, pady=5, font="Arial 9 bold")
label_fluences_range1.grid(row=1, column=2, sticky="e")

label_fluences_max = tk.Label(frame2, text="Fluences Max(n/cm^2):", padx=5, pady=5, font="Arial 9 bold")
label_fluences_max.grid(row=2, column=0, sticky="e")

# Text Entry for Fluences Max with border and padding
validate_fluences_max = (root.register(validate_numerical), '%P')
textbox_fluences_max = ttk.Entry(frame2, style="TEntry", validate="key", validatecommand=validate_fluences_max)
textbox_fluences_max.grid(row=2, column=1, sticky="w")
label_fluences_range2 = tk.Label(frame2, text="e^13", padx=5, pady=5, font="Arial 9 bold")
label_fluences_range2.grid(row=2, column=2, sticky="e")

# Frame 3
frame3 = create_frame(0, 4, "", width=4)
# Button size
button_width = 10
button_height = 1

# Button Design
button_bg_color = "lightgray"
button_fg_color = "black"
button_border_color = "black"
button_border_width = 2

#Buttons

execute_button = tk.Button(frame3, text="Execute", command=draw_graph, width=button_width, height=button_height, bg=button_bg_color, fg=button_fg_color, bd=button_border_width, relief="solid")
execute_button.grid(row=0, column=1, padx=5, pady=5)

save_button = tk.Button(frame3, text="Save", command=save_plot_data, width=button_width, height=button_height, bg=button_bg_color, fg=button_fg_color, bd=button_border_width, relief="solid")
save_button.grid(row=1, column=1, padx=5, pady=5)

clear_button = tk.Button(frame3, text="Clear", command=clear_function, width=button_width, height=button_height, bg=button_bg_color, fg=button_fg_color, bd=button_border_width, relief="solid")
clear_button.grid(row=2, column=1, padx=5, pady=5)



def on_closing():
    """I was having issues with the application not closing all the way when I pressed the X button on the GUI.
    This function fixed that."""
    plt.close('all')  # Close all Matplotlib figures
    root.destroy()  # Destroy the Tkinter window

root.protocol("WM_DELETE_WINDOW", on_closing) # set the 'on_closing()' function to be called when you exit the program

# Running the window
root.mainloop()