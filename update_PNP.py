import pandas as pd
import numpy as np


def calculate(x,y):
    slope,intercept = np.polyfit(x,np.log(y),1)
    Vt = 0.02585
    n = 1/(slope*Vt)
    Is = np.exp(intercept)
    return Is, n

def main():
    npn_data = pd.read_excel('test_v1.xlsx', sheet_name='Sheet1') 
    header = ["Dose(krad)", "Is", "n"]

    data=[]
    x= npn_data["Ve"].iloc[22:60]
    for column in npn_data.columns[1:]:
        y= npn_data[column].iloc[22:60]
        # Calculate Is and n
        try:
            Is, n = calculate(x, y)
            # Only add rows where Is and n are not NaN or infinite
            if not (np.isnan(Is) or np.isnan(n) or np.isinf(Is) or np.isinf(n)):
                # print(f"{column}: Is = {Is:.8e}, n = {n:.8f}")
                data.append([column, Is, n])  # Append the results to the data list
        except Exception as e:
            print(f"Error in calculating for column {column}: {e}")
            continue  # Skip columns that cause errors
    if data:
        df = pd.DataFrame(data, columns= header)
        writer = pd.ExcelWriter('excel-files/PNP_diode_paramers_v1.xlsx', engine = 'xlsxwriter')
        df.to_excel(writer, index= False ,  float_format= "%.8e")
        writer.close()
    else:
        print("No valid data found in the input file")

    # writer1 = pd.ExcelWriter('excel-files/PNP_diode_paramers_v.xlsx', engine = 'xlsxwriter')
    # df.to_excel(writer1, sheet_name="data", index= False ,  float_format= "%.8e")
    # additional_data = pd.DataFrame({'Version #': ['1']})
    # additional_data.to_excel(writer1, sheet_name='Additional_Info', index=False)
    # writer1.close()


if __name__ == "__main__":
    main()

     