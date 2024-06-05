import pandas as pd
import os
import re
import utilities as ut
from datetime import datetime

# Define the file paths
dir_path = '/Users/planktonperson/Data/Buskey_FC/SWMP_2014-15_badnames'
output_tsv_path = './test.tsv'

# Read and add all run file metadata

## Define the parameters of interest and their corresponding column names in the DataFrame
parameters_of_interest = {
    'Mode': 'acq_run_mode',
    'Sample Volume Processed': 'acq_vol_processed',
    'Fluid Volume Imaged': 'acq_vol_imaged',
    'Particle Count': 'sample_particle_num',
    'Start': 'acq_process_start',
    'End': 'acq_process_end',
    'Sampling Time': 'acq_process_dur',
    'Software': 'acq_software',
    'Magnification': 'acq_magnification',
    'Calibration Factor': 'acq_calib_factor',
    'Used': 'acq_imgused',
    'Total': 'acq_imgtotal',
}

files = [d for d in os.listdir(os.path.join(dir_path, 'raw'))]

meta_runsum = pd.DataFrame()
for file_name in files:
    if file_name.endswith('_run_summary.txt'):
        print(file_name)
        # Initialize a dictionary to store the extracted values
        extracted_values = {value: None for value in parameters_of_interest.values()}

        # Parse the text file
        with open(os.path.join(dir_path, 'raw', file_name), 'r') as file:
            lines = file.readlines()
            for line in lines:
                for param, column_name in parameters_of_interest.items():
                    if param in line:
                        extracted_values[column_name] = line.split(':')[1].strip()

        extracted_values['object_run_id'] = re.sub("_run_summary.txt", "", file_name)

        # add to df
        meta_runsum = pd.concat([meta_runsum, pd.DataFrame([extracted_values])], ignore_index=True)


# Extract additional metadata information
# did this in a function to just keep scoping not an issue
# this was copied from a bad old function
# it's confusing since originally these were directories hence names dirs but now its just ids and I didn't change it
def sample_infomation(meta_df):
    ids = meta_df['object_run_id']
    temp_ids = ids    

    def meta_extractor(reg_code, dirs):

        # initialize new structures
        codes = []
        mod_dirs = []
        #loop through
        for d in dirs:
            
            # codes
            code_match = re.search(reg_code, d) # pull code
            code= code_match.group() if code_match else None
            codes.append(code)

            # remove from list of dirs
            mod_dir = re.sub(reg_code, "", d)
            mod_dirs.append(mod_dir)

            del code, mod_dir, code_match
        
        return {
            'codes': codes,
            'dir_names': mod_dirs
        }
    

    # extract site code
    site_regex = r'(AB|CE|CW|MB|SC)'

    site_data = meta_extractor(site_regex, temp_ids)

    #loop to check for debugs
    for n in set(site_data['codes']):
        if n is None:
            print(f'Site issue {n}')

    # add to data
    meta_df.insert(1, 'sample_site', site_data['codes']) #add site codes
    temp_ids = site_data['dir_names'] # update dir names

    # extract date codes
    date_regex = r'(\d{6})'

    date_data = meta_extractor(date_regex, temp_ids)
    dates = []
    for date in date_data['codes']:
        dates.append(datetime.strptime(date, '%m%d%y').strftime('%Y-%m-%d'))


    #loop to check for debugs
    for n in set(date_data['codes']):
        if n is None:
            print(f'date issue {n}')

    meta_df.insert(2, 'sample_date', dates)
    temp_ids = date_data['dir_names']

    # now create replicate number
    # this will only work once all other numbers have been removed careful in other applications
    repl_regex = r'(\d{1})'
    repl_data = meta_extractor(repl_regex, temp_ids)

    repls = []
    for rep in repl_data['codes']:
        if rep is None or rep == "1":
            repls.append("A")
        elif rep == "2":
            repls.append("B")
        elif rep == "3":
            repls.append('C')
        else:
            print(f" There's a {rep}")

    #loop to check for debugs
    for n in set(repls):
        if n is None:
            print(f'code issue {n}')

    meta_df.insert(3, 'acq_run_replicate', repls)
    return(meta_df)


all_meta = sample_infomation(meta_runsum)


all_meta.to_csv(os.path.join(dir_path, 'metadata', 'meta.csv'))


# # read in the date sampling metadata
# meta_dirnames = pd.read_csv(os.path.join(dir_path, 'metadata','meta_dirnames.csv'))


# all_meta = pd.merge(meta_runsum, meta_dirnames, on = 'object_run_id', how = 'left')


# read in ecotaxa tsv file
etx = pd.read_csv(os.path.join(dir_path, 'morphocut','Ecotaxa','ecotaxa_export.tsv'), sep='\t',skiprows=[1])

etx['object_run_id'] = etx['object_id'].str.replace(r'_\d+$','',regex=True)

# check that all object run id's match
not_in_meta = etx[~etx['object_run_id'].isin(all_meta['object_run_id'])]['object_run_id']
print(not_in_meta.unique())

# print('\n___\n')
# print(list(set(all_meta['object_run_id'] - set(etx['object_run_id']))))


# # merge it all togetherf
# new_etx = pd.merge(etx, all_meta, on = 'object_run_id', how = 'left')

# print(new_etx.tail())
# # new_etx = ut.add_dtype_line(new_etx)

# # new_etx.to_csv(output_tsv_path, set = '\t', index = False)

# # df_with_types = ut.add_dtype_line(df)

# # # Save the DataFrame to a .tsv file
# new_etx.to_csv(output_tsv_path, sep='\t', index=False)

# # print(f"Data saved to {output_tsv_path}")
