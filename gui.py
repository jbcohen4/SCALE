import tkinter as tk
from tkinter import ttk #importing packages

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

initial_window_dimensions = { # these numbers will be used to display the inital window
    "x": 50,
    "y": 50,
    "width": 1500,
    "height": 1000
}

parts = ["part 1", "part 2", "part 3"]

def main():
    root = tk.Tk()
    root.title("Radiation on BJT explorer")
    dims = initial_window_dimensions # rename shorter so it's easier to use. The long name is also good because it's descriptive
    root.geometry(f"{dims['width']}x{dims['height']}+{dims['x']}+{dims['y']}")
    root.resizable(True, True)
    part_combobox = ttk.Combobox(root, values=parts)
    label = tk.Label(root, text="choose a part:")
    label.place(x=20, y=20)
    root.update() # this is needed so that objects know thier correct dimensions
    label_dimensions = {
        'x': label.winfo_x(),
        'y': label.winfo_y(),
        'width': label.winfo_width(),
        'height': label.winfo_height()
    }

    part_combobox.place(
        x=label_dimensions["x"] + label_dimensions["width"] + 20,
        y=label_dimensions["y"]
    )
    part_combobox.current(0) # set default value
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


main()
