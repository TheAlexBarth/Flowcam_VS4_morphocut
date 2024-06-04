import pandas as pd
import re
import os
import shutil

# add tsv top line
def add_dtype_line(df):
    """
    Write top line for ecotaxa tsv format
    """

    # Define a function to determine the data type
    def assign_tsv_type(data):
        if isinstance(data, (int, float, complex)):
            return '[f]'
        else:
            return '[t]'
        
    def as_num_if_num(value):

        # Check if the string matches a numeric pattern
        if re.fullmatch(r"^\d+(\.\d+)?$", value):
            # Convert to float and return
            return float(value)
        else:
            # Return the original string
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
