import pandas as pd
import utilities as ut

# Define the file paths
text_file_path = '/Users/planktonperson/Data/Buskey_FC/SWMP_2014-17/AB_030917a/AB_030917a_run_summary.txt'
output_tsv_path = './test.tsv'

# Define the parameters of interest and their corresponding column names in the DataFrame
parameters_of_interest = {
    'Mode': 'acq_run_mode',
    'Used': 'images_used',
    'Total': 'images_total'
}

# Initialize a dictionary to store the extracted values
extracted_values = {value: None for value in parameters_of_interest.values()}

# Parse the text file
with open(text_file_path, 'r') as file:
    lines = file.readlines()
    for line in lines:
        for param, column_name in parameters_of_interest.items():
            if param in line:
                extracted_values[column_name] = line.split(':')[1].strip()

# Create a DataFrame
df = pd.DataFrame([extracted_values])

df_with_types = ut.add_dtype_line(df)

# Save the DataFrame to a .tsv file
df_with_types.to_csv(output_tsv_path, sep='\t', index=False)

print(f"Data saved to {output_tsv_path}")