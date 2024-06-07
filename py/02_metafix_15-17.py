'''
This is a script to 
'''

import os
import re
import csv
import shutil
import utilities as ut
import pandas as pd
from datetime import datetime

large_dir = '/Users/planktonperson/Data/Buskey_FC/SWMP_2015-17'

dir_names = [d for d in os.listdir(large_dir) if os.path.isdir(os.path.join(large_dir, d))] # add all directories to this list
dir_names = [d for d in dir_names if d not in ['metadata','raw','morphocut']]

meta_df = pd.DataFrame(
    {'object_run_id': dir_names}
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
site_regex = r'(AB|CE|CW|MB|SC|sc|ab|ce|cw|mb)'

site_data = meta_extractor(site_regex, dir_names)
meta_df.insert(1, 'sample_site', site_data['codes']) #add site codes
dir_names = site_data['dir_names'] # update dir names



# extract date codes

# there's one date code which is messed up
# 10295 should be 102915, going to change only here
# should work but leaves filenames without major changes in the system

for i in range(0, len(dir_names)-1):
    dir_names[i] = re.sub('10295', '102915', dir_names[i])



date_regex = r'(\d{6})'

date_data = meta_extractor(date_regex, dir_names)

dates = []
count = 0
for date in date_data['codes']:
    dates.append(datetime.strptime(date, '%m%d%y').strftime('%Y-%m-%d'))

meta_df.insert(2, 'sample_date', dates)
dir_names = date_data['dir_names']

# now create replicate number
'''
This is tricky since it is sometimes a 1 and othertimes a lower/uppercase ABCD
so I'm just going to go strip the last character
'''

repl = []
for d in dir_names:
    final = d[len(d)-1].strip().lower()
    if final == 'a' or final == '1':
        repl.append('A')
    elif final == 'b':
        repl.append('B')
    elif final == 'c':
        repl.append('C')
    elif final == 'd':
        repl.append('D')
    else:
        raise ValueError(f'Something wrong with {d}')

meta_df.insert(3, 'sample_replicate', repl)

# save the output

print(meta_df)

if not os.path.exists(os.path.join(large_dir, 'metadata')):
    os.mkdir(os.path.join(large_dir, 'metadata'))

meta_df.to_csv(os.path.join(large_dir, 'metadata', 'meta_dirnames.csv'), index=False) 