
import numpy as np

import funwave_ds.fw_py as fpy


def print_FRICTION_OR_BREAKWATER_FILE(var_dict):
    print('\t\tChecking for FRICTION_FILE and/or BREAKWATER_FILE...')
    
    ## Figure out friction
    DOM = var_dict['DOM']
    
    if "friction" in DOM.data_vars:
        print('\t\tIdentified FRICTION_FILE!')
        print('\t\tStarted printing friction file (FRICTION_FILE)...')
        # Unpack variables
        friction_array = var_dict['DOM']['friction'].values.T
        ITER = int(var_dict['ITER'])

        # Get path for bathymetry file- this is DEPTH_FILE
        ptr = fpy.get_key_dirs(tri_num = ITER)
        friction_path = ptr['fr']

        # Print
        np.savetxt(friction_path, friction_array, delimiter=' ', fmt='%f')
        
        print(f'\t\tFRICTION_FILE file successfully saved to: {friction_path}')
        return {'FRICTION_FILE': friction_path}
    
    if "BW_Width" in DOM.data_vars:
        print('\t\tIdentified BREAKWATER_FILE!')
        print('\t\tStarted printing breakwater file (BREAKWATER_FILE)...')
        # Unpack variables
        BWAC_array = var_dict['DOM']['BW_Width'].values.T
        ITER = int(var_dict['ITER'])

        # Get path for bathymetry file- this is DEPTH_FILE
        ptr = fpy.get_key_dirs(tri_num = ITER)
        bwac_path = ptr['bw']

        # Print
        np.savetxt(bwac_path, BWAC_array, delimiter=' ', fmt='%f')
        
        print(f'\t\tBREAKWATER_FILE file successfully saved to: {bwac_path}')
        return {'BREAKWATER_FILE': bwac_path}
        
    else:
        raise ValueError('Must as specify `USE_CDBWAC` as `CD` or `BWAC`, even if value 0!')
        
        



