from typing import List, Tuple
import exe_tools
from pathlib import Path
import re, tempfile, os
import pandas as pd
from constants import AD590_NETLIST_TEMPLATE_PATH, XYCE_EXE_PATH, LM741_NETLIST_PATH , IOS_VOS_IB_1_PATH, IOS_VOS_IB_2_PATH, IOS_VOS_IB_3_PATH, NPN_DF, PNP_DF
import concurrent.futures
import numpy as np
from functools import lru_cache


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
    Returns the updated content or an error if a placeholder is not found in the dictionary."""

    """Example: given: content="Hi. {x} says {y}." and replacements_dict={"x": bob, "y": howdy}, 
    This func will return "Hi. bob says howdy."
    """
    # Find all placeholders in the content
    placeholders = re.findall(r'\{(.*?)\}', content) # uses a regex from chatgpt. It finds all substrings enclosed by {}
    
    missing_keys = [placeholder for placeholder in placeholders if placeholder not in replacements_dict]
    if missing_keys: # if there is at least 1 required key that is not found
        return Err(f"Error: Looked for {', '.join(missing_keys)} but did not find.")
    else:
        for key, val in replacements_dict.items():
            placeholder = "{" + key + "}"
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


def parse_output_data(content: str) -> List[Tuple[float, float]]:
    """This takes the content of a file that xyce wrote to and returns a list of tuples of the numbers it gave
    Ex: if the content is
            V(2)             I(VOUT)     
                0.00000000e+00    7.88778843e-25
                1.00000000e+00    9.66696441e-06
                        ...(more rows)...
                2.90000000e+01    2.99970895e-04
                3.00000000e+01    3.00012198e-04
            End of Xyce(TM) Simulation
        
    then this function will return
        [
            (0.0, 7.88778843e-25),
            (1.0, 9.66696441e-06),
                    ...
            (29.0, 2.99970895e-04),
            (30.0, 3.00012198e-04)
        ]
    """
    # Regular expression to match lines with two floating-point numbers
    pattern = r'\s*([\d\.\+\-eE]+)\s+([\d\.\+\-eE]+)'
    
    # Find all matches of the pattern
    matches = re.findall(pattern, content)
    
    # Convert matches to tuples of floats
    data_tuples = [(float(v1), float(v2)) for v1, v2 in matches]
    
    return data_tuples

@lru_cache
def run_xyce_on_netlist_template(netlist_template: str, desired_vcc: float, fluences_min: float, fluences_max: float) -> List[Tuple[float, float]]:
    """You give this function a voltage and netlist template. The template should need to be filled in with exactly the following: 
        {output_filename}, {PNP_IS}, {PNP_N}, {NPN_IS}, {NPN_N}. If the given template has more fields than this, this function will not work.
    Also: The filled in netlist should have Xyce output a file with exactly 2 coloumns, or this function won't work. The AD590 netlist has 
        2 output columns, so do the LM471 netlists for generating VO1, VO2, and VO3.
    This function will NOT work for the LM471 generating slew rate or open loop gain, since those netlists make xyce output files with more than 2 columns.
    """
    def process_row(row_npn, row_pnp):
        avg_fluences = (row_npn['fluences (n/cm^2)'] + row_pnp['fluences (n/cm^2)']) / 2
        if fluences_min <= avg_fluences <= fluences_max:
            netlist_tempfile = tempfile.NamedTemporaryFile(delete=False)
            xyce_output_file = tempfile.NamedTemporaryFile(delete=False)
            try:
                netlist_tempfile.close()
                xyce_output_file.close()
                temp_netlist_filename = netlist_tempfile.name
                temp_xyce_output_filename = xyce_output_file.name
                d = {
                    "output_filename": temp_xyce_output_filename,
                    "PNP_IS": row_pnp['Is'],
                    "PNP_N": row_pnp['n'],
                    "NPN_IS": row_npn['Is'],
                    "NPN_N": row_npn['n']
                }
                filled_in_netlist_str = process_string_with_replacements(netlist_template, d)
                write_string_to_file(temp_netlist_filename, filled_in_netlist_str)
                cmd_string = f"{XYCE_EXE_PATH} {temp_netlist_filename}"
                stdout, stderr, return_code = run_command(cmd_string)
                out_text = read_file_as_string(temp_xyce_output_filename)
                out_data = parse_output_data(out_text)
                for vcc, other in out_data:
                    if vcc == desired_vcc:
                        return (avg_fluences, other)
                assert False
            finally:
                netlist_tempfile.close()
                xyce_output_file.close()
                os.remove(netlist_tempfile.name)
                os.remove(xyce_output_file.name)
        else:
            return None
    with concurrent.futures.ThreadPoolExecutor() as ex:
        tasks_args = [(row_npn, row_pnp) for (_, row_npn), (_, row_pnp) in zip(NPN_DF.iterrows(), PNP_DF.iterrows())]
        results = list(ex.map(lambda args: process_row(*args), tasks_args))
        return [r for r in results if r is not None]


def generate_data_for_AD590(voltage, fluences_min=-inf, fluences_max=inf):
    AD590_netlist_template_str = read_file_as_string(AD590_NETLIST_TEMPLATE_PATH)
    xs, ys = [], []
    for fluences, current in run_xyce_on_netlist_template(AD590_netlist_template_str, voltage, fluences_min, fluences_max):
        assert fluences_min <= fluences <= fluences_max
        xs.append(fluences)
        ys.append(current * 10 ** 6) # convert amps to micro amps
    return {
        'Fluences (n/cm^2)': xs,
        'I_out (µA)': ys
    }

def matrix_math_LM741(vO1: float, vO2: float, vO3: float):
    """Triet gave us a matrix to use for calculating V_os, I_ib, I_os from V_O1, V_O2, V_O3.
    This function is just following the instructions he sent us in an email"""

    # These R values come from Triet
    R1 = 10e6
    R2 = 1e6
    R3 = 9e6
    
    v_out = np.array([[vO1],[vO2],[vO3]])
    matrix = np.array([
        [-(R1/R2+1), R1-R3*(R1/R2+1), (R1+R3*(R1/R2+1))/2],
        [-1, -R3, R3/2],
        [-(R1/R2+1), R1, R1/2],
    ])

    result_vector = np.linalg.solve(matrix,v_out)

    V_os, I_ib, I_os = result_vector[0,0], result_vector[1,0], result_vector[2,0]

    return  V_os, I_ib, I_os

def generate_data_for_LM741(voltage, fluences_min, fluences_max, specification: str):
    testbench_paths = [IOS_VOS_IB_1_PATH, IOS_VOS_IB_2_PATH, IOS_VOS_IB_3_PATH]
    testbench_strings = [read_file_as_string(path) for path in testbench_paths]
    subcircuit_string = read_file_as_string(LM741_NETLIST_PATH)
    full_netlist_templates = [testbench_string + "\n" + subcircuit_string for testbench_string in testbench_strings]
    xyce_outputs = [run_xyce_on_netlist_template(netlist_template_str, voltage, fluences_min, fluences_max) for netlist_template_str in full_netlist_templates]
    assert all(len(l) == len(xyce_outputs[0]) for l in xyce_outputs) # all 3 lists in xyce_outputs should be the same length
    f1_f2_f3 = [(f1, f2, f3) for (f1, _), (f2, _), (f3, _) in zip(*xyce_outputs)] # get all the fluence values
    for f1, f2, f3 in f1_f2_f3: assert f1 == f2 == f3 # the fluence values should be identical
    v_outs = [(vout1, vout2, vout3) for (_, vout1), (_, vout2), (_, vout3) in zip (*xyce_outputs)]
    Vos_Iib_Ios = [matrix_math_LM741(vout1, vout2, vout3) for vout1, vout2, vout3 in v_outs]
    fluences = [f1 for (f1, _), (f2, _), (f3, _) in zip(*xyce_outputs)]
    if specification == "V_os":
        return {
            'Fluences (n/cm^2)': fluences,
            'V_os (mV)': [V_os * 10 ** 3 for V_os, I_ib, I_os in Vos_Iib_Ios]
        }
    elif specification == "I_b":
        return {
            'Fluences (n/cm^2)': fluences,
            'I_ib (nA)': [I_ib * 10 ** 9 for V_os, I_ib, I_os in Vos_Iib_Ios]
        }
    elif specification == "I_os":
        return {
            'Fluences (n/cm^2)': fluences,
            'I_os (nA)': [I_os * 10 ** 9 for V_os, I_ib, I_os in Vos_Iib_Ios]
        }
    else:
        assert False


# Function to return the data to GUI 
def generate_data(Selected_Part, Selected_Specification, Voltage, Fluence_Min, Fluence_Max):
    if Selected_Part == "AD590":
        return generate_data_for_AD590(voltage=Voltage, fluences_min=Fluence_Min, fluences_max=Fluence_Max)
    elif Selected_Part == "LM741":
        return generate_data_for_LM741(voltage=Voltage, fluences_min=Fluence_Min, fluences_max=Fluence_Max, specification=Selected_Specification)
    else:
        assert False
    pass

def main():
    data = all_data_points_fluences_vs_Vos_Ib_Ios_LM741(desired_voltage=15)
    first_5_datapoints = [next(data) for _ in range(5)]
    df = pd.DataFrame(first_5_datapoints)
    print(df)
    pass

if __name__ == "__main__":
    main()


