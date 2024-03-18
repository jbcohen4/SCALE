import argparse
import pandas as pd

# Set up argument parser
parser = argparse.ArgumentParser(description='Convert Excel file to CSV.')
parser.add_argument('excel_file', help='Path to the input Excel file.')
parser.add_argument('csv_file', help='Path to the output CSV file.')

# Parse arguments
args = parser.parse_args()

# Load the Excel file
df = pd.read_excel(args.excel_file)

# Convert to CSV
df.to_csv(args.csv_file, index=False)

