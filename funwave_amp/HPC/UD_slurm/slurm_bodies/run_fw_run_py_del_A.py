## RUN CONDENSE AND DELETE
def run_fw_run_py_del_A(file=None,env=None):
    # Get function name and construct output file
    func_name = run_fw_run_py_del_A.__name__ 

    text_content = f"""
    ## Access environment variables
    source {env}

    . /opt/shared/slurm/templates/libexec/openmpi.sh
    
    ## Construct name of file
        input_dir="$in"
        task_id=$(printf "%05d" $SLURM_ARRAY_TASK_ID)
        input_file="${{input_dir}}/input_${{task_id}}.txt"

    ## Run FUNWAVE
        ${{UD_MPIRUN}} $FW_ex "$input_file"

    ## Activate Python Environment
    conda activate $conda

    ## Export out environment variables
    export $(xargs <{env})
    export TRI_NUM=$SLURM_ARRAY_TASK_ID
    export FUNC_NAME={func_name}
    
    ## Run the Compression File
    python "{file}"

    ## Run the Raw Output Deletions
    
    echo "Deleting Raw Outputs from: ${{or}}/out_raw_${{task_id}}"
    rm -rf "${{or}}/out_raw_${{task_id}}"
  
    """
    return text_content


