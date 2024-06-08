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
LM111_TESTBENCH_TEMPLATE = exe_tools.read_txt_file("testbenches/LM111_Vos_Iib_Ios_testbench.cir")

# paths for LM193
LM193_SUBCKT_PRE_RAD_TEMPLATE = exe_tools.read_txt_file("netlists/LM193_subckt_Prerad.cir")
LM193_SUBCKT_POST_RAD_TEMPLATE = exe_tools.read_txt_file("netlists/LM193_subckt_Postrad.cir")
LM193_TESTBENCH_TEMPLATE = exe_tools.read_txt_file("testbenches/LM193_Vos_Iib_Ios_testbench.cir")

# NPN and PNP parameters as dataframes
NPN_DF = exe_tools.read_csv_to_df('csvs/NPN_diode_parameters_V0.csv')
PNP_DF = exe_tools.read_csv_to_df('csvs/PNP_diode_parameters_V1.csv')

# Object to Store the mapping of the Part and Specifications Dropdown
DROPDOWN_MAPPING = {
    "AD590": ["I_out"],
    "LM741": ["V_os", "I_ib", "I_os", "Slew_rate", "Supply_current", "Ac_gain", "CMRR"],
    "LM193" : ["V_os", "I_ib", "I_os"],
    "LM111" : ["V_os", "I_ib", "I_os"]
}

# List to store the types of Neutrons
NEUTRON_TYPE = ["1MeV"]


# object to store values of the specifications for dotter plot
DOTTER_SPECIFICATIONS = {
    "AD590": {
        "I_out": 0
    },
    "LM741": {
        "V_os": 6,
        "I_ib": 500,
        "I_os": 20,
        "Slew_rate": 0,
        "Supply_current": 0,
        "Ac_gain": 36,
        "CMRR": 0
    },
    "LM193": {
        "V_os": 4,
        "I_ib": 150,
        "I_os": 20
    },
    "LM111": {
        "V_os": 9,
        "I_ib": 300,
        "I_os": 100
    }
}
