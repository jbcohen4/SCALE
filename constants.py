import exe_tools
import pandas as pd

XYCE_EXE_PATH = exe_tools.adjust_path("xyce/Xyce.exe")
# paths for the AD590
AD590_PRE_RAD_NETLIST_TEMPLATE = exe_tools.read_txt_file("netlists/AD590_template_Prerad.cir")
AD590_POST_RAD_NETLIST_TEMPLATE = exe_tools.read_txt_file("netlists/AD590_template_Postrad.cir")

#paths for the LM741
LM741_SUBCKT_POST_RAD_TEMPLATE = exe_tools.read_txt_file("netlists/LM741_subckt_Postrad.cir")
LM741_SUBCKT_PRE_RAD_TEMPLATE = exe_tools.read_txt_file("netlists/LM741_subckt_Prerad.cir")

#testbenches for the LM741
LM741_CLUDGE_TESTBENCH = exe_tools.read_txt_file("testbenches/LM741_cludge_testbench_v1.cir")
LM741_SLEW_RATE_TESTBENCH = exe_tools.read_txt_file("testbenches/LM741_slewrate_tb_v2.cir")
LM741_AC_GAIN_TESTBENCH = exe_tools.read_txt_file("testbenches/LM741_AC_Gain_testbench.cir")
LM741_CMRR_TESTBENCH = exe_tools.read_txt_file("testbenches/LM741_CMRR_testbench.cir")

# LM741 temp test bench
LM741_TEMP_VOS_TESTBENCH = exe_tools.read_txt_file("testbenches/LM741_temp_Vos_testbench.cir")
LM741_TEMP_IB_TESTBENCH = exe_tools.read_txt_file("testbenches/LM741_temp_Ib_testbench.cir")
LM741_TEMP_IOS_TESTBENCH = exe_tools.read_txt_file("testbenches/LM741_temp_Ios_testbench.cir")

#paths for the LM124
LM124_SUBCKT_PRE_RAD_TEMPLATE = exe_tools.read_txt_file("netlists/LM124_subckt_Prerad_test.cir")
LM124_SUBCKT_POST_RAD_TEMPLATE = exe_tools.read_txt_file("netlists/LM124_subckt_Postrad_test.cir")
LM124_VOS_TESTBENCH_TEMPLATE = exe_tools.read_txt_file("testbenches/LM124_Vos_Iib_Ios_testbench.cir")

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
LM139_SUBCKT_PRE_RAD_TEMPLATE = exe_tools.read_txt_file("netlists/LM139_subckt_Prerad_V2.cir")
LM139_SUBCKT_POST_RAD_TEMPLATE = exe_tools.read_txt_file("netlists/LM139_subckt_Postrad_V2.cir")
LM139_OUTPUT_CURRENT_TESTBENCH_TEMPLATE = exe_tools.read_txt_file("testbenches/LM139_OutputCurrents_testbench_V0.cir")
LM139_VOS_TESTBENCH_TEMPLATE = exe_tools.read_txt_file("testbenches/LM139_Vos_Iib_Ios_testbench_V1.cir")

# paths for LM117
LM117_SUBCKT_PRE_RAD_TEMPLATE = exe_tools.read_txt_file("netlists/LM117_subckt_Prerad.cir")
LM117_SUBCKT_POST_RAD_TEMPLATE = exe_tools.read_txt_file("netlists/LM117_subckt_Postrad.cir")
LM117_VREF_TESTBENCH_TEMPLATE = exe_tools.read_txt_file("testbenches/LM117_Vref_Iadj_testbench.cir")

# Paths for OP27
OP27_SUBCKT_PRE_RAD_TEMPLATE = exe_tools.read_txt_file("netlists/OP27_subckt_Prerad_V1.cir")
OP27_SUBCKT_POST_RAD_TEMPLATE = exe_tools.read_txt_file("netlists/OP27_subckt_Postrad_V1.cir")
OP27_VOS_TESTBENCH_TEMPLATE = exe_tools.read_txt_file("testbenches/OP27_Vos_Iib_Ios_testbench.cir")
OP27_POSITIVE_IB_TEMPLATE = exe_tools.read_txt_file("testbenches/OP27_PositiveIb_testbench_V1.cir")

# NPN and PNP parameters as dataframes
NPN_DF = exe_tools.read_csv_to_df('csvs/NPN_diode_parameters_V0.csv')
PNP_DF = exe_tools.read_csv_to_df('csvs/PNP_diode_parameters_V1.csv')

# Object to Store the mapping of the Part and Specifications Dropdown
DROPDOWN_MAPPING = {
    "AD590": ["I_out"],
    # "LM741": ["V_os", "I_ib", "I_os", "Slew_rate", "Supply_current", "Ac_gain", "CMRR"],
    "LM741": ["V_os", "I_ib", "I_os", "Supply_current", "Ac_gain", "CMRR"],
    "LM124" : ["V_os", "I_ib", "I_os"],
    "LM193" : ["I_ol","I_oh","V_os", "I_ib", "I_os"],
    "LM139" : ["I_ol","I_oh","V_os", "I_ib", "I_os"],
    # "LM111" : ["I_ol","I_oh","V_os", "I_ib", "I_os"]
    "LM111" : ["V_os", "I_ib", "I_os"],
    "LM117" : ["V_ref", "I_adj", "V_out"],
    "LM741_Test": ["V_os", "I_ib", "I_os"],
    "OP27" : ["V_os", "I_ib", "I_os"]
}

# object to store values of the specifications for dotter plot
DOTTER_SPECIFICATIONS = {
    "AD590": {
        "I_out": {"min": 0, "typical": 'NA', "max": 0}
    },
    "LM741": {
        "V_os": {"min": 0, "typical": 'NA', "max": 6},
        "I_ib": {"min": 0, "typical": 80, "max": 500},
        "I_os": {"min": 0, "typical": 20, "max": 200},
        "Slew_rate": {"min": 0, "typical": 0.5, "max": 0},
        "Supply_current": {"min": 0, "typical": 1.7, "max": 2.8},
        "Ac_gain": {"min": 25, "typical": 'NA', "max": 0},
        "CMRR": {"min": 80, "typical": 95, "max": 0}
    },
     "LM124": {
        "V_os": {"min": 0, "typical": 'NA', "max": 7},
        "I_ib": {"min": 0, "typical": 20, "max": 150}, #Negative in datasheet
        "I_os": {"min": 0, "typical": 2, "max": 30},
    },
    "LM193": {
        "I_ol": {"min": 6, "typical": 'NA', "max": 0},
        "I_oh": {"min": 0, "typical": 0.1, "max": 1000},
        "V_os": {"min": 0, "typical": 2, "max": 5},
        "I_ib": {"min": 0, "typical": 25, "max": 300},
        "I_os": {"min": 0, "typical": 'NA', "max": 100}
    },
    "LM139": {
        "I_ol": {"min": 6, "typical": 16, "max": 0},
        "I_oh": {"min": 0, "typical": 0.1, "max": 1000},
        "V_os": {"min": 0, "typical": 2, "max": 5},
        "I_ib": {"min": 0, "typical": 25, "max": 300},
        "I_os": {"min": 0, "typical": 'NA', "max": 100}
    },
    "LM111": {
        "I_ol": {"min": 0, "typical": 'NA', "max": 0},
        "I_oh": {"min": 0, "typical": 'NA', "max": 0},
        "V_os": {"min": 0, "typical": 0.7, "max": 4},
        "I_ib": {"min": 0, "typical": 60, "max": 150},
        "I_os": {"min": 0, "typical": 4.0, "max": 20}
    },
    "LM117": {
        "V_ref": {"min": 0, "typical": 0, "max": 1.3},
        "I_adj": {"min": 0, "typical": 0, "max": 100},
        "V_out": {"min": 0, "typical": 0, "max": 0}
    },
    "LM741_Test": {
        "V_os": {"min": 0, "typical": 'NA', "max": 6},
        "I_ib": {"min": 0, "typical": 80, "max": 500},
        "I_os": {"min": 0, "typical": 20, "max": 200},
    },
    "OP27": {
        "V_os": {"min": 0, "typical": 0, "max": 0},
        "I_ib": {"min": 0, "typical": 0, "max": 0},
        "I_os": {"min": 0, "typical": 0, "max": 0}
    }
}

# List to store the types of Neutrons
NEUTRON_TYPE = ["1MeV"]

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
    3.27E+13, 3.51E+13, 3.76E+13, 4.04E+13, 4.33E+13, 4.64E+13
]

# Backend fluences with more precision
BACKEND_FLUENCES = [
    4.038510e+11, 4.329380e+11, 4.640795e+11, 4.978510e+11, 5.338350e+11, 5.721185e+11, 
    6.137955e+11, 6.579665e+11, 7.052400e+11, 7.562315e+11, 8.110655e+11, 8.698745e+11,
    9.328015e+11, 1.000000e+12, 1.071135e+12, 1.149880e+12, 1.231425e+12, 1.320970e+12,
    1.418735e+12, 1.519955e+12, 1.629875e+12, 1.748765e+12, 1.871910e+12, 2.009615e+12,
    2.152215e+12, 2.310065e+12, 2.478540e+12, 2.658045e+12, 2.849020e+12, 3.051930e+12,
    3.272275e+12, 3.510595e+12, 3.762470e+12, 4.038510e+12, 4.329380e+12, 4.640795e+12,
    4.978510e+12, 5.338350e+12, 5.721185e+12, 6.137955e+12, 6.579665e+12, 7.052400e+12,
    7.562315e+12, 8.110655e+12, 8.698745e+12, 9.328015e+12, 1.000000e+13, 1.071135e+13,
    1.149880e+13, 1.231425e+13, 1.320970e+13, 1.418735e+13, 1.519955e+13, 1.629875e+13,
    1.748765e+13, 1.871910e+13, 2.009615e+13, 2.152215e+13, 2.310065e+13, 2.478540e+13,
    2.658045e+13, 2.849020e+13, 3.051930e+13, 3.272275e+13, 3.510595e+13, 3.762470e+13,
    4.038510e+13, 4.329380e+13, 4.640795e+13
]

# Values for TID parameters
DOSE_RATE = [0.01,0.1,100]
HYDROGEN = [0,0.1,100]
BIAS = [0]

# valid combination between the TID parameters
VALID_TID_COMBINATIONS = {
    0.01: [0.1],
    0.1: [100],
    100: [0,100]
}
# List to store the radtion doses for TID
TID_DOSES = ["DR=0.01_H2=0.1_B=0", "DR=0.1_H2=100_B=0", "DR=100_H2=100_B=0", "DR=100_H2=0_B=0"]

# TID MAPPING 
TID_MAPPING = {
    "DR=0.01_H2=0.1_B=0": ["csvs/TID_NPN_SHEET1_V0.csv","csvs/TID_PNP_SHEET1_V0.csv","csvs/TID_SPNP_SHEET1_V0.csv"], # Temporary
    "DR=0.1_H2=100_B=0": ["csvs/TID_NPN_SHEET2_V0.csv","csvs/TID_PNP_SHEET2_V0.csv", "csvs/TID_SPNP_SHEET1_V0.csv"],
    "DR=100_H2=100_B=0": ["csvs/TID_NPN_SHEET3_V0.csv","csvs/TID_PNP_SHEET3_V0.csv","csvs/TID_SPNP_SHEET2_V0.csv"],
    "DR=100_H2=0_B=0": ["csvs/TID_NPN_SHEET4_V0.csv","csvs/TID_PNP_SHEET4_V0.csv","csvs/TID_SPNP_SHEET2_V0.csv"] # Temporary
}

# NPN & PNP selection based on TID input
NPN_DF_TID = None
PNP_DF_TID = None
SPNP_DF_TID = None # Temporary

TID_DOSE_MIN = None
TID_DOSE_MAX = None

def update_tid_dataframes(selection_key):
    global NPN_DF_TID, PNP_DF_TID, SPNP_DF_TID # Temporary
    if selection_key in TID_MAPPING:
        npn_file_path = TID_MAPPING[selection_key][0]
        pnp_file_path = TID_MAPPING[selection_key][1]
        spnp_file_path = TID_MAPPING[selection_key][2] # Temporary

        NPN_DF_TID = exe_tools.read_csv_to_df(npn_file_path)
        PNP_DF_TID = exe_tools.read_csv_to_df(pnp_file_path)
        SPNP_DF_TID = exe_tools.read_csv_to_df(spnp_file_path)  # Temporary
        
        # function to calculate the min and max dose
        calculate_min_max_dose(NPN_DF_TID, PNP_DF_TID)
    else:
        print(f"Invalid selection key:{ selection_key }")

def calculate_min_max_dose(npn_df, pnp_df):
    global TID_DOSE_MIN, TID_DOSE_MAX
    # Convert 'Is' column to numeric and remove rows where 'Is' is NaN
    npn_df["Is"] = pd.to_numeric(npn_df["Is"], errors='coerce')
    npn_df = npn_df.dropna(subset=["Is"])

    pnp_df["Is"] = pd.to_numeric(pnp_df["Is"], errors='coerce')
    pnp_df = pnp_df.dropna(subset=["Is"])

    # Select rows where 'Is' is greater than 0 directly on the DataFrame to avoid misalignment issues
    npn_first_non_zero_row = npn_df.loc[npn_df["Is"] > 0].iloc[0]
    npn_max_row = npn_df.loc[npn_df["Is"] > 0].iloc[-1]

    pnp_first_non_zero_row = pnp_df.loc[pnp_df["Is"] > 0].iloc[0]
    pnp_max_row = pnp_df.loc[pnp_df["Is"] > 0].iloc[-1]

    # Get the dose values from the 'delta_Ib_column'
    npn_min_dose = npn_first_non_zero_row["Dose(krad)"]
    npn_max_dose = npn_max_row["Dose(krad)"]

    pnp_min_dose = pnp_first_non_zero_row["Dose(krad)"]
    pnp_max_dose = pnp_max_row["Dose(krad)"]

    # Calculate global minimum and maximum dose
    TID_DOSE_MIN = min(npn_min_dose, pnp_min_dose)
    TID_DOSE_MAX = max(npn_max_dose, pnp_max_dose)
    # print(f"Min dose: {TID_DOSE_MIN}, Max dose: {TID_DOSE_MAX}")

def get_tid_dataframes():
    return NPN_DF_TID, PNP_DF_TID, SPNP_DF_TID

def get_tid_dose_limits():
    return (TID_DOSE_MIN, TID_DOSE_MAX)

# Values for TID Fluence Didiode Calculation 
# NPN and PNP parameters as dataframes for TID & Fluence
NPN_DF_TF = exe_tools.read_csv_to_df('csvs/TID_FLUENCE_NPN_Didiode.csv')
PNP_DF_TF = exe_tools.read_csv_to_df('csvs/TID_FLUENCE_PNP_Didiode.csv')

# Postrad Netlist paths for all the parts
AD590_NETLIST_TEMPLATE_TF = exe_tools.read_txt_file("netlists/AD590_TF_subckt.cir")
#npaths for LM741
LM741_SUBCKT_POST_RAD_TEMPLATE_TF = exe_tools.read_txt_file("netlists/LM741_TF_subckt_Postrad.cir")
#npaths for LM124
LM124_SUBCKT_POST_RAD_TEMPLATE_TF = exe_tools.read_txt_file("netlists/LM124_TF_subckt_Postrad.cir")
# paths for LM111
LM111_SUBCKT_POST_RAD_TEMPLATE_TF = exe_tools.read_txt_file("netlists/LM111_TF_subckt_Postrad.cir")
# paths for LM193
LM193_SUBCKT_POST_RAD_TEMPLATE_TF = exe_tools.read_txt_file("netlists/LM193_TF_subckt_Postrad.cir")
# paths for LM139
LM139_SUBCKT_POST_RAD_TEMPLATE_TF = exe_tools.read_txt_file("netlists/LM139_TF_subckt_Postrad.cir")

# List to store the types of Protons
PROTON_TYPE = ["200MeV"]


# Values for TID_FLUENCE parameters
DOSE_RATE_TF = [100]
HYDROGEN_TF = [0]
BIAS_TF = [0]

# fluence values 
FLUENCES_TF = [
    4.04E+11, 5.34E+11,7.05E+11
]

# Backend fluences with more precision
BACKEND_FLUENCES_TF = [
    4.038510e+11, 5.338350e+11, 7.052400e+11
]