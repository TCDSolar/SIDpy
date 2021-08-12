"""
Verify and generate archive structure, specify paths of newly processed files
and archive them accordingly. The default structure of the archive is
{site}/YYYY/MM/DD/{file_type}/.

@author:
    Oscar Sage David O'Hara
@email:
    oharao@tcd.ie
"""

import logging
import os
from datetime import datetime
from pathlib import Path


class Archiver:
    """
    Class used to generate archive structure, specify paths of newly processed
    files and archive them accordingly. The default structure of the archive
    is {site}/YYYY/MM/DD/{file_type}/.
    """

    def __init__(self, root):
        self.root = root

    def archive_path(self, header, original_sid):
        """
        Create archive path root taking into consideration the instrument and site.

        Parameters
        ----------
        header : dict
            Dictionary containing observation parameters, eg. transmitter freq.
        original_sid : bool
            Statement on whether SID or Supersid data is being used.

        Returns
        -------
        parents : list
            Containing live data path and %Y/%m/%d archive path.

        """
        instrument = 'super_sid'
        if original_sid == True:
            instrument = 'sid'

        instra_path = (Path(self.root) / header['Site'].lower() / instrument /
                       datetime.strptime(header['UTC_StartTime'], '%Y-%m-%d%H:%M:%S').strftime('%Y/%m/%d') / 'csv')
        parents = [(Path(self.root) / header['Site'].lower() / 'live'), instra_path]
        return parents

    def static_summary_path(self, site):
        """
        Verifies and generates static paths for live data plots.

        Parameters
        ----------
         site : str
            Site name.
        """
        site = site.lower().replace(' ', '_')
        live_dir = (Path(self.root) / site / 'live')
        if not live_dir.exists():
            os.makedirs(live_dir)
            logging.debug('%s live directory created.', site)
