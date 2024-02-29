import tkinter as tk
from tkinter import LabelFrame, StringVar, OptionMenu, ttk

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

import csv

# Create Window for GUI
root = tk.Tk()

# Set title of the window
root.title("Radiation on BJT explorer")

# Set dimensions of the window
root.geometry("800x750")

# Set the background color of the root window
root.configure(bg="darkgray")

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

# Execute function
def execute_function(sample_data):

    csv_file_path = 'output/fluences-vs-temp.csv' 
    with open(csv_file_path, 'r') as file:
        csv_reader = csv.reader(file)
        header_row = next(csv_reader)
    
        xs_column_name = header_row[0]
        ys_column_name = header_row[1]

        for row in csv_reader:
            xs_value = float(row[0])
            ys_value = float(row[1])

            sample_data['xs'].append(xs_value)
            sample_data['ys'].append(ys_value)

    # Frame 4 for graph
    graph_frame = create_frame(2, 0, "Graph", width=6, height=4)

    # Plotting the line chart
    xs = np.array(sample_data['xs'])
    ys = np.array(sample_data['ys'])

    fig, ax = plt.subplots()
    ax.plot(xs, ys)
    ax.set_xlabel(xs_column_name)
    ax.set_ylabel(ys_column_name)
    ax.set_title("Line Chart")
    plt.subplots_adjust(left=0.2)

    # Embedding the plot in the Tkinter window
    canvas = FigureCanvasTkAgg(fig, master=graph_frame)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.grid(row=0, column=0, sticky="nsew")
    graph_frame.update_idletasks()

# Clear function 
def clear_function():
    textbox_temp.delete(0, tk.END)
    textbox_fluences_min.delete(0, tk.END)
    textbox_fluences_max.delete(0, tk.END)
    print("Clear all the fields")

# Frame 1
frame1 = create_frame(0, 0, "", width=2, height=2)

label_Parts = tk.Label(frame1, text="Parts:", padx=5, pady=5, font="Arial 10 bold")
label_Parts.grid(row=0, column=0, sticky="e")

# Dropdown Parts
options_part = ["AD590", "TL431", "TEMP0"]
var1 = StringVar()
var1.set(options_part[0])
dropdown_part = OptionMenu(frame1, var1, *options_part)
dropdown_part.grid(row=0, column=1, sticky="w", padx=5, pady=5)

label_Specifications = tk.Label(frame1, text="Specifications:", padx=5, pady=5, font="Arial 9 bold")
label_Specifications.grid(row=1, column=0, sticky="e")

# Dropdown Specifications
options_specifications = ["Vref", "SPECIFICATION 01", "SPECIFICATION 02"]
var2 = StringVar()
var2.set(options_specifications[0])
dropdown_specifications = OptionMenu(frame1, var2, *options_specifications)
dropdown_specifications.grid(row=1, column=1, sticky="w", padx=5, pady=5)

label_dataset = tk.Label(frame1, text="Dataset:", padx=5, pady=5, font="Arial 9 bold")
label_dataset.grid(row=2, column=0, sticky="we")

label_dataset_vcc = tk.Label(frame1, text="VCC(0~25,step-1):", padx=5, pady=5, font="Arial 9 bold")
label_dataset_vcc.grid(row=3, column=0, sticky="e")

# Themed Entry for Dataset with border and padding
validate_dataset_vcc = (root.register(validate_numerical), '%P')
textbox_dataset_vcc = ttk.Entry(frame1, style="TEntry", validate="key", validatecommand=validate_dataset_vcc)
textbox_dataset_vcc.grid(row=3, column=1, sticky="w")

# Frame 2
frame2 = create_frame(0, 2, "", width=2, height=2)

label_temp = tk.Label(frame2, text="Temperature (C):", padx=5, pady=5, font="Arial 9 bold")
label_temp.grid(row=0, column=0, sticky="e")

# Themed Entry for Temperature with border and padding
validate_temp = (root.register(validate_numerical), '%P')
textbox_temp = ttk.Entry(frame2, style="TEntry", validate="key", validatecommand=validate_temp)
textbox_temp.grid(row=0, column=1, sticky="w")

label_fluences_min = tk.Label(frame2, text="Fluences Min(K):", padx=5, pady=5, font="Arial 9 bold")
label_fluences_min.grid(row=1, column=0, sticky="e")

# Themed Entry for Fluences Min with border and padding
validate_fluences_min = (root.register(validate_numerical), '%P')
textbox_fluences_min = ttk.Entry(frame2, style="TEntry", validate="key", validatecommand=validate_fluences_min)
textbox_fluences_min.grid(row=1, column=1, sticky="w")

label_fluences_max = tk.Label(frame2, text="Fluences Max(K):", padx=5, pady=5, font="Arial 9 bold")
label_fluences_max.grid(row=2, column=0, sticky="e")

# Themed Entry for Fluences Max with border and padding
validate_fluences_max = (root.register(validate_numerical), '%P')
textbox_fluences_max = ttk.Entry(frame2, style="TEntry", validate="key", validatecommand=validate_fluences_max)
textbox_fluences_max.grid(row=2, column=1, sticky="w")

# Frame 3
frame3 = create_frame(0, 4, "", width=4)
# Button size
button_width = 10
button_height = 1

# Sample data
sample_data = {'xs': [], 'ys': []}

#Buttons
execute_button = tk.Button(frame3, text="Execute", command=lambda: execute_function(sample_data), width=button_width, height=button_height)
execute_button.grid(row=0, column=1, padx=5, pady=5)

change_scale_button = tk.Button(frame3, text="Change Scale", command="", width=button_width, height=button_height)
change_scale_button.grid(row=2, column=1, padx=5, pady=5)

save_button = tk.Button(frame3, text="Save", command="", width=button_width, height=button_height)
save_button.grid(row=3, column=1, padx=5, pady=5)

clear_button = tk.Button(frame3, text="Clear", command=clear_function, width=button_width, height=button_height)
clear_button.grid(row=4, column=1, padx=5, pady=5)

# Running the window
root.mainloop()