"""
Created on Sat Oct 24 13:49:31 2020

@author: oscar
"""

from vlfclient import VLFClient 
from archiver import Archiver
from pathlib import Path
import shutil
import os
from supersid_config import data_path as config_data, archive_path as config_archive


def process_file(file):
    """
    Process single given csv file meeting the appropriate criteria. Before 
    saving the conresponding png and input csv to the appropriate archive
    location.
    
    Parameters
    ----------
    file : str
        File path.
        
    Returns
    -------
    temp_image_path : str
        Tempory path of generated png.
    """
    if file.endswith('.csv') and not file.__contains__("current") and not file.__contains__(" "):
        vlfclient = VLFClient()
        archiver = Archiver(file)
        dataframe = vlfclient.read_csv(file)
        header = vlfclient.get_header(dataframe)
        data = vlfclient.get_data(dataframe)
        temp_image_path = vlfclient.create_plot(header, data, file)
        archive_dict = archiver.archive(header)
        shutil.move(temp_image_path,
                    Path(config_archive) / str(archive_dict['image_path']
                    / (file[len(config_data)+1:-4] + '.png')))
        shutil.move(file,
                    Path(config_archive) / str(archive_dict['data_path']
                    / file[len(config_data)+1:]))
        return True, temp_image_path
    else:
        return False, None
    

def run_hourly():
    """
    Function to be run hourly in order to process and archive all files listed
    within the data_path specified within supersid_config.py. 
    
    Parameters
    ----------
    None
    
    Returns
    -------
    None
    """
    # vlfclient = VLFClient()
    # vlfclient.summary_plot()
    for file in os.listdir(config_data):
        status, temp_image = process_file(config_data +"/" + file)
        if status == True:
            print(file, ": Has been processed and archived.")
        else:
            print(file, ": Could not be processed, please try again later.")
            
run_hourly()