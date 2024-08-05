import exe_tools

XYCE_EXE_PATH = exe_tools.adjust_path("xyce/Xyce.exe")
# paths for the AD590
AD590_NETLIST_TEMPLATE = exe_tools.read_txt_file("netlists/AD590_new_subckt_V0.cir")

#paths for the LM741
LM741_SUBCKT_POST_RAD_TEMPLATE = exe_tools.read_txt_file("netlists/LM741_new_subckt_Postrad_V0.cir")
LM741_SUBCKT_PRE_RAD_TEMPLATE = exe_tools.read_txt_file("netlists/LM741_new_subckt_Prerad_V0.cir")

#testbenches for the LM741
LM741_CLUDGE_TESTBENCH = exe_tools.read_txt_file("testbenches/LM741_cludge_testbench_v1.cir")
LM741_SLEW_RATE_TESTBENCH = exe_tools.read_txt_file("testbenches/LM741_slewrate_tb_v2.cir")
LM741_AC_GAIN_TESTBENCH = exe_tools.read_txt_file("testbenches/LM741_AC_Gain_testbench.cir")
LM741_CMRR_TESTBENCH = exe_tools.read_txt_file("testbenches/LM741_CMRR_testbench.cir")

# paths for LM111
LM111_SUBCKT_PRE_RAD_TEMPLATE = exe_tools.read_txt_file("netlists/LM111_new_subckt_Prerad.cir")
LM111_SUBCKT_POST_RAD_TEMPLATE = exe_tools.read_txt_file("netlists/LM111_new_subckt_Postrad.cir")
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
NPN_DF = exe_tools.read_csv_to_df('csvs/NPN_diode_parameters_V1.csv')
PNP_DF = exe_tools.read_csv_to_df('csvs/PNP_diode_parameters_V2.csv')


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
        "I_ib": {"min": 0, "typical": 0, "max": 500},
        "I_os": {"min": 0, "typical": 0, "max": 200},
        "Slew_rate": {"min": 0, "typical": 0, "max": 0},
        "Supply_current": {"min": 0, "typical": 0, "max": 2.8},
        "Ac_gain": {"min": 25, "typical": 0, "max": 0},
        "CMRR": {"min": 80, "typical": 0, "max": 0}
    },
    "LM193": {
        "I_ol": {"min": 6, "typical": 0, "max": 0},
        "I_oh": {"min": 0, "typical": 0, "max": 0},
        "V_os": {"min": 0, "typical": 0, "max": 5},
        "I_ib": {"min": 0, "typical": 0, "max": 300},
        "I_os": {"min": 0, "typical": 0, "max": 100}
    },
    "LM139": {
        "I_ol": {"min": 6, "typical": 0, "max": 0},
        "I_oh": {"min": 0, "typical": 0, "max": 0},
        "V_os": {"min": 0, "typical": 0, "max": 5},
        "I_ib": {"min": 0, "typical": 0, "max": 300},
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
