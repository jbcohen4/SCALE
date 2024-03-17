import pandas as pd
import os, sys
print('version 4')
def read_csv_to_df(csv_path: str) -> pd.DataFrame:
    """Works for both running as a python script and running as a .exe from pyinstaller"""
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(__file__))
    return pd.read_csv(os.path.join(base_path, csv_path))
df = read_csv_to_df("csvs/dummy.csv")
print(df.head())
