import numpy as np
import funwave_ds.fw_py as fpy


"""
Code to print out the DEPTH_FILE for FUNWAVE-TVD
"""

def print_DEPTH_FILE(vars):
    print('\t\tStarted printing bathymetry file (DEPTH_FILE)...')

    # Unpack variables
    bathy_array = vars['DOM']['Z'].values.T
    ITER = int(vars['ITER'])

    # Get path for bathymetry file- this is DEPTH_FILE
    ptr = fpy.get_key_dirs(tri_num = ITER)
    bathy_path = ptr['ba']

    # Print
    np.savetxt(bathy_path, bathy_array, delimiter=' ', fmt='%f')
    
    print(f'\t\tDEPTH_FILE file successfully saved to: {bathy_path}')
    return {'DEPTH_FILE': bathy_path}