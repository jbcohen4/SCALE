import tkinter as tk
from tkinter import ttk #importing packages

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Create the main window
root = tk.Tk()
root.title("Simple Window")

initial_window_dimensions = { # these numbers will be used to display the inital window
    "x": 50,
    "y": 50,
    "width": 1500,
    "height": 1000
}

init_dim = initial_window_dimensions # rename shorter so it's easier to use. The long name is good because it's descriptive
root.geometry(f"{init_dim['width']}x{init_dim['height']}+{init_dim['x']}+{init_dim['y']}")

# Make the window resizable
root.resizable(True, True)


parts = ["part 1", "part 2", "part 3"]
part_combobox = ttk.Combobox(root, values=parts) # make a combo box

label = tk.Label(root, text="Choose a part:")
label.place(x=20, y=20)

root.update() # this is needed so that all the objects know their correct x, y, width, height, etc.

label_dimensions = { # these values will be used to calculate where to put the part_combobox
    "x": label.winfo_x(),
    "y": label.winfo_y(),
    "width": label.winfo_width(),
    "height": label.winfo_height()
}



# Positioning the combobox
part_combobox.place(
    x=label_dimensions["x"] + label_dimensions["width"] + 20,
    y=label_dimensions["y"]
)

# Setting the default value
part_combobox.current(0)

# To resize, you can use the width property
part_combobox.config(width=20)


# Sample data
x_coords = [1, 2, 3, 4, 5]
y_coords = [2, -3, 5, -7, 11]

# Create a figure for the plot
fig, ax = plt.subplots()
ax.plot(x_coords, y_coords)

# Embedding the plot in Tkinter
canvas = FigureCanvasTkAgg(fig, master=root)
canvas_widget = canvas.get_tk_widget()
canvas_widget.pack()

# Start the GUI
root.mainloop()
