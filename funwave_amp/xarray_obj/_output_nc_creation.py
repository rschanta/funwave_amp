
import os
import numpy as np
import xarray as xr
import funwave_amp as fpy
from pathlib import Path
import warnings
from pathlib import Path
from typing import  Dict, Any, Optional
from pathlib import Path

def find_prefixes_path(directory):
        prefixes = []
        for filename in os.listdir(directory):
            # Split at extension
            name, _ = os.path.splitext(filename)
            
            # Identify time step files (ends in XXXXX)
            if name[-5:].isdigit() and len(name) > 5:
                variable_ = name[:-5]
            # Identify station files (ends in XXXX)
            elif name[-4:].isdigit() and len(name) > 4:
                variable_ = name[:-4]
            # Identify non time-step files
            else:
                variable_ = name
            # Append to list
            prefixes.append(variable_)

        # Remove duplicates
        prefix_list = list(set(prefixes))
        return prefix_list

def get_var_out_paths(RESULT_FOLDER: Path, var: str) -> list[Path]:
    '''
    Gets a list of paths to all of the output files in RESULT_FOLDER that have 
    names that begin with the string specified by `var`. For example, use `eta_` 
    to get the eta files.
    
    ARGUMENTS:
        - var (str): substring to search for at the beginning of file names. 
            Best to use up to last underscore (ie- `eta_`, `U_undertow`) to 
            avoid issues with similarly named variables
    RETURNS: 
        -path_of_vars (List(Path)): all the paths to the variables 
            searched for

    '''
    out_XXXXX_path = Path(RESULT_FOLDER)
    var_files = []
    for file in out_XXXXX_path.iterdir():
        if file.name.startswith(var):
                var_files.append(file)
                
    path_of_vars = sorted(var_files, key=lambda p: p.name)            
    return path_of_vars

def get_vars_out_paths(RESULT_FOLDER: Path, var_search: list[str])-> Dict[str,list[Path]]:
    '''
    Applies `get_var_in_path` to the path specified for the variables 
    specified in var_search to output a dictionary of path lists. Cleans up 
    name a bit (trailing _)
    
    ARGUMENTS:
        - out_XXXXX (Path): Path to out_XXXXX file
    RETURNS: 
        - var_search (List[str]): list of substrings for `get_var_output_paths`
    '''
    
    all_var_paths = {}
    for var in var_search:
        varname = var[:-1] if var.endswith('_') else var  # Remove trailing _ if they exist
        all_var_paths[varname] = get_var_out_paths(RESULT_FOLDER,var)
    return all_var_paths

#%% HELPER FUNCTIONS

def load_array(var_XXXXX: Path, 
               Mglob: int, Nglob: int):
    '''
    Load a FUNWAVE-TVD output file into a NumPy array.

    This function assumes that `IO_TYPE = BINARY` was used in FUNWAVE-TVD,
    meaning most outputs are binary. Two exceptions are allowed:
    - `time_dt.txt`
    - station files (`sta_*.txt`)

    If reading fails for any reason, a zero-filled array of the appropriate
    dimensions is returned instead of raising an error.
    '''
    
    try:
        # Allowable ASCII files: time_dt and station files
        if var_XXXXX.name == 'time_dt.txt':
            return np.loadtxt(var_XXXXX,dtype=np.float32)
        elif var_XXXXX.name.startswith('sta_'):
            return np.loadtxt(var_XXXXX,dtype=np.float32)
        
        # Everything else must be binary
        else:
            return np.fromfile(var_XXXXX, dtype=np.float32).reshape(Nglob,Mglob)

    # Pad with zeros otherwise if error
    except Exception as e:
        warnings.warn(
            f"Issue reading {var_XXXXX.name} ({e}). "
            "Substituting with zeros to avoid crashing.",
            UserWarning
        )
        return np.zeros((Nglob, Mglob), dtype=np.float32)
    
    
    
def load_and_stack_to_tensors(Mglob,Nglob,all_var_dict):
    '''
    Load and stack FUNWAVE-TVD time series outputs into tensors.

    For each variable key in `all_var_dict`, this function loads the associated
    files (using `load_array`), stacks them into a single tensor along a new
    leading axis (time/file index), and returns a dictionary of tensors.
    '''

    tri_tensor_dict = {}
    
    # Loop through all variables found in RESULT_FOLDER
    for var, file_list in all_var_dict.items(): 
        print(f'\tCompressing: {var}')
        
        var_arrays = []
        # Loop through all files of this variable and load in
        for file_path in file_list:
            var_array = load_array(file_path,Mglob,Nglob)
            var_arrays.append(var_array)
        
        # Form into tensor, squeeze out any extra dimensions
        try:
            var_tensor = np.squeeze(np.stack(var_arrays, axis=0))
            tri_tensor_dict[var] = var_tensor
        except:
            print('Issue!')
    return tri_tensor_dict


#%% MAIN OUTPUT 
def get_into_netcdf():
    print('\nStarted compressing raw output files in NetCDF...')

    # Acess necessary paths
    ptr = fpy.get_key_dirs()

    # Get the NETCDF Created in the input phase
    ds = xr.load_dataset(ptr['nc'])
    # Get dimensions needed from inputs
    Mglob, Nglob = ds.attrs['Mglob'], ds.attrs['Nglob']

    # Stations
    try:
        NumberStations = ds.attrs['NumberStations']
    except:
        print('No stations specified')

    # Get paths to outputs
    RESULT_FOLDER = ptr['or']

    # Get list of all variables found in the result folder (eta, u, sta, time_dt, etc.)
    var_list = find_prefixes_path(RESULT_FOLDER)
    
    # Dictionary with keys for each variable type (eta,u,sta,etc.) and values a sorted list of all files
        # for each one (ie- {'eta': ['eta_00000','eta_00001', 'eta_00002' ...]})
    var_paths = get_vars_out_paths(RESULT_FOLDER, var_list)

    ## Get all outputs
    output_variables = load_and_stack_to_tensors(Mglob,Nglob,var_paths)
    
    # Pop off some problematic ones
    for key in ['dep','dep_Xco','dep_Yco','time_dt']:
        output_variables.pop(key, None)
        
    ## Get time and add
    time_dt = np.loadtxt(ptr['time_dt'])


    t_FW = time_dt[:,0]
    ds = ds.assign_coords({"t_FW": ("t_FW", t_FW)})

    
    ## Add other variables
    for var_name, var_value in output_variables.items():
        
        
        # TIME STEP FILES
        if (var_value.ndim == 3 and var_value.shape == (t_FW.size,Nglob,Mglob)):
            # Create variable with specified dimensions
            ds = ds.assign( {var_name: ( ['t_FW','Y','X'], var_value)})
        elif var_value.ndim == 2 and Nglob == 1 and var_value.shape == (t_FW.size, Mglob):
            var_value = var_value[:, np.newaxis, :]
            ds = ds.assign({var_name: (['t_FW','Y','X'], var_value)})
        
        
        # STATION FILES
        elif (var_name=='sta'):
            print('\tCompressing station data...')
            # Separate out eta,u,v
            t_station = np.squeeze(var_value[0,:,0])
            eta_station = np.squeeze(var_value[:,:,1])
            u_station = np.squeeze(var_value[:,:,2])
            v_station = np.squeeze(var_value[:,:,3])

            # Create a station NetCDF
            ds_station= xr.Dataset(
                coords={
                    'GAGE_NUM': ds.coords['GAGE_NUM'],  
                    't_station': ('t_station', t_station),
                    'X': ds.coords['X'],
                    'Y': ds.coords['Y'],
                },
                data_vars={
                    'eta_sta': (['GAGE_NUM', 't_station'], eta_station),
                    'u_sta': (['GAGE_NUM', 't_station'], u_station),
                    'v_sta': (['GAGE_NUM', 't_station'], v_station),
                    'Mglob_gage': (['GAGE_NUM'], ds['Mglob_gage'].values),
                    'Nglob_gage': (['GAGE_NUM'], ds['Nglob_gage'].values),
                    'Z': (['X','Y'], ds['Z'].values)  
                }
            )

            ds_station.attrs = ds.attrs.copy()
            # Save to netcdf
            ds_station.to_netcdf(ptr['ns'])
            print(f"\t\tSuccessfully compressed station data to .nc file: {ptr['ns']}")

        # TIME AVERAGE FILES
        elif (var_value.ndim == 3 and var_value.shape[1:] == (Nglob,Mglob)):
            # Create dimension if not there
            if "t_AVE" not in ds.coords:
                ave_dim = var_value.shape[0]
                t_AVE = np.arange(0,ave_dim)
                ds = ds.assign_coords({"t_AVE": ("t_AVE", t_AVE)})
                
            # Add variable
            ds = ds.assign( {var_name: ( ['t_AVE','Y','X'], var_value)})

    # EDIT 3-17
    comp = dict(zlib=True, complevel=4)  # Compression level 1 (low) to 9 (high)
    encoding = {var: comp for var in ds.data_vars}  # Apply to all variables

    # Save to netcdf
    ds.to_netcdf(ptr['nc'],mode='w', encoding=encoding)
    print(f"Succesfully compressed data to .nc file: {ptr['nc']}")
    return ds
