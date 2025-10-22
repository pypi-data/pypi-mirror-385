"""Visualization functions for plotting clusters and heat maps."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np
import pandas as pd
import pygeodesy
import staticmaps
from range_key_dict import RangeKeyDict

from .cluster_functions import calculate_geohashes

if TYPE_CHECKING:
    from .cluster import Cluster, SuperCluster

tp = staticmaps.tile_provider_OSM
TRED = staticmaps.Color(255, 0, 0, 100)
RED = staticmaps.RED
TYELLOW = staticmaps.Color(255, 255, 0, 100)
YELLOW = staticmaps.YELLOW
TGREEN = staticmaps.Color(0, 255, 0, 100)
GREEN = staticmaps.GREEN
TBLUE = staticmaps.Color(0, 0, 255, 100)
BLUE = staticmaps.BLUE


class Context(staticmaps.Context):
    """Extended Context class with additional methods for cluster visualization."""

    def add_hash_poly(
        self, h: str, fill_color: staticmaps.Color, width: int, color: staticmaps.Color
    ) -> None:
        """
        Add a geohash polygon to the map.

        Args:
            h: Geohash string
            fill_color: Color to fill the polygon
            width: Border width
            color: Border color
        """
        self.add_object(
            staticmaps.Area(
                make_hash_poly_points(h), fill_color=fill_color, width=width, color=color
            )
        )

    def add_neighbor_hash_polys(
        self, h: str, fill_color: staticmaps.Color, width: int, color: staticmaps.Color
    ) -> None:
        """
        Add neighboring geohash polygons to the map.

        Args:
            h: Central geohash string
            fill_color: Color to fill the polygons
            width: Border width
            color: Border color
        """
        hashes = pygeodesy.geohash.neighbors(h)
        for n in hashes.values():
            self.add_object(
                staticmaps.Area(
                    make_hash_poly_points(n), fill_color=fill_color, width=width, color=color
                )
            )

    def add_cluster(
        self,
        cluster: Cluster,
        size: int = 6,
        color: staticmaps.Color | None = None,
        fill_color: staticmaps.Color | None = None,
        width: int = 2,
        colors: dict[str, staticmaps.Color] | None = None,
    ) -> None:
        """
        Add cluster points to the map.

        Args:
            cluster: Cluster object to visualize
            size: Size of marker points
            color: Default color for markers
            fill_color: Fill color for markers
            width: Border width
            colors: Dictionary mapping IDs to colors
        """
        for lat, lon, id_val, _day in zip(cluster.lats, cluster.lons, cluster.ids, cluster.days):
            if colors is not None:
                color = colors[id_val]
            point = staticmaps.create_latlng(lat, lon)
            self.add_object(staticmaps.Marker(point, color=color, size=size))

    def add_heat_hashes(self, lats: list[float], lons: list[float], precision: int) -> None:
        """
        Add heat map visualization using geohashes.

        Args:
            lats: List of latitude values
            lons: List of longitude values
            precision: Geohash precision
        """
        hashes = calculate_geohashes(lats, lons, precision)
        sr = pd.Series(hashes, name="hashes")
        counts = dict(sr.value_counts())
        colors = density_colors(list(counts.values()))
        for h, count in counts.items():
            c = colors[count]
            self.add_hash_poly(h, c, 1, staticmaps.TRANSPARENT)


def plot_heat_hashes(
    lats: list[float],
    lons: list[float],
    precision: int,
    tileprovider: staticmaps.TileProvider = tp,
    size: tuple[int, int] = (800, 500),
) -> Any:
    """
    Plot a heat map of coordinate density using geohashes.

    Args:
        lats: List of latitude values
        lons: List of longitude values
        precision: Geohash precision
        tileprovider: Map tile provider
        size: Output image size (width, height)

    Returns:
        PIL Image of the heat map
    """
    context = Context()
    context.set_tile_provider(tileprovider)
    context.add_heat_hashes(lats, lons, precision)
    return context.render_pillow(*size)


def density_colors(
    counts: list[int], transparency: int = 150
) -> RangeKeyDict[tuple[float, float], staticmaps.Color]:
    """
    Generate color mapping based on density counts.

    Args:
        counts: List of count values
        transparency: Alpha value for colors (0-255)

    Returns:
        RangeKeyDict mapping count ranges to colors
    """
    RED = staticmaps.Color(255, 0, 0, transparency)
    ORANGE = staticmaps.Color(255, 128, 0, transparency)
    YELLOW = staticmaps.Color(255, 255, 0, transparency)
    GREEN = staticmaps.Color(0, 255, 0, transparency)
    BLUE = staticmaps.Color(0, 0, 255, transparency)
    colors = [BLUE, GREEN, YELLOW, ORANGE, RED]
    counts = [n for n in counts if n > 0]
    chunks = len(colors)
    lowest = min(counts)
    highest = max(counts)

    if len(set(counts)) == 1:
        ranges = [(lowest, highest + 0.1)]
        return RangeKeyDict(dict(zip(ranges, colors)))

    chunk_size = (highest - lowest) / chunks
    previous = None
    ranges = []
    for i in np.arange(lowest, highest + 0.1, chunk_size):
        if previous is not None:
            ranges.append((previous, i))
        previous = i
    ranges[-1] = ranges[-1][0], ranges[-1][1] + 0.1
    return RangeKeyDict(dict(zip(ranges, colors)))


def plot_cluster(
    cluster: Cluster,
    tileprovider: staticmaps.TileProvider = tp,
    size: tuple[int, int] = (800, 500),
) -> Any:
    """
    Plot a single cluster on a map.

    Args:
        cluster: Cluster object to visualize
        tileprovider: Map tile provider
        size: Output image size (width, height)

    Returns:
        PIL Image of the cluster
    """
    context = Context()
    context.set_tile_provider(tileprovider)
    context.add_cluster(
        cluster, fill_color=staticmaps.parse_color("#00FF003F"), width=2, color=staticmaps.BLUE
    )
    return context.render_pillow(*size)


def plot_super_cluster(
    hashes: list[str],
    tileprovider: staticmaps.TileProvider = tp,
    size: tuple[int, int] = (800, 500),
) -> Any:
    """
    Plot multiple geohash regions on a map.

    Args:
        hashes: List of geohash strings
        tileprovider: Map tile provider
        size: Output image size (width, height)

    Returns:
        PIL Image of the super cluster
    """
    context = Context()
    context.set_tile_provider(tileprovider)
    for h in hashes:
        context.add_hash_poly(
            h, fill_color=staticmaps.parse_color("#00FF003F"), width=2, color=staticmaps.BLUE
        )
    return context.render_pillow(*size)


def plot_heat_map(
    super_cluster: SuperCluster,
    p: int,
    tileprovider: staticmaps.TileProvider = tp,
    size: tuple[int, int] = (800, 500),
) -> Any:
    """
    Plot a heat map from a SuperCluster.

    Args:
        super_cluster: SuperCluster object to visualize
        p: Geohash precision
        tileprovider: Map tile provider
        size: Output image size (width, height)

    Returns:
        PIL Image of the heat map
    """
    context = Context()
    context.set_tile_provider(tileprovider)
    lats, lons = super_cluster.lats, super_cluster.lons
    context.add_heat_hashes(lats, lons, p)
    return context.render_pillow(*size)


def make_hash_poly_points(h: str) -> list[staticmaps.LatLng]:
    """
    Create polygon points for a geohash boundary.

    Args:
        h: Geohash string

    Returns:
        List of LatLng points forming a polygon
    """
    b = pygeodesy.geohash.bounds(h)
    sw = b.latS, b.lonW
    nw = b.latN, b.lonW
    ne = b.latN, b.lonE
    se = b.latS, b.lonE
    polygon = [sw, nw, ne, se, sw]
    return [staticmaps.create_latlng(lat, lon) for lat, lon in polygon]


def plot_hash(
    h: str, tileprovider: staticmaps.TileProvider = tp, size: tuple[int, int] = (800, 500)
) -> Any:
    """
    Plot a single geohash region.

    Args:
        h: Geohash string
        tileprovider: Map tile provider
        size: Output image size (width, height)

    Returns:
        PIL Image of the geohash
    """
    context = Context()
    context.set_tile_provider(tileprovider)
    context.add_hash_poly(
        h, fill_color=staticmaps.parse_color("#00FF003F"), width=2, color=staticmaps.BLUE
    )
    return context.render_pillow(*size)


def plot_neighbors(
    h: str, tileprovider: staticmaps.TileProvider = tp, size: tuple[int, int] = (800, 500)
) -> Any:
    """
    Plot neighboring geohash regions.

    Args:
        h: Central geohash string
        tileprovider: Map tile provider
        size: Output image size (width, height)

    Returns:
        PIL Image of the neighboring geohashes
    """
    context = Context()
    context.set_tile_provider(tileprovider)
    context.add_neighbor_hash_polys(
        h, fill_color=staticmaps.parse_color("#00FF003F"), width=2, color=staticmaps.BLUE
    )
    return context.render_pillow(*size)


def plot_nine(
    h: str, tileprovider: staticmaps.TileProvider = tp, size: tuple[int, int] = (800, 500)
) -> Any:
    """
    Plot a geohash and its neighbors (nine total).

    Args:
        h: Central geohash string
        tileprovider: Map tile provider
        size: Output image size (width, height)

    Returns:
        PIL Image of the nine geohashes
    """
    context = Context()
    context.set_tile_provider(tileprovider)
    context.add_hash_poly(
        h, fill_color=staticmaps.parse_color("#00FF010F"), width=5, color=staticmaps.BLUE
    )
    context.add_neighbor_hash_polys(
        h, fill_color=staticmaps.parse_color("#00FF003F"), width=2, color=staticmaps.BLUE
    )
    return context.render_pillow(*size)
