import re
import subprocess


def submit_slurm_job(script_path):
    
    # Try running the sbatch command
    try:
        # Subprocess command
        result = subprocess.run(
            ['sbatch', script_path],
            capture_output=True,    # To get jobID
            text=True,              # To get as text (not bytes)
            check=True              # To get errors
        )
        
        # Extract the job ID using a regular expression
        output = result.stdout
        job_id_match = re.search(r'Submitted batch job (\d+)', output)
        
        # Return job ID if found
        if job_id_match:
            job_id = job_id_match.group(1)
            return job_id
        else:
            return "Job ID not found in sbatch output."
    
    # Return error if any issues
    except subprocess.CalledProcessError as e:
        # Handle errors in the subprocess call
        return f"Error occurred: {e.stderr}"