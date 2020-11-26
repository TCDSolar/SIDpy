# SuperSid
Collection of Python scripts used to process and archive data from the SuperSIDs at Birr and Dunsink.  

Designed to be run on Windows 10. Requires Anaconda3.

The scripts may be automatically run using Windows Task Scheduler. To do this, the processing_script.bat needs to be configured.

# Instillation 
1. Clone repository to a convienient location eg. Desktop.
2. Open Windows command prompt, and cd into the repo. 
3. Run "pip install requirements.txt"
4. Open the supersid_config.py and change the corresponding paths to those which suit your machine. N.B. use absolute paths to ensure that windows scheduler can run the scripts. 
5. Running supersid_run.py will proceed to process all files in the specified path before archiving the png along with the coresponding csv. 

