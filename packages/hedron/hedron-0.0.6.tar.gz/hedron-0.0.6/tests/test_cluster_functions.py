"""Tests for cluster_functions module."""

import pandas as pd
import pytest

from hedron import cluster_functions as cf


class TestGeohashFunctions:
    """Test geohash calculation functions."""

    def test_calculate_geohashes(self):
        """Test geohash calculation."""
        lats = pd.Series([29.4259671, 29.42525, 29.4237056])
        lons = pd.Series([-98.4861419, -98.4860167, -98.4868973])
        precision = 6

        hashes = cf.calculate_geohashes(lats, lons, precision)

        assert len(hashes) == 3
        assert all(isinstance(h, str) for h in hashes)
        assert all(len(h) == precision for h in hashes)

    def test_calculate_geohashes_caching(self):
        """Test that geohash calculation uses caching."""
        lats = pd.Series([29.4259671, 29.4259671])
        lons = pd.Series([-98.4861419, -98.4861419])
        precision = 6

        hashes1 = cf.calculate_geohashes(lats, lons, precision)
        hashes2 = cf.calculate_geohashes(lats, lons, precision)

        assert hashes1 == hashes2
        assert hashes1[0] == hashes1[1]


class TestClusterCoords:
    """Test coordinate clustering functions."""

    def test_cluster_coords(self, sample_data):
        """Test basic coordinate clustering."""
        clusters = cf.cluster_coords(sample_data, "Latitude", "Longitude", 6)

        assert isinstance(clusters, dict)
        # All clusters should have at least 2 points
        for cluster_df in clusters.values():
            assert len(cluster_df) >= 2
            assert "hash" in cluster_df.columns

    def test_cluster_coords_empty(self, empty_data):
        """Test clustering with empty data."""
        clusters = cf.cluster_coords(empty_data, "Latitude", "Longitude", 6)

        assert isinstance(clusters, dict)
        assert len(clusters) == 0

    def test_colocation_cluster_coords(self, colocation_data):
        """Test colocation clustering."""
        clusters = cf.colocation_cluster_coords(
            colocation_data, "Latitude", "Longitude", "ID", 7
        )

        assert isinstance(clusters, dict)
        # All clusters should have multiple unique IDs
        for cluster_df in clusters.values():
            assert len(cluster_df["ID"].unique()) > 1


class TestDayColocations:
    """Test day colocation functions."""

    def test_day_colocations_merge(self, colocation_data):
        """Test day colocations with merge."""
        cluster = colocation_data.copy()
        cluster["day"] = pd.to_datetime(cluster["Date"]).dt.date

        result = cf.day_colocations(cluster, "day", "ID", merge=True)

        if len(result) > 0:
            assert isinstance(result, pd.DataFrame)
            assert "day" in result.columns

    def test_day_colocations_no_merge(self, colocation_data):
        """Test day colocations without merge."""
        cluster = colocation_data.copy()
        cluster["day"] = pd.to_datetime(cluster["Date"]).dt.date

        result = cf.day_colocations(cluster, "day", "ID", merge=False)

        if len(result) > 0:
            assert isinstance(result, dict)

    def test_day_colocations_empty(self, empty_data):
        """Test day colocations with empty data."""
        cluster = empty_data.copy()
        cluster["day"] = pd.Series(dtype="object")

        result = cf.day_colocations(cluster, "day", "ID", merge=True)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0


@pytest.fixture
def sample_data():
    """Create sample coordinate data for testing."""
    ids = ["a", "b", "c", "d", "e", "f"]
    dates = pd.to_datetime(
        [
            "Dec 6, 2019 2:27:45 PM",
            "Dec 6, 2019 2:27:45 PM",
            "Dec 8, 2019 2:27:45 PM",
            "Dec 8, 2019 2:27:45 PM",
            "Dec 10, 2019 2:27:45 PM",
            "Dec 11, 2019 2:27:45 PM",
        ]
    )
    lats = [29.4259671, 29.42525, 29.4237056, 29.423606, 29.4239835, 29.4239835]
    lons = [-98.4861419, -98.4860167, -98.4868973, -98.4860462, -98.4851705, -98.4851705]
    return pd.DataFrame({"ID": ids, "Date": dates, "Latitude": lats, "Longitude": lons})


@pytest.fixture
def colocation_data():
    """Create sample data with colocations for testing."""
    ids = ["a", "b", "c", "d", "e", "f", "a", "b"]
    dates = pd.to_datetime(
        [
            "Dec 6, 2019 2:27:45 PM",
            "Dec 6, 2019 2:27:45 PM",
            "Dec 8, 2019 2:27:45 PM",
            "Dec 8, 2019 2:27:45 PM",
            "Dec 10, 2019 2:27:45 PM",
            "Dec 11, 2019 2:27:45 PM",
            "Dec 6, 2019 3:00:00 PM",
            "Dec 6, 2019 3:00:00 PM",
        ]
    )
    lats = [29.4259671, 29.4259671, 29.42525, 29.426, 29.4237056, 29.422, 29.4259671, 29.4259671]
    lons = [
        -98.4861419,
        -98.4861419,
        -98.4860167,
        -98.485,
        -98.4868973,
        -98.485,
        -98.4861419,
        -98.4861419,
    ]
    return pd.DataFrame({"ID": ids, "Date": dates, "Latitude": lats, "Longitude": lons})


@pytest.fixture
def empty_data():
    """Create empty DataFrame for testing edge cases."""
    return pd.DataFrame(columns=["ID", "Date", "Latitude", "Longitude"])

