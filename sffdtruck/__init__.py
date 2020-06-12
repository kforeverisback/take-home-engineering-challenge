# -*- coding: utf-8 -*-
from pathlib import Path

from diskcache import Cache

from .__meta__ import __author__, __version__


class CONSTS:
    csv_url = "https://data.sfgov.org/api/views/rqzj-sfat/rows.csv?accessType=DOWNLOAD"
    cache_dir = str(Path.joinpath(Path.home(), ".cache", "sffdtruck"))
    csv_cache_file = str(Path.joinpath(Path.home(), ".cache", "sffdtruck", "cache.csv"))


def dist_haversine(p1, p2):
    from math import radians, sin, cos, atan2, sqrt

    """
    Haversine distance of this node and point
    Followed this impl
    https://stackoverflow.com/questions/19412462/getting-distance-between-two-points-based-on-latitude-longitude
    """
    R = 6373.0  # earths avg radius in miles

    ll1 = (radians(p1[0]), radians(p1[1]))
    ll2 = (radians(p2[0]), radians(p2[1]))

    dlon = ll2[1] - ll1[1]
    dlat = ll2[0] - ll1[0]

    a = sin(dlat / 2) ** 2 + cos(ll1[0]) * cos(ll2[0]) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance
