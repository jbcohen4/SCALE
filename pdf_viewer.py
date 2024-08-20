# pdf_viewer.py

import tkinter as tk
from PIL import Image, ImageTk
import fitz  # PyMuPDF

class PDFViewer(tk.Toplevel):
    def __init__(self, master, pdf_path):
        super().__init__(master)
        self.title("PDF Viewer")
        self.pdf_path = pdf_path
        self.doc = fitz.open(pdf_path)
        self.page_num = 0
        self.zoom_level = 1.0

        self.setup_ui()
        self.show_page()

        self.attributes('-fullscreen', True)

    def setup_ui(self):
        self.canvas = tk.Canvas(self, bg="black")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.create_navigation_buttons()

    def create_navigation_buttons(self):
        button_config = {'bg': "brown4", 'fg': "white", 'bd': 0, 'relief': "solid"}
        self.btn_prev = tk.Button(self, text="Previous", command=self.prev_page, **button_config)
        self.btn_next = tk.Button(self, text="Next", command=self.next_page, **button_config)
        self.btn_zoom_in = tk.Button(self, text="Zoom In", command=self.zoom_in, **button_config)
        self.btn_zoom_out = tk.Button(self, text="Zoom Out", command=self.zoom_out, **button_config)
        self.btn_exit = tk.Button(self, text="Exit Fullscreen", command=self.exit_fullscreen, bg="red", fg="white")

        self.btn_prev.pack(side=tk.LEFT, padx=10, pady=10)
        self.btn_next.pack(side=tk.LEFT, padx=10, pady=10)
        self.btn_zoom_out.pack(side=tk.LEFT, padx=10, pady=10)
        self.btn_zoom_in.pack(side=tk.LEFT, padx=10, pady=10)
        self.btn_exit.pack(side=tk.BOTTOM, pady=10)

    def show_page(self):
        page = self.doc.load_page(self.page_num)
        mat = fitz.Matrix(self.zoom_level, self.zoom_level)
        pix = page.get_pixmap(matrix=mat)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        self.img_tk = ImageTk.PhotoImage(img)

        self.canvas.create_image(0, 0, anchor="nw", image=self.img_tk)
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

    def next_page(self):
        if self.page_num < len(self.doc) - 1:
            self.page_num += 1
            self.show_page()

    def prev_page(self):
        if self.page_num > 0:
            self.page_num -= 1
            self.show_page()

    def zoom_in(self):
        self.zoom_level *= 1.2
        self.show_page()

    def zoom_out(self):
        if self.zoom_level > 0.5:
            self.zoom_level /= 1.2
            self.show_page()

    def exit_fullscreen(self):
        self.attributes('-fullscreen', False)
        self.geometry("800x600")