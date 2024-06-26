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
                if os.path.exists(os.path.join(destination_dir, file)):
                    print('\n\n\n')
                    print('-------------')
                    print(f'WARNING: {file} was already moved. Skipping but check')
                    print('-------------------')
                    print('\n\n\n\n')
                else:
                    shutil.move(os.path.join(root, file), destination_dir)



#################
# Date Extracting Functions
#################
def sampleinfo18(meta_df):
    ids = meta_df['acq_id']
    temp_ids = ids

    # Pull metadata sequentially
    # function for any reg code and list of directories

    # extract site code
    site_regex = r'(AB|CE|CW|MB|SC|sc|ab|ce|cw|mb)'

    site_data = meta_extractor(site_regex, temp_ids)
    meta_df.insert(1, 'sample_site', site_data['codes']) #add site codes
    temp_ids = site_data['dir_names'] # update dir names



    # extract date codes

    date_regex = r'(\d{6})'

    date_data = meta_extractor(date_regex, temp_ids)

    dates = []
    count = 0
    for date in date_data['codes']:
        dates.append(datetime.strptime(date, '%m%d%y').strftime('%Y-%m-%d'))

    meta_df.insert(2, 'sample_date', dates)
    temp_ids = date_data['dir_names']

    # need to extract dilution factor

    acq_dil_fact = []
    for id in temp_ids:
        dil_match = re.search(r'(\d+\.?\d*)dil', id)
        if dil_match:
            acq_dil_fact.append(float(dil_match.group(1)))
        else:
            acq_dil_fact.append(1)

    meta_df.insert(3, 'acq_dil_fact', acq_dil_fact)

    # now create replicate number
    '''
    This is tricky since it is sometimes a 1 and othertimes a lower/uppercase ABCD
    so I'm just going to go strip the last character
    '''

    repl = []

    # for i in range(0, len(temp_ids)-1):
    #     x = temp_ids[i]
    #     if x.upper().endswith("TEST"):
    #         print(f'Error at {ids[i]} is {x}')
    #     elif x.upper().endswith('AA'):
    #         print(f'Error {ids[i]} is {x}')
    #     elif x.upper().endswith('_'):
    #         print(f'Error {ids[i]} is {x}')

    # print(temp_ids)
    # raise ValueError('stop')
    for d in temp_ids:
        final = d[len(d)-1].strip().lower()
        if final in ['a','1','_', 't']: # had to make lots of special cases t is for test
            repl.append('A')
        elif final == 'b':
            repl.append('B')
        elif final == 'c':
            repl.append('C')
        elif final == 'd':
            repl.append('D')
        else:
            raise ValueError(f'Something wrong with {d}')

    meta_df.insert(4, 'sample_replicate', repl)
    meta_df.insert(5, 'sample_id', meta_df['sample_site'] + "_" + meta_df['sample_date'])
    return(meta_df)



# meta for 15-17 dates
def sampleinfo_15_17(meta_df):
    ids = meta_df['acq_id']
    temp_ids = ids


    # extract site code
    site_regex = r'(AB|CE|CW|MB|SC|sc|ab|ce|cw|mb)'

    site_data = meta_extractor(site_regex, temp_ids)
    meta_df.insert(1, 'sample_site', site_data['codes']) #add site codes
    temp_ids = site_data['dir_names'] # update dir names



    # extract date codes

    # there's one date code which is messed up
    # 10295 should be 102915, going to change only here
    # should work but leaves filenames without major changes in the system

    for i in range(0, len(temp_ids)-1):
        temp_ids[i] = re.sub('10295', '102915', temp_ids[i])



    date_regex = r'(\d{6})'

    date_data = meta_extractor(date_regex, temp_ids)

    dates = []
    count = 0
    for date in date_data['codes']:
        dates.append(datetime.strptime(date, '%m%d%y').strftime('%Y-%m-%d'))

    meta_df.insert(2, 'sample_date', dates)
    temp_ids = date_data['dir_names']

    # now create replicate number
    '''
    This is tricky since it is sometimes a 1 and othertimes a lower/uppercase ABCD
    so I'm just going to go strip the last character
    '''

    repl = []

    # for i in range(0, len(temp_ids)-1):
    #     x = temp_ids[i]
    #     if x.upper().endswith("TEST"):
    #         print(f'Error at {ids[i]} is {x}')
    #     elif x.upper().endswith('AA'):
    #         print(f'Error {ids[i]} is {x}')
    #     elif x.upper().endswith('_'):
    #         print(f'Error {ids[i]} is {x}')

    # print(temp_ids)
    # raise ValueError('stop')
    for d in temp_ids:
        final = d[len(d)-1].strip().lower()
        if final in ['a','1','_', 't']: # had to make lots of special cases t is for test
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
    meta_df.insert(4, 'sample_id', meta_df['sample_site'] + "_" + meta_df['sample_date'])
    return(meta_df)


# Extract additional metadata information
# did this in a function to just keep scoping not an issue
# this was copied from a bad old function
# it's confusing since originally these were directories hence names dirs but now its just ids and I didn't change it
def badnames_sampleinfo(meta_df):
    ids = meta_df['acq_id']
    temp_ids = ids        

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


'''


Sample metadata extractor 
this works for a regex when there is a usable regex
this pulls the code and returns a modified dir_name



'''
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