import numpy as np
import pandas as pd
from itertools import product
import xarray as xr
import os
## NOTE: These must be here for compatibility reasons
from netCDF4 import Dataset
import h5py

#%% SUMMARY FILES FROM GENERATION
def make_pass_parquet(summary_data,p):
    '''
    Summarizes all the attribute data for the ensemble of runs that passed
    through the filters, including all strings, integers, booleans, and 
    floats after all processing pipelines have been applied.
    '''
    dataframes = []
    
    # Loops through objects in a var_dict
    for key, nc_data in summary_data.items():
        # Create a DataFrame row from the attributes
        df = pd.DataFrame(nc_data.attrs, index=[0])
        dataframes.append(df)
    
    ## Merge all dataframes, filling in columns that don't exist with NaNs
    merged_df = pd.concat(dataframes, axis=0, join="outer", ignore_index=True)
    merged_df.to_parquet(p['I_pass'], index=False)

    return merged_df

def make_fail_parquet(fail_data,p):
    '''
    Summarizes all the failed runs, should they exist
    '''
    if fail_data:
        merged_df = pd.concat(fail_data.values(), ignore_index=True)
        merged_df.to_parquet(p['I_fail'], index=False)
        return merged_df
    

#%% Main function

def save_out_summary(success_dict,fail_dict,summary_formats):
    # Pass data
    df_pass = pd.DataFrame(success_dict)
    # Failure data
    df_fail = pd.DataFrame(fail_dict)

    # File Paths
    base_path = os.getenv('is')
    name = os.getenv('name')

    # Save out as parquet
    if 'parquet' in summary_formats:
        pass_name = f'{name}_input_summary.parquet'
        fail_name = f'{name}_failure_summary.parquet'
        df_pass.to_parquet(os.path.join(base_path,pass_name))
        df_fail.to_parquet(os.path.join(base_path,fail_name))

    if 'csv' in summary_formats:
        pass_name = f'{name}_input_summary.csv'
        fail_name = f'{name}_failure_summary.csv'
        df_pass.to_csv(os.path.join(base_path,pass_name), index=False)
        df_fail.to_csv(os.path.join(base_path,fail_name), index=False)


    return df_pass,df_fail
