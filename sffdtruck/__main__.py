# -*- coding: utf-8 -*-
import argparse
import csv
import json
import os
import pickle
from io import StringIO

from sffdtruck import CONSTS, __version__, kdtree
from sffdtruck.retrieve import retrieve

# Importing 3rd party distance calculation packages
# If not downloaded, we'll use local version.
# We've added a local version to make
try:
    from vincenty import vincenty as dist_vincenty
except ImportError:
    from sffdtruck.external.vincenty import vincenty as dist_vincenty

try:
    from haversine import haversine as dist_haversine
except ImportError:
    from sffdtruck.external.haversine import haversine as dist_haversine


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
        "--count", "-c", default=5, type=int, help="""Number of locations to return.""",
    )
    parser.add_argument(
        "--radius",
        "-r",
        default=float("Inf"),
        type=float,
        help="""Return results within {radius} Miles.""",
    )
    parser.add_argument(
        "--dist",
        "-d",
        default="haversine",
        choices=["euclidean", "e", "haversine", "h", "vincenty", "v"],
        help="""Distance calculation function""",
    )
    parser.add_argument(
        "--format",
        "-f",
        default="plain",
        choices=["csv", "json", "plain"],
        help="""Output format (shown in closest-first order)""",
    )
    parser.add_argument("--version", "-v", action="version", version=version)
    return parser


def get_dist_fn(dist_type, radius_miles=float("Inf")):
    def radius_dist(p1, p2, dist_fn):
        d = dist_fn(p1, p2)
        # Convert to km
        if d <= radius_miles * 1.609344:
            return d
        else:
            return float("Inf")

    if dist_type[0] == "h":
        dist_fn = dist_haversine
    elif dist_type[0] == "v":
        dist_fn = dist_vincenty
    else:
        dist_fn = kdtree.dist_sq

    if radius_miles != float("Inf"):
        if dist_type[0] == "e":
            print(
                "Euclidean lat/lon distance is not a real distance. Use Haversine or Vincenty distance for radius search\n"
            )
        else:
            return lambda p1, p2: radius_dist(p1, p2, dist_fn)

    return dist_fn


def get_output(out_type, input_nodes):
    if input_nodes is None or len(input_nodes) == 0:
        return "Nothing was found in the search!!"

    capture = ["Applicant", "Address", "FacilityType", "FoodItems"]
    console_format = [
        "Food Truck Name : {}",
        "Address         : {}",
        "Truck Type      : {}",
        "Available Items : {}",
        "Location        : {}",
    ]
    out = None
    if out_type[0] == "c":
        header = ",".join(capture) + ",Location\n"
        with StringIO() as sio:
            sio.writelines(header)
            for inode in input_nodes:
                sio.writelines(
                    [
                        ",".join([inode.ft_data.data[c] for c in capture]),
                        f',{inode.ft_data.data["Location"]}',
                        "\n",
                    ]
                )
            out = sio.getvalue()
    elif out_type[0] == "j":
        out = {
            "food_trucks": [
                {
                    **{c: inode.ft_data.data[c] for c in capture},
                    **{"Location": inode.ft_data.latlon},
                }
                for inode in input_nodes
            ]
        }
        out = json.dumps(out, indent=2)
    else:
        with StringIO() as sio:
            sio.writelines("----(Closest)---- \n")
            for inode in input_nodes:
                form_val = [inode.ft_data.data[c] for c in capture]
                form_val.append(inode.ft_data.latlon)
                sio.writelines("\n".join(console_format).format(*form_val))
                sio.writelines("\n-----------------\n")
            out = sio.getvalue()

    return out


def main(args=None):
    args = arg_parser().parse_args(args)

    csv_bytes, is_newer = retrieve(check_update=args.update, timeout=args.timeout)
    if is_newer:
        # We read CSV and 're-'build KDTree cache
        with StringIO(csv_bytes) as sio:
            all_csv_entries = list(csv.DictReader(sio))
            valid_entries = [
                kdtree.FTData(d)
                for d in all_csv_entries
                if float(d["Latitude"]) != 0 and float(d["Longitude"]) != 0
            ]
            if len(all_csv_entries) != len(valid_entries):
                print(
                    f"There were {len(all_csv_entries) - len(valid_entries)} entries with no Lat/Lon values"
                )
            tree_root = kdtree.FTNode.build_tree(valid_entries)
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
    res = tree_root.search(
        lat_lon, k=args.count, dist_fn=get_dist_fn(args.dist[0], args.radius)
    )

    # s=json.dumps({'output':[r.ft_data.to_json() for r in res]}, indent=2)
    # for r in res:
    print(get_output(args.format, res))


if __name__ == "__main__":
    main()
