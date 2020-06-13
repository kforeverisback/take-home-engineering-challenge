# -*- coding: utf-8 -*-
import argparse
import csv
import os
import pickle
from io import StringIO

from sffdtruck import CONSTS, __version__, dist_haversine, kdtree
from sffdtruck.retrieve import retrieve, update_cache
from vincenty import vincenty as dist_vincenty


def arg_parser():
    parser = argparse.ArgumentParser("sffdtruck")
    version = "%(prog)s " + __version__
    parser.add_argument(
        "--lat-lon",
        "-l",
        nargs=2,
        dest="lat_lon",
        required=True,
        help="""Specify target (latitude, longitude). Eg. `-l -37.234124 74.812810`""",
    )
    parser.add_argument(
        "--update",
        default=False,
        action="store_true",
        help="""Update existing cache.""",
    )
    parser.add_argument(
        "--timeout", "-t", default=3, type=int, help="""Download timeout."""
    )
    parser.add_argument(
        "--count",
        "-c",
        default=5,
        type=int,
        choices=range(1, 100),
        help="""Number of food truck locations to return.""",
    )
    parser.add_argument(
        "--dist",
        "-d",
        default="haversine",
        choices=["euclidean", "e", "haversine", "h", "vincenty", "v"],
        help="""Distance calculation function""",
    )
    parser.add_argument("--version", "-v", action="version", version=version)
    return parser


def main(args=None):
    args = arg_parser().parse_args(args)

    csv_bytes, is_newer = retrieve(args.update)
    if is_newer:
        # We read CSV and 're-'build KDTree cache
        with StringIO(csv_bytes) as sio:
            entries = [
                kdtree.FTData(d)
                for d in list(csv.DictReader(sio))
                if float(d["Latitude"]) != 0 and float(d["Longitude"]) != 0
            ]
            tree_root = kdtree.FTNode.build_tree(entries, dist_fn=dist_haversine)
            with open(CONSTS.kdtree_cache_file, "wb") as f:
                # Pickle the 'data' dictionary using the highest protocol available.
                pickle.dump(tree_root, f, pickle.HIGHEST_PROTOCOL)
        pass
    else:
        with open(CONSTS.kdtree_cache_file, "rb") as f:
            tree_root = pickle.load(f)

    # Now we have a tree_root
    # Perform the search
    lat_lon = (float(args.lat_lon[0]), float(args.lat_lon[1]))
    res = tree_root.search(lat_lon, k=args.count)
    [print(r) for r in res]
    if args.dist[0] == "h":
        pass
    elif args.dist[0] == "v":
        pass
    else:
        pass


if __name__ == "__main__":
    main()
