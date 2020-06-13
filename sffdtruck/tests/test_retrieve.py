# -*- coding: utf-8 -*-
import csv
import logging as l
import os
import pytest
import unittest
import time
from datetime import datetime, timedelta
from io import StringIO
from tempfile import mkdtemp

import pytest
import sffdtruck
import sffdtruck.retrieve as retr


# Setup Global cache for this file
@pytest.fixture
def init_setup(tmp_path):
    l.info(f"Temp dir: {tmp_path}")
    old = sffdtruck.CONSTS.cache_dir
    sffdtruck.CONSTS.cache_dir = str(tmp_path)
    sffdtruck.CONSTS.csv_cache_file = sffdtruck.CONSTS.cache_dir + "/cached_csv.csv"
    sffdtruck.CONSTS.kdtree_cache_file = sffdtruck.CONSTS.cache_dir + "/cached_tree.bin"
    if os.path.exists(sffdtruck.CONSTS.csv_cache_file):
        os.remove(sffdtruck.CONSTS.csv_cache_file)
    if os.path.exists(sffdtruck.CONSTS.kdtree_cache_file):
        os.remove(sffdtruck.CONSTS.kdtree_cache_file)
    bts = None
    with open(
        os.path.dirname(__file__) + "/../../Mobile_Food_Facility_Permit.csv", "rb"
    ) as f:
        bts = f.read()

    def download(url=sffdtruck.CONSTS.csv_url, timeout=2):
        return bts

    orig = sffdtruck.retrieve.download_csv
    sffdtruck.retrieve.download_csv = download
    return {"tmpdir": str(tmp_path), "to": 10, "download": orig}


def test_retrieve(init_setup):
    l.info(
        f"Cache files {sffdtruck.CONSTS.csv_cache_file}, {sffdtruck.CONSTS.kdtree_cache_file}"
    )
    existing = None
    # Basic version
    existing, is_new = retr.retrieve(timeout=init_setup["to"], check_update=True)
    with StringIO(existing) as sio:
        try:
            csv.reader(sio)
        except Exception as e:
            pytest.fail("URL/CSV raises exception!")
    assert (len(existing) > 0 and is_new == True)
    # Just making sure we have a dummy file
    with open(sffdtruck.CONSTS.kdtree_cache_file, "wb") as f:
        f.write(os.urandom(10))

    # No check update
    l.info(sffdtruck.CONSTS.csv_cache_file)
    new, is_new = retr.retrieve(timeout=init_setup["to"], check_update=False)
    assert (len(new) == len(existing) and is_new == False and new == existing)

    new, is_new = retr.retrieve(timeout=init_setup["to"], check_update=True)
    assert (len(new) == len(existing) and is_new == False)

    # Check outdated cache
    mod = time.mktime((datetime.now() - timedelta(weeks=2)).timetuple())
    os.utime(sffdtruck.CONSTS.csv_cache_file, (mod, mod))
    new = retr.retrieve(timeout=init_setup["to"], check_update=False)[0]
    assert len(new) == len(existing) and is_new == False

    # Messing with the Content for HASH calcculation
    with open(sffdtruck.CONSTS.csv_cache_file, "wb") as f:
        f.write(os.urandom(10))
    mod = time.mktime((datetime.now() - timedelta(weeks=2)).timetuple())
    os.utime(sffdtruck.CONSTS.csv_cache_file, (mod, mod))
    new, is_new = retr.retrieve(timeout=init_setup["to"], check_update=False)
    assert len(new) == len(existing) and is_new == True

    # Exception test
    retr.retrieve(timeout=init_setup["to"], check_update=True)
    from urllib.request import URLError

    def download(url=sffdtruck.CONSTS.csv_url, timeout=2):
        raise URLError("TEST")

    old, sffdtruck.retrieve.download_csv = sffdtruck.retrieve.download_csv, download
    new, is_new = retr.retrieve(timeout=init_setup["to"], check_update=True)
    assert len(new) == len(existing) and is_new == False
    sffdtruck.retrieve.download_csv = old


def test_download(init_setup):
    bts = init_setup["download"](timeout=init_setup["to"])
    assert len(bts) > 0
    with StringIO(bts.decode("utf-8")) as sio:
        try:
            csv.reader(sio)
        except Exception as e:
            pytest.fail("CSV raises exception!")


def test_update_cache(init_setup):
    assert retr.update_cache(None) == None
    # Check creation of file
    bts = os.urandom(1024)
    assert retr.update_cache(bts) == bts
    assert os.path.exists(sffdtruck.CONSTS.csv_cache_file) == True
    assert os.stat(sffdtruck.CONSTS.csv_cache_file).st_size == len(bts)
    # Check deletion of existing file
    bts = os.urandom(2048)
    assert retr.update_cache(bts) == bts
    assert os.stat(sffdtruck.CONSTS.csv_cache_file).st_size == len(bts)


def test_csv_cache(init_setup):
    utf_str = retr.retrieve(timeout=init_setup["to"], check_update=True)
    assert os.path.exists(sffdtruck.CONSTS.csv_cache_file)
    assert os.stat(sffdtruck.CONSTS.csv_cache_file).st_size == len(utf_str[0])
