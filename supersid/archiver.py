"""
Verify and generate archive structure, specify paths of newly processed files
and archive them accordingly. The default structure of the archive is
{site}/YYYY/MM/DD/{file_type}/.

@author:
    Oscar Sage David O'Hara
@email:
    oharao@tcd.ie
"""

import os
import logging
from datetime import datetime
from pathlib import Path

from supersid.config.config import archive_path as config_archive


class Archiver:
    """
    Class used to generate archive structure, specify paths of newly processed
    files and archive them accordingly. The default structure of the archive
    is {site}/YYYY/MM/DD/{file_type}/.
    """

    def __init__(self, temp_data_path):
        self.temp_data_path = temp_data_path

    def static_summary_path(self, site):
        """
        Verifies and generates static paths for live data plots.

        Parameters
        ----------
         site : str
            Site name.
        """
        site = site.lower().replace(' ', '_')
        live_dir = (Path(config_archive) / site / 'live')
        if not os.path.exists(live_dir):
            os.system('mkdir ' + str(live_dir))
            logging.debug('%s live directory created.', site)
