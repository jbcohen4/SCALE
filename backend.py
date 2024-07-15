from typing import List, Tuple
import exe_tools
from pathlib import Path
import re, tempfile, os
import pandas as pd
from constants import * 
import concurrent.futures
import numpy as np
from functools import lru_cache
import ast 

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

def parse_output_data_dynamic(content: str) -> List[Tuple[float, ...]]:
    """
    Parses the content of a file written by Xyce and returns a list of tuples with the numbers it contains.
    This function dynamically handles rows with any number of numeric columns.
    """
    data_tuples = []
    
    # Split the content into lines
    lines = content.strip().split('\n')

    for index, line in enumerate(lines):
        # Try to split the line into numeric values
        try:
            numbers = tuple(map(float, line.split()))
            if numbers:
                data_tuples.append((index-1, ) + numbers)
        except ValueError:
            # Skip lines that do not contain valid numeric data like headers 
            continue

    return data_tuples

def write_output_to_file(filename, content, index):
    output_folder = "output/" 
    output_file = output_folder + filename 
    with open(output_file, 'a') as file:
        file.write(f"Index: {index}\n")
        file.write(content)
        file.write("\n\n")

def write_output_to_multiple_file(filename, content, index):
    output_folder = "output/" 
    output_file = output_folder + filename + str(index) + ".txt"
    with open(output_file, 'w') as file:
        file.write(content)

@lru_cache
def get_pre_rad_xyce_output_txt(netlist_template:str, vos:float = 0.0) -> List[Tuple[float, str]]:
    assert "{output_filename}" in netlist_template
    netlist_tempfile = tempfile.NamedTemporaryFile(delete=False)
    xyce_output_file = tempfile.NamedTemporaryFile(delete=False)
    try:
        netlist_tempfile.close()
        xyce_output_file.close()
        temp_netlist_filename = netlist_tempfile.name
        temp_xyce_output_filename = xyce_output_file.name
        d = {
            "output_filename": temp_xyce_output_filename
        }
        if vos != 0.0:
            d["Vos"] = vos

        filled_in_netlist_str = process_string_with_replacements(netlist_template, d)
        write_string_to_file(temp_netlist_filename, filled_in_netlist_str)
        cmd_string = f"{XYCE_EXE_PATH} {temp_netlist_filename}"
        stdout, stderr, return_code = run_command(cmd_string)
        out_text = read_file_as_string(temp_xyce_output_filename)
        # print(out_text)
        assert len(out_text) > 0
        return (out_text)
    finally:
        netlist_tempfile.close()
        xyce_output_file.close()
        os.remove(netlist_tempfile.name)
        os.remove(xyce_output_file.name)


@lru_cache # all subcircuits + testbenches + specifications should use this. It's super general and works great.
# We'll have to modify it a little bit to deal with AC gain. That's cool. We will do that.
def get_all_xyce_output_txt(netlist_template: str, Vos_values: List[float] = None) -> List[Tuple[float, str]]:
    """Returns an array of (float, str) tuples. The float represents the fluences of the run, the string is the data that xyce gave us back."""
    assert "{output_filename}" in netlist_template
    def process_row(row_npn, row_pnp, row_index, vos=None):
        avg_fluences = (row_npn['fluences (n/cm^2)'] + row_pnp['fluences (n/cm^2)']) / 2
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
            if vos is not None:  # Add vos to the dictionary only if vos_list is not None
                d["Vos"] = round(vos,3)
            filled_in_netlist_str = process_string_with_replacements(netlist_template, d)
            write_string_to_file(temp_netlist_filename, filled_in_netlist_str)
            
            # For Debugging - in case netlist need to be printed and checked
            # write_output_to_multiple_file("NETLIST_741_SLEW_RATE", filled_in_netlist_str, row_index)
            
            cmd_string = f"{XYCE_EXE_PATH} {temp_netlist_filename}"
            stdout, stderr, return_code = run_command(cmd_string)
            out_text = read_file_as_string(temp_xyce_output_filename)
            # print(out_text)
            assert len(out_text) > 0
            return (avg_fluences, out_text)
        finally:
                netlist_tempfile.close()
                xyce_output_file.close()
                os.remove(netlist_tempfile.name)
                os.remove(xyce_output_file.name)
    
    with concurrent.futures.ThreadPoolExecutor() as ex:
        if Vos_values is not None and Vos_values:
            # Create task arguments with vos
            all_task_args = [
                (row_npn, row_pnp, row_index, vos)
                for row_index, ((_, row_npn), (_, row_pnp), vos) in enumerate(zip(NPN_DF.iterrows(), PNP_DF.iterrows(), Vos_values), start=1)]
        else:
            # If vos_list is None or empty, use None for Vos
            all_task_args = [
                (row_npn, row_pnp, row_index, None)
                for row_index, ((_, row_npn), (_, row_pnp)) in enumerate(zip(NPN_DF.iterrows(), PNP_DF.iterrows()), start=1)
            ]
        # Execute the tasks
        results = list(ex.map(lambda args: process_row(*args), all_task_args))
        return results


def generate_data_for_AD590(voltage, fluences_min=-inf, fluences_max=inf):
    xyce_output = [(fluence, out_txt) for (fluence, out_txt) in get_all_xyce_output_txt(AD590_NETLIST_TEMPLATE) if fluences_min <= fluence <= fluences_max]
    xs, ys = [], []
    for fluence, out_txt in xyce_output:
        parsed_output = parse_output_data_dynamic(out_txt)
        for row in parse_output_data_dynamic(out_txt):
            _, Vcc, I_out = row
            if Vcc == voltage:
                xs.append(fluence)
                ys.append(I_out * 10 ** 6) # convert amps to micro amps
                break
        else:
            raise Exception(f"The user asked for voltage: {voltage}V, but that was not one of the Vcc settings that we ran")
    return {
        'Fluence (n/cm^2)': xs,
        'I_out (µA)': ys
    }

def generate_data_for_LM741(VCC, VEE, fluence_min, fluence_max, specification: str):
    subcircuit_pre_rad = LM741_SUBCKT_PRE_RAD_TEMPLATE
    subcircuit = LM741_SUBCKT_POST_RAD_TEMPLATE
    testbench = process_string_with_replacements(LM741_CLUDGE_TESTBENCH, {"Vcc": VCC, "Vee": VEE})
    pre_rad_full_netlist = testbench + "\n" + subcircuit_pre_rad
    full_netlist = testbench + "\n" + subcircuit
    xyce_output_pre_rad = get_pre_rad_xyce_output_txt(pre_rad_full_netlist)
    all_xyce_output = get_all_xyce_output_txt(full_netlist)
    xyce_output = [(fluence, out_txt) for (fluence, out_txt) in all_xyce_output if fluence_min <= fluence <= fluence_max]
    fluences, v_oss, i_ibs, i_oss = [], [], [], [] # the wierd s's in v_oss and such are meant to pronounced v_os's (the plural of v_os)
    # process for pre_rad
    pre_rad_parsed_output = parse_output_data_dynamic(xyce_output_pre_rad)
    set_fluence = 1e11
    for row in pre_rad_parsed_output:
        _, Vcc, _, V_os, I_ib, I_os = row
        if Vcc == 15:
                fluences.append(set_fluence)
                v_oss.append(V_os * 10 ** 3) # volts to mV
                i_ibs.append(I_ib * 10 ** 9) # amps to nA
                i_oss.append(I_os * 10 ** 9) # amps to nA
                break
    # process for post_rad
    for fluence, out_text in xyce_output:
        assert fluence_min <= fluence <= fluence_max
        parsed_output = parse_output_data_dynamic(out_text)
        for row in parsed_output:
            _, Vcc, _, V_os, I_ib, I_os = row # the first _ is the idx. The second _ is V(3) in the xyce output. 
            if Vcc == VCC:
                fluences.append(fluence)
                v_oss.append(V_os * 10 ** 3) # volts to mV
                i_ibs.append(I_ib * 10 ** 9) # amps to nA
                i_oss.append(I_os * 10 ** 9) # amps to nA
                break
        else: # google "python for else" if confused
            print(f"you asked for a Vcc of {VCC} but we can't give that to you right now.")
            assert False # The problem here is that we can't give them the voltage they asked for. We should probably give them an error message instead of crashing.
    if specification == "V_os":
        return {'Fluence (n/cm^2)': fluences, 'V_os (mV)': v_oss}
    elif specification == "I_ib":
        return {'Fluence (n/cm^2)': fluences, 'I_ib (nA)': i_ibs}
    elif specification == "I_os":
        return {'Fluence (n/cm^2)': fluences, 'I_os (nA)': i_oss}
    else:
        assert False

def generate_data_for_LM741_SLEW_RATE(VCC, fluence_min, fluence_max, specification: str):
    subcircuit_pre_rad = LM741_SUBCKT_PRE_RAD_TEMPLATE
    subcircuit = LM741_SUBCKT_POST_RAD_TEMPLATE
    testbench = LM741_SLEW_RATE_TESTBENCH
    pre_rad_full_netlist = testbench + "\n" + subcircuit_pre_rad
    full_netlist = testbench + "\n" + subcircuit

    xyce_output_pre_rad = get_pre_rad_xyce_output_txt(pre_rad_full_netlist)
    all_xyce_output = get_all_xyce_output_txt(full_netlist)
    xyce_output = [(fluence, out_txt) for (fluence, out_txt) in all_xyce_output if fluence_min <= fluence <= fluence_max]
    fluences, Slew_rate, Supply_current = [], [], []
    
    # process for pre_rad
    pre_rad_parsed_output = parse_output_data_dynamic(xyce_output_pre_rad)
    set_fluence = 1e11
    if pre_rad_parsed_output:
        fluences.append(set_fluence)
        Supply_current.append(pre_rad_parsed_output[0][4] * 10 ** 6) # amps to µA
        v3_values = [v_3 for _, _, _, v_3, _ in pre_rad_parsed_output]
        min_v3 = min(v3_values)
        max_v3 = max(v3_values)
        delta_v3 = max_v3 - min_v3

        v1 = (delta_v3 * 0.4) + min_v3
        v2 = (delta_v3 * 0.6) + min_v3

        t1 = t2 = prev_time = None

        for _, time, _, v_3, _ in pre_rad_parsed_output:
            # if t1 is None and v_3 >= v1:
            #     t1 = prev_time if prev_time is not None else time
            # if t2 is None and v_3 >= v2:
            #     t2 = prev_time if prev_time is not None else time
            # prev_time = time
            if t1 is None and v_3 >= v1:
                    t1 = time
            if t2 is None and v_3 >= v2:
                    t2 = time

            if t1 is not None and t2 is not None:
                break
        
        if t1 is not None and t2 is not None and t1 != t2:
            slew_rate = ((v2 - v1) / (t2 - t1)) / 10 ** 6
        else:
            slew_rate = None
        
        Slew_rate.append(slew_rate)

    # process for post_rad
    flag = False
    index = 1
    for fluence, out_text in xyce_output:
        assert fluence_min <= fluence <= fluence_max
        # display values in console for first iteration only
        # if flag == False:
        #     print(out_text)
        #     flag = True
        # DEBUG: Store the xyce output files in output folder
        # write_output_to_file("post_rad_LM741_slew_rate.txt", out_text, index)

        parsed_output = parse_output_data_dynamic(out_text)
        if parsed_output:
            fluences.append(fluence)
            Supply_current.append(parsed_output[0][4] * 10 ** 6) # amps to µA
            
            v3_values = [v_3 for _, _, _, v_3, _ in parsed_output]
            min_v3 = min(v3_values) 
            max_v3 = max(v3_values) 
            delta_v3 = max_v3 - min_v3 

            v1 = (delta_v3 * 0.4) + min_v3 
            v2 = (delta_v3 * 0.6) + min_v3 

            t1 = t2 = prev_time = None

            for _, time, _, v_3, _ in parsed_output:
                # if t1 is None and v_3 >= v1:
                #     t1 = prev_time if prev_time is not None else time
                # if t2 is None and v_3 >= v2:
                #     t2 = prev_time if prev_time is not None else time
                # prev_time = time
                if t1 is None and v_3 >= v1:
                    t1 = time
                if t2 is None and v_3 >= v2:
                    t2 = time

                if t1 is not None and t2 is not None:
                    break
            
            if t1 is not None and t2 is not None and t1 != t2:
                slew_rate = ((v2 - v1) / (t2 - t1)) / 10 ** 6
            else:
                slew_rate = None      
            Slew_rate.append(slew_rate)
            # print(f"index: {index}, v1: {v1}, v2: {v2}, t1: {t1}, t2: {t2}, slew_rate: {slew_rate}\n")
            index += 1

    if specification == "Slew_rate":
        return {'Fluence (n/cm^2)': fluences, 'Slew_rate (V/µs)': Slew_rate}
    elif specification == "Supply_current":
        return {'Fluence (n/cm^2)': fluences, 'Supply_current (µA)': Supply_current}
    else:
        assert False

def generate_data_for_LM741_AC_GAIN(VCC, VEE, fluence_min, fluence_max, specification: str):
    subcircuit_pre_rad = LM741_SUBCKT_PRE_RAD_TEMPLATE
    subcircuit = LM741_SUBCKT_POST_RAD_TEMPLATE
    testbench = process_string_with_replacements(LM741_AC_GAIN_TESTBENCH, {"Vcc": VCC, "Vee": VEE})
    pre_rad_full_netlist = testbench + "\n" + subcircuit_pre_rad
    full_netlist = testbench + "\n" + subcircuit
    
    # Get Vos values for ac gain calculation
    Vos_data = generate_data_for_LM741(VCC=VCC, VEE=VEE, fluence_min=fluence_min, fluence_max=fluence_max, specification="V_os")
    Vos_values = Vos_data["V_os (mV)"]
    xyce_output_pre_rad = get_pre_rad_xyce_output_txt(pre_rad_full_netlist, round(Vos_values[0],3))
    # print(f"xyce_output_pre_rad: {xyce_output_pre_rad}")

    # passing vos_values as tuple as lists are not hashable and it need to be used as keys 
    all_xyce_output = get_all_xyce_output_txt(full_netlist, tuple(Vos_values[1:]))
    xyce_output = [(fluence, out_txt) for (fluence, out_txt) in all_xyce_output if fluence_min <= fluence <= fluence_max]
    fluences, Ac_gain = [], []

    # process for pre_rad
    pre_rad_parsed_output = parse_output_data_dynamic(xyce_output_pre_rad)
    set_fluence = 1e11
    # we just need the fisrt row from Xyce output to calculate the Ac gain
    fluences.append(set_fluence)
    _, freq, re_v3, im_v3, re_v2, im_v2 = pre_rad_parsed_output[0]
    # print(re_v3, im_v3, re_v2, im_v2)
    Ac_gain.append((np.sqrt((re_v3**2 + im_v3**2) / (re_v2**2 + im_v2**2)))/1000)

    # process for post_rad
    for fluence, out_text in xyce_output:
        assert fluence_min <= fluence <= fluence_max
        parsed_output = parse_output_data_dynamic(out_text)
        _,freq, re_v3, im_v3, re_v2, im_v2 = parsed_output[0]
        fluences.append(fluence)
        Ac_gain.append((np.sqrt((re_v3**2 + im_v3**2) / (re_v2**2 + im_v2**2)))/1000)
    
    if specification == "Ac_gain":
        return {'Fluence (n/cm^2)': fluences, 'Ac_gain (mV)': Ac_gain}
    else:
        assert False

def generate_data_for_LM741_CMRR(VCC, VEE, fluence_min, fluence_max, specification: str):
    subcircuit_pre_rad = LM741_SUBCKT_PRE_RAD_TEMPLATE
    subcircuit = LM741_SUBCKT_POST_RAD_TEMPLATE
    testbench = process_string_with_replacements(LM741_CMRR_TESTBENCH, {"Vcc": VCC, "Vee": VEE})
    pre_rad_full_netlist = testbench + "\n" + subcircuit_pre_rad
    full_netlist = testbench + "\n" + subcircuit

    xyce_output_pre_rad = get_pre_rad_xyce_output_txt(pre_rad_full_netlist)
    all_xyce_output = get_all_xyce_output_txt(full_netlist)
    xyce_output = [(fluence, out_txt) for (fluence, out_txt) in all_xyce_output if fluence_min <= fluence <= fluence_max]
    fluences, cmrr = [], []

    # process for pre_rad
    pre_rad_parsed_output = parse_output_data_dynamic(xyce_output_pre_rad)
    set_fluence = 1e11
    # we just need the fisrt row from Xyce output to calculate the CMRR
    fluences.append(set_fluence)
    _, freq, re_v3, im_v3, re_v4, im_v4 = pre_rad_parsed_output[0]
    print(re_v3, im_v3, re_v4, im_v4)
    const_val = 6.02059
    cmrr.append(const_val - 20 * (np.log10(abs(np.sqrt(re_v3**2 + im_v3**2)))))

    # process for post_rad
    for fluence, out_text in xyce_output:
        assert fluence_min <= fluence <= fluence_max
        parsed_output = parse_output_data_dynamic(out_text)
        _,freq, re_v3, im_v3, re_v4, im_v4 = parsed_output[0]
        fluences.append(fluence)
        cmrr.append(const_val - 20 * (np.log10(abs(np.sqrt(re_v3**2 + im_v3**2)))))
    
    if specification == "CMRR":
        return {'Fluence (n/cm^2)': fluences, 'CMRR_db': cmrr}
    else:
        assert False

def generate_data_for_LM111_OUTPUT_CURRENT(VCC, VEE, fluence_min, fluence_max, specification: str):
    subcircuit_pre_rad = LM111_SUBCKT_PRE_RAD_TEMPLATE
    subcircuit_post_rad = LM111_SUBCKT_POST_RAD_TEMPLATE

    testbench = process_string_with_replacements(LM111_OUTPUT_CURRENT_TESTBENCH_TEMPLATE, {"Vcc": VCC, "Vee": VEE})
    pre_rad_full_netlist = testbench + "\n" + subcircuit_pre_rad
    post_rad_full_netlist = testbench + "\n" + subcircuit_post_rad

    xyce_output_pre_rad = get_pre_rad_xyce_output_txt(pre_rad_full_netlist)
    all_xyce_output = get_all_xyce_output_txt(post_rad_full_netlist)

    xyce_output = [(fluence, out_txt) for (fluence, out_txt) in all_xyce_output if fluence_min <= fluence <= fluence_max]
    fluences, I_ol ,I_oh  = [], [], []

    # process for pre_rad
    pre_rad_parsed_output = parse_output_data_dynamic(xyce_output_pre_rad)
    set_fluence = 1e11
    for index, row in enumerate(pre_rad_parsed_output):
        _, v_2, i_vout = row
        if index == 0:
            fluences.append(set_fluence)
            I_ol.append(-i_vout * 10 ** 3) # amps to mA
        if index == 1:
            I_oh.append(-i_vout * 10 ** 9) # volts to nA

    # process for post_rad
    store = False
    for fluence, out_text in xyce_output:
        assert fluence_min <= fluence <= fluence_max
        # if store == False:
        #     with open("output/post_rad_LM193.txt", 'w') as file:
        #         file.write(out_text)
        #     store = True
        parsed_output = parse_output_data_dynamic(out_text)
        for index, row in enumerate(parsed_output[:2]):
            _, v_2, i_vout = row
            if index == 0:
                fluences.append(fluence)
                I_ol.append(-i_vout * 10 ** 3) # amps to mA
            if index == 1:
                I_oh.append(-i_vout * 10 ** 9) # volts to nA
    if specification == "I_ol":
        return {'Fluence (n/cm^2)': fluences, 'I_ol (mA)': I_ol}
    elif specification == "I_oh":
        return {'Fluence (n/cm^2)': fluences, 'I_oh (nA)': I_oh}
    else:
        assert False 

def generate_data_for_LM111_VOS(VCC, VEE, fluence_min, fluence_max, specification: str):
    subcircuit_pre_rad = LM111_SUBCKT_PRE_RAD_TEMPLATE
    subcircuit_post_rad = LM111_SUBCKT_POST_RAD_TEMPLATE

    testbench = process_string_with_replacements(LM111_VOS_TESTBENCH_TEMPLATE, {"Vcc": VCC, "Vee": VEE})
    pre_rad_full_netlist = testbench + "\n" + subcircuit_pre_rad
    post_rad_full_netlist = testbench + "\n" + subcircuit_post_rad
    xyce_output_pre_rad = get_pre_rad_xyce_output_txt(pre_rad_full_netlist)
    all_xyce_output = get_all_xyce_output_txt(post_rad_full_netlist)
    xyce_output = [(fluence, out_txt) for (fluence, out_txt) in all_xyce_output if fluence_min <= fluence <= fluence_max]
    fluences, v_os, i_ib, i_os = [], [], [], []
    
    # process for pre_rad
    pre_rad_parsed_output = parse_output_data_dynamic(xyce_output_pre_rad)
    set_fluence = 1e11
    for row in pre_rad_parsed_output:
        _, V_os, V_out, I_ib, I_os = row
        if V_os == 0:
            fluences.append(set_fluence)
            i_ib.append(I_ib * 10 ** 9) # amps to nA
            i_os.append(I_os * 10 ** 9) # amps to nA
        if V_out > 4.89:
            v_os.append(V_os * 10 ** 3) # volts to mV
            break
    
    # process for post_rad
    store = False
    for fluence, out_text in xyce_output:
        assert fluence_min <= fluence <= fluence_max
        # if store == False:
        #     with open("output/post_rad_LM111.txt", 'w') as file:
        #         file.write(out_text)
        #     store = True
        parsed_output = parse_output_data_dynamic(out_text)
        for row in parsed_output:
            _, V_os, V_out, I_ib, I_os = row
            if V_os ==  0:
                fluences.append(fluence)
                i_ib.append(I_ib * 10 ** 9) # amps to nA
                i_os.append(I_os * 10 ** 9) # amps to nA
            if V_out > 4.89:
                v_os.append(V_os * 10 ** 3) # volts to mV
                break
        else:
            assert False
    
    if specification == "V_os":
        return {'Fluence (n/cm^2)': fluences, 'V_os (mV)': v_os}
    elif specification == "I_ib":
        return {'Fluence (n/cm^2)': fluences, 'I_ib (nA)': i_ib}
    elif specification == "I_os":
        return {'Fluence (n/cm^2)': fluences, 'I_os (nA)': i_os}
    else:
        assert False 

def generate_data_for_LM193_OUTPUT_CURRENT(VCC, VEE, fluence_min, fluence_max, specification: str):
    subcircuit_pre_rad = LM193_SUBCKT_PRE_RAD_TEMPLATE
    subcircuit_post_rad = LM193_SUBCKT_POST_RAD_TEMPLATE

    testbench = process_string_with_replacements(LM193_OUTPUT_CURRENT_TESTBENCH_TEMPLATE, {"Vcc": VCC})
    pre_rad_full_netlist = testbench + "\n" + subcircuit_pre_rad
    post_rad_full_netlist = testbench + "\n" + subcircuit_post_rad

    xyce_output_pre_rad = get_pre_rad_xyce_output_txt(pre_rad_full_netlist)
    all_xyce_output = get_all_xyce_output_txt(post_rad_full_netlist)

    xyce_output = [(fluence, out_txt) for (fluence, out_txt) in all_xyce_output if fluence_min <= fluence <= fluence_max]
    fluences, I_ol ,I_oh  = [], [], []

    # process for pre_rad
    pre_rad_parsed_output = parse_output_data_dynamic(xyce_output_pre_rad)
    set_fluence = 1e11
    for index, row in enumerate(pre_rad_parsed_output):
        _, v_2, i_vout = row
        if index == 0:
            fluences.append(set_fluence)
            I_ol.append(-i_vout * 10 ** 3) # amps to mA
        if index == 1:
            I_oh.append(-i_vout * 10 ** 9) # volts to nA

    # process for post_rad
    store = False
    for fluence, out_text in xyce_output:
        assert fluence_min <= fluence <= fluence_max
        # if store == False:
        #     with open("output/post_rad_LM193.txt", 'w') as file:
        #         file.write(out_text)
        #     store = True
        parsed_output = parse_output_data_dynamic(out_text)
        for index, row in enumerate(parsed_output[:2]):
            _, v_2, i_vout = row
            if index == 0:
                fluences.append(fluence)
                I_ol.append(-i_vout * 10 ** 3) # amps to mA
            if index == 1:
                I_oh.append(-i_vout * 10 ** 9) # volts to nA
    if specification == "I_ol":
        return {'Fluence (n/cm^2)': fluences, 'I_ol (mA)': I_ol}
    elif specification == "I_oh":
        return {'Fluence (n/cm^2)': fluences, 'I_oh (nA)': I_oh}
    else:
        assert False 

def generate_data_for_LM193_VOS(VCC, VEE, fluence_min, fluence_max, specification: str):
    subcircuit_pre_rad = LM193_SUBCKT_PRE_RAD_TEMPLATE
    subcircuit_post_rad = LM193_SUBCKT_POST_RAD_TEMPLATE

    testbench = process_string_with_replacements(LM193_VOS_TESTBENCH_TEMPLATE, {"Vcc": VCC})
    pre_rad_full_netlist = testbench + "\n" + subcircuit_pre_rad
    post_rad_full_netlist = testbench + "\n" + subcircuit_post_rad

    xyce_output_pre_rad = get_pre_rad_xyce_output_txt(pre_rad_full_netlist)
    all_xyce_output = get_all_xyce_output_txt(post_rad_full_netlist)

    xyce_output = [(fluence, out_txt) for (fluence, out_txt) in all_xyce_output if fluence_min <= fluence <= fluence_max]
    fluences, v_os, i_ib, i_os = [], [], [], []
    
    # process for pre_rad
    pre_rad_parsed_output = parse_output_data_dynamic(xyce_output_pre_rad)
    set_fluence = 1e11
    for row in pre_rad_parsed_output:
        _, V2, V4, IVIN1, IVIN2 = row
        if V4 >= 1.4:
            fluences.append(set_fluence)
            v_os.append((V2 - 2.5) * 10 ** 3) # amps to mV
            i_os.append((IVIN2-IVIN1) * 10 ** 9) # amps to nA
            i_ib.append(-((IVIN1 + IVIN2)/2) * 10 ** 9) # volts to nA
            break

    # process for post_rad
    store = False
    for fluence, out_text in xyce_output:
        assert fluence_min <= fluence <= fluence_max
        # if store == False:
        #     with open("output/post_rad_LM193.txt", 'w') as file:
        #         file.write(out_text)
        #     store = True
        parsed_output = parse_output_data_dynamic(out_text)
        for row in parsed_output:
            _, V2, V4, IVIN1, IVIN2 = row
            if V4 >= 1.4:
                fluences.append(fluence)
                v_os.append((V2 - 2.5) * 10 ** 3) # amps to mV
                i_os.append((IVIN2-IVIN1) * 10 ** 9) # amps to nA
                i_ib.append(-((IVIN1 + IVIN2)/2) * 10 ** 9) # volts to nA
                break
        else:
            assert False

    if specification == "V_os":
        return {'Fluence (n/cm^2)': fluences, 'V_os (mV)': v_os}
    elif specification == "I_os":
        return {'Fluence (n/cm^2)': fluences, 'I_os (nA)': i_os}
    elif specification == "I_ib":
        return {'Fluence (n/cm^2)': fluences, 'I_ib (nA)': i_ib}
    else:
        assert False 

def generate_data_for_LM193_VOS_Old_calculation(VCC, VEE, fluence_min, fluence_max, specification: str):
    subcircuit_pre_rad = LM193_SUBCKT_PRE_RAD_TEMPLATE
    subcircuit_post_rad = LM193_SUBCKT_POST_RAD_TEMPLATE

    testbench = process_string_with_replacements(LM193_VOS_TESTBENCH_TEMPLATE, {"Vcc": VCC})
    pre_rad_full_netlist = testbench + "\n" + subcircuit_pre_rad
    post_rad_full_netlist = testbench + "\n" + subcircuit_post_rad

    xyce_output_pre_rad = get_pre_rad_xyce_output_txt(pre_rad_full_netlist)
    all_xyce_output = get_all_xyce_output_txt(post_rad_full_netlist)

    xyce_output = [(fluence, out_txt) for (fluence, out_txt) in all_xyce_output if fluence_min <= fluence <= fluence_max]
    fluences, v_os, i_ib, i_os = [], [], [], []
    
    # process for pre_rad
    pre_rad_parsed_output = parse_output_data_dynamic(xyce_output_pre_rad)
    set_fluence = 1e11
    for row in pre_rad_parsed_output:
        _, V_os, V_out, I_ib, I_os = row
        if V_os == 0:
            fluences.append(set_fluence)
            i_ib.append(I_ib * 10 ** 9) # amps to nA
            i_os.append(I_os * 10 ** 9) # amps to nA
        if V_out >  4.89 :
            v_os.append(V_os * 10 ** 3) # volts to mV
            break
    
    # process for post_rad
    store = False
    for fluence, out_text in xyce_output:
        assert fluence_min <= fluence <= fluence_max
        # if store == False:
        #     with open("output/post_rad_LM111.txt", 'w') as file:
        #         file.write(out_text)
        #     store = True
        parsed_output = parse_output_data_dynamic(out_text)
        vos_flag = False
        for row in parsed_output:
            _, V_os, V_out, I_ib, I_os = row
            if V_os ==  0:
                fluences.append(fluence)
                i_ib.append(I_ib * 10 ** 9) # amps to nA
                i_os.append(I_os * 10 ** 9) # amps to nA
                vos_flag = True
            if V_out > 4.89 and vos_flag:
                v_os.append(V_os * 10 ** 3) # volts to mV
                break
        else:
            assert False

    if specification == "V_os":
        return {'Fluence (n/cm^2)': fluences, 'V_os (mV)': v_os}
    elif specification == "I_os":
        return {'Fluence (n/cm^2)': fluences, 'I_os (nA)': i_os}
    elif specification == "I_ib":
        return {'Fluence (n/cm^2)': fluences, 'I_ib (nA)': i_ib}
    else:
        assert False 

def generate_data_for_LM139_OUTPUT_CURRENT(VCC, VEE, fluence_min, fluence_max, specification: str):
    subcircuit_pre_rad = LM139_SUBCKT_PRE_RAD_TEMPLATE
    subcircuit_post_rad = LM139_SUBCKT_POST_RAD_TEMPLATE

    testbench = process_string_with_replacements(LM139_OUTPUT_CURRENT_TESTBENCH_TEMPLATE, {"Vcc": VCC})
    pre_rad_full_netlist = testbench + "\n" + subcircuit_pre_rad
    post_rad_full_netlist = testbench + "\n" + subcircuit_post_rad

    xyce_output_pre_rad = get_pre_rad_xyce_output_txt(pre_rad_full_netlist)
    all_xyce_output = get_all_xyce_output_txt(post_rad_full_netlist)

    xyce_output = [(fluence, out_txt) for (fluence, out_txt) in all_xyce_output if fluence_min <= fluence <= fluence_max]
    fluences, I_ol ,I_oh  = [], [], []

    # process for pre_rad
    pre_rad_parsed_output = parse_output_data_dynamic(xyce_output_pre_rad)
    set_fluence = 1e11
    for index, row in enumerate(pre_rad_parsed_output):
        _, v_2, i_vout = row
        if index == 0:
            fluences.append(set_fluence)
            I_ol.append(-i_vout * 10 ** 3) # amps to mA
        if index == 1:
            I_oh.append(-i_vout * 10 ** 9) # volts to nA
    # process for post_rad
    store = False
    for fluence, out_text in xyce_output:
        assert fluence_min <= fluence <= fluence_max
        # if store == False:
        #     with open("output/post_rad_LM139.txt", 'w') as file:
        #         file.write(out_text)
        #     store = True
        parsed_output = parse_output_data_dynamic(out_text)
        for index, row in enumerate(parsed_output[:2]):
            _, v_2, i_vout = row
            if index == 0:
                fluences.append(fluence)
                I_ol.append(-i_vout * 10 ** 3) # amps to mA
            if index == 1:
                I_oh.append(-i_vout * 10 ** 9) # volts to nA
    if specification == "I_ol":
        return {'Fluence (n/cm^2)': fluences, 'I_ol (mA)': I_ol}
    elif specification == "I_oh":
        return {'Fluence (n/cm^2)': fluences, 'I_oh (nA)': I_oh}
    else:
        assert False 

def generate_data_for_LM139_VOS(VCC, VEE, fluence_min, fluence_max, specification: str):
    subcircuit_pre_rad = LM139_SUBCKT_PRE_RAD_TEMPLATE
    subcircuit_post_rad = LM139_SUBCKT_POST_RAD_TEMPLATE

    testbench = process_string_with_replacements(LM139_VOS_TESTBENCH_TEMPLATE, {"Vcc": VCC})
    pre_rad_full_netlist = testbench + "\n" + subcircuit_pre_rad
    post_rad_full_netlist = testbench + "\n" + subcircuit_post_rad

    xyce_output_pre_rad = get_pre_rad_xyce_output_txt(pre_rad_full_netlist)
    all_xyce_output = get_all_xyce_output_txt(post_rad_full_netlist)

    xyce_output = [(fluence, out_txt) for (fluence, out_txt) in all_xyce_output if fluence_min <= fluence <= fluence_max]
    fluences, v_os, i_ib, i_os = [], [], [], []
    
    # process for pre_rad
    pre_rad_parsed_output = parse_output_data_dynamic(xyce_output_pre_rad)
    set_fluence = 1e11
    for row in pre_rad_parsed_output:
        _, V_os, V_out, I_ib, I_os = row
        if V_os == 0:
            fluences.append(set_fluence)
            i_ib.append(I_ib * 10 ** 9) # amps to nA
            i_os.append(I_os * 10 ** 9) # amps to nA
        if V_out > 4.89 :
            v_os.append(V_os * 10 ** 3) # volts to mV
            break

    # process for post_rad
    store = False
    for fluence, out_text in xyce_output:
        assert fluence_min <= fluence <= fluence_max
        # if store == False:
        #     with open("output/post_rad_LM139.txt", 'w') as file:
        #         file.write(out_text)
        #     store = True
        # print(out_text)
        parsed_output = parse_output_data_dynamic(out_text)
        for row in parsed_output:
            _, V_os, V_out, I_ib, I_os = row
            if V_os == 0:
                temp_ib = I_ib * 10 ** 9
                temp_os = I_os * 10 ** 9
            if V_out >  4.89:
                v_os.append(V_os * 10 ** 3) # volts to mV
                fluences.append(fluence)
                i_ib.append(temp_ib) # amps to nA
                i_os.append(temp_os) # amps to nA
                break
        else:
            continue
            assert False

    if specification == "V_os":
        return {'Fluence (n/cm^2)': fluences, 'V_os (mV)': v_os}
    elif specification == "I_os":
        return {'Fluence (n/cm^2)': fluences, 'I_os (nA)': i_os}
    elif specification == "I_ib":
        return {'Fluence (n/cm^2)': fluences, 'I_ib (nA)': i_ib}
    else:
        assert False 


# Function to return the data to GUI 
def generate_data(Selected_Part, Selected_Specification, VCC, VEE, Temperature, Fluence_Min, Fluence_Max):
    if Selected_Part == "AD590":
        return generate_data_for_AD590(voltage=VCC, fluences_min=Fluence_Min, fluences_max=Fluence_Max)
    elif Selected_Part == "LM741":
        if Selected_Specification in ["V_os", "I_ib", "I_os"]:
            return generate_data_for_LM741(VCC=VCC, VEE=VEE, fluence_min=Fluence_Min, fluence_max=Fluence_Max, specification=Selected_Specification)
        elif Selected_Specification in ["Slew_rate", "Supply_current"]:
            return generate_data_for_LM741_SLEW_RATE(VCC=VCC, fluence_min=Fluence_Min, fluence_max=Fluence_Max, specification=Selected_Specification)
        elif Selected_Specification == "Ac_gain":
            return generate_data_for_LM741_AC_GAIN(VCC=VCC, VEE=VEE, fluence_min=Fluence_Min, fluence_max=Fluence_Max, specification=Selected_Specification)
        elif Selected_Specification == "CMRR":
            return generate_data_for_LM741_CMRR(VCC=VCC, VEE=VEE, fluence_min=Fluence_Min, fluence_max=Fluence_Max, specification=Selected_Specification)
    elif Selected_Part == "LM111":
        if Selected_Specification in ["I_ol", "I_oh"]:
            return generate_data_for_LM111_OUTPUT_CURRENT(VCC=VCC, VEE=VEE, fluence_min=Fluence_Min, fluence_max=Fluence_Max, specification=Selected_Specification)
        elif Selected_Specification in ["V_os", "I_ib", "I_os"]:
            return generate_data_for_LM111_VOS(VCC=VCC, VEE=VEE, fluence_min=Fluence_Min, fluence_max=Fluence_Max, specification=Selected_Specification)
    elif Selected_Part == "LM193":
        if Selected_Specification in ["I_ol", "I_oh"]:
            return generate_data_for_LM193_OUTPUT_CURRENT(VCC=VCC, VEE=VEE, fluence_min=Fluence_Min, fluence_max=Fluence_Max, specification=Selected_Specification)
        elif Selected_Specification in ["V_os", "I_ib", "I_os"]:
            return generate_data_for_LM193_VOS_Old_calculation(VCC=VCC, VEE=VEE, fluence_min=Fluence_Min, fluence_max=Fluence_Max, specification=Selected_Specification)
    elif Selected_Part == "LM139":
        if Selected_Specification in ["I_ol", "I_oh"]:
            return generate_data_for_LM139_OUTPUT_CURRENT(VCC=VCC, VEE=VEE, fluence_min=Fluence_Min, fluence_max=Fluence_Max, specification=Selected_Specification)
        elif Selected_Specification in ["V_os", "I_ib", "I_os"]:
             return generate_data_for_LM139_VOS(VCC=VCC, VEE=VEE, fluence_min=Fluence_Min, fluence_max=Fluence_Max, specification=Selected_Specification)
    else:
        assert False
    pass

def main():
    pass

if __name__ == "__main__":
    main()


