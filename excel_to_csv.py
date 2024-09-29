import argparse
import pandas as pd

# Set up argument parser with default values for input and output files
parser = argparse.ArgumentParser(description='Convert Excel file to CSV.')
parser.add_argument('excel_file', nargs='?', default='csvs/TID_PNP_SHEET1_V0.xlsx', help='Path to the input Excel file.')
parser.add_argument('csv_file', nargs='?', default='csvs/TID_PNP_SHEET1_V0.csv', help='Path to the output CSV file.')

# Parse arguments
args = parser.parse_args()

# Load the Excel file specified by the user or use the default
df = pd.read_excel(args.excel_file)

# Convert to CSV file at the specified location or use the default
df.to_csv(args.csv_file, index=False)

print(f"Excel file '{args.excel_file}' has been successfully converted to '{args.csv_file}'.")