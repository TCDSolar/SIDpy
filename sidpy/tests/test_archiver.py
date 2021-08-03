"""
Python tests for archiver.py.

@author:
    Oscar Sage David O'Hara
@email:
    oharao@tcd.ie
"""

from sidpy.archiver import Archiver
import pytest
import os
from pathlib import Path
from datetime import datetime


@pytest.fixture(scope="session")
def create_tmpdir(tmpdir_factory):
    base = tmpdir_factory.mktemp("data")
    return base


def test_archiver_archive_path():
    header = {'Site': 'test', 'UTC_StartTime': '2020-01-0112:12:12'}
    archiver = Archiver(root='test')
    parents = archiver.archive_path(header, True)
    assert len(parents) == 2
    assert parents[1] == (Path('test') / header['Site'] / 'sid' /
                          datetime.strptime(header['UTC_StartTime'], '%Y-%m-%d%H:%M:%S').strftime('%Y/%m/%d') / 'csv')
    assert parents[0] == (Path('test') / header['Site'].lower() / 'live')
    parents = archiver.archive_path(header, False)
    assert parents[1] == (Path('test') / header['Site'] / 'super_sid' /
                          datetime.strptime(header['UTC_StartTime'], '%Y-%m-%d%H:%M:%S').strftime('%Y/%m/%d') / 'csv')


def test_static_summary_path(create_tmpdir):
    archiver = Archiver(create_tmpdir)
    archiver.static_summary_path('test_site')
    assert os.path.exists(create_tmpdir / 'test_site' / "live")
