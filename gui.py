import tkinter as tk
import threading

from tkinter import LabelFrame, StringVar, OptionMenu, ttk
from PIL import Image, ImageTk
from tkinter import Label, LabelFrame, StringVar, OptionMenu, ttk, filedialog, scrolledtext

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd

import backend
import exe_tools
import fitz 

from pdf_viewer import PDFViewer 
from constants import *
INFINITY = float('inf') 

# Global variables to keep track of the chart and axes
global fig, ax, canvas, current_y_scale , message_widget
current_y_scale = 'linear'

# Create Window for GUI
root = tk.Tk()

# Set title of the window
root.title("Impact Neutron")

# Set the window to full screen
root.attributes('-fullscreen', True)

# Function to exit full-screen mode when Escape is pressed
def exit_full_screen(event=None):
    root.attributes('-fullscreen', False)
    root.geometry("1200x1000")  # Optionally, set to a default window size when exiting full screen

# Bind the Escape key to exit full-screen mode
root.bind("<Escape>", exit_full_screen)

# Set the background color of the root window
root.configure(bg="white")

# Configure grid to ensure equal column widths
for i in range(7):  # Assuming 7 columns
    root.grid_columnconfigure(i, weight=1)

# Custom style for the progress bar
style = ttk.Style()
style.theme_use('default')  

# Custom style: style name as 'Maroon.Horizontal.TProgressbar' in frame 1
style.configure('Maroon.Horizontal.TProgressbar', 
                background='maroon',  
                troughcolor='white',  
                bordercolor='maroon',  
                borderwidth = 2,
                thickness=15)

# Adding frames for parts and specifications
def create_frame(row, column, text, width=2, height=2, borderwidth=2, bg="white", padx=10, pady=10, highlightbackground="white", highlightthickness=0):
    frame = LabelFrame(root, text=text, padx=padx, pady=pady, borderwidth=borderwidth, relief="solid", width=width, height=height, bg=bg, highlightbackground=highlightbackground, highlightthickness=highlightthickness)
    frame.grid(row=row, column=column, padx=padx, pady=pady, columnspan=width, rowspan=height, sticky="ewns")
    return frame

# Validation function to allow only numerical values
def validate_numerical(value):
    if value == '' or value == "-":
        return True
    try:
        float(value)
        return True
    except ValueError:
        return False


# Function to log messages directly to the Text widget
def log_message(message):
    """Append a message to the message widget."""
    if message_widget: 
        message_widget.insert(tk.END, message + "\n")
        message_widget.see(tk.END)  
    else:
        print("Message widget is not initialized.")

# Function to create the message frame within the graph frame
def setup_graph():
    global fig, ax, canvas, current_y_scale, message_widget

    # Create the main graph frame
    graph_frame = create_frame(4, 0, "Graph", width=20, height=4)

    # Create a sub-frame within the graph frame to hold the graph and messages side by side
    graph_sub_frame = tk.Frame(graph_frame, bg="white")
    graph_sub_frame.grid(row=0, column=0, sticky="nsew")
    graph_frame.grid_columnconfigure(0, weight=4)
    graph_frame.grid_columnconfigure(1, weight=1)

    # Create the matplotlib figure and canvas in the left side of the sub-frame
    fig, ax = plt.subplots()
    canvas = FigureCanvasTkAgg(fig, master=graph_sub_frame)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.grid(row=0, column=0, sticky="nsew")
    graph_sub_frame.grid_columnconfigure(0, weight=4)
    graph_sub_frame.grid_columnconfigure(1, weight=1)

    # Create the message frame on the right side of the sub-frame
    message_frame = tk.Frame(graph_sub_frame, bg="lightgray", width=200)
    message_frame.grid(row=0, column=1, sticky="nsew")
    graph_sub_frame.grid_rowconfigure(0, weight=1)

    # Add the Text widget to the message frame
    message_widget = scrolledtext.ScrolledText(message_frame, wrap=tk.WORD, bg="lightgray", width=40)
    message_widget.pack(expand=True, fill='both')

    return graph_frame

# Function to get data from backend in a separate thread
def generate_data_thread():
    # show the progress bar
    progress_bar.grid()  
    progress_bar.start(10)  
    progress_label.grid(row=3, column=1, padx=2, pady=2, sticky="e")

    try:
        # get data from user inputs
        Selected_Part = var1.get()
        Selected_Specification = var2.get()
        VCC = spinbox_vcc.get()
        VEE = spinbox_vee.get()
        Temperature = spinbox_temp.get() # at the moment, the backend can't use this
        Fluence_Min = fluence_min_var.get()
        Fluence_Max = fluence_max_var.get()
        
        # validate data and put in default values as needed
        if Selected_Part in ("AD590", "LM193", "LM139"):
            VCC = 5.0 if VCC == "" else float(VCC)
            VEE = None if VEE == "NA" else float(VEE)
        else:
            VCC = 15.0 if VCC == "" else float(VCC)
            VEE = -15.0 if VEE == "" else float(VEE)
        Fluence_Min = -INFINITY if Fluence_Min == "" else float(Fluence_Min)
        Fluence_Max = +INFINITY if Fluence_Max == "" else float(Fluence_Max)

        data = backend.generate_data(Selected_Part, Selected_Specification, VCC, VEE, Temperature, Fluence_Min, Fluence_Max)
        root.after(0, draw_graph, data, Selected_Part, Selected_Specification)
    except Exception as e:
        print(f"An error occurred: {e}")
        log_message(f"An error occurred: {e}")
        root.after(0,stop_progress_bar)

# Function to draw the graph with new data
def draw_graph(data, Selected_Part, Selected_Specification):
    global plot_data,fig, ax, canvas, current_y_scale
    
    if not data or all(not v for v in data.values()):
        print("No data available to plot.")
        return 
    
    plot_data = pd.DataFrame.from_dict(data, orient='index').transpose()
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(plot_data)
    (x_axis_name, x_axis_data), (y_axis_name, y_axis_data) = data.items()
    xs = np.array(x_axis_data)
    ys = np.array(y_axis_data)
    
    # Create new graph frame
    graph_frame = setup_graph()
    
    # Log plot data to the message box
    log_message("Plot Data:")
    log_message(plot_data.to_string())

    ax.plot(xs, ys, color = "maroon")

    if Selected_Part in DOTTER_SPECIFICATIONS:
        if Selected_Specification in DOTTER_SPECIFICATIONS[Selected_Part]:
            dotted_line_min = DOTTER_SPECIFICATIONS[Selected_Part][Selected_Specification]["min"]
            dotted_line_typical = DOTTER_SPECIFICATIONS[Selected_Part][Selected_Specification]["typical"]
            dotted_line_max = DOTTER_SPECIFICATIONS[Selected_Part][Selected_Specification]["max"]
            if dotted_line_min:
                ax.axhline(y= dotted_line_min , color = "black", linestyle = "--")
                ax.text(1.02, dotted_line_min, f"min: {dotted_line_min}", color="black", ha='left', va='center', fontsize=8, transform=ax.get_yaxis_transform())
            if dotted_line_typical:
                ax.axhline(y= dotted_line_typical , color = "black", linestyle = "--")
                ax.text(1.02, dotted_line_typical, f"typ: {dotted_line_typical}", color="black", ha='left', va='center', fontsize=8, transform=ax.get_yaxis_transform())
            if dotted_line_max:
                ax.axhline(y= dotted_line_max , color = "black", linestyle = "--")
                ax.text(1.02, dotted_line_max, f"max: {dotted_line_max}", color="black", ha='left', va='center', fontsize=8, transform=ax.get_yaxis_transform())

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
    stop_progress_bar()

# Function to stop the progress bar
def stop_progress_bar():
    progress_bar.stop()
    progress_bar.grid_remove()
    progress_label.grid_remove() 

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
    # Clear spinbox entries
    spinbox_vcc.delete(0, tk.END)
    spinbox_vcc.insert(0, 5) 

    spinbox_vee.delete(0, tk.END)
    spinbox_vee.insert(0, 'NA')  

    spinbox_temp.delete(0, tk.END) 
    print("Clear all the fields")

    # Find and destroy the existing graph frame
    for widget in root.winfo_children():
        if isinstance(widget, LabelFrame) and widget.cget("text") == "Graph":
            widget.destroy()

# Frame 0
frame0 = create_frame(0, 0, "", width=10, height=2, borderwidth=0, padx=0, pady=0, bg="gold")

# ASU logo
asu_logo = Image.open(exe_tools.adjust_path('images/ASU_logo.png'))
asu_logo_resized = asu_logo.resize((144, 81), Image.LANCZOS)
asu_logo_tk = ImageTk.PhotoImage(asu_logo_resized)

canvas_asu = tk.Canvas(frame0, width=asu_logo_tk.width(), height=asu_logo_tk.height(), bg="gold", bd=0, highlightthickness=0)
canvas_asu.create_image(0, 0, anchor="nw", image=asu_logo_tk)
canvas_asu.pack(side="left", anchor="w", padx=10, pady=2)  # Padding on left side

# Sandia logo
sandia_logo = Image.open(exe_tools.adjust_path('images/Sandia_logo.png'))
sandia_logo_resized = sandia_logo.resize((144, 81), Image.LANCZOS)
sandia_logo_tk = ImageTk.PhotoImage(sandia_logo_resized)

canvas_sandia = tk.Canvas(frame0, width=sandia_logo_tk.width(), height=sandia_logo_tk.height(), bg="gold", bd=0, highlightthickness=0)
canvas_sandia.create_image(0, 0, anchor="nw", image=sandia_logo_tk)
canvas_sandia.pack(side="right", anchor="e", padx=10, pady=2)  # Padding on right side

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

def datasheet_open():
    selected_part = var1.get()
    pdf_filename = f"{selected_part}.pdf"

    pdf_path = exe_tools.get_pdf_path(pdf_filename)

    if pdf_path.exists():
        PDFViewer(root, pdf_path)  # Use the imported PDFViewer class
    else:
        print(f"PDF file {pdf_filename} not found.")

# data sheet button
datasheet_button = tk.Button(frame1, text="Open Datasheet", command=lambda: threading.Thread(target=datasheet_open, daemon=True).start(), width=15, height=1, bg="brown4", fg="white", bd=0, relief="solid")
datasheet_button.grid(row=0, column=2, padx=10, pady=5)

label_Specifications = tk.Label(frame1, text="Specifications:", padx=5, pady=5, font="Arial 9 bold", bg="gold")
label_Specifications.grid(row=1, column=0, sticky="e")

label_Specification_Typical = tk.Label(frame1, text="", padx=5, pady=5, font="Arial 9 bold", bg="gold", fg="black")
label_Specification_Typical.grid(row=1, column=2, sticky="e")

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

# Function to update the specification label based on the selected part and specification
def update_specification_label(*args):
    selected_part = var1.get()
    selected_specification = var2.get()

    # Check if the part and specification are in the DOTTER_SPECIFICATIONS dictionary
    if selected_part in DOTTER_SPECIFICATIONS:
        if selected_specification in DOTTER_SPECIFICATIONS[selected_part]:
            typical_value = DOTTER_SPECIFICATIONS[selected_part][selected_specification]["typical"]
            label_Specification_Typical.config(text=f"Typical value = {typical_value}")
        else:
            label_Specification_Typical.config(text="")  # Clear if specification is not found
    else:
        label_Specification_Typical.config(text="")  # Clear if part is not found

# Trace changes in Dropdown 1 and update Dropdown 2 accordingly
var1.trace_add('write', update_dropdown_specifications)
var1.trace_add('write', update_specification_label)

# Trace changes in Dropdown 2 and update the label accordingly
var2.trace_add('write', update_specification_label)

# Progress Bar
progress_bar = ttk.Progressbar(frame1, style='Maroon.Horizontal.TProgressbar', orient="horizontal", length=100, mode='indeterminate')
progress_bar.grid(row=2, column=1, padx=2, pady=2)
progress_bar.grid_remove()

# Progress bar label 
progress_label = tk.Label(frame1, text="simulation running", font="Arial 8 italic", bg="gold")
progress_label.grid(row=3, column=1, padx=2, pady=2, sticky="we")
progress_label.grid_remove()

# Frame 2
frame2 = create_frame(2, 2, "", width=2, height=2, borderwidth=0, highlightbackground="brown4", highlightthickness=3, bg="gold")
# label_dataset = tk.Label(frame2, text="Dataset:", padx=5, pady=5, font="Arial 9 bold", bg="gold")
# label_dataset.grid(row=0, column=0, sticky="we")

label_dataset_vcc = tk.Label(frame2, text="VCC (0~25, step-1):", padx=5, pady=5, font="Arial 9 bold", bg="gold")
label_dataset_vcc.grid(row=0, column=0, sticky="e")

#set default VCC & VEE based on spec
def update_default_voltage(*args):
    # Clear the current values of all spinboxes
    spinbox_vcc.delete(0, tk.END)
    spinbox_vee.delete(0, tk.END)
    spinbox_temp.delete(0, tk.END)

    # Determine if the selected part requires VEE to be 'NA' or a numeric value
    if var1.get() in ('AD590', 'LM193', 'LM139'):
        default_voltage = 5
        spinbox_vee.insert(0, 'NA')  # Set VEE to 'NA'
        spinbox_vee.config(state='disabled')  # Disable VEE spinbox
    else:
        default_voltage = 15
        spinbox_vee.config(state='normal')  # Enable VEE spinbox
        spinbox_vee.delete(0, tk.END)
        spinbox_vee.insert(0, -default_voltage)  # Set VEE to -15

    # Set VCC, temperature, and fluence values
    spinbox_vcc.insert(0, default_voltage)  # Set default VCC
    spinbox_temp.insert(0, 25)  # Set default temperature
    
# Bind the update_default_voltage function to changes in var1 (the part selection)
var1.trace_add('write', update_default_voltage)

spinbox_vcc = tk.Spinbox(frame2, from_=0, to=15, increment=1, width=7)
spinbox_vcc.grid(row=0, column=1, sticky="w")

label_dataset_vee = tk.Label(frame2, text= "VEE (-25~0, step-1):", padx=5, pady=5, font="Arial 9 bold", bg="gold")
label_dataset_vee.grid(row=1, column=0,sticky="e")

spinbox_vee = tk.Spinbox(frame2, from_=-15, to=0, increment=1, width=7)
spinbox_vee.grid(row=1, column=1, sticky="w")

label_temp = tk.Label(frame2, text="Circuit Temp (C):", padx=10, pady=10, font="Arial 9 bold", bg="gold")
label_temp.grid(row=2, column=0, sticky="e")

spinbox_temp = tk.Spinbox(frame2, from_=25, to=25, increment=0, width=7)
spinbox_temp.grid(row=2, column=1, sticky="w")

label_temp_temp = tk.Label(frame2, text="* for further dev", padx=5, pady=5, font="Arial 9 bold", bg="gold", fg="red")
label_temp_temp.grid(row=2, column=2, sticky="e")

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

label_fluences_min = tk.Label(frame3, text="Fluence Min(n/cm^2):", padx=10, pady=10, font="Arial 9 bold", bg="gold")
label_fluences_min.grid(row=1, column=0, sticky="e")
# formattign the fluences
formatted_fluences = [f"{fluence:.2E}" for fluence in FLUENCES]
fluence_min_var = StringVar(root)
fluence_min_var.set(formatted_fluences[0])
# Create OptionMenu dropdowns for Fluence Min
fluence_min_combobox = ttk.Combobox(frame3, textvariable=fluence_min_var, values=formatted_fluences, height=10, width=10)  # Limiting dropdown height to 10 items
fluence_min_combobox.grid(row=1, column=1, sticky="w")

label_fluences_max = tk.Label(frame3, text="Fluence Max(n/cm^2):", padx=10, pady=10, font="Arial 9 bold", bg="gold")
label_fluences_max.grid(row=2, column=0, sticky="e")
fluence_max_var = StringVar(root)
fluence_max_var.set(formatted_fluences[-1])
fluence_max_combobox = ttk.Combobox(frame3, textvariable=fluence_max_var, values=formatted_fluences, height=10, width=10)  # Limiting dropdown height to 10 items
fluence_max_combobox.grid(row=2, column=1, sticky="w")

# Function to update the max fluence value based on the min fluence value
def update_fluence_constraints(*args):
    # Get the current selected values
    min_fluence = float(fluence_min_var.get())
    max_fluence = float(fluence_max_var.get())

    # Check if the max fluence is less than or equal to min fluence
    if max_fluence <= min_fluence:
        # Find the next possible max value that is greater than min fluence
        next_max_index = formatted_fluences.index(f"{min_fluence:.2E}") + 1
        
        # Check if the next index is within range
        if next_max_index < len(formatted_fluences):
            fluence_max_var.set(formatted_fluences[next_max_index])
        else:
            # If no higher value exists, reset to the first higher option
            fluence_max_var.set(formatted_fluences[-1])

# Bind the function to check fluence constraints whenever a selection is made
fluence_min_var.trace_add('write', update_fluence_constraints)
fluence_max_var.trace_add('write', update_fluence_constraints)

# Call the function initially to set defaults for the first selected part
update_default_voltage()

# Frame 4
frame4 = create_frame(2, 6,"",width=2, height=2, borderwidth=0, highlightbackground="brown4", highlightthickness=3, bg="gold")
# Button size
button_text_scale = "Change to Log Scale"
button_width = len(button_text_scale) + 4  # Add some padding to the width
button_height = 1

# Button Design
button_bg_color = "brown4"
button_fg_color = "white"
button_border_color = "white"
button_border_width = 2

#Buttons
execute_button = tk.Button(frame4, text="Execute", command=lambda: threading.Thread(target=generate_data_thread, daemon=True).start(), width=button_width, height=button_height, bg=button_bg_color, fg=button_fg_color, bd=0, relief="solid")
execute_button.grid(row=0, column=1, padx=10, pady=5)

def change_scale(button):
    global fig, ax, canvas, current_y_scale
    
    # Toggle between 'linear' and 'log'
    if current_y_scale == 'linear':
        current_y_scale = 'log'
        button.config(text="Change to Linear Scale")  # Update button text
    else:
        current_y_scale = 'linear'
        button.config(text="Change to Log Scale")  # Update button text

    ax.set_yscale(current_y_scale)
    fig.canvas.draw_idle()

# Create the button
change_scale_button = tk.Button(frame4, text=button_text_scale, command=lambda: change_scale(change_scale_button), width=button_width, height=button_height, bg=button_bg_color, fg=button_fg_color, bd=0, relief="solid")
change_scale_button.grid(row=1, column=1, padx=10, pady=5)

save_button = tk.Button(frame4, text="Save to csv", command=save_plot_data, width=button_width, height=button_height, bg=button_bg_color, fg=button_fg_color, bd=0, relief="solid")
save_button.grid(row=2, column=1, padx=10, pady=5)

clear_button = tk.Button(frame4, text="Clear input", command=clear_function, width=button_width, height=button_height, bg=button_bg_color, fg=button_fg_color, bd=0, relief="solid")
clear_button.grid(row=3, column=1, padx=10, pady=5)

# Overwrite the on_closing function to restore stdout
def on_closing():
    plt.close('all')  # Close all Matplotlib figures
    root.destroy()  # Destroy the Tkinter window

root.protocol("WM_DELETE_WINDOW", on_closing) # set the 'on_closing()' function to be called when you exit the program

# Running the window
root.mainloop()