import numpy as np
import funwave_amp as fpy


"""
Code to print out the DEPTH_FILE for FUNWAVE-TVD
"""

def print_FRICTION_FILE(vars):
    print('\t\tStarted printing friction file (FRICTION_FILE)...')

    # Unpack variables
    friction_array = vars['DOM']['friction'].values.T
    ITER = int(vars['ITER'])

    # Get path for bathymetry file- this is DEPTH_FILE
    ptr = fpy.get_key_dirs(tri_num = ITER)
    friction_path = ptr['fr']

    # Print
    np.savetxt(friction_path, friction_array, delimiter=' ', fmt='%f')
    
    print(f'\t\tFRICTION_FILE file successfully saved to: {friction_path}')
    return {'FRICTION_FILE': friction_path}
