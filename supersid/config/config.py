"""
Configuration file for the supersid processing scripts. The required
parameters must be initialised correctly in order for the code to run.

@author:
    Oscar Sage David O'Hara
@email:
    oharao@tcd.ie
"""

### [PARAMETERS] ###

# Path to the file directory locating the raw csv data you wish to process.
data_path = 'C:/Users/oscar/Desktop/temp'

# Output path of archive - archive will be generated within the specified directory.
archive_path = 'C:/Users/oscar/Desktop/SuperSid/data'

### [TRANSMITTERS] ###

# Currently used vlf transmitter codes, with their corresponding latitude and
# longitude. Used to identify transmitter from file header and calculate
# sunrise and sunset times.

transmitters = {
    'JJI': [32.082, 130.828],
    'NDT': [32.082, 130.828],
    'NAA': [44.644, -67.282],
    'FTA': [48.545, 2.579],
    'VTX4': [8.387, 77.753],
    'DHO38': [53.079, 7.615],
    'DH038': [53.079, 7.615],
    'SRC': [57.113, 12.397],
    'NRK': [63.850, 22.467]
}
