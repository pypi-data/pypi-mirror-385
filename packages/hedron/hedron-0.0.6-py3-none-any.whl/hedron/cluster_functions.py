"""Functions for clustering coordinate data using geohashes."""

from __future__ import annotations

from functools import lru_cache

import pandas as pd
from pygeodesy import geohash


@lru_cache(maxsize=10000)
def _encode_geohash(lat: float, lon: float, precision: int) -> str:
    """
    Encode a latitude/longitude pair into a geohash with caching.

    Args:
        lat: Latitude coordinate
        lon: Longitude coordinate
        precision: Geohash precision (number of characters)

    Returns:
        Geohash string representation of the coordinate
    """
    return str(geohash.encode(lat, lon, precision))


def calculate_geohashes(lats: pd.Series, lons: pd.Series, precision: int) -> list[str]:
    """
    Calculate geohashes for a series of latitude/longitude pairs.

    Args:
        lats: Series of latitude values
        lons: Series of longitude values
        precision: Geohash precision (number of characters)

    Returns:
        List of geohash strings
    """
    hashes = []
    for lat, lon in zip(lats, lons):
        h = _encode_geohash(float(lat), float(lon), precision)
        hashes.append(h)
    return hashes


def day_colocations_clusters(
    clusters: dict[str, pd.DataFrame], day_header: str, id_header: str
) -> dict[str, pd.DataFrame]:
    """
    Check each cluster for IDs on the same day.

    Args:
        clusters: Dictionary of cluster DataFrames
        day_header: Column name for day information
        id_header: Column name for ID information

    Returns:
        Dictionary of clusters that have colocations on the same day
    """
    out = {}
    for key, df in clusters.items():
        day_co = day_colocations(df, day_header, id_header)
        if len(day_co) > 0:
            out[key] = day_co
    return out


def day_colocations(
    cluster: pd.DataFrame, day_header: str, id_header: str, merge: bool = True
) -> pd.DataFrame | dict[str, pd.DataFrame]:
    """
    Find rows where multiple IDs appear on the same day.

    Args:
        cluster: DataFrame containing cluster data
        day_header: Column name for day information
        id_header: Column name for ID information
        merge: If True, merge all colocations into a single DataFrame

    Returns:
        Either a merged DataFrame or a dictionary of DataFrames by day
    """
    cluster = cluster.copy()
    day_clusters = cluster.groupby(day_header)
    colocated = {key: df for key, df in day_clusters if len(df[id_header].unique()) > 1}

    if len(colocated) == 0:
        return pd.DataFrame()

    # Add back date to each df
    for key, df in colocated.items():
        df[day_header] = [key for _ in range(len(df))]

    if merge:
        # Combine DataFrames
        return pd.concat(colocated.values(), axis=0)
    else:
        return colocated


def cluster_coords(
    df: pd.DataFrame, lat_header: str, lon_header: str, precision: int
) -> dict[str, pd.DataFrame]:
    """
    Cluster coordinates by geohash, keeping only clusters with multiple points.

    Args:
        df: DataFrame containing coordinate data
        lat_header: Column name for latitude
        lon_header: Column name for longitude
        precision: Geohash precision (number of characters)

    Returns:
        Dictionary mapping geohash to cluster DataFrame
    """
    df = df.copy()
    # Make lat,lon hash column
    df["hash"] = calculate_geohashes(df[lat_header], df[lon_header], precision)
    # Make dict with hash:cluster, clusters need more than 1 point to count as a cluster
    return {key: cluster_df for key, cluster_df in df.groupby("hash") if len(cluster_df) > 1}


def colocation_clusters(
    clusters: dict[str, pd.DataFrame], id_header: str
) -> dict[str, pd.DataFrame]:
    """
    Filter clusters to only those with more than one unique ID.

    Args:
        clusters: Dictionary of cluster DataFrames
        id_header: Column name for ID information

    Returns:
        Dictionary of clusters that have multiple unique IDs
    """
    return {key: df for key, df in clusters.items() if len(df[id_header].unique()) > 1}


def colocation_cluster_coords(
    df: pd.DataFrame, lat_header: str, lon_header: str, id_header: str, precision: int
) -> dict[str, pd.DataFrame]:
    """
    Cluster coordinates by geohash, keeping only colocations (multiple unique IDs).

    Args:
        df: DataFrame containing coordinate data
        lat_header: Column name for latitude
        lon_header: Column name for longitude
        id_header: Column name for ID information
        precision: Geohash precision (number of characters)

    Returns:
        Dictionary mapping geohash to colocation cluster DataFrame
    """
    df = df.copy()
    # Make lat,lon hash column
    df["hash"] = calculate_geohashes(df[lat_header], df[lon_header], precision)
    # Make dict with hash:colocation cluster, clusters need more than 1 id to be a colocation cluster
    return {
        key: cluster_df
        for key, cluster_df in df.groupby("hash")
        if len(cluster_df[id_header].unique()) > 1
    }
