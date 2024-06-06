import pandas as pd
import numpy as np
import re
import os
import shutil
from datetime import datetime

# add tsv top line
def add_dtype_line(df):
    """
    Write top line for ecotaxa tsv format
    """
    # Define a function to determine the data type
    def assign_tsv_type(data):
        if isinstance(data, (float)):
            return '[f]'
        else:
            return '[t]'
        
    def as_num_if_num(value):

        # Check if the string matches a numeric pattern
        if isinstance(value, str):
            if re.fullmatch(r"^\d+(\.\d+)?$", value):
                # Convert to float and return
                return float(value)
            else:
                # Return the original string
                return value
        else:
            return value
        
    df_dtypes = df.map(as_num_if_num).map(assign_tsv_type)

    out_df = pd.concat([df_dtypes.iloc[[0]], df], ignore_index=True)
    return(out_df)


# move files
def move_files(source_dir, destination_dir):
    # Ensure destination directory exists
    os.makedirs(destination_dir, exist_ok=True)

    # check files to see if all files exist
    
    # Move all files except those starting with 'cal_image'
    for root, dirs, files in os.walk(source_dir):

        #verfiy bin files
        img_names = []
        bin_names = []
        for file in files:
            if not file.startswith('cal_image'):
                if re.search(r'_(\d{6})\.tif$', file):
                    img_names.append(file)
                elif re.search(r'_(\d{6})_bin\.tif', file):
                    bin_names.append(re.sub('_bin','',file))
        
        if(set(img_names) == set(bin_names)):
            print('\n')
            print(f'All is good for {source_dir}, moving files')
        else:
            print(f'{source_dir} has missing bin files')

        # move all non cal files
        for file in files:
            if not file.startswith('cal_image'):
                shutil.move(os.path.join(root, file), destination_dir)



#################
# Date Extracting Functions
#################

# Extract additional metadata information
# did this in a function to just keep scoping not an issue
# this was copied from a bad old function
# it's confusing since originally these were directories hence names dirs but now its just ids and I didn't change it
def badnames_sampleinfo(meta_df):
    ids = meta_df['acq_id']
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
        dates.append(datetime.strptime(date, '%m%d%y').strftime('%Y%m%d'))


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

    meta_df.insert(3, 'sample_replicate', repls)
    meta_df.insert(4, 'sample_id', meta_df['sample_site'] + "_" + meta_df['sample_date'])
    return(meta_df)
