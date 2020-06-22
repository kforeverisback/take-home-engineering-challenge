# Submission
Submitted a Python ( $\geq$ 3.6) module named `sffdtruck`. It can be used from command line interface.
Running the command line would give you {count} number of Food Truck locations along with their name and address.
See [Features](#features) for full list of features

It is a standalone unit which loosely depends on two modules. `harvesine` and `vincenty` for lat/lon distance calculation.
Although, installing these two dep is recommended, those calculations are also included in the source code.
Basic usage:
```bash
$ git clone https://github.com/kforeverisback/take-home-engineering-challenge
$ cd take-home-engineering-challenge
# $ pip3 install -r requirements.txt ## Optional
# Example usage
$ python3 -m sffdtruck --lat-lon 37.7879549596858 -122.397236543731 --count 5 --dist haversine -f json --update
# For full cli documentation
$ python3 -m sffdtruck --help
usage: sffdtruck [-h] --lat-lon LAT_LON LAT_LON [--update] [--timeout TIMEOUT]
                 [--count COUNT] [--radius RADIUS]
                 [--dist {euclidean,e,haversine,h,vincenty,v}]
                 [--format {csv,json,plain}] [--version]

optional arguments:
  -h, --help            show this help message and exit
  --lat-lon LAT_LON LAT_LON, -l LAT_LON LAT_LON
                        Specify target (latitude, longitude) point. Eg. `-l 37.78795 -122.3972`
  --update              Update existing cache.
  --timeout TIMEOUT, -t TIMEOUT
                        Download timeoutz.
  --count COUNT, -c COUNT
                        Number of locations to return.
  --radius RADIUS, -r RADIUS
                        Return results within {radius} Miles from the point.
  --dist {euclidean,e,haversine,h,vincenty,v}, -d {euclidean,e,haversine,h,vincenty,v}
                        Distance calculation function
  --format {csv,json,plain}, -f {csv,json,plain}
                        Output format (shown in closest-first order)
  --version, -v         show program's version number and exit
```

## Features
- Uses Kd-Tree to generate 2d-BST
  - KD-tree is widely used for fast spatial data store and search
- Downloads the CSV from original URL
- Configurable number of outputs
- Configurable output format
  - JSON, CSV, PlainText
- Caching of CSV and Tree
  - Hash calculation matching with existing
  - Uses cached CSV and tree data (binary)
  - Faster search the second time since only cache
  - Updates the cache if more than a week old
  - Cache can be updated manually from cli
- Radius search functionality
- Configurable distance function selection

## Usage
### Find 5 food trucks around a lat/lon
```bash
python3 -m sffdtruck --lat-lon 37.7879549596858 -122.397236543731
python3 -m sffdtruck -l 37.7879549596858 -122.397236543731
```
PS: It will generate cache at `$HOME/.cache/sffdtruck`

### Find 5 food trucks around a lat/lon with vincenty distance
```bash
python3 -m sffdtruck -l 37.7879549596858 -122.397236543731 --dist vincenty
python3 -m sffdtruck -l 37.7879549596858 -122.397236543731 -d v
```

### Find 10 food trucks around a lat/lon with vincenty distance, show in json format
```bash
python3 -m sffdtruck -l 37.7879549596858 -122.397236543731 --dist vincenty --count 10 --format json
```

### Find 10 food trucks around a lat/lon with harvesine distance in a `.1` mile radius, show in csv format
```bash
python3 -m sffdtruck -l 37.7879549596858 -122.397236543731 -d harvesine -c 10 -f json -r .1
```

### Update the cache and find 10 food trucks around a lat/lon
```bash
python3 -m sffdtruck -l 37.7879549596858 -122.397236543731 -c 10 --update
```

## Implementation

## TODO (Improvements)
- Implement R-Tree with intelligent clustering/grouping. Kd-Tree is fast, but if we want to do more intelligent search with grouping/clustering we should consider R-Tree implementation
- CSV Validation. One of the core features I'd implement first is the CSV validator. With CSV validation many of CSV reading and receiving error would be eliminated.
- Better exception handling. Given time, it'd implement better exception handling and with better OOP structure. Currently only the KDTree follows somewhat OOP. Most of the program is functional
- Implement better distance function integrating OpenMap/Google/Bing map, to find exact street distance. Currently, we are calculating direct spherical point to point distance. But in reality, the point to point distance is the same as street distance.
- Implement a `setup.py` which will install it as an pip3 module, which can be run from any terminal/powershell
- Turn it into a proper module with functions and classes, so that it can be used in WebAPIs
