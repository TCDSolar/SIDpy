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
import urllib.request, urllib.parse, urllib.error
from datetime import datetime, timedelta

from supersid.config.config import data_path as config_data, archive_path as config_archive
from supersid.archiver import Archiver
from supersid.vlfclient import VLFClient


def process_file(file, gl=None, gs=None):
    """
    Process single given csv file meeting the appropriate criteria, before
    saving the corresponding png and input csv to the appropriate archive
    location.

    Parameters
    ----------
    file : str
        File path.
    gl : pandas.Series
        GOES XRS Long data.
    gs : pandas.Series
        GOES XRS Short data.

    Returns
    -------
    image_path : str
        Temporary path of generated png.
    """
    if file.endswith('.csv') and not file.__contains__("current") and not file.__contains__(" "):
        vlfclient = VLFClient()

        dataframe = vlfclient.read_csv(file)
        header = vlfclient.get_header(dataframe)
        data = vlfclient.get_data(dataframe)

        if datetime.strptime(header['UTC_StartTime'], '%Y-%m-%d%H:%M:%S') > datetime.utcnow() - timedelta(days=6):
            image_path = vlfclient.create_plot_xrs(header, data, file, gl, gs)
        else:
            image_path = vlfclient.create_plot(header, data, file)

        parents = [(Path(config_archive) / header['Site'].lower() / 'live'),
                   (Path(config_archive) / header['Site'].lower() /
                    datetime.strptime(header['UTC_StartTime'], '%Y-%m-%d%H:%M:%S').strftime('%Y/%m/%d') / 'csv')]
        for path in parents:
            if not path.exists():
                path.mkdir(parents=True)

        shutil.copy(image_path, parents[0] / (header['StationID'] + '.png'))
        shutil.move(Path(file), parents[1] / file.split('/')[-1])
        return image_path


def process_directory():
    """Function to be run hourly in order to process and archive all files listed
    within the data_path specified within config.cfg."""
    vlfclient, archiver = VLFClient(), Archiver(temp_data_path=None)
    archiver.static_summary_path()
    gl, gs = vlfclient.get_recent_goes()

    for directory in config_data:
        for file in os.listdir(directory):
            image = process_file(directory + "/" + file, gl, gs)
            if image:
                print(file, ": Has been processed and archived.")
            else:
                print(file, ": Could not be processed, please try again later.")

# process_directory()  # For development purposes
