import os


def make_log_folders(log_dir,all_slurm_flags):
    '''
    Make the folders for the log files from slurm outputs, and
    adjust flags as needed to work with this.
    '''

    # Just one folder if no array
    if all_slurm_flags.get('array') is None:
        # Get the job name from the slurm flags
        job_name = all_slurm_flags['job-name']
        # Construct/make the directory for the logs `log_dir/job_name`
        out_err_dir = os.path.join(log_dir,job_name)
        os.makedirs(out_err_dir, exist_ok=True)
        # Construct the actual name of the path to an error/out file
        all_slurm_flags['output'] =  os.path.join(out_err_dir,'out.out')
        all_slurm_flags['error'] =  os.path.join(out_err_dir, 'err.out') 
        print(f'Slurm output log folder created in: {out_err_dir}')
        print(f'Slurm error log folder created in : {out_err_dir}')

    # If array, need to do slurm flags with %- add an extra folder layer for clarity
    else:
        # Get the job name from the slurm flags
        job_name = all_slurm_flags['job-name']
        # Construct/make the directory for the out logs `log_dir/job_name/out`
        out_dir = os.path.join(log_dir,job_name,'out')
        os.makedirs(out_dir, exist_ok=True)
        # Construct/make the directory for the error logs `log_dir/job_name/out`
        err_dir = os.path.join(log_dir, job_name,'err')
        os.makedirs(err_dir, exist_ok=True)
        # Construct the actual name of the path to an error/out file, using array syntax
        all_slurm_flags['output'] = os.path.join(out_dir,'out%a.out')
        all_slurm_flags['error'] = os.path.join(err_dir, 'err%a.out') 
        # Echo results
        print(f'Slurm output log folder created: {out_dir}')
        print(f'Slurm error log folder created: {err_dir}')
    return all_slurm_flags



