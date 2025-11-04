## RUN CONDENSE AND DELETE
def run_fw_run_py_del_A(file=None, env=None):
    '''
    Creates a PBS script body that can be run to run FUNWAVE-TVD by:
        - Reading in the environment variables
        - Constructing the path to `input.txt`
        - Using MPIRUN to run it,
        
    and immediately executes a python script to be run in the same session,
    after FUNWAVE-TVD has written all its outputs. Note that this inherently 
    assumes that the job is submitted as part of an array, such that the 
    `PBS_ARRAY_INDEX` exists. It also relies on the environment variables 
    previously specified to actually find the input.txt file.
    
    '''
    
    # Get function name and construct output file
    func_name = run_fw_run_py_del_A.__name__ 

    text_content = f"""
    ## Access environment variables
    source {env}

    ## Access MPI Functionality [TODO: Change to however you call MPI on USACE servers]
    . /opt/shared/slurm/templates/libexec/openmpi.sh
    
    ## Construct name of file
        input_dir="$in"
        task_id=$(printf "%05d" $PBS_ARRAY_INDEX)
        input_file="${{input_dir}}/input_${{task_id}}.txt"

    ## Run FUNWAVE [TODO: Change to however you call MPI on USACE servers]
        ${{UD_MPIRUN}} $FW_ex "$input_file"

    ## Activate Python Environment
    conda activate $conda

    ## Export out environment variables
    export $(xargs <{env})
    export TRI_NUM=$PBS_ARRAY_INDEX
    export FUNC_NAME={func_name}
    
    ## Run the Compression File
    python "{file}"

    ## Run the Raw Output Deletions
    echo "Deleting Raw Outputs from: ${{or}}/out_raw_${{task_id}}"
    rm -rf "${{or}}/out_raw_${{task_id}}"
    """
    return text_content


