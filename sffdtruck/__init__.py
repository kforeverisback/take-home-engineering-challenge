# -*- coding: utf-8 -*-
from pathlib import Path

from .__meta__ import __author__, __version__


class CONSTS:
    csv_url = "https://data.sfgov.org/api/views/rqzj-sfat/rows.csv?accessType=DOWNLOAD"
    cache_dir = str(Path.joinpath(Path.home(), ".cache", "sffdtruck"))
    csv_cache_file = str(
        Path.joinpath(Path.home(), ".cache", "sffdtruck", "cached_csv.csv")
    )
    kdtree_cache_file = str(
        Path.joinpath(Path.home(), ".cache", "sffdtruck", "cached_tree.bin")
    )
