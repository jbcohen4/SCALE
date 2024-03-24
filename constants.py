import exe_tools
AD590_NETLIST_TEMPLATE_PATH = exe_tools.adjust_path("netlists/AD590_template.cir")
XYCE_EXE_PATH = exe_tools.adjust_path("xyce/Xyce.exe")

# Object to Store the mapping of the Part and Specifications Dropdown
DROPDOWN_MAPPING = {
    "AD590": ["I_out"],
    "LM741": ["V_os", "I_b", "I_os"]

}