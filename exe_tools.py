import pandas as pd
import os, sys
from pathlib import Path
def adjust_path(path: str):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(__file__))
    return Path(os.path.join(base_path, path))

def read_csv_to_df(csv_path: str) -> pd.DataFrame:
    """Works for both running as a python script and running as a .exe from pyinstaller"""
    return pd.read_csv(adjust_path(csv_path))

def read_txt_file(path: str) -> str:
    path = adjust_path(path)
    with open(path, 'r') as file:
        return file.read()

def get_pdf_path(pdf_filename: str) -> Path:
    """Returns the path to the PDF file in the pdf directory, adjusted for executable mode."""
    pdf_directory = adjust_path('pdf')  # Adjust the path to point to the pdf directory
    pdf_path = pdf_directory / pdf_filename
    return pdf_path

from uuid import uuid4 # ChatGPT says uuid4 is the best kind of uuid
PYTHON_MODE = uuid4() 
EXE_MODE = uuid4()
def curr_mode():
    in_exe_mode = getattr(sys, '_MEIPASS', False)
    if in_exe_mode:
        return EXE_MODE
    else:
        return PYTHON_MODE