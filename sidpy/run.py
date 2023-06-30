"""
Process all csv data found within the data path specified in config.cfg,
verifies and creates archive structure before saving the corresponding files to
their specified locations.

@author:
    Oscar Sage David O'Hara
@email:
    oharao@tcd.ie
"""

import shutil
from datetime import datetime, timedelta
from pathlib import Path

from sidpy.config.config import transmitters
from sidpy.archiver import Archiver
from sidpy.logger import init_logger
from sidpy.vlfclient import VLFClient

logger = init_logger()


def process_file(file_path, archive_path, gl=None, gs=None):
    """
    Process single given csv file meeting the appropriate criteria, before
    saving the corresponding png and input csv to the appropriate archive
    location.

    Parameters
    ----------
    file_path : str
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
    if (str(file_path).endswith('.csv') and any(i in str(file_path) for i in transmitters)
                and not str(file_path).__contains__("current")
                    and not str(file_path).__contains__(" ")):
        vlfclient, archiver = VLFClient(), Archiver(archive_path)
        logger.debug('The vlfclient and archiver have been initialised.')

        dataframe = vlfclient.read_csv(file_path)
        header = vlfclient.get_header(dataframe)

        archiver.static_summary_path(header['Site'])

        # Determine VLF receiver which is recording data.
        original_sid = False
        if '-' in header['MonitorID']:
            original_sid = True

        data = vlfclient.get_data(dataframe, original_sid)

        if (datetime.strptime(header['UTC_StartTime'], '%Y-%m-%d%H:%M:%S') > datetime.utcnow() - timedelta(days=6) and
                gs is not None):
            image_path = vlfclient.create_plot_xrs(header, data, file_path, archive_path, gl, gs, original_sid)
        else:
            image_path = vlfclient.create_plot(header, data, file_path, archive_path, original_sid)

        parents = archiver.archive_path(header, original_sid)
        for path in parents:
            if not path.exists():
                path.mkdir(parents=True)

        if True == original_sid:
            shutil.copy(image_path, parents[0] / (header['StationID'] + '_SID.png'))
        else:
            shutil.copy(image_path, parents[0] / (header['StationID'] + '_SuperSID.png'))
        logger.debug('PNGs copied to archive.')
        shutil.move(Path(file_path), parents[1] / file_path.name)
        logger.debug('CSVs moved to archive.')
        return image_path


def process_directory(data_path, archive_path):
    """Function to be run hourly in order to process and archive all files listed
    within the data_path specified within config.cfg.

    Parameters
    ----------
    data_path : str
        Directory containing data to be processed.
    archive_path : str
        Directory whhere the data will be archived.
    """
    logger.info('Processing called')
    archive_path = Path(archive_path)
    try:
        vlfclient = VLFClient()
        gl, gs = vlfclient.get_recent_goes()

        for directory in data_path:
            directory = Path(directory)
            for file in Path.iterdir(directory):
                image = process_file(directory / file, archive_path, gl, gs)
                if image:
                    logger.debug('%s : Has been processed and archived.', file)
                else:
                    logger.warning('%s : Could not be processed.', file)
        logger.info('Processing completed.')
    except Exception:
        logger.exception("The following exception was raised:")


""""
process_directory(['C:/Users/oscar/OneDrive/Desktop/temp/1', 'C:/Users/oscar/OneDrive/Desktop/temp/2'],
                  'C:/Users/oscar/Desktop/SuperSid/data')  # For development purposes
"""
