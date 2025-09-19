'''
No longer functional
'''
## DELETE RAW DATA
def delete_raws(file=None,env=None):

    text_content = f"""
    ## Access environment variables
    source {env}
    
    ## Construct name of file
        input_dir="$DATA_DIR/$FW_MODEL/$RUN_NAME/inputs/"
        task_id=$(printf "%05d" $SLURM_ARRAY_TASK_ID)
        input_file="${{input_dir}}input_${{task_id}}.txt"

    echo "Deleting Raw Outputs from: ${{TEMP_DIR}}/${{FW_MODEL}}/${{RUN_NAME}}/outputs-raw/out_${{task_id}}"
    rm -rf "${{TEMP_DIR}}/${{FW_MODEL}}/${{RUN_NAME}}/outputs-raw/out_${{task_id}}"
    """
    return text_content


