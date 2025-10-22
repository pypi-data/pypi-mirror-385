# Hedron

[![Tests](https://github.com/eddiethedean/hedron/actions/workflows/test.yml/badge.svg)](https://github.com/eddiethedean/hedron/actions/workflows/test.yml)
[![Lint](https://github.com/eddiethedean/hedron/actions/workflows/lint.yml/badge.svg)](https://github.com/eddiethedean/hedron/actions/workflows/lint.yml)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python package for geolocation clustering analysis using geohash-based spatial indexing.

## Overview

Hedron provides tools for analyzing and clustering coordinate data based on geographic proximity. It uses geohash encoding to efficiently group locations and identify patterns such as:

- Spatial clusters of coordinates
- Colocation events (multiple IDs at the same location)
- Temporal colocation (multiple IDs at the same location on the same day)

## Features

- **Geohash-based clustering**: Efficient spatial grouping using configurable precision
- **Colocation detection**: Identify when multiple entities appear at the same location
- **Temporal analysis**: Find colocation events on specific days
- **Visualization**: Built-in map plotting and heat map generation with OpenStreetMap tiles
- **Pandas integration**: Works seamlessly with pandas DataFrames
- **Type hints**: Full type annotation support for better IDE integration
- **Export capabilities**: Save clusters to Excel (with separate sheets) or CSV
- **Comprehensive examples**: 5 Jupyter notebooks with working visualizations

## Installation

### From PyPI (recommended)

```bash
pip install hedron
```

**Note**: For visualization features to work, Pillow version 9.x is required (automatically installed). If you have Pillow 10+ already installed, the maps may not render correctly.

### From source

```bash
git clone https://github.com/eddiethedean/hedron.git
cd hedron
pip install -e .
```

### Development installation

```bash
pip install -e ".[dev]"
pre-commit install
```

## Examples

Check out the [`examples/`](https://github.com/eddiethedean/hedron/tree/master/examples) directory for complete Jupyter notebooks with working code:

- **[01_basic_clustering.ipynb](https://github.com/eddiethedean/hedron/blob/master/examples/01_basic_clustering.ipynb)** - Introduction to clustering
- **[02_colocation_analysis.ipynb](https://github.com/eddiethedean/hedron/blob/master/examples/02_colocation_analysis.ipynb)** - Finding when entities meet
- **[03_temporal_analysis.ipynb](https://github.com/eddiethedean/hedron/blob/master/examples/03_temporal_analysis.ipynb)** - Day-based colocation detection
- **[04_advanced_usage.ipynb](https://github.com/eddiethedean/hedron/blob/master/examples/04_advanced_usage.ipynb)** - Performance and large datasets
- **[05_visualization_and_maps.ipynb](https://github.com/eddiethedean/hedron/blob/master/examples/05_visualization_and_maps.ipynb)** - Map generation with examples

All notebooks include executed outputs and are ready to run!

## Quick Start

```python
import pandas as pd
import hedron as hd

# Create a DataFrame with coordinate data
data = pd.DataFrame({
    'ID': ['a', 'b', 'c', 'd', 'e', 'f'],
    'Date': pd.to_datetime([
        'Dec 6, 2019 2:27:45 PM',
        'Dec 6, 2019 2:27:45 PM',
        'Dec 8, 2019 2:27:45 PM',
        'Dec 8, 2019 2:27:45 PM',
        'Dec 10, 2019 2:27:45 PM',
        'Dec 11, 2019 2:27:45 PM'
    ]),
    'Latitude': [29.4259671, 29.42525, 29.4237056, 29.423606, 29.4239835, 29.4239835],
    'Longitude': [-98.4861419, -98.4860167, -98.4868973, -98.4860462, -98.4851705, -98.4851705]
})

# Create a Cluster object
cluster = hd.Cluster(
    data,
    lat_header='Latitude',
    lon_header='Longitude',
    date_time_header='Date',
    id_header='ID'
)

# Create spatial clusters (precision 7 ≈ 150m accuracy)
clusters = cluster.make_clusters(digits=7)
print(f"Found {len(clusters)} clusters")

# Get only colocations (multiple IDs in same location)
colocations = clusters.colocation_clusters()
print(f"Found {len(colocations)} colocation clusters")

# Visualize clusters on a map
image = cluster.plot(size=(800, 500))
image.save('cluster_map.png')  # Save as PNG
# or display in Jupyter: display(image)

# Create a heat map (shows density: blue=low, red=high)
heat_map = clusters.plot_heat(precision=6)
heat_map.save('heatmap.png')

# Export to Excel (each cluster = one sheet)
clusters.to_xlsx('analysis_results.xlsx')
```

## Geohash Precision Guide

The `digits` parameter controls clustering granularity:

| Digits | Lat/Lon Accuracy | Approximate Size |
|--------|------------------|------------------|
| 4      | ±2.4 km          | Large neighborhood |
| 5      | ±610 m           | Neighborhood |
| 6      | ±76 m            | Street block |
| 7      | ±19 m            | Building |
| 8      | ±2.4 m           | Room |

## API Reference

### Cluster Class

The main class for working with coordinate data.

```python
cluster = Cluster(
    df,                    # pandas DataFrame
    lat_header,            # Latitude column name
    lon_header,            # Longitude column name
    date_time_header,      # Datetime column name
    id_header,             # ID column name
    colors=None            # Optional color mapping for IDs
)
```

#### Methods

- `make_clusters(digits)` - Create spatial clusters by geohash
- `colocation_clusters(digits)` - Create clusters with multiple IDs
- `day_colocation_cluster()` - Get colocations on same day
- `day_colocation_clusters()` - Get separate clusters per day
- `plot(size=(800, 500))` - Visualize cluster on a map

#### Properties

- `lats` - Latitude values as Series
- `lons` - Longitude values as Series
- `ids` - ID values as Series
- `dates` - Datetime values as Series
- `days` - Date values as Series

### SuperCluster Class

Container for multiple Cluster objects.

```python
super_cluster = SuperCluster(
    clusters_dict,         # Dict of cluster name to Cluster
    colors=None            # Optional color mapping
)
```

#### Methods

- `plot()` - Visualize all clusters on a map
- `plot_heat(precision)` - Create a heat map
- `colocation_clusters()` - Filter to only colocation clusters
- `day_colocation_clusters()` - Get day colocations for each cluster
- `merge()` - Combine all clusters into a single Cluster
- `to_xlsx(filename)` - Save each cluster to Excel sheet

#### Properties

- `lats` - All latitude values
- `lons` - All longitude values
- `ids` - All ID values

## Visualization Examples

Hedron includes powerful visualization capabilities:

```python
# Single cluster map
map_image = cluster.plot(size=(800, 500))
map_image.save('locations.png')

# SuperCluster with geohash boundaries
cluster_map = clusters.plot()

# Density heat map (blue → green → yellow → orange → red)
heat_map = clusters.plot_heat(precision=6)
```

See [`examples/05_visualization_and_maps.ipynb`](https://github.com/eddiethedean/hedron/blob/master/examples/05_visualization_and_maps.ipynb) for working map examples with outputs!

## Use Cases

### Finding Meeting Points

Identify locations where multiple people/devices appear together:

```python
# Find all locations where 2+ IDs appear
colocations = cluster.colocation_clusters(digits=7)

# Further refine to same-day meetings
meetings = colocations.day_colocation_clusters()
```

### Analyzing Movement Patterns

Cluster GPS tracks to find frequently visited areas:

```python
# Group all coordinates into neighborhood-sized clusters
areas = cluster.make_clusters(digits=5)

# Export to Excel for analysis
areas.to_xlsx('movement_patterns.xlsx')
```

### Heat Map Generation

Visualize activity density across a geographic area:

```python
clusters = cluster.make_clusters(digits=6)
heat_map = clusters.plot_heat(precision=5)
heat_map.save('activity_heatmap.png')
```

## Advanced Usage

### Working with Large Datasets

For large datasets, consider:

1. Filtering data by time windows before clustering
2. Using lower precision (fewer digits) for initial analysis
3. Leveraging the built-in caching for repeated analyses

```python
# Filter to specific time period
recent = data[data['Date'] > '2019-12-01']
cluster = hd.Cluster(recent, 'Latitude', 'Longitude', 'Date', 'ID')

# Start with broad clusters
broad = cluster.make_clusters(digits=5)

# Refine specific areas of interest
for name, cluster in broad.items():
    detailed = cluster.make_clusters(digits=7)
    print(f"Area {name}: {len(detailed)} detailed clusters")
```

### Custom Visualization

```python
import staticmaps

# Create custom colored markers
colors = {
    'a': staticmaps.RED,
    'b': staticmaps.BLUE,
    'c': staticmaps.GREEN
}

cluster = hd.Cluster(data, 'Latitude', 'Longitude', 'Date', 'ID', colors=colors)
image = cluster.plot()
```

## Development

### Running Tests

```bash
# Run full test suite
pytest

# With coverage report
pytest --cov=hedron --cov-report=html
```

### Code Quality

```bash
# Format code
black hedron tests

# Lint
ruff check hedron tests

# Type check
mypy hedron --ignore-missing-imports

# Run all checks
pytest && ruff check hedron tests && mypy hedron --ignore-missing-imports
```

### Pre-commit Hooks

```bash
pre-commit install
pre-commit run --all-files
```

### Exploring Examples

```bash
# Launch Jupyter with examples
cd examples
jupyter notebook

# Or open a specific notebook
jupyter notebook 05_visualization_and_maps.ipynb
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with tests
4. Run the test suite and linters
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Requirements

- Python 3.9+
- pandas >= 1.5.0
- pygeodesy >= 21.6.9
- py-staticmaps >= 0.4.0
- range-key-dict >= 1.1.0
- Pillow >= 9.0.0, < 10.0.0 (for visualization compatibility)

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/eddiethedean/hedron/blob/master/LICENSE) file for details.

## Acknowledgments

- Uses [pygeodesy](https://github.com/mrJean1/PyGeodesy) for geohash encoding
- Map rendering via [py-staticmaps](https://github.com/flopp/py-staticmaps)

## Citation

If you use Hedron in your research, please cite:

```bibtex
@software{hedron,
  author = {Matthews, Odos},
  title = {Hedron: Geolocation Clustering Analysis},
  year = {2021},
  url = {https://github.com/eddiethedean/hedron}
}
```

## Support

- Issues: [GitHub Issues](https://github.com/eddiethedean/hedron/issues)
- Email: odosmatthews@gmail.com
