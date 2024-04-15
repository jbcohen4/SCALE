import exe_tools

XYCE_EXE_PATH = exe_tools.adjust_path("xyce/Xyce.exe")
# paths for the AD590
AD590_NETLIST_TEMPLATE = exe_tools.read_txt_file("netlists/AD590_template.cir")

#paths for the LM741
LM741_NETLIST = exe_tools.read_txt_file("netlists/LM741_template.cir") # I figured reading in the actual file would be better, since we'll have to do it later anyways

# I want to eventually stop putting paths here and just load the files. I think it would help us catch bugs faster when files get renamed. (--Joe)
LM741_NETLIST_PATH = exe_tools.adjust_path("netlists/LM471_template.cir")
#testbenches for the LM741
LM741_CLUDGE_TESTBENCH = exe_tools.read_txt_file("testbenches/LM741_cludge_testbench_v1.cir")

# paths for LM111
LM111_SUBCKT_PRE_RAD_TEMPLATE = exe_tools.read_txt_file("netlists/LM111_subckt_Prerad.cir")
LM111_SUBCKT_POST_RAD_TEMPLATE = exe_tools.read_txt_file("netlists/LM111_subckt_Postrad.cir")
LM111_TESTBENCH_TEMPLATE = exe_tools.read_txt_file("testbenches/LM111_Vos_Iib_Ios_testbench.cir")

# paths for LM193
LM193_SUBCKT_PRE_RAD_TEMPLATE = exe_tools.read_txt_file("netlists/LM193_subckt_Prerad.cir")
LM193_SUBCKT_POST_RAD_TEMPLATE = exe_tools.read_txt_file("netlists/LM193_subckt_Postrad.cir")
LM193_TESTBENCH_TEMPLATE = exe_tools.read_txt_file("testbenches/LM193_Vos_Iib_Ios_testbench.cir")

# below paths can be removed
IOS_VOS_IB_1_PATH = exe_tools.adjust_path("testbenches/Ios_Vos_Ib_1.cir")
IOS_VOS_IB_2_PATH = exe_tools.adjust_path("testbenches/Ios_Vos_Ib_2.cir")
IOS_VOS_IB_3_PATH = exe_tools.adjust_path("testbenches/Ios_Vos_Ib_3.cir")
LM471_ACGAIN_TESTBENCH_PATH = exe_tools.adjust_path("testbenches/LM741_ACgain_testbench.cir")
SLEW_RATE_AND_SUPP_CURRENT_PATH = exe_tools.adjust_path("testbenches/Slew_rate_Supp_curr.cir")


# NPN and PNP parameters as dataframes
NPN_DF = exe_tools.read_csv_to_df('csvs/NPN_diode_parameters_V0.csv')
PNP_DF = exe_tools.read_csv_to_df('csvs/PNP_diode_parameters_V1.csv')

# Object to Store the mapping of the Part and Specifications Dropdown
DROPDOWN_MAPPING = {
    "AD590": ["I_out"],
    "LM741": ["V_os", "I_ib", "I_os"],
    "LM193" : ["V_os", "I_ib", "I_os"],
    "LM111" : ["V_os", "I_ib", "I_os"]
}
