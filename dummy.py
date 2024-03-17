import pandas as pd
import os, sys
print('version 5')
def read_csv_to_df(csv_path: str) -> pd.DataFrame:
    """Works for both running as a python script and running as a .exe from pyinstaller"""
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(__file__))
    return pd.read_csv(os.path.join(base_path, csv_path))

npn_df = read_csv_to_df('csvs/NPN_diode_parameters_V0.csv')
print("read npn_df")
print(npn_df.head())
pnp_df = read_csv_to_df('csvs/PNP_diode_parameters_V0.csv')
print("read pnp_df")
print(pnp_df.head())
