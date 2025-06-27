import tkinter as tk
import threading
import subprocess, traceback  

from tkinter import LabelFrame, StringVar, OptionMenu, ttk
from PIL import Image, ImageTk
from tkinter import Label, LabelFrame, StringVar, OptionMenu, ttk, filedialog, scrolledtext

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd

import backend, backend_tid, backend_tid_fluence
import exe_tools
import fitz 

from pdf_viewer import PDFViewer 
from constants import *
INFINITY = float('inf') 

#Window for GUI
root = tk.Tk()
root.title("Impact Neutron")
root.attributes('-fullscreen', True)

# Function to exit full-screen mode when Escape is pressed
def exit_full_screen(event=None):
    root.attributes('-fullscreen', False)
    root.geometry("1200x1000") 

# Bind the Escape key to exit full-screen mode
root.bind("<Escape>", exit_full_screen)
root.configure(bg="white")

# Configure grid to ensure equal column widths and ensure all columns expand
total_columns = 7  # Define total columns dynamically - taken 7 for now
for i in range(total_columns):
    root.grid_columnconfigure(i, weight=1)

# Container frame for the header (logo row)
BG_COLOR = "gold" 
HEADER_COLOR = 'white'
header_frame = tk.Frame(root, bg=BG_COLOR, height=100)
header_frame.grid(row=0, column=0, columnspan=total_columns, sticky="ew")

# Grid for precise placement
header_frame.grid_columnconfigure(0, weight=1)
header_frame.grid_columnconfigure(1, weight=2)
header_frame.grid_columnconfigure(2, weight=1)

# ASU logo (left)
asu_logo = Image.open(exe_tools.adjust_path('images/ASU_logo.png'))
asu_logo_resized = asu_logo.resize((220, 130), Image.LANCZOS)
asu_logo_tk = ImageTk.PhotoImage(asu_logo_resized)
canvas_asu = tk.Canvas(header_frame, width=asu_logo_tk.width(), height=asu_logo_tk.height(), bg=BG_COLOR, bd=0, highlightthickness=0)
canvas_asu.create_image(0, 0, anchor="nw", image=asu_logo_tk)
canvas_asu.grid(row=0, column=0, padx=10, pady=2, sticky="w")

# IMPACT logo (center)
impact_logo = Image.open(exe_tools.adjust_path('images/IMPACT_Logo.png'))
impact_logo_resized = impact_logo.resize((700, 110), Image.LANCZOS)
impact_logo_tk = ImageTk.PhotoImage(impact_logo_resized)
canvas_impact = tk.Canvas(header_frame, width=impact_logo_tk.width(), height=impact_logo_tk.height(), bg=BG_COLOR, bd=0, highlightthickness=0)
canvas_impact.create_image(0, 0, anchor="nw", image=impact_logo_tk)
canvas_impact.grid(row=0, column=1, padx=10, pady=2)

# Sandia logo (right)
sandia_logo = Image.open(exe_tools.adjust_path('images/sandia_logo_black.png'))
sandia_logo_resized = sandia_logo.resize((130, 110), Image.LANCZOS)
sandia_logo_tk = ImageTk.PhotoImage(sandia_logo_resized)
canvas_sandia = tk.Canvas(header_frame, width=sandia_logo_tk.width(), height=sandia_logo_tk.height(), bg=BG_COLOR, bd=0, highlightthickness=0)
canvas_sandia.create_image(0, 0, anchor="nw", image=sandia_logo_tk)
canvas_sandia.grid(row=0, column=2, padx=30, pady=2, sticky="e")

root.grid_rowconfigure(1, minsize=5) 

# New row for the navigation buttons (row 1)
button_frame = tk.Frame(root, bg=BG_COLOR, height=50)
button_frame.grid(row=2, column=0, columnspan=total_columns, sticky="ew")

# --- Navigation buttons with highlight logic ---
nav_buttons = {}

def set_active_button(active_key):
    for key, btn in nav_buttons.items():
        if key == active_key:
            btn.config(bg="green", fg="white")
        else:
            btn.config(bg="brown4", fg="white")

def show_frame(frame):
    # Hide all frames by removing them from the grid
    for f in frames:
        f.grid_remove()
    # Show the selected frame using grid (place in row 3)
    frame.grid(row=3, column=0, columnspan=total_columns, sticky="nsew")
    # Highlight the correct button
    if frame == fluence_frame:
        set_active_button("neutron")
    elif frame == tid_frame:
        set_active_button("tid")
    elif frame == tid_fluence_frame:
        set_active_button("combined")

# Navigation buttons
nav_buttons["neutron"] = tk.Button(
    button_frame, text="NEUTRON ENV",
    command=lambda: show_frame(fluence_frame),
    width=15, height=2, bg="green", fg="white", bd=0, relief="solid"
)
nav_buttons["neutron"].pack(side="left", padx=20, pady=5)

nav_buttons["tid"] = tk.Button(
    button_frame, text="TID ENV",
    command=lambda: show_frame(tid_frame),
    width=15, height=2, bg="brown4", fg="white", bd=0, relief="solid"
)
nav_buttons["tid"].pack(side="left", padx=20, pady=5)

nav_buttons["combined"] = tk.Button(
    button_frame, text="COMBINED ENV",
    command=lambda: show_frame(tid_fluence_frame),
    width=15, height=2, bg="brown4", fg="white", bd=0, relief="solid"
)
nav_buttons["combined"].pack(side="left", padx=20, pady=5)

# Container for holding all the frames
frames = []

# Fluence Frame
fluence_frame = tk.Frame(root, bg="white")
fluence_frame.grid(row=0, column=0, columnspan=total_columns, rowspan=4, sticky="nsew")
frames.append(fluence_frame)

# Separate frame for TID GUI
tid_frame = tk.Frame(root, bg="white")
tid_frame.grid(row=0, column=0, columnspan=total_columns, rowspan=4, sticky="nsew")
frames.append(tid_frame)

# Separate frame for TID_Fluence GUI
tid_fluence_frame = tk.Frame(root, bg="white")
tid_fluence_frame.grid(row=0, column=0, columnspan=total_columns, rowspan=4, sticky="nsew")
frames.append(tid_fluence_frame)

#Fluence Frame
def create_fluence_gui():
    global fig, ax, canvas, current_y_scale, message_widget, plot_data
    current_y_scale = 'linear'
    plot_data = pd.DataFrame()
    
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
    def create_frame( row, column, text, width=2, height=2, borderwidth=2, bg="white", padx=10, pady=10, highlightbackground="white", highlightthickness=0):
        frame = LabelFrame(fluence_frame, text=text, padx=padx, pady=pady, borderwidth=borderwidth, relief="solid", width=width, height=height, bg=bg, highlightbackground=highlightbackground, highlightthickness=highlightthickness)
        frame.grid(row=row, column=column, padx=padx, pady=pady, columnspan=width, rowspan=height, sticky="ewns")
        return frame

    # Function to log messages directly to the Text widget
    def log_message(message):
        # Append a message to the message widget.
        try:
            if message_widget:
                message_widget.insert(tk.END, message + "\n")
                message_widget.see(tk.END)
            else:
                raise NameError("Message widget is not defined.")
        except NameError:
            print("Message widget not found. Logging to console:")
            print(message)

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
        # Show the progress bar
        progress_bar.grid()
        progress_bar.start(10)
        progress_label.grid(row=3, column=1, padx=2, pady=2, sticky="e")

        try:
            # Get data from user inputs
            Selected_Part = var1.get()
            Selected_Specification = var2.get()
            VCC = spinbox_vcc.get()
            VEE = spinbox_vee.get()
            Temperature = spinbox_temp.get()
            Fluence_Min = fluence_mapping[fluence_min_var.get()]
            Fluence_Max = fluence_mapping[fluence_max_var.get()]

            # Validate inputs and assign defaults
            if Selected_Part in ("AD590", "LM193", "LM139"):
                VCC = 5.0 if VCC == "" else float(VCC)
                VEE = None if VEE == "NA" else float(VEE)
            else:
                VCC = 15.0 if VCC == "" else float(VCC)
                VEE = -15.0 if VEE == "" else float(VEE)
            Fluence_Min = -INFINITY if Fluence_Min == "" else float(Fluence_Min)
            Fluence_Max = +INFINITY if Fluence_Max == "" else float(Fluence_Max)

            # Call backend to generate data
            data = backend.generate_data(Selected_Part, Selected_Specification, VCC, VEE, Temperature, Fluence_Min, Fluence_Max)
            # Plot the data
            root.after(0, draw_graph, data, Selected_Part, Selected_Specification)

        except Exception as e:
            # Log the full error details to the console
            print("An error occurred:")
            traceback.print_exc()

            # Show a generic error message in the graph area
            root.after(0, display_error_message, "An error occurred while generating data.")
        finally:
            # Stop the progress bar
            root.after(0, stop_progress_bar)
        
    def display_error_message(error_message):
        #Clear the graph area and display a generic error message.
        for widget in fluence_frame.winfo_children():
            if isinstance(widget, LabelFrame) and widget.cget("text") == "Graph":
                for child in widget.winfo_children():
                    child.destroy()
                widget.destroy()

        # Create a new frame to show the error message
        graph_frame = create_frame(4, 0, "Graph", width=20, height=4)
        error_label = tk.Label(graph_frame, text=error_message, fg="red", font=("Arial", 14), bg="white", wraplength=400)
        error_label.pack(expand=True, fill="both")

    # Function to draw the graph with new data
    def draw_graph(data, Selected_Part, Selected_Specification):
        global plot_data,fig, ax, canvas, current_y_scale
        
        # Create new graph frame
        graph_frame = setup_graph()

        if not data or all(not v for v in data.values()):
            print("No data available to plot.")
            return 
        
        plot_data = pd.DataFrame.from_dict(data, orient='index').transpose()
        with pd.option_context('display.max_rows', None, 'display.max_columns', None):
            print(plot_data)
        (x_axis_name, x_axis_data), (y_axis_name, y_axis_data) = data.items()
        xs = np.array(x_axis_data)
        ys = np.array(y_axis_data)
        
        # Log plot data to the message box
        log_message("Plot Data:")
        log_message(plot_data.to_string())

        ax.plot(xs, ys, color = "maroon")

        if Selected_Part in DOTTER_SPECIFICATIONS:
            if Selected_Specification in DOTTER_SPECIFICATIONS[Selected_Part]:
                dotted_line_min = DOTTER_SPECIFICATIONS[Selected_Part][Selected_Specification]["min"]
                dotted_line_max = DOTTER_SPECIFICATIONS[Selected_Part][Selected_Specification]["max"]
                if dotted_line_min:
                    ax.axhline(y= dotted_line_min , color = "black", linestyle = "--")
                    ax.text(1.02, dotted_line_min, f"min: {dotted_line_min}", color="black", ha='left', va='center', fontsize=8, transform=ax.get_yaxis_transform())
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

        # Find and destroy the existing graph frame and its children
        for widget in fluence_frame.winfo_children():
            if isinstance(widget, LabelFrame) and widget.cget("text") == "Graph":
                # Destroy all children of the graph frame
                for child in widget.winfo_children():
                    child.destroy()
                # Destroy the graph frame itself
                widget.destroy()

    for col in range(7):
        fluence_frame.grid_columnconfigure(col, weight=1)

    # Frame 1
    frame1 = create_frame(2, 0, "Parts & Spec Conditions", width=2, height=2, borderwidth=0, highlightbackground="brown4", highlightthickness=3, bg=BG_COLOR)
    label_Parts = tk.Label(frame1, text="Parts:", padx=5, pady=5, font="Arial 9 bold", bg=BG_COLOR)
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

    label_Specifications = tk.Label(frame1, text="Specifications:", padx=5, pady=5, font="Arial 9 bold", bg=BG_COLOR)
    label_Specifications.grid(row=1, column=0, sticky="e")

    label_Specification_Typical = tk.Label(frame1, text="", padx=5, pady=5, font="Arial 9 bold", bg=BG_COLOR, fg="black")
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
    progress_label = tk.Label(frame1, text="simulation running", font="Arial 8 italic", bg=BG_COLOR)
    progress_label.grid(row=3, column=1, padx=2, pady=2, sticky="we")
    progress_label.grid_remove()

    # Frame 2
    frame2 = create_frame(2, 2, "Bias & Temp Conditions", width=2, height=2, borderwidth=0, highlightbackground="brown4", highlightthickness=3, bg=BG_COLOR)
    # label_dataset = tk.Label(frame2, text="Dataset:", padx=5, pady=5, font="Arial 9 bold", bg=BG_COLOR)
    # label_dataset.grid(row=0, column=0, sticky="we")

    label_dataset_vcc = tk.Label(frame2, text="VCC (0~25):", padx=5, pady=5, font="Arial 9 bold", bg=BG_COLOR)
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

    label_dataset_vee = tk.Label(frame2, text= "VEE (-25~0):", padx=5, pady=5, font="Arial 9 bold", bg=BG_COLOR)
    label_dataset_vee.grid(row=1, column=0,sticky="e")

    spinbox_vee = tk.Spinbox(frame2, from_=-15, to=0, increment=1, width=7)
    spinbox_vee.grid(row=1, column=1, sticky="w")

    label_temp = tk.Label(frame2, text="Circuit Temp (C):", padx=10, pady=10, font="Arial 9 bold", bg=BG_COLOR)
    label_temp.grid(row=2, column=0, sticky="e")

    spinbox_temp = tk.Spinbox(frame2, from_=25, to=25, increment=0, width=7)
    spinbox_temp.grid(row=2, column=1, sticky="w")

    label_temp_temp = tk.Label(frame2, text="* for further dev", padx=5, pady=5, font="Arial 9 bold", bg=BG_COLOR, fg="red")
    label_temp_temp.grid(row=2, column=2, sticky="e")

    # Frame 3
    frame3 = create_frame(2, 4, "Neutron Testing Conditions", width=2, height=2, borderwidth=0, highlightbackground="brown4", highlightthickness=3, bg=BG_COLOR)
    label_neutron_type = tk.Label(frame3, text="Neutron Type:", padx=5, pady=5, font="Arial 9 bold", bg=BG_COLOR)
    label_neutron_type.grid(row=0, column=0, sticky="e")

    # Dropdown Neutron Type
    options_neutron = NEUTRON_TYPE
    var_neutron = StringVar()
    var_neutron.set(options_neutron[0])
    dropdown_neutron = OptionMenu(frame3, var_neutron, *options_neutron)
    dropdown_neutron.grid(row=0, column=1, sticky="w", padx=5, pady=5)
    dropdown_neutron.config(bg="white")
    neutron_type_uom = tk.Label(frame3, text="equ.", padx=5, pady=5, font="Arial 9 bold", bg=BG_COLOR)
    neutron_type_uom.grid(row=0, column=2, sticky="e")

    label_fluences_min = tk.Label(frame3, text="Fluence Min(n/cm^2):", padx=10, pady=10, font="Arial 9 bold", bg=BG_COLOR)
    label_fluences_min.grid(row=1, column=0, sticky="e")
    # formattign the fluences
    fluence_mapping = {f"{fluence:.2E}": backend for fluence, backend in zip(FLUENCES, BACKEND_FLUENCES)}
    formatted_fluences = list(fluence_mapping.keys())
    fluence_min_var = StringVar(root)
    fluence_min_var.set(formatted_fluences[0])
    # Create OptionMenu dropdowns for Fluence Min
    fluence_min_combobox = ttk.Combobox(frame3, textvariable=fluence_min_var, values=formatted_fluences[:-1], height=10, width=10)  # Limiting dropdown height to 10 items
    fluence_min_combobox.grid(row=1, column=1, sticky="w")

    label_fluences_max = tk.Label(frame3, text="Fluence Max(n/cm^2):", padx=10, pady=10, font="Arial 9 bold", bg=BG_COLOR)
    label_fluences_max.grid(row=2, column=0, sticky="e")
    fluence_max_var = StringVar(root)
    fluence_max_var.set(formatted_fluences[-1])
    fluence_max_combobox = ttk.Combobox(frame3, textvariable=fluence_max_var, values=formatted_fluences[1:], height=10, width=10)  # Limiting dropdown height to 10 items
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
    frame4 = create_frame(2, 6,"",width=2, height=2, borderwidth=0, highlightbackground="brown4", highlightthickness=3, bg=BG_COLOR)
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

# TID Frame
def create_tid_gui():
    global fig, ax, canvas, current_y_scale, message_widget, plot_data
    current_y_scale = 'linear'
    plot_data = pd.DataFrame()
    
    # overlay functionalities
    global prev_data, overlay_mode, prev_part, prev_spec, prev_dr, prev_h2
    prev_data = None
    overlay_mode = False
    prev_part = None
    prev_spec = None
    prev_dr = None
    prev_h2 = None

    def reset_overlay(*args):
        global prev_data, overlay_mode, prev_part, prev_spec, prev_dr, prev_h2
        prev_data = None
        overlay_mode = False
        prev_part = var1.get()
        prev_spec = var2.get()
        prev_dr = var_dr.get()
        prev_h2 = var_h2.get()

    def overlay_plot():
        global prev_data, overlay_mode, prev_part, prev_spec, prev_dr, prev_h2
        if not plot_data.empty:
            prev_data = plot_data.copy()
            overlay_mode = True
            prev_part = var1.get()
            prev_spec = var2.get()
            prev_dr = var_dr.get()
            prev_h2 = var_h2.get()

            log_message("Overlay mode enabled. Run Execute to plot overlay.")
        else:
            log_message("No data to overlay.")
    
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
    def create_frame( row, column, text, width=2, height=2, borderwidth=2, bg="white", padx=10, pady=10, highlightbackground="white", highlightthickness=0):
        frame = LabelFrame(tid_frame, text=text, padx=padx, pady=pady, borderwidth=borderwidth, relief="solid", width=width, height=height, bg=bg, highlightbackground=highlightbackground, highlightthickness=highlightthickness)
        frame.grid(row=row, column=column, padx=padx, pady=pady, columnspan=width, rowspan=height, sticky="ewns")
        return frame

    # Validation function to allow only numerical values, not used as of now 
    def validate_numerical(value):
        if value == '' or value == "-":
            return True
        try:
            float(value)
            return True
        except ValueError:
            return False

    def log_message(message):
        """Append a message to the message widget."""
        try:
            if message_widget:
                message_widget.insert(tk.END, message + "\n")
                message_widget.see(tk.END)
            else:
                raise NameError("Message widget is not defined.")
        except NameError:
            print("Message widget not found. Logging to console:")
            print(message)

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
            tid_min = total_dose_min_var.get()
            tid_max = total_dose_max_var.get()
            
            # validate data and put in default values as needed
            if Selected_Part in ("AD590", "LM193", "LM139"):
                VCC = 5.0 if VCC == "" else float(VCC)
                VEE = None if VEE == "NA" else float(VEE)
            else:
                VCC = 15.0 if VCC == "" else float(VCC)
                VEE = -15.0 if VEE == "" else float(VEE)
            tid_min = -INFINITY if tid_min == "" else float(tid_min)
            tid_max = +INFINITY if tid_max == "" else float(tid_max)

            data = backend_tid.generate_data(Selected_Part, Selected_Specification, VCC, VEE, Temperature, tid_min, tid_max)
            root.after(0, draw_graph, data, Selected_Part, Selected_Specification)
        except Exception as e:
            # Log the full error details to the console
            print("An error occurred:")
            traceback.print_exc()

            # Show a generic error message in the graph area
            root.after(0, display_error_message, "An error occurred while generating data.")
        finally:
            # Stop the progress bar
            root.after(0, stop_progress_bar)
        

    def display_error_message(error_message):
        #Clear the graph area and display a generic error message.
        for widget in fluence_frame.winfo_children():
            if isinstance(widget, LabelFrame) and widget.cget("text") == "Graph":
                for child in widget.winfo_children():
                    child.destroy()
                widget.destroy()

        # Create a new frame to show the error message
        graph_frame = create_frame(4, 0, "Graph", width=20, height=4)
        error_label = tk.Label(graph_frame, text=error_message, fg="red", font=("Arial", 14), bg="white", wraplength=400)
        error_label.pack(expand=True, fill="both")

    # Function to draw the graph with new data
    def draw_graph(data, Selected_Part, Selected_Specification):
        global plot_data,fig, ax, canvas, current_y_scale, prev_data, overlay_mode, prev_part, prev_spec
        
        # Create new graph frame
        graph_frame = setup_graph()

        if not data or all(not v for v in data.values()):
            print("No data available to plot.")
            return 
        
        plot_data = pd.DataFrame.from_dict(data, orient='index').transpose()
        with pd.option_context('display.max_rows', None, 'display.max_columns', None):
            print(plot_data)
        (x_axis_name, x_axis_data), (y_axis_name, y_axis_data) = data.items()
        xs = np.array(x_axis_data)
        ys = np.array(y_axis_data)
    
        
        # Log plot data to the message box
        log_message("Plot Data:")
        log_message(plot_data.to_string())

        # Overlay logic
        if overlay_mode and prev_data is not None and prev_part == Selected_Part and prev_spec == Selected_Specification:
            prev_xs = prev_data.iloc[:, 0].values
            prev_ys = prev_data.iloc[:, 1].values

            # Get previous and current dropdown values for labels
            prev_label = f"Prev: DR={prev_dr}, H2={prev_h2}"
            curr_label = f"Current: DR={var_dr.get()}, H2={var_h2.get()}"
            
            # Take min of x and max of y for axis limits
            min_x = max(np.min(xs), np.min(prev_xs))
            max_x = min(np.max(xs), np.max(prev_xs))
            min_y = min(np.min(ys), np.min(prev_ys))
            max_y = max(np.max(ys), np.max(prev_ys))

            # Add Padding to the axes limits
            x_pad = 0.02 * (max_x - min_x) if max_x > min_x else 1
            y_pad = 0.05 * (max_y - min_y) if max_y > min_y else 1

            ax.plot(prev_xs, prev_ys, color="blue", label= prev_label)
            ax.plot(xs, ys, color="maroon", label= curr_label)

            ax.set_xlim([min_x - x_pad, max_x + x_pad])
            ax.set_ylim([min_y - y_pad, max_y + y_pad])

            ax.legend()
            overlay_mode = False
            prev_data = None
            log_message("Overlay complete. Back to normal mode.")
        else:
            curr_label = f"Current: DR={var_dr.get()}, H2={var_h2.get()}"
            ax.plot(xs, ys, color="maroon", label=curr_label)
            ax.legend().remove() if ax.get_legend() else None

        if Selected_Part in DOTTER_SPECIFICATIONS:
            if Selected_Specification in DOTTER_SPECIFICATIONS[Selected_Part]:
                dotted_line_min = DOTTER_SPECIFICATIONS[Selected_Part][Selected_Specification]["min"]
                dotted_line_max = DOTTER_SPECIFICATIONS[Selected_Part][Selected_Specification]["max"]
                if dotted_line_min:
                    ax.axhline(y= dotted_line_min , color = "black", linestyle = "--")
                    ax.text(1.02, dotted_line_min, f"min: {dotted_line_min}", color="black", ha='left', va='center', fontsize=8, transform=ax.get_yaxis_transform())
                if dotted_line_max:
                    ax.axhline(y= dotted_line_max , color = "black", linestyle = "--")
                    ax.text(1.02, dotted_line_max, f"max: {dotted_line_max}", color="black", ha='left', va='center', fontsize=8, transform=ax.get_yaxis_transform())

        ax.set_xscale('linear') # Set the x-axis to linear scale for TID
        ax.set_yscale(current_y_scale)  # Set the y-axis to current scale - which is linear in begining.
        ax.set_xlabel(x_axis_name)
        ax.set_ylabel(y_axis_name)

        # Define a custom formatter function
        def custom_formatter(x, pos):
            if x == 0:  # Check if the tick is at 0
                return 'pre_rad'
            else:
                return x  # show original TID value on x axis

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

    # Clear function 
    def clear_function():
        # Clear spinbox entries
        spinbox_vcc.delete(0, tk.END)
        spinbox_vcc.insert(0, 5) 

        spinbox_vee.delete(0, tk.END)
        spinbox_vee.insert(0, 'NA')  

        spinbox_temp.delete(0, tk.END) 
        print("Clear all the fields")

        # Find and destroy the existing graph frame and its children
        for widget in fluence_frame.winfo_children():
            if isinstance(widget, LabelFrame) and widget.cget("text") == "Graph":
                # Destroy all children of the graph frame
                for child in widget.winfo_children():
                    child.destroy()
                # Destroy the graph frame itself
                widget.destroy()

    for col in range(7):
        tid_frame.grid_columnconfigure(col, weight=1)

    # Frame 1
    frame1 = create_frame(2, 0, "Parts & Spec Conditions", width=2, height=2, borderwidth=0, highlightbackground="brown4", highlightthickness=3, bg=BG_COLOR)
    label_Parts = tk.Label(frame1, text="Parts:", padx=5, pady=5, font="Arial 9 bold", bg=BG_COLOR)
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

    label_Specifications = tk.Label(frame1, text="Specifications:", padx=5, pady=5, font="Arial 9 bold", bg=BG_COLOR)
    label_Specifications.grid(row=1, column=0, sticky="e")

    label_Specification_Typical = tk.Label(frame1, text="", padx=5, pady=5, font="Arial 9 bold", bg=BG_COLOR, fg="black")
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

    # Reset overlay if part or spec changes
    var1.trace_add('write', reset_overlay)
    var2.trace_add('write', reset_overlay)

    # Progress Bar
    progress_bar = ttk.Progressbar(frame1, style='Maroon.Horizontal.TProgressbar', orient="horizontal", length=100, mode='indeterminate')
    progress_bar.grid(row=2, column=1, padx=2, pady=2)
    progress_bar.grid_remove()

    # Progress bar label 
    progress_label = tk.Label(frame1, text="simulation running", font="Arial 8 italic", bg=BG_COLOR)
    progress_label.grid(row=3, column=1, padx=2, pady=2, sticky="we")
    progress_label.grid_remove()

    # Frame 2
    frame2 = create_frame(2, 2, "Bias & Temp Conditions", width=2, height=2, borderwidth=0, highlightbackground="brown4", highlightthickness=3, bg=BG_COLOR)
    # label_dataset = tk.Label(frame2, text="Dataset:", padx=5, pady=5, font="Arial 9 bold", bg=BG_COLOR)
    # label_dataset.grid(row=0, column=0, sticky="we")

    label_dataset_vcc = tk.Label(frame2, text="VCC (0~25):", padx=5, pady=5, font="Arial 9 bold", bg=BG_COLOR)
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

    label_dataset_vee = tk.Label(frame2, text= "VEE (-25~0):", padx=5, pady=5, font="Arial 9 bold", bg=BG_COLOR)
    label_dataset_vee.grid(row=1, column=0,sticky="e")

    spinbox_vee = tk.Spinbox(frame2, from_=-15, to=0, increment=1, width=7)
    spinbox_vee.grid(row=1, column=1, sticky="w")

    label_temp = tk.Label(frame2, text="Circuit Temp (C):", padx=10, pady=10, font="Arial 9 bold", bg=BG_COLOR)
    label_temp.grid(row=2, column=0, sticky="e")

    spinbox_temp = tk.Spinbox(frame2, from_=25, to=25, increment=0, width=7)
    spinbox_temp.grid(row=2, column=1, sticky="w")

    label_temp_temp = tk.Label(frame2, text="* for further dev", padx=5, pady=5, font="Arial 9 bold", bg=BG_COLOR, fg="red")
    label_temp_temp.grid(row=2, column=2, sticky="e")

    # Frame 3
    frame3 = create_frame(2, 4, "TID Testing Conditions", width=2, height=2, borderwidth=0, highlightbackground="brown4", highlightthickness=3, bg=BG_COLOR)

    # Dose Rate Label and DropDown
    label_dr_type = tk.Label(frame3, text="Dose Rate (rad/S):", padx=5, pady=5, font="Arial 9 bold", bg=BG_COLOR)
    label_dr_type.grid(row=0, column=0, sticky="e")
    options_dr = DOSE_RATE
    var_dr = StringVar()
    var_dr.set(options_dr[0])
    dropdown_dr = OptionMenu(frame3, var_dr, *options_dr)
    dropdown_dr.grid(row=0, column=1, sticky="w", padx=5, pady=5)
    dropdown_dr.config(bg="white")

    # Hydrogen label and DropDown
    label_h2_type = tk.Label(frame3, text="Hydrogen (%):", padx=5, pady=5, font="Arial 9 bold", bg=BG_COLOR)
    label_h2_type.grid(row=1, column=0, sticky="e")
    options_h2 = HYDROGEN
    var_h2 = StringVar()
    var_h2.set(options_h2[0])
    dropdown_h2 = OptionMenu(frame3, var_h2, *options_h2)
    dropdown_h2.grid(row=1, column=1, sticky="w", padx=5, pady=5)
    dropdown_h2.config(bg="white")

    # Bias label and DropDown
    label_bi_type = tk.Label(frame3, text="Bias (V):", padx=5, pady=5, font="Arial 9 bold", bg=BG_COLOR)
    label_bi_type.grid(row=2, column=0, sticky="e")
    options_bi = BIAS
    var_bi = StringVar()
    var_bi.set(options_bi[0])
    dropdown_bi = OptionMenu(frame3, var_bi, *options_bi)
    dropdown_bi.grid(row=2, column=1, sticky="w", padx=5, pady=5)
    dropdown_bi.config(bg="white")

    total_dose_min_var = StringVar()
    total_dose_max_var = StringVar()
    
    # form the combined argumetn to get the TID values
    def form_argument_key():
        dose_rate = var_dr.get()
        hydrogen = var_h2.get()
        bias = var_bi.get()
        argument_string = f"DR={dose_rate}_H2={hydrogen}_B={bias}"
        return argument_string

    # Use *args to capture the event parameters]
    def update_hydrogen(*args):
        selected_dose_rate = float(var_dr.get())
        hydrogen_values = VALID_TID_COMBINATIONS[selected_dose_rate]
        menu = dropdown_h2['menu']
        menu.delete(0, 'end')
        for value in hydrogen_values:
            menu.add_command(label=value, command=lambda v = value: var_h2.set(v))
        var_h2.set(hydrogen_values[0])
        call_update_tid()
    
    # Calling update_tid_dataframes Function on hydrogen dropdown change
    def call_update_tid(*args):
        # Calling update function with the default value when the dropdown is created
        combined_key = form_argument_key() 
        update_tid_dataframes(combined_key)
        
        # Calling fucntion to update the tid dose min and max values 
        TID_VALUES = get_tid_dose_limits()
        total_dose_min, total_dose_max = TID_VALUES
        total_dose_min_var.set(total_dose_min)
        total_dose_max_var.set(total_dose_max)

    # Function to update the TID dataframes based on the selected dose rate
    var_dr.trace_add('write', update_hydrogen)
    var_h2.trace_add('write', call_update_tid)

    # Calling update function with the default value when the dropdown is created
    update_hydrogen()  

    label_total_dose_min = tk.Label(frame3, text="Total Dose Min (krad):", padx=5, pady=5, font="Arial 9 bold", bg=BG_COLOR)
    label_total_dose_min.grid(row=0, column=2, sticky="e")

    total_dose_min_combobox = ttk.Combobox(frame3, textvariable=total_dose_min_var, values=[], height=10, width=10) 
    total_dose_min_combobox.grid(row=0, column=3, sticky="w")

    label_total_dose_max = tk.Label(frame3, text="Total Dose Max (krad)):", padx=5, pady=5, font="Arial 9 bold", bg=BG_COLOR)
    label_total_dose_max.grid(row=1, column=2, sticky="e")

    total_dose_max_combobox = ttk.Combobox(frame3, textvariable=total_dose_max_var, values=[], height=10, width=10)  
    total_dose_max_combobox.grid(row=1, column=3, sticky="w")

    # Call the function initially to set defaults for the first selected part
    update_default_voltage()

    # Frame 4
    frame4 = create_frame(2, 6,"",width=2, height=2, borderwidth=0, highlightbackground="brown4", highlightthickness=3, bg=BG_COLOR)
    # Button size
    button_text_scale = "Change to Log Scale"
    button_width = len(button_text_scale) + 4  # Add some padding to the width
    button_height = 1

    # Button Design
    button_bg_color = "brown4"
    button_fg_color = "white"

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

    overlay_button = tk.Button(frame4, text="Overlay Plot", command=overlay_plot, width=button_width, height=button_height, bg=button_bg_color, fg=button_fg_color, bd=0, relief="solid")
    overlay_button.grid(row=3, column=1, padx=10, pady=5)

    clear_button = tk.Button(frame4, text="Clear input", command=clear_function, width=button_width, height=button_height, bg=button_bg_color, fg=button_fg_color, bd=0, relief="solid")
    clear_button.grid(row=4, column=1, padx=10, pady=5)

# TID_Fluence Frame
def create_ion_fluence_gui():
    global fig, ax, canvas, current_y_scale, message_widget, plot_data
    current_y_scale = 'linear'
    plot_data = pd.DataFrame()
    
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
    def create_frame( row, column, text, width=2, height=2, borderwidth=2, bg="white", padx=10, pady=10, highlightbackground="white", highlightthickness=0):
        frame = LabelFrame(tid_fluence_frame, text=text, padx=padx, pady=pady, borderwidth=borderwidth, relief="solid", width=width, height=height, bg=bg, highlightbackground=highlightbackground, highlightthickness=highlightthickness)
        frame.grid(row=row, column=column, padx=padx, pady=pady, columnspan=width, rowspan=height, sticky="ewns")
        return frame


    def log_message(message):
        """Append a message to the message widget."""
        try:
            if message_widget:
                message_widget.insert(tk.END, message + "\n")
                message_widget.see(tk.END)
            else:
                raise NameError("Message widget is not defined.")
        except NameError:
            print("Message widget not found. Logging to console:")
            print(message)

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
            Fluence_Min = fluence_mapping[fluence_min_var.get()]
            Fluence_Max = fluence_mapping[fluence_max_var.get()]
            
            # validate data and put in default values as needed
            if Selected_Part in ("AD590", "LM193", "LM139"):
                VCC = 5.0 if VCC == "" else float(VCC)
                VEE = None if VEE == "NA" else float(VEE)
            else:
                VCC = 15.0 if VCC == "" else float(VCC)
                VEE = -15.0 if VEE == "" else float(VEE)
            Fluence_Min = -INFINITY if Fluence_Min == "" else float(Fluence_Min)
            Fluence_Max = +INFINITY if Fluence_Max == "" else float(Fluence_Max)

            data = backend_tid_fluence.generate_data(Selected_Part, Selected_Specification, VCC, VEE, Temperature, Fluence_Min, Fluence_Max)
            root.after(0, draw_graph, data, Selected_Part, Selected_Specification)
        except Exception as e:
            # Log the full error details to the console
            print("An error occurred:")
            traceback.print_exc()

            # Show a generic error message in the graph area
            root.after(0, display_error_message, "An error occurred while generating data.")
        finally:
            # Stop the progress bar
            root.after(0, stop_progress_bar)
        

    def display_error_message(error_message):
        #Clear the graph area and display a generic error message.
        for widget in fluence_frame.winfo_children():
            if isinstance(widget, LabelFrame) and widget.cget("text") == "Graph":
                for child in widget.winfo_children():
                    child.destroy()
                widget.destroy()

        # Create a new frame to show the error message
        graph_frame = create_frame(4, 0, "Graph", width=20, height=4)
        error_label = tk.Label(graph_frame, text=error_message, fg="red", font=("Arial", 14), bg="white", wraplength=400)
        error_label.pack(expand=True, fill="both")

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
                dotted_line_max = DOTTER_SPECIFICATIONS[Selected_Part][Selected_Specification]["max"]
                if dotted_line_min:
                    ax.axhline(y= dotted_line_min , color = "black", linestyle = "--")
                    ax.text(1.02, dotted_line_min, f"min: {dotted_line_min}", color="black", ha='left', va='center', fontsize=8, transform=ax.get_yaxis_transform())
                if dotted_line_max:
                    ax.axhline(y= dotted_line_max , color = "black", linestyle = "--")
                    ax.text(1.02, dotted_line_max, f"max: {dotted_line_max}", color="black", ha='left', va='center', fontsize=8, transform=ax.get_yaxis_transform())

        ax.set_xscale('log') # Set the x-axis to log scale for TID_Fluence
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

    # Find and destroy the existing graph frame and its children
        for widget in fluence_frame.winfo_children():
            if isinstance(widget, LabelFrame) and widget.cget("text") == "Graph":
                # Destroy all children of the graph frame
                for child in widget.winfo_children():
                    child.destroy()
                # Destroy the graph frame itself
                widget.destroy()

    for col in range(7):
        tid_fluence_frame.grid_columnconfigure(col, weight=1)

    # Frame 1
    frame1 = create_frame(2, 0, "Parts & Spec Conditions", width=2, height=2, borderwidth=0, highlightbackground="brown4", highlightthickness=3, bg=BG_COLOR)
    label_Parts = tk.Label(frame1, text="Parts:", padx=5, pady=5, font="Arial 9 bold", bg=BG_COLOR)
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

    label_Specifications = tk.Label(frame1, text="Specifications:", padx=5, pady=5, font="Arial 9 bold", bg=BG_COLOR)
    label_Specifications.grid(row=1, column=0, sticky="e")

    label_Specification_Typical = tk.Label(frame1, text="", padx=5, pady=5, font="Arial 9 bold", bg=BG_COLOR, fg="black")
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
    progress_label = tk.Label(frame1, text="simulation running", font="Arial 8 italic", bg=BG_COLOR)
    progress_label.grid(row=3, column=1, padx=2, pady=2, sticky="we")
    progress_label.grid_remove()

    # Frame 2
    frame2 = create_frame(2, 2, "Bias & Temp Conditions", width=2, height=2, borderwidth=0, highlightbackground="brown4", highlightthickness=3, bg=BG_COLOR)
    # label_dataset = tk.Label(frame2, text="Dataset:", padx=5, pady=5, font="Arial 9 bold", bg=BG_COLOR)
    # label_dataset.grid(row=0, column=0, sticky="we")

    label_dataset_vcc = tk.Label(frame2, text="VCC (0~25):", padx=5, pady=5, font="Arial 9 bold", bg=BG_COLOR)
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

    label_dataset_vee = tk.Label(frame2, text= "VEE (-25~0):", padx=5, pady=5, font="Arial 9 bold", bg=BG_COLOR)
    label_dataset_vee.grid(row=1, column=0,sticky="e")

    spinbox_vee = tk.Spinbox(frame2, from_=-15, to=0, increment=1, width=7)
    spinbox_vee.grid(row=1, column=1, sticky="w")

    label_temp = tk.Label(frame2, text="Circuit Temp (C):", padx=10, pady=10, font="Arial 9 bold", bg=BG_COLOR)
    label_temp.grid(row=2, column=0, sticky="e")

    spinbox_temp = tk.Spinbox(frame2, from_=25, to=25, increment=0, width=7)
    spinbox_temp.grid(row=2, column=1, sticky="w")

    label_temp_temp = tk.Label(frame2, text="* for further dev", padx=5, pady=5, font="Arial 9 bold", bg=BG_COLOR, fg="red")
    label_temp_temp.grid(row=2, column=2, sticky="e")

    # Frame 3
    frame3 = create_frame(2, 4, "ION Testing Conditions", width=2, height=2, borderwidth=0, highlightbackground="brown4", highlightthickness=3, bg=BG_COLOR)

    # Dose Rate Label and DropDown
    label_dr_type = tk.Label(frame3, text="Dose Rate (rad/S):", padx=5, pady=5, font="Arial 9 bold", bg=BG_COLOR)
    label_dr_type.grid(row=0, column=0, sticky="e")
    options_dr = DOSE_RATE_TF
    var_dr = StringVar()
    var_dr.set(options_dr[0])
    dropdown_dr = OptionMenu(frame3, var_dr, *options_dr)
    dropdown_dr.grid(row=0, column=1, sticky="w", padx=5, pady=5)
    dropdown_dr.config(bg="white")

    # Hydrogen label and DropDown
    label_h2_type = tk.Label(frame3, text="Hydrogen (%):", padx=5, pady=5, font="Arial 9 bold", bg=BG_COLOR)
    label_h2_type.grid(row=1, column=0, sticky="e")
    options_h2 = HYDROGEN_TF
    var_h2 = StringVar()
    var_h2.set(options_h2[0])
    dropdown_h2 = OptionMenu(frame3, var_h2, *options_h2)
    dropdown_h2.grid(row=1, column=1, sticky="w", padx=5, pady=5)
    dropdown_h2.config(bg="white")

    # Bias label and DropDown
    label_bi_type = tk.Label(frame3, text="Bias (V):", padx=5, pady=5, font="Arial 9 bold", bg=BG_COLOR)
    label_bi_type.grid(row=2, column=0, sticky="e")
    options_bi = BIAS_TF
    var_bi = StringVar()
    var_bi.set(options_bi[0])
    dropdown_bi = OptionMenu(frame3, var_bi, *options_bi)
    dropdown_bi.grid(row=2, column=1, sticky="w", padx=5, pady=5)
    dropdown_bi.config(bg="white")

    # Proton type
    label_neutron_type = tk.Label(frame3, text="Proton Type:", padx=5, pady=5, font="Arial 9 bold", bg=BG_COLOR)
    label_neutron_type.grid(row=0, column=2, sticky="e")
    options_proton = PROTON_TYPE
    var_proton = StringVar()
    var_proton.set(options_proton[0])
    dropdown_proton = OptionMenu(frame3, var_proton, *options_proton)
    dropdown_proton.grid(row=0, column=3, sticky="w", padx=5, pady=5)
    dropdown_proton.config(bg="white")
    proton_type_uom = tk.Label(frame3, text="equ.", padx=5, pady=5, font="Arial 9 bold", bg=BG_COLOR)
    proton_type_uom.grid(row=0, column=4, sticky="e")
    
    label_fluences_min = tk.Label(frame3, text="Fluence Min(n/cm^2):", padx=10, pady=10, font="Arial 9 bold", bg=BG_COLOR)
    label_fluences_min.grid(row=1, column=2, sticky="e")
    # formattign the fluences
    fluence_mapping = {f"{fluence:.2E}": backend for fluence, backend in zip(FLUENCES_TF, BACKEND_FLUENCES_TF)}
    formatted_fluences = list(fluence_mapping.keys())
    fluence_min_var = StringVar(root)
    fluence_min_var.set(formatted_fluences[0])
    # Create OptionMenu dropdowns for Fluence Min
    fluence_min_combobox = ttk.Combobox(frame3, textvariable=fluence_min_var, values=formatted_fluences[:-1], height=10, width=10)  # Limiting dropdown height to 10 items
    fluence_min_combobox.grid(row=1, column=3, sticky="w")

    label_fluences_max = tk.Label(frame3, text="Fluence Max(n/cm^2):", padx=10, pady=10, font="Arial 9 bold", bg=BG_COLOR)
    label_fluences_max.grid(row=2, column=2, sticky="e")
    fluence_max_var = StringVar(root)
    fluence_max_var.set(formatted_fluences[-1])
    fluence_max_combobox = ttk.Combobox(frame3, textvariable=fluence_max_var, values=formatted_fluences[1:], height=10, width=10)  # Limiting dropdown height to 10 items
    fluence_max_combobox.grid(row=2, column=3, sticky="w")

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
    frame4 = create_frame(2, 6,"",width=2, height=2, borderwidth=0, highlightbackground="brown4", highlightthickness=3, bg=BG_COLOR)
    # Button size
    button_text_scale = "Change to Log Scale"
    button_width = len(button_text_scale) + 4  # Add some padding to the width
    button_height = 1

    # Button Design
    button_bg_color = "brown4"
    button_fg_color = "white"

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

# Create the Fluence GUI
create_fluence_gui()

# create the TID GUI
create_tid_gui()

# create the TID_Fluence GUI
create_ion_fluence_gui()

# Display Fluence Frame initially
show_frame(fluence_frame)

# Overwrite the on_closing function to restore stdout
def on_closing():
    plt.close('all')  # Close all Matplotlib figures
    root.destroy()  # Destroy the Tkinter window

root.protocol("WM_DELETE_WINDOW", on_closing) # set the 'on_closing()' function to be called when you exit the program

# Running the window
root.mainloop()