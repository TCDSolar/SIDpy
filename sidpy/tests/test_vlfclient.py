from sidpy.vlfclient import VLFClient
from sidpy.tests.test_archiver import create_tmpdir
import pytest
import os
from pathlib import Path
from datetime import datetime


def test_get_header():
    vlfclient = VLFClient
    df = vlfclient.read_csv(Path('.') / 'data' / '20210703_000000_NAA_S-0055.csv')
    header = vlfclient.get_header(df)
    assert header == {'Site': 'Dunsink',
                      'Longitude': '-6.34',
                      'Latitude': '53.39',
                      'UTC_Offset': '+00:00',
                      'TimeZone': 'GMTStandardTime',
                      'UTC_StartTime': '2021-07-0300:00:00',
                      'StationID': 'NAA',
                      'Frequency': '24KHZ',
                      'MonitorID': 'S-0055-FB-0055',
                      'SampleRate': '1'}


def test_get_data():
    vlfclient = VLFClient
    df = vlfclient.read_csv(Path('.') / 'data' / '20210703_000000_NAA_S-0055.csv')
    data = vlfclient.get_data(df, True)
    for i in range(data.index[0], data.index[-1]):
        assert data['datetime'][i].strftime('%Y-%m-%d %H:%M:%S') == df['datetime'][i]
        assert data['signal_strength'][i] == df['signal_strength'][i]
