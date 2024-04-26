import tkinter as tk

from tkinter import LabelFrame, StringVar, OptionMenu, ttk
from PIL import Image, ImageTk
from tkinter import filedialog
from tkinter import Label, LabelFrame, StringVar, OptionMenu, ttk, filedialog

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd

import backend
import exe_tools

from constants import *
INFINITY = float('inf') 

# Global variables to keep track of the chart and axes
global fig, ax, canvas, current_y_scale 
current_y_scale = 'linear'

# Create Window for GUI
root = tk.Tk()

# Set title of the window
root.title("Radiation on BJT explorer")

# Set dimensions of the window
root.geometry("1000x800")

# Set the background color of the root window
root.configure(bg="white")

# Adding frames for parts and specifications
def create_frame(row, column, text, width=2, height=2, borderwidth = 2, bg = "white", padx=10, pady=10,highlightbackground="white", highlightthickness=0):
    frame = LabelFrame(root, text=text, padx=padx, pady=pady, borderwidth=borderwidth, relief="solid", width=width, height=height, bg=bg,highlightbackground=highlightbackground, highlightthickness=highlightthickness)
    frame.grid(row=row, column=column, padx=padx, pady=pady, columnspan=width, rowspan=height, sticky="ewns")
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

def setup_graph():
    global fig, ax, canvas, current_y_scale
  
    graph_frame = create_frame(4, 0, "Graph", width=20, height=4)
    fig, ax = plt.subplots()
    canvas = FigureCanvasTkAgg(fig, master=graph_frame)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.grid(row=0, column=2, sticky="nsew")
    graph_frame.update_idletasks()
    
    return graph_frame

def draw_graph():
    global plot_data, fig, ax, canvas, current_y_scale
    # get data from user inputs
    Selected_Part = var1.get()
    Selected_Specification = var2.get()
    VCC = textbox_dataset_vcc.get()
    VEE = textbox_dataset_vee.get()
    Temperature = textbox_temp.get() # at the moment, the backend can't use this
    Fluence_Min = textbox_fluences_min.get()
    Fluence_Max = textbox_fluences_max.get()
    
    # validate data and put in default values as needed
    if Selected_Part == "AD590":
        VCC = 5.0 if VCC == "" else float(VCC)
        VEE = None if VEE == "" else float(VEE)
    else:
        VCC = 15.0 if VCC == "" else float(VCC)
        VEE = -15.0 if VEE == "" else float(VEE)
    Fluence_Min = -INFINITY if Fluence_Min == "" else float(Fluence_Min) * 10 ** 11
    Fluence_Max = +INFINITY if Fluence_Max == "" else float(Fluence_Max) * 10 ** 13

    data = backend.generate_data(Selected_Part, Selected_Specification, VCC, VEE, Temperature, Fluence_Min, Fluence_Max)
    
    plot_data = pd.DataFrame.from_dict(data, orient='index').transpose()
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(plot_data)
    (x_axis_name, x_axis_data), (y_axis_name, y_axis_data) = data.items()
    xs = np.array(x_axis_data)
    ys = np.array(y_axis_data)
    
    # Creatw new graph frame
    graph_frame = setup_graph()
    ax.plot(xs, ys, color = "maroon")

    if Selected_Part in DOTTER_SPECIFICATIONS:
        if Selected_Specification in DOTTER_SPECIFICATIONS[Selected_Part]:
            dotted_line = DOTTER_SPECIFICATIONS[Selected_Part][Selected_Specification]
            if dotted_line:
                ax.axhline(y= dotted_line , color = "black", linestyle = "--")

    ax.set_xscale('log') # Set the x-axis to log scale
    ax.set_yscale(current_y_scale)  # Set the y-axis to current scale - which is linear in begining.
    ax.set_xlabel(x_axis_name)
    ax.set_ylabel(y_axis_name)

    # Define a custom formatter function
    def custom_formatter(x, pos):
        if x == 1e11:  # Check if the tick is at 10^11
            return 'pre_rad'
        else:
            return f'{x:.0e}'  # Default scientific notation

    # Apply the custom formatter to the x-axis
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(custom_formatter))
    plt.subplots_adjust(left=0.2)
    canvas.draw_idle()

# Function to change the scale of the graph on y-axis
def change_scale():
    global fig, ax, canvas, current_y_scale
    # Toggle between 'linear' and 'log'
    current_y_scale = 'linear' if current_y_scale == 'log' else 'log'
    ax.set_yscale(current_y_scale)
    fig.canvas.draw_idle()

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


# Clear function 
def clear_function():
    # Clear text entries
    textbox_dataset_vcc.delete(0, tk.END)
    textbox_dataset_vee.delete(0, tk.END)
    textbox_temp.delete(0, tk.END)
    textbox_fluences_min.delete(0, tk.END)
    textbox_fluences_max.delete(0, tk.END)
    print("Clear all the fields")

    # Find and destroy the existing graph frame
    for widget in root.winfo_children():
        if isinstance(widget, LabelFrame) and widget.cget("text") == "Graph":
            widget.destroy()

# Frame 0
frame0 = create_frame(0,0,"",width=10,height= 2,borderwidth=0, padx=0, pady=0, bg="gold")
asu_logo = Image.open(exe_tools.adjust_path('images/ASU_logo.png'))
asu_logo_resized = asu_logo.resize((144, 81), Image.LANCZOS)  
asu_logo_tk = ImageTk.PhotoImage(asu_logo_resized)

canvas = tk.Canvas(frame0, width=asu_logo_tk.width(), height=asu_logo_tk.height(), bg="gold", bd=0, highlightthickness=0)
canvas.create_image(0, 0, anchor="nw", image=asu_logo_tk)
canvas.pack(anchor="n", padx=2, pady=2)

# Set column 0 to expand
root.grid_columnconfigure(0, weight=1)  

# Frame 1
frame1 = create_frame(2, 0, "", width=2, height=2, borderwidth=0, highlightbackground="brown4", highlightthickness=3, bg="gold")
label_Parts = tk.Label(frame1, text="Parts:", padx=5, pady=5, font="Arial 9 bold", bg="gold")
label_Parts.grid(row=0, column=0, sticky="e")

# Dropdown Parts
options_part = list(DROPDOWN_MAPPING.keys())
var1 = StringVar()
var1.set(options_part[0])
dropdown_part = OptionMenu(frame1, var1, *options_part)
dropdown_part.grid(row=0, column=1, sticky="w", padx=5, pady=5)
dropdown_part.config(bg="white")

label_Specifications = tk.Label(frame1, text="Specifications:", padx=5, pady=5, font="Arial 9 bold", bg="gold")
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

# Frame 2
frame2 = create_frame(2, 2, "", width=2, height=2, borderwidth=0, highlightbackground="brown4", highlightthickness=3, bg="gold")
# label_dataset = tk.Label(frame2, text="Dataset:", padx=5, pady=5, font="Arial 9 bold", bg="gold")
# label_dataset.grid(row=0, column=0, sticky="we")

label_dataset_vcc = tk.Label(frame2, text="VCC (0~25, step-1):", padx=5, pady=5, font="Arial 9 bold", bg="gold")
label_dataset_vcc.grid(row=0, column=0, sticky="e")

#set default VCC & VEE based on spec
def update_default_voltage(*args):
    textbox_dataset_vcc.delete(0, 'end')
    textbox_dataset_vee.delete(0, 'end')
    textbox_temp.delete(0, 'end')
    textbox_fluences_min.delete(0, 'end')
    textbox_fluences_max.delete(0, 'end')
    if var1.get() == 'AD590':
        default_voltage = "5"
    else:
        default_voltage = "15"
        textbox_dataset_vee.insert(0, -1 * float(default_voltage))
    textbox_dataset_vcc.insert(0, float(default_voltage))
    textbox_temp.insert(0, "25")
    textbox_fluences_min.insert(0, "4.03")
    textbox_fluences_max.insert(0, "10")
    

# Whenever the spec changes, update the default voltage accordingly
var1.trace_add('write', update_default_voltage)

# Text Entry for Dataset with border and padding
validate_dataset_vcc = (root.register(validate_numerical), '%P')
textbox_dataset_vcc = ttk.Entry(frame2, style="TEntry", validate="key", validatecommand=validate_dataset_vcc,width=7)
textbox_dataset_vcc.insert(0,"5")
textbox_dataset_vcc.grid(row=0, column=1, sticky="w")

label_dataset_vee = tk.Label(frame2, text= "VEE (-25~0, step-1):", padx=5, pady=5, font="Arial 9 bold", bg="gold")
label_dataset_vee.grid(row=1, column=0,sticky="e")

validate_dataset_vee = (root.register(validate_numerical), '%P')
textbox_dataset_vee = ttk.Entry(frame2, style="TEntry", validate="key", validatecommand=validate_dataset_vee,width=7)
textbox_dataset_vee.grid(row=1, column=1, sticky="w")

label_temp = tk.Label(frame2, text="Circuit Temp (C):", padx=10, pady=10, font="Arial 9 bold", bg="gold")
label_temp.grid(row=2, column=0, sticky="e")

# Text Entry for Temperature with border and padding
validate_temp = (root.register(validate_numerical), '%P')
textbox_temp = ttk.Entry(frame2, style="TEntry", validate="key", validatecommand=validate_temp, width=7)
textbox_temp.insert(0,"25")
textbox_temp.grid(row=2, column=1, sticky="w")

# Frame 3
frame3 = create_frame(2, 4, "", width=2, height=2, borderwidth=0, highlightbackground="brown4", highlightthickness=3, bg="gold")
label_neutron_type = tk.Label(frame3, text="Neutron Type:", padx=5, pady=5, font="Arial 9 bold", bg="gold")
label_neutron_type.grid(row=0, column=0, sticky="e")

# Dropdown Neutron Type
options_neutron = NEUTRON_TYPE
var_neutron = StringVar()
var_neutron.set(options_neutron[0])
dropdown_neutron = OptionMenu(frame3, var_neutron, *options_neutron)
dropdown_neutron.grid(row=0, column=1, sticky="w", padx=5, pady=5)
dropdown_neutron.config(bg="white")
neutron_type_uom = tk.Label(frame3, text="equ.", padx=5, pady=5, font="Arial 9 bold", bg="gold")
neutron_type_uom.grid(row=0, column=2, sticky="e")

label_fluences_min = tk.Label(frame3, text="Fluences Min(n/cm^2):", padx=10, pady=10, font="Arial 9 bold", bg="gold")
label_fluences_min.grid(row=1, column=0, sticky="e")

# Text Entry for Fluences Min with border and padding
validate_fluences_min = (root.register(validate_numerical), '%P')
textbox_fluences_min = ttk.Entry(frame3, style="TEntry", validate="key", validatecommand=validate_fluences_min,width=10)
textbox_fluences_min.insert(0,"4.03")
textbox_fluences_min.grid(row=1, column=1, sticky="w")
label_fluences_range1 = tk.Label(frame3, text="e^11", padx=5, pady=5, font="Arial 9 bold", bg="gold")
label_fluences_range1.grid(row=1, column=2, sticky="e")

label_fluences_max = tk.Label(frame3, text="Fluences Max(n/cm^2):", padx=10, pady=10, font="Arial 9 bold", bg="gold")
label_fluences_max.grid(row=2, column=0, sticky="e")

# Text Entry for Fluences Max with border and padding
validate_fluences_max = (root.register(validate_numerical), '%P')
textbox_fluences_max = ttk.Entry(frame3, style="TEntry", validate="key", validatecommand=validate_fluences_max, width=10)
textbox_fluences_max.insert(0,"10")
textbox_fluences_max.grid(row=2, column=1, sticky="w")
label_fluences_range2 = tk.Label(frame3, text="e^13", padx=5, pady=5, font="Arial 9 bold", bg="gold")
label_fluences_range2.grid(row=2, column=2, sticky="e")

# Frame 4
frame4 = create_frame(2, 6,"",width=2, height=2, borderwidth=0, highlightbackground="brown4", highlightthickness=3, bg="gold")
# Button size
button_width = 10
button_height = 1

# Button Design
button_bg_color = "brown4"
button_fg_color = "white"
button_border_color = "white"
button_border_width = 2

#Buttons
execute_button = tk.Button(frame4, text="Execute", command=draw_graph, width=button_width, height=button_height, bg=button_bg_color, fg=button_fg_color, bd=0 , relief="solid")
execute_button.grid(row=0, column=1, padx=10, pady=5)

change_scale_button = tk.Button(frame4, text="Change Scale", command=change_scale, width=button_width, height=button_height, bg=button_bg_color, fg=button_fg_color, bd=0, relief="solid")
change_scale_button.grid(row=1, column=1, padx=10, pady=5)

save_button = tk.Button(frame4, text="Save", command=save_plot_data, width=button_width, height=button_height, bg=button_bg_color, fg=button_fg_color, bd=0, relief="solid")
save_button.grid(row=2, column=1, padx=10, pady=5)

clear_button = tk.Button(frame4, text="Clear", command=clear_function, width=button_width, height=button_height, bg=button_bg_color, fg=button_fg_color, bd=0, relief="solid")
clear_button.grid(row=3, column=1, padx=10, pady=5)

def on_closing():
    """I was having issues with the application not closing all the way when I pressed the X button on the GUI.
    This function fixed that."""
    plt.close('all')  # Close all Matplotlib figures
    root.destroy()  # Destroy the Tkinter window

root.protocol("WM_DELETE_WINDOW", on_closing) # set the 'on_closing()' function to be called when you exit the program

# Running the window
root.mainloop()