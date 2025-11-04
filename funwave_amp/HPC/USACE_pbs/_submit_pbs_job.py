import subprocess
import re

def submit_pbs_job(script_path):
    """
    Submit a PBS job script using qsub and return the Job ID.
    """

    try:
        # Submit PBS job
        result = subprocess.run(
            ['qsub', script_path],
            capture_output=True,
            text=True,
            check=True
        )

        # Grab the ID: may need to be edited
        output = result.stdout.strip()
        job_id_match = re.search(r'(\d+[\.\w-]*)', output)

        if job_id_match:
            job_id = job_id_match.group(1)
            return job_id
        else:
            return f"Job ID not found in qsub output: {output}"

    except subprocess.CalledProcessError as e:
        # Capture stderr from qsub
        return f"Error occurred: {e.stderr.strip()}"