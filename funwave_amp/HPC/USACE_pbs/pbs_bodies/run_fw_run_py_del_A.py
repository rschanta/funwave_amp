## RUN CONDENSE AND DELETE
def run_fw_run_py_del_A(file=None, env=None):
    """
    Creates a PBS script body that can be run to run FUNWAVE-TVD by:
        - Reading in the environment variables
        - Constructing the path to `input.txt`
        - Using MPIRUN to run it,

    and immediately executes a python script to be run in the same session,
    after FUNWAVE-TVD has written all its outputs. Note that this inherently
    assumes that the job is submitted as part of an array, such that the
    `PBS_ARRAY_INDEX` exists. It also relies on the environment variables
    previously specified to actually find the input.txt file.

    """

    # Get function name and construct output file
    func_name = run_fw_run_py_del_A.__name__

    text_content = f"""
    ## Access environment variables
    cd $PBS_O_WORKDIR
    source {env}

    ## Activate Python Environment
    source /apps/unsupported/funwaveportal/pyvenv/ftools/bin/activate
    
    # HDF5_USE_FILE_LOCKING=FALSE
    #
    ## Construct name of input file and output directory
    input_dir="$in"
    task_id=$(printf "%05d" $PBS_ARRAY_INDEX)
    input_file="${{input_dir}}/input_${{task_id}}.txt"
    output_dir=${{or}}/out_raw_${{task_id}}

    ## Checking for input file incase misconfigured task_id
    if [[ ! -f "$input_file" ]]; then
        echo "ERROR: Input file not found: $input_file" >&2
        exit 1 
    fi

    ## Creating output directory 
    mkdir -p $output_dir

    ## Loading HPC modules 
    module swap PrgEnv-cray PrgEnv-intel
    module load cray-netcdf

    ## Run FUNWAVE
    cd $output_dir
    aprun -n 44 $FW_ex $input_file

    ## Switching back to run directory for python call
    cd $PBS_O_WORKDIR

    ## Export out environment variables
    export $(xargs <{env})
    export TRI_NUM=$PBS_ARRAY_INDEX
    export FUNC_NAME={func_name}
    
    ## Run the Compression File
    python "{file}"

    ## Run the Raw Output Deletions
    echo "Deleting Raw Outputs from: ${{or}}/out_raw_${{task_id}}"
    # rm -rf "${{or}}/out_raw_${{task_id}}"
    """
    return text_content
