def run_py_A(file=None,env=None):
    '''
    Creates a slurm script body that can be run to run a python script in an HPC
    system, by:
        - Reading in the environment variables
        - Activating the conda environment
        - Exporting the environment variables
        - Running the file
        
    Note that this inherently assumes that the job is submitted as part of an
    ARRAY, such that the `SLURM_ARRAY_TASK_ID` exists.

    '''
    
    text_content = f"""
    ## Access environment variables
    source {env}

    ## Activate Python Environment
    conda activate $CONDA_ENV

    ## Export out environment variables
    export $(xargs <{env})
    export TRI_NUM=$SLURM_ARRAY_TASK_ID
    
    python "{file}"

    """
    return text_content



