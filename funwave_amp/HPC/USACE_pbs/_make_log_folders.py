import os

def make_log_folders(log_dir, all_pbs_flags):
    '''
    Make the folders for the log files from PBS outputs, and
    adjust flags as needed to work with this.
    '''

    # Just one folder if no array
    if all_pbs_flags.get('-J') is None and all_pbs_flags.get('-t') is None:
        # Get the job name from the PBS flags
        job_name = all_pbs_flags['-N']
        # Construct/make the directory for the logs `log_dir/job_name`
        out_err_dir = os.path.join(log_dir, job_name)
        os.makedirs(out_err_dir, exist_ok=True)
        # Construct the actual name of the path to an error/out file
        all_pbs_flags['-o'] = os.path.join(out_err_dir, 'out.out')
        all_pbs_flags['-e'] = os.path.join(out_err_dir, 'err.out')
        print(f'pbs output log folder created in: {out_err_dir}')
        print(f'pbs error log folder created in : {out_err_dir}')

    # If array, need to do PBS flags with % and add an extra folder layer for clarity
    else:
        # Get the job name from the PBS flags
        job_name = all_pbs_flags['-N']
        # Construct/make the directory for the out logs `log_dir/job_name/out`
        out_dir = os.path.join(log_dir, job_name, 'out')
        os.makedirs(out_dir, exist_ok=True)
        # Construct/make the directory for the error logs `log_dir/job_name/err`
        err_dir = os.path.join(log_dir, job_name, 'err')
        os.makedirs(err_dir, exist_ok=True)
        # Construct the actual name of the path to an error/out file, using array syntax
        all_pbs_flags['-o'] = os.path.join(out_dir, 'out_${PBS_ARRAY_INDEX}.out')
        all_pbs_flags['-e'] = os.path.join(err_dir, 'err_${PBS_ARRAY_INDEX}.out')
        # Echo results
        print(f'pbs output log folder created: {out_dir}')
        print(f'pbs error log folder created: {err_dir}')
        
    # Patch up paths
    for flag in ('-o', '-e'):
        all_pbs_flags[flag] = all_pbs_flags[flag].replace('\\', '/')
    
    return all_pbs_flags
