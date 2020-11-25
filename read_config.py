"""
Read configuration file config.ini contents before intalizing the contained 
variables as a dependency to avoid circular imports.

@author: 
    Oscar Sage David O'Hara
@email: 
    oharao@tcd.ie
"""

from configparser import ConfigParser

# Initialize config file
config_object = ConfigParser()
config_object.read("config/config.ini")
config_data, config_archive = (config_object['PARAMETERS']['data_path'],
                               config_object['PARAMETERS']['archive_path'])
