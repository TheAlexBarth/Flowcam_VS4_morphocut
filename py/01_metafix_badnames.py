# script to fix a typo in much of these files
# should do nothing now.

import os
import re

dir_path = '/Users/planktonperson/Data/Buskey_FC/SWMP_2014-15_badnames' # my files



# Iterate over each directory
for dir_name in os.listdir(dir_path):

    if os.path.isdir(os.path.join(dir_path, dir_name)):
        if '0708414' in dir_name:
            # Make new dir name
            new_dir_name = re.sub('0708414', '070814', dir_name)
            
            os.rename(os.path.join(dir_path, dir_name), os.path.join(dir_path, new_dir_name))


            # messsages
            print('----------------------')
            print(f"{dir_name} changed to {new_dir_name}")
            print('\n')

            # Iterate over each file in the directory
            for file_name in os.listdir(os.path.join(dir_path, new_dir_name)):
                new_file_name = re.sub('0708414', '070814', file_name)

                # os.rename(os.path.join(dir_path, new_dir_name, file_name),os.path.join(dir_path, new_dir_name, new_file_name))
                
                print('---')
                print(f"{file_name} changed to {new_file_name}")
                print('---')