
import os
import subprocess
from pathlib import Path
import concurrent.futures
from typing import List
import pandas as pd
import re # regex library
from constants import *

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
        return Err("File not found.")

def format_string_with_dict(content: str, replacements_dict):
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

def write_string_to_file(filename, string):
    with open(filename, 'w') as file:
        file.write(string)


def delete_files_in_folder(folder_path):
    # Check if the folder exists
    if not os.path.exists(folder_path):
        print(f"Folder '{folder_path}' not found.")
        return

    # Get a list of files in the folder
    files_to_delete = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

    # Delete each file
    for file_name in files_to_delete:
        file_path = os.path.join(folder_path, file_name)
        os.remove(file_path)
        # print(f"Deleted file: {file_path}")

def run_command(command):
    """Example usage:
    command = "echo Hello, world!"
    stdout, stderr, exit_code = run_command(command)
    """
    # Run the command and capture the output
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Return the standard output, standard error, and exit code from the command
    return result.stdout, result.stderr, result.returncode

def parse_output_data(content: str):
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


def generate_netlist(pnp_is: float, pnp_n: float, npn_is: float, npn_n: float, desired_voltage: float, idx: int):
    # Adjust the output file and template names based on the index
    outfile = Path(get_output_path(idx))
    temp_netlist_name = get_netlist_path(idx)

    d = {
        "output_filename": outfile,
        "PNP_IS": pnp_is,
        "PNP_N": pnp_n,
        "NPN_IS": npn_is,
        "NPN_N": npn_n
    }
    
    processed_text = process_file_with_replacements(AD590_NETLIST_TEMPLATE, d)
    write_string_to_file(temp_netlist_name, processed_text)


def run_commands_in_parallel(command_template="xyce\\Xyce.exe {file_name}", num_files:int = 1):
    def execute_command(file_name):
        command = command_template.format(file_name=file_name)
        subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Generate a list of file names based on the specified format
    file_names = [f"tempfiles/netlists/netlist_{idx}.cir" for idx in range(num_files)]
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Submit tasks for each file in the list
        futures = [executor.submit(execute_command, file_name) for file_name in file_names]

        # Wait for all tasks to complete
        concurrent.futures.wait(futures)

def find_current_for_desired_voltage(index_count, desired_voltage: float) -> List[float]:
    # a serial function
    result = []
    for index in range(index_count): 
        outfile = (f"tempfiles/xyce_output/xoutput_{index}.out")

        try:
            outtext = read_file_as_string(outfile)
            out_data = parse_output_data(outtext)
            
            for voltage, current in out_data:
                if voltage == desired_voltage:
                    result.append(current)
            
        except Exception as e:
            print(f"Error processing {outfile}: {str(e)}")
    return result

def all_data_points_fluences_vs_current(desired_voltage):
    npn_df = pd.read_excel('excel-files/NPN_diode_parameters_V0.xlsx')
    pnp_df = pd.read_excel('excel-files/PNP_diode_parameters_V0.xlsx')
    index_count = len(npn_df)
    fluences = []
    
    # Clean the previous netlist files
    netlist_folder_path = OUTPUT_DIR
    delete_files_in_folder(netlist_folder_path)
    xyce_output_folder_path = TEMP_NETLIST_DIR
    delete_files_in_folder(xyce_output_folder_path)

    # write the netlists serially
    for (idx_npn, data_npn), (idx_pnp, data_pnp) in zip(npn_df.iterrows(), pnp_df.iterrows()):
        avg_fluences = (data_npn['fluences (n/cm^2)'] + data_pnp['fluences (n/cm^2)']) / 2
        generate_netlist(
            pnp_is=data_pnp['Is'],
            pnp_n=data_pnp['n'],
            npn_is=data_npn['Is'],
            npn_n=data_npn['n'],
            desired_voltage=desired_voltage,
            idx=idx_npn
        )
        fluences.append(avg_fluences)
    
    # calling the xyce to execute the netlist files
    command_template = "xyce\\Xyce.exe {file_name}"
    run_commands_in_parallel(command_template, index_count)
        
    currents = find_current_for_desired_voltage(index_count, desired_voltage)
    return list(zip(fluences, currents))

def generate_data_for_AD590(voltage, fluences_min, fluences_max):
    xs = []
    ys = []
    for fluences, current in all_data_points_fluences_vs_current(voltage):
        if fluences_min <= fluences <= fluences_max:
            xs.append(fluences)
            ys.append(current * 10 ** 6) # convert amps to micro amps
    return {
        'Fluences (n/cm^2)': xs,
        'I_out (µA)': ys
    }

if __name__ == "__main__": # python best practice. Ask google or ChatGPT if confused.
    data = generate_data_for_AD590(5.0, -float('inf'), float('inf'))
    print(len(data.items()))