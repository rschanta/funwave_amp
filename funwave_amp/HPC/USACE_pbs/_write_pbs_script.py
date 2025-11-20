import os


def write_pbs_script(batch_dir, all_pbs_flags, script_body=None):
    """
    Write the pbs script, with the required flags
    and the input body
    """

    # Get name/path of batch script based on job-name (-N)
    job_name = all_pbs_flags.get("-N", "pbs_job")
    file_name = f"{job_name}.qs"
    script_path = os.path.join(batch_dir, file_name)

    # Open the file to write to
    with open(script_path, "w") as file:
        # Write the shebang line
        file.write("#!/bin/bash -l\n")
        file.write("#\n")

        # Write the PBS directives
        for directive, value in all_pbs_flags.items():
            if value is not None:
                # HACK: for walltime syntax
                if "walltime" in directive:
                    file.write(f"#PBS {directive}={value}\n")
                elif "depend" in directive:
                    file.write(f"#PBS {directive}:{value}\n")
                else:
                    file.write(f"#PBS {directive} {value}\n")
        file.write("#\n")

        # Write the pbs body defined
        if script_body:
            file.write(script_body)

    print(f"Batch script created: {script_path}")
    return script_path
