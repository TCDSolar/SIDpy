"""
Python tests for vlfclient.py.

@author:
    Oscar Sage David O'Hara
@email:
    oharao@tcd.ie
"""

from sidpy.vlfclient import VLFClient
import pytest
import pandas as pd
from pathlib import Path
from datetime import datetime


@pytest.fixture(scope="session")
def create_tmpdir(tmpdir_factory):
    base = tmpdir_factory.mktemp("data")
    return base


@pytest.fixture(scope='session')
def header():
    return {'Site': 'Dunsink',
            'Longitude': '-6.34',
            'Latitude': '53.39',
            'UTC_Offset': '+00:00',
            'TimeZone': 'GMTStandardTime',
            'UTC_StartTime': '2021-07-0300:00:00',
            'StationID': 'NAA',
            'Frequency': '24KHZ',
            'MonitorID': 'S-0055-FB-0055',
            'SampleRate': '1'}


@pytest.fixture(scope='session')
def png_path(header, create_tmpdir):
    return (create_tmpdir / header['Site'].lower() / 'sid' /
            datetime.strptime(header['UTC_StartTime'], '%Y-%m-%d%H:%M:%S').strftime('%Y/%m/%d') /
            'png' / ('20210703_000000_NAA_S-0055.csv'.split('.')[0] + '.png'))


def test_get_header(header):
    vlfclient = VLFClient()
    df = vlfclient.read_csv(Path(__file__).parent / 'data' / '20210703_000000_NAA_S-0055.csv')
    header_result = vlfclient.get_header(df)
    assert header_result == header


def test_get_data():
    vlfclient = VLFClient()
    df = vlfclient.read_csv(Path(__file__).parent / 'data' / '20210703_000000_NAA_S-0055.csv')
    data = vlfclient.get_data(df, True)
    for i in range(data.index[0], data.index[-1]):
        assert data['datetime'][i].strftime('%Y-%m-%d %H:%M:%S') == df['datetime'][i]
        assert data['signal_strength'][i] == df['signal_strength'][i]


def test_create_plot(create_tmpdir, header, png_path):
    vlfclient = VLFClient()
    file_path = Path(__file__).parent / 'data' / '20210703_000000_NAA_S-0055.csv'
    df = vlfclient.read_csv(file_path)
    df = df[~df['datetime'].astype(str).str.startswith('#')]
    df['datetime'] = pd.to_datetime(df['datetime'], format='%Y-%m-%d %H:%M:%S')
    image_path = vlfclient.create_plot(header, df, file_path=str(file_path).split('\\')[-1],
                                       archive_path=create_tmpdir, original_sid=True)
    assert image_path == png_path


def test_create_plot_xrs(create_tmpdir, header, png_path):
    vlfclient = VLFClient()
    file_path = Path(__file__).parent / 'data' / '20210703_000000_NAA_S-0055.csv'
    df = vlfclient.read_csv(file_path)
    df = df[~df['datetime'].astype(str).str.startswith('#')]
    df['datetime'] = pd.to_datetime(df['datetime'], format='%Y-%m-%d %H:%M:%S')
    gl, gs = vlfclient.get_recent_goes(Path(__file__).parent / 'data' / 'xrays-3-day.json')
    image_path = vlfclient.create_plot_xrs(header, df, file_path=str(file_path).split('\\')[-1],
                                           archive_path=create_tmpdir, gl=gl, gs=gs, original_sid=True)
    assert image_path == png_path


#AssertionError: assert PosixPath('/home/vsts/work/1/s/.tox/py37/lib/python3.7/site-packages/sidpy/tests/data/20210703_000000_NAA_S-0055.png') == local('/tmp/pytest-of-vsts/pytest-0/data1/dunsink/sid/2021/07/03/png/20210703_000000_NAA_S-0055.png')
