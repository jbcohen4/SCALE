from typing import List, Tuple
import exe_tools
from pathlib import Path
import re, tempfile, os
import pandas as pd
from constants import AD590_NETLIST_TEMPLATE_PATH, XYCE_EXE_PATH
import concurrent.futures



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

def format_string_with_dict(content: str, replacements_dict) -> str:
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


def process_file_with_replacements(file_path, replacements_dict):
    """Processes the file with given replacements, printing an error or returning the updated content."""
    content_or_error = read_file_as_string(file_path)
    if is_error(content_or_error):
        print(content_or_error.message)
        return

    updated_content_or_error = format_string_with_dict(content_or_error, replacements_dict)
    if is_error(updated_content_or_error):
        print(updated_content_or_error.message)
        return

    return updated_content_or_error

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
        
        then this function will return[
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


def generate_single_current_value_AD590(pnp_is: float, pnp_n: float, npn_is: float, npn_n: float, desired_voltage: float) -> float:
    """This function is threadsafe and will work in the executable"""
    netlist_tempfile = tempfile.NamedTemporaryFile(delete=False)
    xyce_output_tempfile = tempfile.NamedTemporaryFile(delete=False)
    try:
        netlist_tempfile.close()
        xyce_output_tempfile.close()
        temp_netlist_file_name = netlist_tempfile.name
        temp_xyce_output_file_name = xyce_output_tempfile.name
        d = {
            "output_filename": temp_xyce_output_file_name,
            "PNP_IS": pnp_is,
            "PNP_N": pnp_n,
            "NPN_IS": npn_is,
            "NPN_N": npn_n
        }
        path_to_AD590_template = AD590_NETLIST_TEMPLATE_PATH
        filled_in_netlist_str = process_file_with_replacements(path_to_AD590_template, d)
        write_string_to_file(temp_netlist_file_name, filled_in_netlist_str)
        path_to_xyce_exe = XYCE_EXE_PATH
        cmd_string = f"{path_to_xyce_exe} {temp_netlist_file_name}"
        stdout, stderr, return_code = run_command(cmd_string)
        out_text = read_file_as_string(temp_xyce_output_file_name)
        out_data = parse_output_data(out_text)
        for voltage, current in out_data:
            if voltage == desired_voltage:
                return current
        assert False
    finally:
        netlist_tempfile.close()
        xyce_output_tempfile.close()
        os.remove(netlist_tempfile.name)
        os.remove(xyce_output_tempfile.name)

def all_data_points_fluences_vs_current_AD590_parrallel(desired_voltage):
    npn_path = exe_tools.adjust_path('csvs/NPN_diode_parameters_V0.csv')
    pnp_path = exe_tools.adjust_path('csvs/PNP_diode_parameters_V0.csv')
    npn_df = pd.read_csv(npn_path)
    pnp_df = pd.read_csv(pnp_path)

    def process_row(row_npn, row_pnp, desired_voltage):
        avg_fluences = (row_npn['fluences (n/cm^2)'] + row_pnp['fluences (n/cm^2)']) / 2
        current = generate_single_current_value_AD590(
            pnp_is=row_pnp['Is'],
            pnp_n=row_pnp['n'],
            npn_is=row_npn['Is'],
            npn_n=row_npn['n'],
            desired_voltage=desired_voltage
        )
        return (avg_fluences, current)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        tasks_args = [(row_npn, row_pnp, desired_voltage) for (_, row_npn), (_, row_pnp) in zip (npn_df.iterrows(), pnp_df.iterrows())]
        results = list(executor.map(lambda args: process_row(*args), tasks_args))
        return results

def all_data_points_fluences_vs_current_AD590_serial(desired_voltage):
    npn_path = exe_tools.adjust_path('csvs/NPN_diode_parameters_V0.csv')
    pnp_path = exe_tools.adjust_path('csvs/PNP_diode_parameters_V0.csv')
    npn_df = pd.read_csv(npn_path)
    pnp_df = pd.read_csv(pnp_path)

    for (idx_npn, data_npn), (idx_pnp, data_pnp) in zip(npn_df.iterrows(), pnp_df.iterrows()):
        avg_fluences = (data_npn['fluences (n/cm^2)'] + data_pnp['fluences (n/cm^2)']) / 2
        current = generate_single_current_value_AD590(
            pnp_is=data_pnp['Is'],
            pnp_n=data_pnp['n'],
            npn_is=data_npn['Is'],
            npn_n=data_npn['n'],
            desired_voltage=desired_voltage
        )
        yield (avg_fluences, current)

def generate_data_for_AD590(voltage, fluences_min, fluences_max):
    xs = []
    ys = []
    for fluences, current in all_data_points_fluences_vs_current_AD590_parrallel(voltage):
        if fluences_min <= fluences <= fluences_max:
            xs.append(fluences)
            ys.append(current * 10 ** 6) # convert amps to micro amps
    return {
        'Fluences (n/cm^2)': xs,
        'I_out (µA)': ys
    }

def main():
    data = generate_data_for_AD590(voltage=5.0, fluences_min=-inf, fluences_max=inf)
    (x_axis_name, x_axis_data), (y_axis_name, y_axis_data) = data.items()
    print(f"{x_axis_name}\t{y_axis_name}")
    for i in range(5):
        print(f"{x_axis_data[i]}\t\t{y_axis_data[i]}")
    pass

if __name__ == "__main__": # python best practice. Ask google or ChatGPT if confused.
    main()


