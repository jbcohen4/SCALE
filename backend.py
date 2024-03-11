
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

def write_string_to_file(filename, string):
    with open(filename, 'w') as file:
        file.write(string)

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
    import re
    # Regular expression to match lines with two floating-point numbers
    pattern = r'\s*([\d\.\+\-eE]+)\s+([\d\.\+\-eE]+)'
    
    # Find all matches of the pattern
    matches = re.findall(pattern, content)
    
    # Convert matches to tuples of floats
    data_tuples = [(float(v1), float(v2)) for v1, v2 in matches]
    
    return data_tuples


def generate_single_current_value(pnp_is: float, pnp_n: float, npn_is: float, npn_n: float, desired_voltage: float) -> float:
    from pathlib import Path

    outfile = Path("tempfiles/t1.out")

    d = {
        "output_filename": outfile,
        "PNP_IS": pnp_is,
        "PNP_N": pnp_n,
        "NPN_IS": npn_is,
        "NPN_N": npn_n
    }

    processed_text = process_file_with_replacements("netlists/AD590_template.cir", d)

    temp_netlist_name = "tempfiles/netlist.cir"

    write_string_to_file(temp_netlist_name, processed_text)

    run_command(f"xyce\\Xyce.exe {temp_netlist_name}")

    outtext = read_file_as_string(outfile)
    out_data = parse_output_data(outtext)
    for voltage, current in out_data:
        if voltage == desired_voltage:
            return current
    assert False


def all_data_points_fluences_vs_current(desired_voltage):
    import pandas as pd
    npn_df = pd.read_excel('excel-files/NPN_diode_parameters_V0.xlsx')
    pnp_df = pd.read_excel('excel-files/PNP_diode_parameters_V0.xlsx')

    for (idx_npn, data_npn), (idx_pnp, data_pnp) in zip(npn_df.iterrows(), pnp_df.iterrows()):
        avg_fluences = (data_npn['fluences (n/cm^2)'] + data_pnp['fluences (n/cm^2)']) / 2
        current = generate_single_current_value(
            pnp_is=data_pnp['Is'],
            pnp_n=data_pnp['n'],
            npn_is=data_npn['Is'],
            npn_n=data_npn['n'],
            desired_voltage=desired_voltage
        )
        yield (avg_fluences, current)

def current_to_temp_for_AD590(current: float) -> float:
    """The AD590 circuit is a temperature sensor. Higher temperatures will cause it to output more current.
    There is a formula to calculate the temperature given the current. 
    Temp = Current * 10 ^ 6 - 273, where Temp is in °C, and Current is in Amps."""
    return current * 10**6 - 273

# Function to write the output of the generator to a CSV file
def write_fluences_vs_temp_to_csv(filename, desired_voltage=5.0):
    import csv
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Fluences (n/cm^2)', 'Temperature (Celsius)'])  # Writing the headers
        
        # Calling the generator and writing its output to the CSV
        for avg_fluences, current in all_data_points_fluences_vs_current(desired_voltage):
            temp = current_to_temp_for_AD590(current)
            writer.writerow([avg_fluences, temp])

def generate_data_for_AD590(voltage, fluences_min, fluences_max):
    xs = []
    ys = []
    for fluences, current in all_data_points_fluences_vs_current(voltage):
        if fluences_min <= fluences <= fluences_max:
            temp = current_to_temp_for_AD590(current)
            xs.append(fluences)
            ys.append(temp)
    return {
        'Fluences (n/cm^2)': xs,
        'Temperature (Celsius)': ys
    }


if __name__ == "__main__": # python best practice. Ask google or ChatGPT if confused.
    write_fluences_vs_temp_to_csv('output/fluences-vs-temp.csv')


