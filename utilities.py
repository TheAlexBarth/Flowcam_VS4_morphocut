import pandas as pd
import re
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

    out_df = pd.concat([df_dtypes, df], ignore_index=True)
    return(out_df)