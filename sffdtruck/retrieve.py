# -*- coding: utf-8 -*-
import csv
import os
import pickle
import ssl
import sys
import urllib.request as urlr
from datetime import datetime, timedelta
from hashlib import blake2b as hasher
from io import StringIO
from pathlib import Path

from sffdtruck import CONSTS


def download_csv(url=CONSTS.csv_url, timeout=2):
    # c=ssl.create_default_context()
    # c.check_hostname=False
    # c.verify_mode=ssl.CERT_NONE
    # u=urlr.urlopen(url,context=c)
    with urlr.urlopen(url, timeout=timeout) as u:
        return u.read()


def update_cache(csv_bytes):
    if csv_bytes is None:
        return None

    if os.path.exists(CONSTS.csv_cache_file):
        os.remove(CONSTS.csv_cache_file)
    with open(CONSTS.csv_cache_file, "wb") as f:
        f.write(csv_bytes)
    return csv_bytes


# Simple caching
def retrieve(check_update=True, timeout=3):
    """
    Retrieve Data as dict.
    If refresh_data is ``True`` then it will download the data from default URL
    TODO: Otherwise, first it will look for cached data, if not available or it's outdated then it will download
    """
    is_newer = False
    if os.path.exists(CONSTS.csv_cache_file) and os.path.exists(
        CONSTS.kdtree_cache_file
    ):
        with open(CONSTS.csv_cache_file, "rb") as f:
            cached_csv_bytes = f.read()
        cache_time = datetime.fromtimestamp(os.stat(CONSTS.csv_cache_file).st_mtime)
        # If refresh or our db is more than a day old, try update it
        if check_update or cache_time + timedelta(weeks=1) < datetime.now():
            try:
                # If something happened to download
                # We might still want to use
                new_csv_bytes = download_csv(timeout=timeout)
                if (
                    new_csv_bytes is not None
                    or hasher(new_csv_bytes).hexdigest()
                    != hasher(cached_csv_bytes).hexdigest()
                ):
                    csv_bytes = update_cache(new_csv_bytes)
                    is_newer = True
            except urlr.URLError as uerr:
                sys.stderr.write(f"URL Error:{uerr}.\nUsing cached data")
                csv_bytes = cached_csv_bytes
            # If we already have data we might want to make it faster!
        else:
            # Else we will load the KDTree from file
            csv_bytes = cached_csv_bytes
    else:
        csv_bytes = update_cache(download_csv(timeout=timeout))
        is_newer = True

    return (csv_bytes.decode("utf-8"), is_newer)
