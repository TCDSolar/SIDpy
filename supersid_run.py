"""
Process all csv data found within the data path specified in config.cfg, 
verifies and creates archive structure before saving the corresponding files to
their specified locations.

@author: 
    Oscar Sage David O'Hara
@email: 
    oharao@tcd.ie
"""

import os
import shutil
from pathlib import Path

from read_config import config_data, config_archive
from supersid_archiver import Archiver
from vlfclient import VLFClient


def process_file(file):
    """
    Process single given csv file meeting the appropriate criteria. Before 
    saving the corresponding png and input csv to the appropriate archive
    location.
    
    Parameters
    ----------
    file : str
        File path.
        
    Returns
    -------
    temp_image_path : str
        Temporary path of generated png.
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
                                               / (file[len(config_data) + 1:-4] + '.png')))
        shutil.move(file,
                    Path(config_archive) / str(archive_dict['data_path']
                                               / file[len(config_data) + 1:]))
        return True, temp_image_path
    else:
        return False, None


def process_directory():
    """
    Function to be run hourly in order to process and archive all files listed
    within the data_path specified within config.cfg. 
    
    Parameters
    ----------
    None
    
    Returns
    -------
    None
    """
    vlfclient, archiver = VLFClient(), Archiver(temp_data_path=None)
    archiver.static_summary_path()
    vlfclient.summary_plot()
    for file in os.listdir(config_data):
        status, temp_image = process_file(config_data + "/" + file)
        if status == True:
            print(file, ": Has been processed and archived.")
        else:
            print(file, ": Could not be processed, please try again later.")


process_directory()
