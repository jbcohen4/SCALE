import exe_tools

XYCE_EXE_PATH = exe_tools.adjust_path("xyce/Xyce.exe")
# paths for the AD590
AD590_NETLIST_TEMPLATE = exe_tools.read_txt_file("netlists/AD590_template.cir")

#paths for the LM741
LM741_SUBCKT_POST_RAD_TEMPLATE = exe_tools.read_txt_file("netlists/LM741_subckt_Postrad.cir")
LM741_SUBCKT_PRE_RAD_TEMPLATE = exe_tools.read_txt_file("netlists/LM741_subckt_Prerad.cir")

#testbenches for the LM741
LM741_CLUDGE_TESTBENCH = exe_tools.read_txt_file("testbenches/LM741_cludge_testbench_v1.cir")
LM741_SLEW_RATE_TESTBENCH = exe_tools.read_txt_file("testbenches/LM741_slewrate_tb_v2.cir")
LM741_AC_GAIN_TESTBENCH = exe_tools.read_txt_file("testbenches/LM741_AC_Gain_testbench.cir")
LM741_CMRR_TESTBENCH = exe_tools.read_txt_file("testbenches/LM741_CMRR_testbench.cir")

# paths for LM111
LM111_SUBCKT_PRE_RAD_TEMPLATE = exe_tools.read_txt_file("netlists/LM111_subckt_Prerad.cir")
LM111_SUBCKT_POST_RAD_TEMPLATE = exe_tools.read_txt_file("netlists/LM111_subckt_Postrad.cir")
LM111_OUTPUT_CURRENT_TESTBENCH_TEMPLATE = exe_tools.read_txt_file("testbenches/LM111_OutputCurrents_testbench.cir")
LM111_VOS_TESTBENCH_TEMPLATE = exe_tools.read_txt_file("testbenches/LM111_Vos_Iib_Ios_testbench.cir")

# paths for LM193
# V0 are the old subckts shared by Triet, V1 are given by Ethan 
LM193_SUBCKT_PRE_RAD_TEMPLATE = exe_tools.read_txt_file("netlists/LM193_subckt_Prerad_V0.cir")
LM193_SUBCKT_POST_RAD_TEMPLATE = exe_tools.read_txt_file("netlists/LM193_subckt_Postrad_V0.cir")
LM193_OUTPUT_CURRENT_TESTBENCH_TEMPLATE = exe_tools.read_txt_file("testbenches/LM193_OutputCurrents_testbench_V0.cir")
LM193_VOS_TESTBENCH_TEMPLATE = exe_tools.read_txt_file("testbenches/LM193_Vos_Iib_Ios_testbench_V0.cir")

# paths for LM139
# V0 is subckt shared by Ethan and V1 is the one shared by Triet - which is similar to 193
LM139_SUBCKT_PRE_RAD_TEMPLATE = exe_tools.read_txt_file("netlists/LM139_subckt_Prerad_V1.cir")
LM139_SUBCKT_POST_RAD_TEMPLATE = exe_tools.read_txt_file("netlists/LM139_subckt_Postrad_V1.cir")
LM139_OUTPUT_CURRENT_TESTBENCH_TEMPLATE = exe_tools.read_txt_file("testbenches/LM139_OutputCurrents_testbench_V0.cir")
LM139_VOS_TESTBENCH_TEMPLATE = exe_tools.read_txt_file("testbenches/LM139_Vos_Iib_Ios_testbench_V1.cir")

# NPN and PNP parameters as dataframes
NPN_DF = exe_tools.read_csv_to_df('csvs/NPN_diode_parameters_V0.csv')
PNP_DF = exe_tools.read_csv_to_df('csvs/PNP_diode_parameters_V1.csv')

# Object to Store the mapping of the Part and Specifications Dropdown
DROPDOWN_MAPPING = {
    "AD590": ["I_out"],
    # "LM741": ["V_os", "I_ib", "I_os", "Slew_rate", "Supply_current", "Ac_gain", "CMRR"],
    "LM741": ["V_os", "I_ib", "I_os", "Supply_current", "Ac_gain", "CMRR"],
    "LM193" : ["I_ol","I_oh","V_os", "I_ib", "I_os"],
    "LM139" : ["I_ol","I_oh","V_os", "I_ib", "I_os"],
    "LM111" : ["I_ol","I_oh","V_os", "I_ib", "I_os"]
}

# List to store the types of Neutrons
NEUTRON_TYPE = ["1MeV"]


# object to store values of the specifications for dotter plot
DOTTER_SPECIFICATIONS = {
    "AD590": {
        "I_out": {"min": 0, "typical": 0, "max": 0}
    },
    "LM741": {
        "V_os": {"min": 0, "typical": 0, "max": 6},
        "I_ib": {"min": 0, "typical": 80, "max": 500},
        "I_os": {"min": 0, "typical": 20, "max": 200},
        "Slew_rate": {"min": 0, "typical": 0.5, "max": 0},
        "Supply_current": {"min": 0, "typical": 1.7, "max": 2.8},
        "Ac_gain": {"min": 25, "typical": 0, "max": 0},
        "CMRR": {"min": 80, "typical": 95, "max": 0}
    },
    "LM193": {
        "I_ol": {"min": 6, "typical": 0, "max": 0},
        "I_oh": {"min": 0, "typical": 0, "max": 0},
        "V_os": {"min": 0, "typical": 2, "max": 5},
        "I_ib": {"min": 0, "typical": 25, "max": 300},
        "I_os": {"min": 0, "typical": 0, "max": 100}
    },
    "LM139": {
        "I_ol": {"min": 6, "typical": 0, "max": 0},
        "I_oh": {"min": 0, "typical": 0, "max": 0},
        "V_os": {"min": 0, "typical": 2, "max": 5},
        "I_ib": {"min": 0, "typical": 25, "max": 300},
        "I_os": {"min": 0, "typical": 0, "max": 100}
    },
    "LM111": {
        "I_ol": {"min": 0, "typical": 0, "max": 0},
        "I_oh": {"min": 0, "typical": 0, "max": 0},
        "V_os": {"min": 0, "typical": 0, "max": 4},
        "I_ib": {"min": 0, "typical": 0, "max": 150},
        "I_os": {"min": 0, "typical": 0, "max": 20}
    }
}

# fluence values 
FLUENCES = [
    4.04E+11, 4.33E+11, 4.64E+11, 4.98E+11, 5.34E+11, 5.72E+11, 6.14E+11,
    6.58E+11, 7.05E+11, 7.56E+11, 8.11E+11, 8.7E+11, 9.33E+11, 1E+12,
    1.07E+12, 1.15E+12, 1.23E+12, 1.32E+12, 1.42E+12, 1.52E+12, 1.63E+12,
    1.75E+12, 1.87E+12, 2.01E+12, 2.15E+12, 2.31E+12, 2.48E+12, 2.66E+12,
    2.85E+12, 3.05E+12, 3.27E+12, 3.51E+12, 3.76E+12, 4.04E+12, 4.33E+12,
    4.64E+12, 4.98E+12, 5.34E+12, 5.72E+12, 6.14E+12, 6.58E+12, 7.05E+12,
    7.56E+12, 8.11E+12, 8.7E+12, 9.33E+12, 1E+13, 1.07E+13, 1.15E+13,
    1.23E+13, 1.32E+13, 1.42E+13, 1.52E+13, 1.63E+13, 1.75E+13, 1.87E+13,
    2.01E+13, 2.15E+13, 2.31E+13, 2.48E+13, 2.66E+13, 2.85E+13, 3.05E+13,
    3.27E+13, 3.51E+13, 3.76E+13, 4.04E+13, 4.33E+13, 4.64E+13, 4.98E+13,
    5.34E+13, 5.72E+13, 6.14E+13, 6.58E+13, 7.05E+13, 7.56E+13, 8.11E+13,
    8.7E+13, 9.33E+13, 1E+14
]
