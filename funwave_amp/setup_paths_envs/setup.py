import os

## PATH SETUP
def setup_key_dirs(name='NAME',
                    main_dir = None,
                    input_dir = None,
                    log_dir = None,
                    env_dir = None,
                    result_folder_dir = None,
                    batch_dir = None,
                    bathy_dir = None,
                    spectra_dir = None,
                    station_dir = None,
                    friction_dir = None,
                    breakwater_dir=None,
                    nc_dir = None,
                    nc_sta_dir = None,
                    conda = None,
                    input_sum_dir = None,
                    FW_ex = None,
                    dir_add_ons = None):
    
    
    # main_dir
    if main_dir is None:
        raise ValueError("`main_dir` must be specified")
    else:
        print(f'main_dir Directory set as: {main_dir}')
    
    # input.txt files
    if input_dir is None:
        raise ValueError("`input_dir` must be specified")
    else:
        print(f'Directory for input.txt files set to: {input_dir}')
        
    # RESULT_FOLDER files
    if result_folder_dir is None:
        raise ValueError("`result_folder_dir` must be specified")
    else:
        print(f'Directory for RESULT_FOLDER directories set to: {result_folder_dir}')
        
    # NetCDF
    if nc_dir is None:
        raise ValueError("`nc_dir` must be specified")
    else:
        print(f'Directory for NetCDF outputs set to: {nc_dir}')
        
    # Need NetCDF station directory if specified
    if station_dir:
        if nc_sta_dir is None:
            raise ValueError("`nc_sta_dir` must be specified")
        else:
            print(f'Directory for NetCDF outputs at stations set to: {nc_dir}')

    # Default directories that need to exist
    if log_dir is None:
        log_dir = os.path.join(main_dir,'logs')
        
    if env_dir is None:
        env_dir = os.path.join(main_dir,'envs')
    if batch_dir is None:
        batch_dir = os.path.join(main_dir,'batch_scripts')
        
    if input_sum_dir is None:
        input_sum_dir = os.path.join(main_dir,'input_sum')

    
    # Construct stuff within main_dir
    
    paths = {'in': input_dir,
             'is': input_sum_dir,
             'or': result_folder_dir,
             'ba': bathy_dir,
             'sp': spectra_dir,
             'st': station_dir,
             'fr': friction_dir,
             'bw': breakwater_dir,
             'nc': nc_dir,
             'ns': nc_sta_dir,
             'main': main_dir,
             'batch': batch_dir,
             'envs': env_dir,
             'logs': log_dir,
             'FW_ex': FW_ex,
             'conda': conda,
             'name': name,
             'PYTHONPATH': main_dir}
    
    
    # Make Directories
    for key,path_name in paths.items():
        if key not in {'FW_ex','conda','PYTHONPATH','name'}:
            if path_name:
                  print(f'\tSpecifying {key}: {path_name}')
                  os.makedirs(path_name, exist_ok=True)
            
    # Other directories to add
    if dir_add_ons:
        for key,path_name in dir_add_ons.items():
            print(f'\tMaking {key}: {path_name}')
            os.makedirs(path_name, exist_ok=True)


    # Write to Environment File
    env_path = os.path.join(env_dir,f'{name}.env')
    print(f'.env file created at {env_path}')
    with open(env_path, "w") as f:
        for key,path_name in paths.items():
            if path_name:
                f.write(f"{key}={path_name}\n")
        
        if dir_add_ons:
            for key,path_name in dir_add_ons.items():
                if path_name:
                    f.write(f"{key}={path_name}\n")


    paths['env_file'] = env_path
    return paths
