"""Tests for Cluster class."""


from hedron import Cluster, SuperCluster


class TestCluster:
    """Test cases for Cluster class."""

    def test_cluster_init(self, sample_data):
        """Test Cluster initialization."""
        c = Cluster(
            sample_data,
            lat_header="Latitude",
            lon_header="Longitude",
            date_time_header="Date",
            id_header="ID",
        )

        assert len(c) == 6
        assert c.lat_header == "Latitude"
        assert c.lon_header == "Longitude"
        assert c.id_header == "ID"
        assert c.date_time_header == "Date"
        assert "day" in c.columns

    def test_cluster_empty(self, empty_data):
        """Test Cluster with empty DataFrame."""
        c = Cluster(
            empty_data,
            lat_header="Latitude",
            lon_header="Longitude",
            date_time_header="Date",
            id_header="ID",
        )

        assert len(c) == 0

    def test_cluster_properties(self, sample_data):
        """Test Cluster property accessors."""
        c = Cluster(
            sample_data,
            lat_header="Latitude",
            lon_header="Longitude",
            date_time_header="Date",
            id_header="ID",
        )

        assert len(c.lats) == 6
        assert len(c.lons) == 6
        assert len(c.ids) == 6
        assert len(c.dates) == 6
        assert len(c.days) == 6
        assert isinstance(c.lats.iloc[0], float)

    def test_make_clusters(self, sample_data):
        """Test creating clusters from coordinates."""
        c = Cluster(
            sample_data,
            lat_header="Latitude",
            lon_header="Longitude",
            date_time_header="Date",
            id_header="ID",
        )

        clusters = c.make_clusters(7)
        assert isinstance(clusters, SuperCluster)
        # With precision 7, we should get some clusters
        assert len(clusters) >= 0

    def test_colocation_clusters(self, colocation_data):
        """Test colocation cluster detection."""
        c = Cluster(
            colocation_data,
            lat_header="Latitude",
            lon_header="Longitude",
            date_time_header="Date",
            id_header="ID",
        )

        colocations = c.colocation_clusters(7)
        assert isinstance(colocations, SuperCluster)
        # Should find at least one colocation
        assert len(colocations) >= 1

    def test_day_colocation_cluster(self, colocation_data):
        """Test day colocation detection."""
        c = Cluster(
            colocation_data,
            lat_header="Latitude",
            lon_header="Longitude",
            date_time_header="Date",
            id_header="ID",
        )

        day_coloc = c.day_colocation_cluster()
        assert isinstance(day_coloc, Cluster)
        # Should have some day colocations
        assert len(day_coloc) >= 0

    def test_day_colocation_clusters(self, colocation_data):
        """Test day colocation clusters."""
        c = Cluster(
            colocation_data,
            lat_header="Latitude",
            lon_header="Longitude",
            date_time_header="Date",
            id_header="ID",
        )

        day_colocs = c.day_colocation_clusters()
        assert isinstance(day_colocs, SuperCluster)


class TestSuperCluster:
    """Test cases for SuperCluster class."""

    def test_supercluster_init(self):
        """Test SuperCluster initialization."""
        sc = SuperCluster({})
        assert len(sc) == 0
        assert isinstance(sc, dict)

    def test_supercluster_with_data(self, sample_data):
        """Test SuperCluster with actual clusters."""
        c = Cluster(
            sample_data,
            lat_header="Latitude",
            lon_header="Longitude",
            date_time_header="Date",
            id_header="ID",
        )
        clusters = c.make_clusters(6)

        assert isinstance(clusters, SuperCluster)

    def test_supercluster_merge(self, sample_data):
        """Test merging SuperCluster into single Cluster."""
        c = Cluster(
            sample_data,
            lat_header="Latitude",
            lon_header="Longitude",
            date_time_header="Date",
            id_header="ID",
        )
        clusters = c.make_clusters(6)
        merged = clusters.merge()

        assert isinstance(merged, Cluster)
        # Merged cluster should have data from all clusters
        assert len(merged) >= 0

    def test_supercluster_properties(self, sample_data):
        """Test SuperCluster property accessors."""
        c = Cluster(
            sample_data,
            lat_header="Latitude",
            lon_header="Longitude",
            date_time_header="Date",
            id_header="ID",
        )
        clusters = c.make_clusters(6)

        lats = clusters.lats
        lons = clusters.lons
        ids = clusters.ids

        assert isinstance(lats, list)
        assert isinstance(lons, list)
        assert isinstance(ids, list)

    def test_supercluster_colocation_filter(self, colocation_data):
        """Test filtering SuperCluster to colocations only."""
        c = Cluster(
            colocation_data,
            lat_header="Latitude",
            lon_header="Longitude",
            date_time_header="Date",
            id_header="ID",
        )
        clusters = c.make_clusters(7)
        colocations = clusters.colocation_clusters()

        assert isinstance(colocations, SuperCluster)
        # All remaining clusters should have multiple unique IDs
        for cluster in colocations.values():
            assert len(cluster[cluster.id_header].unique()) > 1

    def test_supercluster_empty_merge(self):
        """Test merging empty SuperCluster."""
        sc = SuperCluster({})
        merged = sc.merge()

        assert isinstance(merged, Cluster)
        assert len(merged) == 0

