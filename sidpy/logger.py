"""
Contains functions to initialise the associated logging parameters. This specifies the
logging format and removes "spam" entries diluting key information.

@author:
    Oscar Sage David O'Hara
@email:
    oharao@tcd.ie
"""

import logging


def init_logger():
    """
    Once called this initialises logging config. By default logging levels have been altered for
    matplotlib, requests & numexpr.
    """
    logging.basicConfig(filename='error.log',
                        level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%Y/%m/%d %H:%M:%S')
    logging.getLogger('requests').setLevel(logging.DEBUG)
    logging.getLogger('matplotlib.font_manager').disabled = True
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    logging.getLogger('numexpr').setLevel(logging.WARNING)
