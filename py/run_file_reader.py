import pandas as pd
import os
import re
import utilities as ut
from datetime import datetime

# Define the file paths
dir_path = '/Users/planktonperson/Data/Buskey_FC/SWMP_2014-15_badnames'
output_tsv_path = os.path.join(dir_path, 'morphocut','Ecotaxa','ecotaxa_export.tsv')


#################################
##
## Read and add all run file metadata
##
################################


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
    'Percentage Used': 'acq_img_perc_used',
    'Total': 'acq_imgtotal',
}

files = [d for d in os.listdir(os.path.join(dir_path, 'raw'))]

meta_runsum = pd.DataFrame()
for file_name in files:
    if file_name.endswith('_run_summary.txt'):
        # Initialize a dictionary to store the extracted values
        extracted_values = {value: None for value in parameters_of_interest.values()}

        # Parse the text file
        with open(os.path.join(dir_path, 'raw', file_name), 'r') as file:
            lines = file.readlines()
            for line in lines:
                for param, column_name in parameters_of_interest.items():
                    if param in line:
                        extracted_values[column_name] = line.split(':', 1)[-1].strip()

        extracted_values['acq_id'] = re.sub("_run_summary.txt", "", file_name)

        # add to df
        meta_runsum = pd.concat([meta_runsum, pd.DataFrame([extracted_values])], ignore_index=True)




all_meta = ut.badnames_sampleinfo(meta_runsum)


all_meta.to_csv(os.path.join(dir_path, 'metadata', 'meta.csv'))

##############################
'''




Metadata checking steps




'''
##########################

# read in ecotaxa tsv file
etx = pd.read_csv(os.path.join(dir_path, 'morphocut','Ecotaxa','ecotaxa_export.tsv'), sep='\t',skiprows=[1])

# create etx fun file
etx['acq_id'] = etx['object_id'].str.replace(r'_\d+$','',regex=True)

#######
# First check sampling parameters
#######

# any case where trigger mode wasn't used 

bad_modes = all_meta[all_meta['acq_run_mode'] != 'Trigger']['acq_id'].unique()
print(all_meta)
if len(bad_modes) > 0:
    print(f'Bad run modes were found for: {bad_modes}')
    resp_ok = False
    while not resp_ok:
        bad_resp = input('Go ahead and remove file(s) [y/n]: ').strip().lower()
        if bad_resp == 'y':
            all_meta = all_meta[all_meta['acq_run_mode'] == 'Trigger']
            print(all_meta)
            resp_ok = True
        elif bad_resp == 'n':
            raise ValueError("intentional stop")
        else:
            print('only y/n response')
            next


############ Remove images from faulty runs #########################################################

not_in_meta = etx[~etx['acq_id'].isin(all_meta['acq_id'])]['acq_id']
not_in_etx = all_meta[~all_meta['acq_id'].isin(etx['acq_id'])]['acq_id']

# if there's something missing from the etx but in the meta, i need an error
if(len(not_in_etx) > 0):
   raise ValueError(f'There is something wrong with {not_in_etx} in the etx file')

# if there's an issue with run files, we need to remove from etx and delete the corresponding data sets
if(len(not_in_meta) > 0):
    print('\n')
    print('_____')
    print(f'There\'s and issue with these run files {not_in_meta.unique()} this will delete from the etx project')
    print('\n')
    resp_ok = False
    while not resp_ok:
        resp = input('Go ahead and delete these from project? [y/n]').strip().lower()
        if resp == 'y':
            etx = etx[etx['acq_id'].isin(all_meta['acq_id'])]
            #get all image files
            img_files = [f for f in os.listdir(os.path.join(dir_path, 'morphocut','Ecotaxa'))]
            #loop through to fine who's not in the meta
            counter = 0
            for file in img_files:
                for bad in not_in_meta.unique():
                    if file.startswith(bad):
                        print('\n')
                        print(f'Removing image file: {file}')
                        counter += 1
                        os.remove(os.path.join(dir_path, 'morphocut','Ecotaxa',file))
            #confirm it worked
            print('\n')
            print(f'Total Removed: {counter}')
            resp_ok = True
        elif resp == 'n':
            raise ValueError('Script intentionally abandoned')
        else:
            print('Enter only [y/n]')


###################
'''




Finalize and merge everything



'''
###################

# # merge it all togetherf
new_etx = pd.merge(etx, all_meta, on = 'acq_id', how = 'left')


# print(new_etx.tail())
new_etx = ut.add_dtype_line(new_etx)

# # new_etx.to_csv(output_tsv_path, set = '\t', index = False)

# df_with_types = ut.add_dtype_line(df)

# # # Save the DataFrame to a .tsv file
new_etx.to_csv(output_tsv_path, sep='\t', index=False)

print(f"Data saved to {output_tsv_path}")
