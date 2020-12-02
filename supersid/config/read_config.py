"""
Read configuration file supersid_config.ini contents before initializing the contained
variables as a dependency to avoid circular imports.

@author:
    Oscar Sage David O'Hara
@email:
    oharao@tcd.ie
"""

from configparser import ConfigParser


def read_config():
    """
    Read contents of supersid_config.ini using ConfigParser.

    Returns
    -------
    config_object : DataFrame Object
        Contents of supersid_config.ini.

    """
    config_object = ConfigParser()
    config_object.read("supersid_config.ini")
    return config_object


def config_data():
    """
    Read path to data directory from supersid_config.ini.

    Returns
    -------
    data_path : str
        Path to data directory.

    """
    config_object = read_config()
    config_data = (config_object['PARAMETERS']['data_path'])
    return config_data


def config_archive():
    """
    Read path to data directory from supersid_config.ini.

    Returns
    -------
    data_path : str
        Path to data directory.

    """
    config_object = read_config()
    config_archive = (config_object['PARAMETERS']['archive_path'])
    return config_archive
