# Defining all the constants here
from pathlib import Path

OUTPUT_DIR = Path("tempfiles/xyce_output")
TEMP_NETLIST_DIR = Path("tempfiles/netlists")
AD590_NETLIST_TEMPLATE = Path("netlists/AD590_template.cir")

def get_output_path(idx):
    return OUTPUT_DIR / f"xoutput_{idx}.out"

def get_netlist_path(idx):
    return TEMP_NETLIST_DIR / f"netlist_{idx}.cir"
