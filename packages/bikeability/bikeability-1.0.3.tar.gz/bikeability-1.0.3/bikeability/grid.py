#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
__author__ = "Simon Nieland, Michael Hardinghaus, María López Díaz"
__copyright__ = (
    "Copyright (c) 2024 Institute of Transport Research, German Aerospace Center"
)
__credits__ = [
    "Simon Nieland",
    "Michael Hardinghaus",
    "Marius Lehne",
    "María López Díaz",
]
__license__ = "MIT"
__version__ = "0.0.2"
__maintainer__ = "Simon Nieland"
__email__ = "Simon.Nieland@dlr.de"
__status__ = "Development"
# =============================================================================
""" Bikeability computes bike-friendliness of specific areas."""
# =============================================================================
import geopandas
import h3
import geopandas as gpd
from shapely.geometry import Polygon
import warnings

with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=DeprecationWarning)


def create_h3_grid(gdf: geopandas.GeoDataFrame, res: int):
    """
    :param gdf: Geometries to use. Should be a GeoDataFrame with polygon geometries.
    :param res: resolution of h3 grid (0-15. see https://h3geo.org/docs/core-library/restable)
    :type res: integer
    :returns: 3h grid for respective region in given resolution
    """
    poly = gdf.to_crs(4326).union_all()
    poly_list = [(i[0], i[1]) for i in list(poly.exterior.coords)]
    h3_poly = h3.LatLngPoly(poly_list)
    hexes = h3.h3shape_to_cells(h3_poly, res=res)
    geoms = []
    for hexa in hexes:
        geoms.append(Polygon(h3.cell_to_boundary(hexa)))
    geodf_poly = gpd.GeoDataFrame(geometry=geoms, crs=4326)
    return geodf_poly
