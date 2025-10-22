"""Main cluster classes for geolocation analysis."""

from __future__ import annotations

from typing import Any

import pandas as pd

from hedron import cluster_functions as cl

from .maps import plot_cluster, plot_heat_map, plot_super_cluster


class Cluster(pd.DataFrame):
    """
    Holds a pandas DataFrame with coordinate data for clustering analysis.

    This class extends pandas DataFrame to provide specialized methods for
    geolocation clustering and visualization.

    Attributes:
        lat_header: Name of the latitude column
        lon_header: Name of the longitude column
        id_header: Name of the ID column
        date_time_header: Name of the datetime column
        day_header: Name of the day column (automatically created)
        colors: Optional dictionary mapping IDs to colors for visualization
    """

    def __init__(
        self,
        df: pd.DataFrame,
        lat_header: str,
        lon_header: str,
        date_time_header: str,
        id_header: str,
        colors: dict[str, Any] | None = None,
    ):
        """
        Initialize a Cluster object.

        Args:
            df: DataFrame containing coordinate data
            lat_header: Column name for latitude
            lon_header: Column name for longitude
            date_time_header: Column name for datetime
            id_header: Column name for ID
            colors: Optional dictionary mapping IDs to colors
        """
        pd.DataFrame.__init__(self, df)
        self.lat_header = lat_header
        self.lon_header = lon_header
        self.id_header = id_header
        self.date_time_header = date_time_header
        self.day_header = "day"
        self.colors = colors
        if len(df) == 0:
            return

        # Try to convert columns to correct data types
        self[lat_header] = self[lat_header].astype(float)
        self[lon_header] = self[lon_header].astype(float)
        self[date_time_header] = pd.to_datetime(df[date_time_header])
        self[id_header] = self[id_header].astype(str)
        # Add day column
        self[self.day_header] = self[date_time_header].dt.date

    @property
    def lats(self) -> pd.Series:
        """Return the latitude column as a Series."""
        return self[self.lat_header]

    @property
    def lons(self) -> pd.Series:
        """Return the longitude column as a Series."""
        return self[self.lon_header]

    @property
    def ids(self) -> pd.Series:
        """Return the ID column as a Series."""
        return self[self.id_header]

    @property
    def dates(self) -> pd.Series:
        """Return the datetime column as a Series."""
        return self[self.date_time_header]

    @property
    def days(self) -> pd.Series:
        """Return the day column as a Series."""
        return self[self.day_header]

    def plot(self, size: tuple = (800, 500)) -> Any:
        """
        Plot the cluster on a map.

        Args:
            size: Output image size (width, height)

        Returns:
            PIL Image of the plotted cluster
        """
        return plot_cluster(self, size=size)

    def make_clusters(self, digits: int) -> SuperCluster:
        """
        Create clusters based on geohash precision.

        Args:
            digits: Geohash precision (number of characters)

        Returns:
            SuperCluster containing all clusters
        """
        if len(self) == 0:
            return SuperCluster({})
        return convert_dict_to_super(
            self,
            cl.cluster_coords(self, self.lat_header, self.lon_header, digits),
            colors=self.colors,
        )

    def colocation_clusters(self, digits: int) -> SuperCluster:
        """
        Create colocation clusters (multiple unique IDs in same location).

        Args:
            digits: Geohash precision (number of characters)

        Returns:
            SuperCluster containing only colocation clusters
        """
        if len(self) == 0:
            return SuperCluster({})
        return convert_dict_to_super(
            self,
            cl.colocation_cluster_coords(
                self, self.lat_header, self.lon_header, self.id_header, digits
            ),
            colors=self.colors,
        )

    def day_colocation_cluster(self) -> Cluster:
        """
        Get cluster of colocations on the same day.

        Returns:
            Cluster containing only day colocations
        """
        if len(self) == 0:
            return self
        return Cluster(
            cl.day_colocations(self, self.day_header, self.id_header),
            self.lat_header,
            self.lon_header,
            self.date_time_header,
            self.id_header,
            colors=self.colors,
        )

    def day_colocation_clusters(self) -> SuperCluster:
        """
        Get separate clusters for each day's colocations.

        Returns:
            SuperCluster with one cluster per day
        """
        if len(self) == 0:
            return SuperCluster({})
        return convert_dict_to_super(
            self,
            cl.day_colocations(self, self.day_header, self.id_header, merge=False),
            colors=self.colors,
        )


class SuperCluster(dict):
    """
    Holds multiple Cluster Objects in a dictionary structure.

    Keys are typically geohash strings or day identifiers, and values are Cluster objects.

    Attributes:
        colors: Optional dictionary mapping IDs to colors for visualization
    """

    def __init__(
        self, iterable: dict[str, Cluster], colors: dict[str, Any] | None = None
    ):
        """
        Initialize a SuperCluster.

        Args:
            iterable: Dictionary of cluster name to Cluster object
            colors: Optional dictionary mapping IDs to colors
        """
        dict.__init__(self, iterable)
        self.colors = colors

    def plot(self) -> Any:
        """
        Plot all clusters on a map.

        Returns:
            PIL Image of the plotted super cluster
        """
        return plot_super_cluster(list(self.keys()))

    def plot_heat(self, p: int) -> Any:
        """
        Plot a heat map of cluster density.

        Args:
            p: Geohash precision for heat map

        Returns:
            PIL Image of the heat map
        """
        return plot_heat_map(self, p)

    def clusters(self) -> list[Cluster]:
        """
        Get a list of all clusters.

        Returns:
            List of Cluster objects
        """
        return list(self.values())

    def names(self) -> list[str]:
        """
        Get a list of all cluster names.

        Returns:
            List of cluster name strings
        """
        return list(self.keys())

    def colocation_clusters(self) -> SuperCluster:
        """
        Filter to only clusters with multiple unique IDs.

        Returns:
            SuperCluster containing only colocation clusters
        """
        if len(self) == 0:
            return self
        return SuperCluster(
            {
                key: cluster
                for key, cluster in self.items()
                if len(cluster[cluster.id_header].unique()) > 1
            }
        )

    def merge(self) -> Cluster:
        """
        Merge all clusters into a single Cluster DataFrame.

        Returns:
            Single Cluster containing all data from all clusters
        """
        if len(self) == 0:
            return Cluster(
                pd.DataFrame(), lat_header="", lon_header="", date_time_header="", id_header=""
            )

        # Get the first cluster to extract headers
        first_cluster = next(iter(self.values()))

        # Combine all cluster DataFrames
        combined_df = pd.concat(self.values(), axis=0, ignore_index=True)

        return Cluster(
            combined_df,
            first_cluster.lat_header,
            first_cluster.lon_header,
            first_cluster.date_time_header,
            first_cluster.id_header,
            colors=self.colors,
        )

    def to_xlsx(self, filename: str) -> None:
        """
        Save each cluster to a separate sheet in an Excel file.

        Args:
            filename: Path to the output Excel file
        """
        if len(self) == 0:
            print("No clusters to save")
            return

        with pd.ExcelWriter(filename, engine="openpyxl") as writer:
            for name, cluster in self.items():
                # Sanitize sheet name (Excel has 31 char limit and special char restrictions)
                sheet_name = str(name)[:31]
                # Remove invalid characters for Excel sheet names
                for char in [":", "\\", "/", "?", "*", "[", "]"]:
                    sheet_name = sheet_name.replace(char, "_")

                cluster.to_excel(writer, sheet_name=sheet_name, index=False)

    def day_colocation_clusters(self) -> SuperCluster:
        """
        Get day colocation clusters for each cluster.

        Returns:
            SuperCluster containing only day colocation clusters
        """
        if len(self) == 0:
            return self
        day_clusters = {}
        for key, cluster in self.items():
            c = cluster.day_colocation_cluster()
            if len(c) > 0:
                day_clusters[key] = c
        return SuperCluster(day_clusters)

    @property
    def ids(self) -> list[str]:
        """
        Get all IDs from all clusters.

        Returns:
            List of all ID values
        """
        out = []
        for c in self.values():
            out.extend(list(c.ids))
        return out

    @property
    def lats(self) -> list[float]:
        """
        Get all latitudes from all clusters.

        Returns:
            List of all latitude values
        """
        out = []
        for c in self.values():
            out.extend(list(c.lats))
        return out

    @property
    def lons(self) -> list[float]:
        """
        Get all longitudes from all clusters.

        Returns:
            List of all longitude values
        """
        out = []
        for c in self.values():
            out.extend(list(c.lons))
        return out


def convert_dict_to_super(
    cluster: Cluster, d: dict[str, pd.DataFrame], colors: dict[str, Any] | None = None
) -> SuperCluster:
    """
    Convert a dictionary of DataFrames to a SuperCluster.

    Args:
        cluster: Original cluster (used to extract headers)
        d: Dictionary of cluster DataFrames
        colors: Optional dictionary mapping IDs to colors

    Returns:
        SuperCluster containing the converted clusters
    """
    if len(d) == 0:
        return SuperCluster({}, colors=colors)
    return SuperCluster(
        {
            key: Cluster(
                df,
                cluster.lat_header,
                cluster.lon_header,
                cluster.date_time_header,
                cluster.id_header,
                colors=colors,
            )
            for key, df in d.items()
        },
        colors=colors,
    )
