"""
Configuration file for the SIDpy processing scripts. The required
parameters must be initialised correctly in order for the code to run.

@author:
    Oscar Sage David O'Hara
@email:
    oharao@tcd.ie
"""

### [PARAMETERS] ###

# Paths to the file directories locating the raw csv data you wish to process.
data_path = ['C:/Users/oscar/OneDrive/Desktop/temp/1', 'C:/Users/oscar/OneDrive/Desktop/temp/2']

# Output path of archive - archive will be generated within the specified directory.
archive_path = 'C:/Users/oscar/Desktop/SuperSid/data'

### [TRANSMITTERS] ###

# Currently used vlf transmitter codes, with their corresponding latitude and
# longitude. Used to identify transmitter from file header and calculate
# sunrise and sunset times.

transmitters = {
    'JJI': [32.082, 130.828, 'Ebino, Japan'],
    'NDT': [32.082, 130.828, 'Ebino, Japan'],
    'NAA': [44.644, -67.282, 'Maine, USA'],
    'FTA': [48.545, 2.579, 'Sainte-Assise, France'],
    'VTX4': [8.387, 77.753, 'Vijayanarayanam, India'],
    'DHO38': [53.079, 7.615, 'Rhauderfehn, Germany'],
    'DH038': [53.079, 7.615, 'Rhauderfehn, Germany'],
    'SRC': [57.113, 12.397, 'Grimeton, Sweden'],
    'NRK': [63.850, 22.467, 'Keflavik, Iceland'],
    'TBB': [37.409, 27.325, 'Bafa, Turkey'],
    'JXN': [66.982, 13.872, 'Gildeskål, Norway'],
    'ICV': [40.923, 9.732, 'Sardinia, Italy'],
    'HWU2': [46.714, 1.244, 'Rosnay, France'],
    'HWU1': [46.714, 1.244, 'Rosnay, France']
}
