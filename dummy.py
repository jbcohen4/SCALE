from typing import List, Tuple
import making_exe
from pathlib import Path

print('version 10')


import tempfile, os


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

    import re # regex library
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
    import re
    # Regular expression to match lines with two floating-point numbers
    pattern = r'\s*([\d\.\+\-eE]+)\s+([\d\.\+\-eE]+)'
    
    # Find all matches of the pattern
    matches = re.findall(pattern, content)
    
    # Convert matches to tuples of floats
    data_tuples = [(float(v1), float(v2)) for v1, v2 in matches]
    
    return data_tuples


def generate_single_current_value(pnp_is: float, pnp_n: float, npn_is: float, npn_n: float, desired_voltage: float) -> float:
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
        path_to_AD590_template = making_exe.adjust_path("netlists/AD590_template.cir")
        filled_in_netlist_str = process_file_with_replacements(path_to_AD590_template, d)
        write_string_to_file(temp_netlist_file_name, filled_in_netlist_str)
        path_to_xyce_exe = making_exe.adjust_path("xyce/Xyce.exe")
        cmd_string = f"{path_to_xyce_exe} {temp_netlist_file_name}"
        print(cmd_string)
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

current = generate_single_current_value(
    pnp_is=9.69548962493215e-16,
    pnp_n=1.202467780625198,
    npn_is=1.393769132284331e-15,
    npn_n=2.045270427325544,
    desired_voltage=5.0
)

print(current)



# temp_netlist_file = tempfile.NamedTemporaryFile(delete=False) # we need to be able to close the files without them getting deleted
# temp_xyce_output_file = tempfile.NamedTemporaryFile(delete=False)
# try:
#     # close both files so you can use them like regular
#     temp_netlist_file.close()
#     temp_xyce_output_file.close()


#     outfile_name = Path(temp_xyce_output_file.name)
#     netlist_name = Path(temp_netlist_file.name)
#     d = {
#         "output_filename": outfile_name,
#         "PNP_IS": 9.69548962493215e-16,
#         "PNP_N": 1.202467780625198,
#         "NPN_IS": 1.393769132284331e-15,
#         "NPN_N": 2.045270427325544,
#     }
#     processed_text = serial_backend.process_file_with_replacements("netlists/AD590_template.cir", d)
#     serial_backend.write_string_to_file(netlist_name, processed_text)
#     # read back the contents of the file so you can check that it was written corrctly
#     netlist_contents = serial_backend.read_file_as_string(netlist_name)

#     # actually run the command here
#     path_to_xyce_exe = Path(making_exe.adjust_path("xyce/Xyce.exe"))
#     cmd_string = f"{path_to_xyce_exe} {netlist_name}"
#     print(f"running command '{cmd_string}'")
#     stdout, stderr, return_code = serial_backend.run_command(f"{cmd_string}")
#     response = serial_backend.read_file_as_string(outfile_name)
#     print(len(response))
# finally:
#     temp_netlist_file.close()
#     temp_xyce_output_file.close()
#     os.remove(temp_netlist_file.name)
#     os.remove(temp_xyce_output_file.name)
#     print('everything was successfully deleted')



# npn_df = making_exe.read_csv_to_df('csvs/NPN_diode_parameters_V0.csv')
# print("read npn_df complete")
# pnp_df = making_exe.read_csv_to_df('csvs/PNP_diode_parameters_V0.csv')
# print("read pnp_df complete")

# outfile = Path("tempfiles/t1.out")

# d = {
#     "output_filename": outfile,
#     "PNP_IS": 9.69548962493215e-16,
#     "PNP_N": 1.202467780625198,
#     "NPN_IS": 1.393769132284331e-15,
#     "NPN_N": 2.045270427325544,
# }

# processed_text = serial_backend.process_file_with_replacements("netlists/AD590_template.cir", d)
# print('text processing complete')

# temp_netlist_name = "tempfiles/netlist.cir"

# serial_backend.write_string_to_file(temp_netlist_name, processed_text)

# path_to_xyce_exe = making_exe.adjust_path("xyce/Xyce.exe")
# stdout, stderr, return_code = serial_backend.run_command(f"{path_to_xyce_exe}")
# print(stdout)

