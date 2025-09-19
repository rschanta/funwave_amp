import os

def write_slurm_script(batch_dir,
                       all_slurm_flags,
                       script_body=None):
    '''
    Write the slurm script, with the required flags 
    and the input body
    '''


    # Get name/path of batch script based on job-name
    job_name = all_slurm_flags["job-name"]
    file_name = f'{job_name}.qs'
    script_path = os.path.join(batch_dir,file_name)

    # Open the file to write to
    with open(script_path, 'w') as file:
        # Write the shebang line
        file.write("#!/bin/bash -l\n")
        file.write("#\n")  
        
        # Write the SLURM directives
        for slurm_flag, flag_value in all_slurm_flags.items():
            if flag_value is not None:
                file.write(f"#SBATCH --{slurm_flag}={flag_value}\n")
        file.write("#\n")  

        # Write the slurm body defined
        if script_body:
                file.write(script_body)

    print(f'Batch script created: {script_path}')
    return script_path

