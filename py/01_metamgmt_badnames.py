# processing for early files:
import os
import re
import csv
import shutil
import utilities as ut
import pandas as pd
from datetime import datetime

large_dir = '/Users/planktonperson/Data/Buskey_FC/SWMP_2014-15_badnames'

dir_names = [d for d in os.listdir(large_dir) if os.path.isdir(os.path.join(large_dir, d))] # add all directories to this list
dir_names = [d for d in dir_names if d not in ['metadata','raw','ecotaxa']]

meta_df = pd.DataFrame(
    {'dir_name': dir_names}
)


# Pull metadata sequentially
# function for any reg code and list of directories
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

site_data = meta_extractor(site_regex, dir_names)
meta_df.insert(1, 'sample_site', site_data['codes']) #add site codes
dir_names = site_data['dir_names'] # update dir names

# extract date codes
date_regex = r'(\d{6})'

date_data = meta_extractor(date_regex, dir_names)
dates = []
for date in date_data['codes']:
    dates.append(datetime.strptime(date, '%m%d%y').strftime('%Y-%m-%d'))

meta_df.insert(2, 'sample_date', dates)
dir_names = date_data['dir_names']

# now create replicate number
# this will only work once all other numbers have been removed careful in other applications
repl_regex = r'(\d{1})'
repl_data = meta_extractor(repl_regex, dir_names)

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

meta_df.insert(3, 'acq_run_replicate', repls)
meta_df = ut.add_dtype_line(meta_df)

# save the output

if not os.path.exists(os.path.join(large_dir, 'metadata')):
    os.mkdir(os.path.join(large_dir, 'metadata'))

meta_df.to_csv(os.path.join(large_dir, 'metadata', '01_meta_dirnames.csv'), sep = '\t', index=False)