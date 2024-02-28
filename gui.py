import tkinter as tk
from tkinter import ttk

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import numpy as np

from dataclasses import dataclass

from uuid import uuid4

initial_window_dimensions = { # these numbers will be used to display the inital window
    "x": 50,
    "y": 50,
    "width": 1500,
    "height": 1000
}

parts = ["part 1", "part 2", "part 3"]

sample_data = {
    'xs': [1, 2, 3, 4, 5],
    'ys': [2, -3, 5, -7, 11]
}


button_id = uuid4()


@dataclass
class Dimensions:
    x: int
    y: int
    width: int
    height: int


def run_gui():
    # make window ----------------------------------------------------------------------------------------------------
    root = tk.Tk()
    root.title("Radiation on BJT explorer")
    dims = initial_window_dimensions # rename shorter so it's easier to use. The long name is also good because it's descriptive
    root.geometry(f"{dims['width']}x{dims['height']}+{dims['x']}+{dims['y']}")
    root.resizable(True, True)
    root.config(bg="gray")

    # place part label -----------------------------------------------------------------------------------------------
    part_lbl = tk.Label(root, text="Choose a part:")
    part_lbl.place(x=20, y=20)
    root.update() # this is needed so that objects know thier correct dimensions

    part_lbl_dims = get_lbl_dims(part_lbl)


    part_combobox = ttk.Combobox(root, values=parts)
    part_combobox.place(
        x=part_lbl_dims.x + part_lbl_dims.width + 20,
        y=part_lbl_dims.y
    )
    part_combobox.current(0) # set default value
    part_combobox.config(width=20)


    # place specification label ---------------------------------------------------------------------------------------
    spec_lbl = tk.Label(root, text="Choose a specification:")
    spec_lbl_x = part_lbl_dims.x
    spec_lbl_y = part_lbl_dims.y + part_lbl_dims.height + 20
    spec_lbl.place(x=spec_lbl_x, y=spec_lbl_y)
    root.update()

    spec_lbl_dims = get_lbl_dims(spec_lbl)
    spec_combobox = ttk.Combobox(root, values=["Vref", "option 2"])
    spec_combobox.place(
        x=spec_lbl_dims.x + spec_lbl_dims.width + 20,
        y=spec_lbl_dims.y
    )

    spec_combobox.current(0)

    # place dataset label ---------------------------------------------------------------------------------------------
    dataset_lbl = tk.Label(root, text="Choose a dataset:")
    dataset_lbl_x = spec_lbl_dims.x
    dataset_lbl_y = spec_lbl_dims.y + spec_lbl_dims.height + 20
    dataset_lbl.place(x=dataset_lbl_x, y=dataset_lbl_y)
    root.update()

    dataset_lbl_dims = get_lbl_dims(dataset_lbl)
    dataset_combobox = ttk.Combobox(root, values=["25", "option 2"])
    dataset_combobox.place(
        x=dataset_lbl_dims.x + dataset_lbl_dims.width + 20,
        y=dataset_lbl_dims.y
    )

    dataset_combobox.current(0)
    

    # make plot -------------------------------------------------------------------------------------------------------
    fig, ax = plt.subplots()
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.place(x=600, y=100)

    repopulate_graph(ax, canvas)
    



    # place button ----------------------------------------------------------------------------------------------------
    button = tk.Button(root, text="regenerate data", command=lambda: repopulate_graph(ax, canvas))
    button.place(x=70, y=300)



    root.mainloop() # start the gui


def get_lbl_dims(lbl: tk.Label) -> Dimensions:
    return Dimensions(
        x=lbl.winfo_x(),
        y=lbl.winfo_y(),
        width=lbl.winfo_width(),
        height=lbl.winfo_height()
    )

def add_noise(numbers):
    import random
    return [x + random.uniform(-1, 1) for x in numbers]

def generate_data():
    xs = np.arange(0, 5, 0.1)
    ys = add_noise(xs)
    return (xs, ys)

def repopulate_graph(ax, canvas):
    ax.clear()
    xs, ys = generate_data()
    ax.plot(xs, ys)
    ax.set_xlabel("Fluences (n/cm^2)")
    canvas.draw()

# import tkinter as tk
# from tkinter import ttk

# import matplotlib.pyplot as plt
# from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# import numpy as np

# def run_gui():
#     root = tk.Tk()
#     root.title("Simple GUI")

#     fig, ax = plt.subplots()
#     canvas = FigureCanvasTkAgg(fig, master=root)
#     canvas_widget = canvas.get_tk_widget()
#     canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

#     xs = np.arange(0, 5, 0.1)
#     ys = np.sin(xs)
#     ax.plot(xs, ys)
#     ax.set_xlabel("X-axis")

#     root.mainloop()

# run_gui()
