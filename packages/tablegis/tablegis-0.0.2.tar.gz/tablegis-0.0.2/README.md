# tablegis

[English](README.md) | [简体中文](README.zh-CN.md)

`tablegis` is a Python package for geospatial data processing and analysis, built on `geopandas`, `pandas`, `shapely`, and `pyproj`. It provides a series of utility functions to simplify common GIS operations.

## Features

*   **Distance Calculation**: Efficiently compute the nearest distance between DataFrames.
*   **Spatial Analysis**: Create buffers (input in meters), Voronoi polygons, Delaunay triangulations, etc.
*   **Format Conversion**: Easily convert between `GeoDataFrame` and formats like `Shapefile`, `KML`, etc.
*   **Coordinate Aggregation**: Provides tools for aggregating coordinate points into grids.
*   **Geometric Operations**: Includes merging polygons, calculating centroids, adding sectors, etc.

## Installation

1、You can install `tablegis` from PyPI:

```bash
pip install tablegis
```

2、Or, install the latest version directly from the GitHub repository:

```bash
pip install git+https://github.com/Non-existent987/tablegis.git
```
3、After downloading the project, it is convenient to import from local files for modification.
```bash
import sys
import pandas as pd
# Find the file path of the tablegis you downloaded.
sys.path.insert(0, r'C:\Users\Administrator\Desktop\tablegis')
# Now it can be imported.
import tablegis as tg
```

## Quick Start

Here is a simple example of how to use `tablegis`:

### 1. Find the nearest point (in df2) for each point in df1 and add its ID, longitude, latitude, and distance.

```python
import pandas as pd
import tablegis as tg

# Create two example DataFrames
df1 = pd.DataFrame({
    'id': [1, 2, 3],
    'lon1': [116.404, 116.405, 116.406],
    'lat1': [39.915, 39.916, 39.917]
})

df2 = pd.DataFrame({
    'id': ['A', 'B', 'C', 'D'],
    'lon2': [116.403, 116.407, 116.404, 116.408],
    'lat2': [39.914, 39.918, 39.916, 39.919]
})

# Calculate the nearest 1 point
result = tg.min_distance_twotable(df1, df2, lon1='lon1', lat1='lat1', lon2='lon2', lat2='lat2', df2_id='id', n=1)
# Calculate the nearest 2 points
result2 = tg.min_distance_twotable(df1, df2, lon1='lon1', lat1='lat1', lon2='lon2', lat2='lat2', df2_id='id', n=2)

print("\nExample result (distance in meters):")
print(result)
print(result2)
```

**Result Display:**

<table>
<tr>
<td style="vertical-align: top; padding-right: 50px;">

**Table df1:**

| id | lon1  | lat1 |
|----|-------|------|
| A  | 114.0 | 30.0 |
| B  | 114.1 | 30.1 |

</td>
<td style="vertical-align: top;">

**Table df2:**

| id | lon2   | lat2  |
|----|--------|-------|
| p1 | 114.01 | 30.01 |
| p2 | 114.05 | 30.05 |
| p3 | 114.12 | 30.12 |

</td>
</tr>
</table>

**Nearest 1 point:**

| id | lon1  | lat1 | nearest1_id | nearest1_lon2 | nearest1_lat2 | nearest1_distance |
|----|-------|------|-------------|---------------|---------------|-------------------|
| A  | 114.0 | 30.0 | p1          | 114.01        | 30.01         | 1470.515926       |
| B  | 114.1 | 30.1 | p3          | 114.12        | 30.12         | 2939.507557       |

**Nearest 2 points:**

| id | lon1  | lat1 | nearest1_id | nearest1_lon2 | nearest1_lat2 | nearest1_distance | nearest2_id | nearest2_lon2 | nearest2_lat2 | nearest2_distance | mean_distance |
|----|-------|------|-------------|---------------|---------------|-------------------|-------------|---------------|---------------|-------------------|---------------|
| A  | 114.0 | 30.0 | p1          | 114.01        | 30.01         | 1470.515926       | p2          | 114.05        | 30.05         | 7351.852775       | 4411.184351   |
| B  | 114.1 | 30.1 | p3          | 114.12        | 30.12         | 2939.507557       | p2          | 114.05        | 30.05         | 7350.037700       | 5144.772629   |

### 2. Find the nearest point for each point within the same table and add its ID, longitude, latitude, and distance.

```python
import pandas as pd
import tablegis as tg

# Create an example DataFrame
df2 = pd.DataFrame({
    'id': ['A', 'B', 'C', 'D'],
    'lon2': [116.403, 116.407, 116.404, 116.408],
    'lat2': [39.914, 39.918, 39.916, 39.919]
})

# Calculate the nearest 1 point
result = tg.min_distance_onetable(df2, 'lon2', 'lat2', idname='id', n=1)
# Calculate the nearest 2 points
result2 = tg.min_distance_onetable(df2, 'lon2', 'lat2', idname='id', n=2)

print("\nExample result (distance in meters):")
print(result)
print(result2)
```

**Result Display:**

**Table df2:**

| id | lon2   | lat2  |
|----|--------|-------|
| p1 | 114.01 | 30.01 |
| p2 | 114.05 | 30.05 |
| p3 | 114.12 | 30.12 |

**Nearest 1 point:**

|    | id | lon2   | lat2  | nearest1_id | nearest1_lon2 | nearest1_lat2 | nearest1_distance |
|---:|----|--------|-------|-------------|---------------|---------------|-------------------|
|  0 | p1 | 114.01 | 30.01 | p2          | 114.05        | 30.05         | 5881.336911       |
|  1 | p2 | 114.05 | 30.05 | p1          | 114.01        | 30.01         | 5881.336911       |
|  2 | p3 | 114.12 | 30.12 | p2          | 114.05        | 30.05         | 10289.545038      |

**Nearest 2 points:**

|    | id | lon2   | lat2  | nearest1_id | nearest1_lon2 | nearest1_lat2 | nearest1_distance | nearest2_id | nearest2_lon2 | nearest2_lat2 | nearest2_distance | mean_distance |
|---:|----|--------|-------|-------------|---------------|---------------|-------------------|-------------|---------------|---------------|-------------------|---------------|
|  0 | p1 | 114.01 | 30.01 | p2          | 114.05        | 30.05         | 5881.336911       | p3          | 114.12        | 30.12         | 16170.880987      | 11026.108949  |
|  1 | p2 | 114.05 | 30.05 | p1          | 114.01        | 30.01         | 5881.336911       | p3          | 114.12        | 30.12         | 10289.545038      | 8085.440974   |
|  2 | p3 | 114.12 | 30.12 | p2          | 114.05        | 30.05         | 10289.545038      | p1          | 114.01        | 30.01         | 16170.880987      | 13230.213012  |

### 3、Replace the longitude and latitude columns in the table with the corresponding values in another coordinate system, and add a new column for longitude and latitude.
```python
import pandas as pd
import tablegis as tg

# Create two sample DataFrames
df = pd.DataFrame({
    'id': ['A', 'B', 'C', 'D'],
    'lon': [116.403, 116.407, 116.404, 116.408],
    'lat': [39.914, 39.918, 39.916, 39.919]
})

# Convert the latitude and longitude in the 84 coordinate system to the latitude and longitude in the web_mercator system.
result = tg.to_lonlat(df,'lon','lat', from_crs="wgs84", to_crs="web_mercator")
print(result)
```
**Result Display:**  
**Added two columns of "web_mercator"：**
| id  | lon      | lat      | web_mercator_lon | web_mercator_lat |
| --- | -------- | -------- | ---------------- | ---------------- |
| A   | 116.403  | 39.914   | 12957922.69      | 4853452.853      |
| B   | 116.407  | 39.918   | 12958367.96      | 4854033.408      |
| C   | 116.404  | 39.916   | 12958034.01      | 4853743.126      |
| D   | 116.408  | 39.919   | 12958479.28      | 4854178.552      |

## Contributing

Contributions in all forms are welcome, including feature requests, bug reports, and code contributions.

## License

This project is licensed under the MIT License.