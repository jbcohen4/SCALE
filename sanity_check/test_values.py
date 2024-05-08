from typing import List, Tuple

from pathlib import Path
import re, tempfile, os
import pandas as pd
import sys
import concurrent.futures
import numpy as np
from functools import lru_cache

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
from constants import * 

inf = float('inf')


class Err:
    def __init__(self, message):
        self.message = message

def is_error(x):
    return isinstance(x, Err)

def read_file_as_string(file_path):
    """Reads the contents of a file and returns it as a string or an error."""
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        return Err(f"File not found: {file_path}")

def write_string_to_file(filename, string):
    with open(filename, 'w') as file:
        file.write(string)

def process_string_with_replacements(content: str, replacements_dict) -> str:
    """Replaces placeholders in the content with values from the replacements_dict.
    Returns the updated content."""

    """Example: given: content="Hi. {x} says {y}." and replacements_dict={"x": bob, "y": howdy}, 
    This func will return "Hi. bob says howdy."
    """
    for key, val in replacements_dict.items():
        placeholder = "{" + key + "}"
        if not placeholder in content: # whatever it is that we're trying to replace, that string should be in the content
            print(f"missing placeholder: {placeholder}")
            assert False
        content = content.replace(placeholder, str(val))
    return content

def run_command(command):
    """Example usage:
    command = "echo Hello, world!"
    stdout, stderr, exit_code = run_command(command)
    """
    import subprocess
    # Run the command and capture the output
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Return the standard output, standard error, and exit code from the command
    return result.stdout, result.stderr, result.returncode


def get_all_xyce_output_1_diode_txt(netlist_template_path: str, fluence, diode:str,number):
    
    netlist_tempfile = tempfile.NamedTemporaryFile(delete=False)
    xyce_output_file = tempfile.NamedTemporaryFile(delete=False)

    with open(netlist_template_path, 'r') as file:
        netlist_template = file.read()
    try:
        netlist_tempfile.close()
        xyce_output_file.close()
        temp_netlist_filename = netlist_tempfile.name
        temp_xyce_output_filename = xyce_output_file.name
        name = "{:.0e}".format(fluence)
        name = name.replace('+','')
        if diode == 'PNP':
            DF = PNP_DF
        else: DF = NPN_DF 
        d = {
                "output_filename": f'MATLAB/{diode}_{name}_{number}.txt',
                f"{diode}_IS1": DF[DF["fluences (n/cm^2)"] == fluence][f'Is_{number}'].values[0],
                f"{diode}_N1": DF[DF["fluences (n/cm^2)"] == fluence][f'n_{number}'].values[0],
            }
        filled_in_netlist_str = process_string_with_replacements(netlist_template, d)
        write_string_to_file(temp_netlist_filename, filled_in_netlist_str)
        cmd_string = f"{XYCE_EXE_PATH} {temp_netlist_filename}"
        stdout, stderr, return_code = run_command(cmd_string)
        out_text = read_file_as_string(temp_xyce_output_filename)
        
    finally:
        netlist_tempfile.close()
        xyce_output_file.close()
        os.remove(netlist_tempfile.name)
        os.remove(xyce_output_file.name)

def get_all_xyce_output_2_diodes_txt(netlist_template_path: str, fluence, diode:str):
    
    netlist_tempfile = tempfile.NamedTemporaryFile(delete=False)
    xyce_output_file = tempfile.NamedTemporaryFile(delete=False)

    with open(netlist_template_path, 'r') as file:
        netlist_template = file.read()
    try:
        netlist_tempfile.close()
        xyce_output_file.close()
        temp_netlist_filename = netlist_tempfile.name
        temp_xyce_output_filename = xyce_output_file.name
        name = "{:.0e}".format(fluence)
        name = name.replace('+','')
        if diode == 'PNP':
            DF = PNP_DF
        else: DF = NPN_DF 
        d = {
                "output_filename": f'MATLAB/{diode}_{name}.txt',
                f"{diode}_IS1": DF[DF["fluences (n/cm^2)"] == fluence]['Is_1'].values[0],
                f"{diode}_N1": DF[DF["fluences (n/cm^2)"] == fluence]['n_1'].values[0],
                f"{diode}_IS2": DF[DF["fluences (n/cm^2)"] == fluence]['Is_2'].values[0],
                f"{diode}_N2": DF[DF["fluences (n/cm^2)"] == fluence]['n_2'].values[0]
            }
        filled_in_netlist_str = process_string_with_replacements(netlist_template, d)
        write_string_to_file(temp_netlist_filename, filled_in_netlist_str)
        cmd_string = f"{XYCE_EXE_PATH} {temp_netlist_filename}"
        stdout, stderr, return_code = run_command(cmd_string)
        out_text = read_file_as_string(temp_xyce_output_filename)
        print(out_text)
    finally:
        netlist_tempfile.close()
        xyce_output_file.close()
        os.remove(netlist_tempfile.name)
        os.remove(xyce_output_file.name)
       


def main():
    fluences_pnp = [403702000000,1000000000000,4037020000000,10000000000000,40370200000000]
    fluences_npn = [404000000000,1000000000000,4040000000000,10000000000000,40400000000000]
    for fluence_pnp,fluence_npn in zip(fluences_pnp, fluences_npn):
        get_all_xyce_output_2_diodes_txt('netlists/PNP_2diode_sanity_check.txt', fluence_pnp,"PNP")
        get_all_xyce_output_2_diodes_txt('netlists/NPN_2diode_sanity_check.txt', fluence_npn,"NPN")
        for i in range(1,3):
            get_all_xyce_output_1_diode_txt('netlists/PNP_diode_sanity_check.txt', fluence_pnp,"PNP",i)
            get_all_xyce_output_1_diode_txt('netlists/NPN_diode_sanity_check.txt', fluence_npn,"NPN",i)
        


if __name__ == "__main__":
    main()


