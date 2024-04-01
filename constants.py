import exe_tools
AD590_NETLIST_TEMPLATE_PATH = exe_tools.adjust_path("netlists/AD590_template.cir")

XYCE_EXE_PATH = exe_tools.adjust_path("xyce/Xyce.exe")

#paths for the LM741
LM741_NETLIST_PATH = exe_tools.adjust_path("netlists/LM741_subckt_post_rad.cir")
#testbenches for the LM741
IOS_VOS_IB_1_PATH = exe_tools.adjust_path("testbenches/Ios_Vos_Ib_1.cir")
IOS_VOS_IB_2_PATH = exe_tools.adjust_path("testbenches/Ios_Vos_Ib_2.cir")
IOS_VOS_IB_3_PATH = exe_tools.adjust_path("testbenches/Ios_Vos_Ib_3.cir")
LM471_ACGAIN_TESTBENCH = exe_tools.adjust_path("testbenches/LM741_ACgain_testbench.cir")


# NPN and PNP parameters as dataframes
NPN_DF = exe_tools.read_csv_to_df('csvs/NPN_diode_parameters_V0.csv')
PNP_DF = exe_tools.read_csv_to_df('csvs/PNP_diode_parameters_V1.csv')

# Object to Store the mapping of the Part and Specifications Dropdown
DROPDOWN_MAPPING = {
    "AD590": ["I_out"],
    "LM741": ["V_os", "I_ib", "I_os"]
}
