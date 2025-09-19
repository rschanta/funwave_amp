import os
from dotenv import load_dotenv
from ._make_log_folders import make_log_folders
from ._submit_slurm_job import submit_slurm_job
from ._write_slurm_script import write_slurm_script


class SlurmPipeline:
    ## INITIALIZE THE PIPELINE
    def __init__(self,
                 slurm_vars = None,
                 env=None):
        
        # Dictionary of default slurm variables
        self.slurm_vars = slurm_vars

        # Load necessary environments
        load_dotenv(dotenv_path=env)
        self.env = env
        self.log_dir = os.getenv('logs')
        self.batch_dir = os.getenv('batch')
        
        # Dictionary of Job IDs
        self.job_id = None


    ## PRIVATE METHOD: ADD JOB TO PIPELINE ------------------------------------
    def __add_job(self, 
                script_content_func, 
                dep_flags = {}, 
                **kwargs):

    
        # Slurm edit parameters
        slurm_edit = kwargs.pop('slurm_edit', {})
        
        # Slurm Flags
        all_slurm_flags = {**self.slurm_vars, # Default flags
                           **slurm_edit,      # Edited flags
                           **dep_flags}       # Dependency flags

        # Make log folders, set/edit slurm flags as needed
        all_slurm_flags = make_log_folders(self.log_dir,
                                           all_slurm_flags)

        ## Body of Script
        script_body = script_content_func(**kwargs)
        
        # Write the slurm script
        script = write_slurm_script(self.batch_dir,
                                        all_slurm_flags,
                                        script_body)
        
        # Run the slurm script
        job_id = submit_slurm_job(script)

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
            
            # All slurm bodies need the environment path
            kwargs['env'] = self.env

            # If this is the first job, just submit the job
            if previous_job_id is None:
                job_id = self.__add_job(step_func, **kwargs)
            
            # If this is a dependent script, also need last job_id
            elif previous_job_id is not None:
                dep_flags = {'dependency': previous_job_id}
                job_id = self.__add_job(step_func,dep_flags = dep_flags **kwargs)
            

            # Update the last job_id
            previous_job_id = job_id
    ## [END] PUBLIC METHOD: RUN THE PIPELINE ---------------------------------- 
        