def run_py_A(file=None, env=None):
    '''
    Creates a PBS script body that can be run to execute a Python script on an HPC
    system, by:
        - Reading in the environment variables
        - Activating the conda environment
        - Exporting the environment variables
        - Running the file

    Note that this inherently assumes that the job is submitted as part of an
    ARRAY, such that the `PBS_ARRAY_INDEX` exists.
    '''

    text_content = f"""
    ## Access environment variables
    source {env}

    ## Activate Python Environment
    conda activate $CONDA_ENV

    ## Export out environment variables
    export $(xargs <{env})
    export TRI_NUM=$PBS_ARRAY_INDEX
    
    python "{file}"

    """
    return text_content
