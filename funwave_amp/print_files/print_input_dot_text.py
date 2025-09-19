
import copy
import funwave_ds.fw_py as fpy

def print_input_dot_text(var_dict):
    print('\nPRINTING input.txt...')
    print('\tStarted printing input file...')

    ptr = fpy.get_key_dirs(tri_num = var_dict['ITER'])
    in_path = ptr['in']
    
    var_dict_copy = copy.deepcopy(var_dict)
    with open(in_path, 'w') as f:
        for var_name, value in var_dict_copy.items():
            if isinstance(value, (str, int, float)):
                f.write(f"{var_name} = {value}\n")
    
    print(f"\tinput.txt file successfully saved to: {ptr['in']}", flush=True)
    return     