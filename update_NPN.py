import pandas as pd
import numpy as np


def calculate(x,y):
    slope,intercept = np.polyfit(x,np.log(y),1)
    Vt = 0.02585
    n = 1/(slope*Vt)
    Is = np.exp(intercept)
    return Is, n

def main():
    npn_data = pd.read_excel('excel-files/deltaIb_neutron_NPNsim_data_V0.xlsx')
    header = ["delta_Ib_column", "Is_1", "n_1", "Is_2", "n_2" ]

    data=[]
    x= npn_data["Ve"].iloc[:21]
    x1 = npn_data["Ve"].iloc[25:46]
    for column in npn_data.columns[2:]:
        y= npn_data[column].iloc[:21]
        y1= npn_data[column].iloc[25:46]
        y = y[y >= 0]
        y1 = y1[y1 >= 0]
        x= npn_data["Ve"].iloc[y.index]
        x1 = npn_data["Ve"].iloc[y1.index]
        Is_1, n_1 = calculate(x,y)
        Is_2, n_2 = calculate(x1,y1)
        data.append([column,Is_1,n_1,Is_2,n_2])
    
    df = pd.DataFrame(data, columns= header)
    writer = pd.ExcelWriter('excel-files/NPN_diode_paramers_v1.xlsx', engine = 'xlsxwriter')
    df.to_excel(writer, index= False ,  float_format= "%.8e")
    writer.close()

    # writer1 = pd.ExcelWriter('excel-files/PNP_diode_paramers_v.xlsx', engine = 'xlsxwriter')
    # df.to_excel(writer1, sheet_name="data", index= False ,  float_format= "%.8e")
    # additional_data = pd.DataFrame({'Version #': ['1']})
    # additional_data.to_excel(writer1, sheet_name='Additional_Info', index=False)
    # writer1.close()


if __name__ == "__main__":
    main()

    