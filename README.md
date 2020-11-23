# SuperSid_Scripts
Collection of python scripts used to process and archive the observational data for Stanford SuperSID. 

Initially designed to be run on windows 10, alongside an instillation of anaconda3.

The Scripts may be automatically ran using windows task scheduler, to do this the processing_script.bat will need to be configured.

# Instillation 
1. Clone reopository to a convienient location eg. Desktop.
2. Open windows command prompt, and cd into the repo. 
3. Run "pip install requirments.txt"
4. Open the supersid_config.py and change the corresponding paths to those which suit your machine. N.B. use absolute paths to ensure that windows schedular can run the scripts. 
5. Running backend.py will proceed to process all files in the specified path before archiving the png along with the coresponding csv. 

