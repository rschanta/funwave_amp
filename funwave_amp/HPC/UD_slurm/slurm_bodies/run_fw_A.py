def run_fw_A(file=None,
           env=None):
    '''
    Creates a slurm script body that can be run to run FUNWAVE-TVD by:
        - Reading in the environment variables
        - Constructing the path to `input.txt`
        - Using MPIRUN to run it, with the University of Delaware's settings
        
    Note that this inherently assumes that the job is submitted as part of an
    ARRAY, such that the `SLURM_ARRAY_TASK_ID` exists. It also relies on the
    environment variables previously specified to actually find the input.txt
    file.
    
    '''
    

    text_content = f"""
    ## Access environment variables
    source {env}

    . /opt/shared/slurm/templates/libexec/openmpi.sh
    
    ## Construct name of file
        input_dir="$in"
        task_id=$(printf "%05d" $SLURM_ARRAY_TASK_ID)
        input_file="${{input_dir}}input_${{task_id}}.txt"
    
    ## Run FUNWAVE
        ${{UD_MPIRUN}} $FW_ex "$input_file"


    """
    return text_content


