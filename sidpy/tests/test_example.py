from sidpy.archiver import Archiver
import pytest
from pathlib import Path

def test_archiver_archive_path():
    archiver = Archiver(temp_data_path=None)
    assert archiver.temp_data_path == None


