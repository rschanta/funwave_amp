import numpy as np
import funwave_amp as fpy


def print_STATIONS_FILE(var_dict):
    print('\t\tStarted printing station file (STATIONS_FILE)...')

    # Unpack variables
    DOM = var_dict['DOM']
    Mglob_pos = DOM['Mglob_gage'].values
    Nglob_pos = DOM['Nglob_gage'].values
    station_array = np.column_stack((Mglob_pos, Nglob_pos))
    station_array = station_array
    ITER = int(var_dict['ITER'])

    # Get directories
    # Get path for bathymetry file- this is DEPTH_FILE
    ptr = fpy.get_key_dirs(tri_num = ITER)
    station_path = ptr['st']

    # Print
    np.savetxt(station_path, station_array, delimiter=' ', fmt='%d')
    
    print(f'\t\tSTATION file successfully saved to: {station_path}')
    return {'STATIONS_FILE':station_path}






