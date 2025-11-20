def run_py(file=None, env=None):
    """
    Creates a slurm script body that can be run to run a python script in an HPC
    system, by:
        - Reading in the environment variables
        - Activating the conda environment
        - Exporting the environment variables
        - Running the file

    """

    text_content = f"""
    ## Access environment variables

    cd $PBS_O_WORKDIR
    source {env}
   
    ## Activate Python Environment
    source /apps/unsupported/funwaveportal/pyvenv/ftools/bin/activate
    #conda activate $CONDA_ENV
    
    ## Export out environment variables
    export $(xargs <{env})
    
    ## Run File
    python "{file}"
    """
    return text_content
