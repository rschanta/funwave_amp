import numpy as np
import funwave_amp as fpy


def print_WK_TIME_SERIES(var_dict):
    ITER = var_dict['ITER']
    WK = var_dict['WK']


    # Get path for bathymetry file- this is DEPTH_FILE
    ptr = fpy.get_key_dirs(tri_num = ITER)
    spectra_path = ptr['sp']

    # Unpack
    period = WK.period.values
    amp = WK.amp.values
    pha = WK.phase.values

    np.savetxt(spectra_path, np.column_stack((period, amp, pha)), fmt='%12.8f')
    print(f'\t\tWaveCompFile successfully saved to: {spectra_path}')

    return {'WaveCompFile': spectra_path}









