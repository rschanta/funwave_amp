import os
from dotenv import load_dotenv
from ._make_log_folders import make_log_folders
from ._submit_pbs_job import submit_pbs_job
from ._write_pbs_script import write_pbs_script


class PBS_Pipeline:
    ## INITIALIZE THE PIPELINE
    def __init__(self,
                 pbs_vars = None,
                 env=None):
        
        # Dictionary of default pbs flags
        self.pbs_vars = pbs_vars

        # Load necessary environments
        load_dotenv(dotenv_path=env)
        self.env = env
        self.log_dir = os.getenv('logs')
        self.batch_dir = os.getenv('batch')
        
        # Dictionary of Job IDs
        self.job_id = None


    ## PRIVATE METHOD: ADD JOB TO PIPELINE ------------------------------------
    def _add_job(self, 
                script_content_func, 
                dep_flags = {}, 
                **kwargs):

    
        # pbs edit parameters
        pbs_edit = kwargs.pop('pbs_edit', {})
        
        # pbs Flags
        all_pbs_flags = {**self.pbs_vars, # Default flags
                           **pbs_edit,      # Edited flags
                           **dep_flags}      # Dependency flags

        # Make log folders, set/edit pbs flags as needed
        all_pbs_flags = make_log_folders(self.log_dir,
                                           all_pbs_flags)

        ## Body of Script
        script_body = script_content_func(**kwargs)
        
        # Write the pbs script
        script = write_pbs_script(self.batch_dir,
                                        all_pbs_flags,
                                        script_body)
        
        # Run the pbs script
        try:
            job_id = submit_pbs_job(script)
        except:
            print(f'Submission failed. Making pbs script {all_pbs_flags["-N"]} but not submitting... ')
            job_id = None

        # Add the IDs to the job id list
        self.job_id = job_id
        return job_id
    ## [END] PRIVATE METHOD: ADD JOB TO PIPELINE ------------------------------
    
    
    
    ## PUBLIC METHOD: RUN THE PIPELINE ----------------------------------------
    def run_pipeline(self, 
                     steps):
        # Track the job ID of the previous step to handle dependencies
        previous_job_id = self.job_id

        # Loop through all steps
        for step_func, kwargs in steps.items():
            
            # All pbs bodies need the environment path
            kwargs['env'] = self.env

            # If this is the first job, just submit the job
            if previous_job_id is None:
                job_id = self._add_job(step_func, **kwargs)
            
            # If this is a dependent script, also need last job_id
            elif previous_job_id is not None:
                dep_flags = {"-W depend=afterok": previous_job_id}
                job_id = self._add_job(step_func,dep_flags = dep_flags, **kwargs)
            

            # Update the last job_id
            previous_job_id = job_id
    ## [END] PUBLIC METHOD: RUN THE PIPELINE ---------------------------------- 
        