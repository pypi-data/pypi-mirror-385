# Kashima

**Machine Learning Tools for Geotechnical Earthquake Engineering**

Kashima is a Python library designed for seismological and geotechnical applications, providing powerful tools for earthquake event visualization, catalog processing, and interactive mapping. Built on top of Folium, it creates rich web maps for seismic data analysis and visualization.

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## Features

- **Interactive Seismic Maps**: Create stunning Folium-based web maps with earthquake events
- **Multi-Catalog Support**: Integrate data from USGS, Global CMT, ISC, and custom blast catalogs
- **Global CMT Integration**: Download complete moment tensor solutions from the Global CMT Project
  - Fast NDK method: 68,718 events (1962-present) in ~30 seconds
  - Full moment tensor components (Mrr, Mtt, Mpp, Mrt, Mrp, Mtp)
  - Nodal plane parameters (strike, dip, rake)
  - Source parameters (half duration, time shift, scalar moment)
- **Global Cache System**: Efficient catalog management
  - Download catalogs once, reuse across projects
  - Incremental updates for new events
  - Fast parquet storage format
  - Platform-specific cache directories
- **Advanced Visualizations**:
  - Magnitude-scaled event markers with customizable color schemes
  - Seismic moment tensor beachball plots
  - Epicentral distance circles
  - Activity heatmaps
  - Geological fault line overlays
  - Seismic station markers
- **Flexible Configuration**: Configuration-driven design using dataclasses
- **Coordinate System Support**: Handle multiple CRS with automatic transformations
- **Large Dataset Handling**: Efficient processing of large seismic catalogs
- **Mining Applications**: Specialized tools for blast event analysis

## Installation

### From PyPI
```bash
pip install kashima
```

### Development Installation
```bash
git clone https://github.com/averriK/kashima.git
cd kashima
pip install -e .
```

### Dependencies
```bash
pip install pandas numpy folium geopandas pyproj requests branca geopy matplotlib obspy pyarrow
```

All dependencies are automatically installed when using `pip install kashima`.

## Quick Start

### Simple API (Recommended)

The easiest way to create maps using the simplified API:

```python
from kashima.mapper import buildMap, buildCatalog

# Minimal call - only coordinates required
# Creates ./data/ and ./maps/ folders in current directory
result = buildMap(
    latitude=-32.86758,
    longitude=-68.88867
)

print(f"Map: {result['html']}")        # ./maps/index.html
print(f"Events: {result['event_count']}")

# Auto-downloads USGS catalog (basic events)
# Auto-searches for moment tensors in:
#   1. ./data/gcmt-events.csv (download with buildCatalog)
#   2. ./data/isc-events.csv (static file)

# With optional parameters
result = buildMap(
    latitude=-32.86758,
    longitude=-68.88867,
    output_dir="./my_project",  # Custom output folder
    radius_km=500,
    vmin=5.5,
    project_name="My Seismic Study",
    show_beachballs_default=True
)

# Download catalog separately first
catalog = buildCatalog(
    source="usgs",
    outputPath="data/usgs-events.csv",
    latitude=-32.86758,
    longitude=-68.88867,
    maxRadiusKm=500,
    minMagnitude=5.0
)
```

### Advanced Usage (Full Control)

Use the bundled CSVs to generate a map without network access:

```python
from pathlib import Path
import logging

from kashima.mapper import MapConfig, EventConfig, FaultConfig
from kashima.mapper import EventMap

# Paths inside the installed package repo (adjust if needed)
root = Path(__file__).resolve().parent  # if running from a clone, e.g. repo root
examples = root / "examples" / "mapper"
data_dir = examples / "data"
out_dir = examples / "maps"
out_dir.mkdir(parents=True, exist_ok=True)

usgs_csv = data_dir / "usgs-events.csv"
legend_csv = data_dir / "legend.csv"
faults_geojson = data_dir / "gem_active_faults.geojson"

map_cfg = MapConfig(
    project_name="Test Site",
    client="Test Client",
    latitude=-32.86758,
    longitude=-68.88867,
    radius_km=500,
    base_zoom_level=9,
    min_zoom_level=7,
    max_zoom_level=15,
    default_tile_layer="Esri.WorldImagery",
    auto_fit_bounds=False,
    lock_pan=True,
    epicentral_circles=5,
)

event_cfg = EventConfig(
    legend_title="Magnitude (Mw)",
    show_events_default=True,
    show_heatmap_default=False,
    show_beachballs_default=True,
)

fault_cfg = FaultConfig(
    include_faults=True,
    faults_gem_file_path=str(faults_geojson),
)

emap = EventMap(
    map_config=map_cfg,
    event_config=event_cfg,
    events_csv=str(usgs_csv),
    legend_csv=str(legend_csv),
    mandatory_mag_col="mag",
    calculate_distance=True,
    fault_config=fault_cfg,
)

emap.loadData()
folium_map = emap.getMap()

html_out = out_dir / "index.html"
csv_out = out_dir / "epicenters.csv"

folium_map.save(html_out)
emap.events_df.to_csv(csv_out, index=False)
print("✔ Map →", html_out)
print("✔ Data →", csv_out)
```

**Example Scripts:**

*Cache Management:*
- `examples/mapper/00_download_catalogs.py` - Download all catalogs to cache (run once)
- `examples/mapper/00_update_catalogs.py` - Update cached catalogs incrementally

*Catalog Downloads:*
- `examples/mapper/01_usgs_catalog.py` - Download USGS catalog
- `examples/mapper/02_gcmt_catalog.py` - Download GCMT catalog (NDK method)
- `examples/mapper/03_isc_catalog.py` - Download ISC catalog
- `examples/mapper/10_blast_catalog.py` - Process mining blast data

*Map Visualizations:*
- `examples/mapper/04_minimal_map.py` - Minimal map (just coordinates!)
- `examples/mapper/05_map_with_beachballs.py` - Map with focal mechanisms
- `examples/mapper/06_map_with_custom_legend.py` - Map with custom legend
- `examples/mapper/07_map_with_heatmap.py` - Map with activity heatmap
- `examples/mapper/08_map_with_faults.py` - Map with fault line overlays
- `examples/mapper/09_map_advanced_config.py` - Low-level API with MapConfig/EventConfig

## Cache System

Kashima v1.2.0.0 introduces a global cache system to avoid repeated catalog downloads across projects.

### First-Time Setup

After installing kashima, download all catalogs to the global cache once:

```python
from kashima.mapper import downloadAllCatalogs

# Download all catalogs (USGS, GCMT, ISC) to cache
# This may take 5-10 minutes depending on your connection
catalogs = downloadAllCatalogs()

print(f"Cache location: {catalogs['cache_dir']}")
print(f"USGS:  {catalogs['usgs']}")   # 302,777 events (12 MB)
print(f"GCMT:  {catalogs['gcmt']}")   # 68,718 events (3.8 MB)
print(f"ISC:   {catalogs['isc']}")    # 470,230 events (9.7 MB)
```

Or use the provided script:
```bash
cd examples/mapper
python 00_download_catalogs.py
```

### Cache Location

- **macOS**: `~/Library/Caches/kashima/`
- **Linux**: `~/.cache/kashima/`
- **Windows**: `%LOCALAPPDATA%\kashima\Cache\`

### Incremental Updates

Update cached catalogs periodically to get new events:

```python
from kashima.mapper import updateAllCatalogs

# Downloads only new events since last update (fast!)
result = updateAllCatalogs()

print(f"USGS: +{result['usgs_new']} new events")
print(f"GCMT: +{result['gcmt_new']} new events")
print(f"ISC:  +{result['isc_new']} new events")
```

Or use the provided script:
```bash
cd examples/mapper
python 00_update_catalogs.py
```

### Cache Benefits

- **Performance**: Catalogs load in seconds instead of minutes
- **Offline Work**: Build maps without network access (after initial download)
- **Consistency**: Same data across all projects
- **Bandwidth**: Avoid re-downloading hundreds of megabytes
- **Storage**: Efficient parquet format (~25 MB for 841,725 events)

### Force Refresh

To force a complete re-download:

```python
catalogs = downloadAllCatalogs(force_update=True)
```

### Clear Cache

To remove all cached catalogs:

```python
from kashima.mapper import clear_cache

clear_cache()
```

## API Reference

### Simplified API

Kashima provides two high-level functions for common workflows:

#### `buildMap()` - Create Interactive Maps

**Minimal signature** (only coordinates required):
```python
from kashima.mapper import buildMap

result = buildMap(
    latitude: float,              # REQUIRED - Center latitude
    longitude: float,             # REQUIRED - Center longitude
)

# Returns: {"html": str, "csv": str, "event_count": int}
# Creates ./data/ and ./maps/ in current directory
```

**Full signature** with all optional parameters:
```python
result = buildMap(
    latitude: float,                       # REQUIRED
    longitude: float,                      # REQUIRED
    output_dir: str = ".",                 # Output directory
    radius_km: float = 500,                # Search radius
    vmin: float = 4.5,                     # Min magnitude
    vmax: float = 9.0,                     # Max magnitude
    project_name: str = "",
    client: str = "",
    show_events_default: bool = True,
    show_beachballs_default: bool = True,
    show_heatmap_default: bool = False,
    base_zoom_level: int = 9,
    # File paths
    faults_geojson_path: str = None,
    legend_csv_path: str = None,
    station_csv_path: str = None,
    # Visual customization (optional - uses sensible defaults)
    mag_bins: list = None,                 # Magnitude bin edges
    dot_palette: dict = None,              # Colors per magnitude range
    dot_sizes: dict = None,                # Marker sizes per magnitude
    beachball_sizes: dict = None,          # Beachball sizes per magnitude
    color_palette: str = "magma",          # Matplotlib colormap
    scaling_factor: float = 2.0,           # Overall size scaling
    # Many more options available...
)
```

#### `buildCatalog()` - Download Seismic Catalogs

```python
from kashima.mapper import buildCatalog

result = buildCatalog(
    source: str,                  # "usgs", "gcmt", or "blast"
    outputPath: str,              # Where to save CSV
    latitude: float = None,       # Center lat (optional)
    longitude: float = None,      # Center lon (optional)
    maxRadiusKm: float = None,    # Search radius (optional)
    minMagnitude: float = 4.5,
    startTime: str = None,        # "YYYY-MM-DD" format
    endTime: str = None,          # "YYYY-MM-DD" format
    eventType: str = "earthquake"
)

# Returns: {"csv": str, "event_count": int, "source": str}

# Example with Global CMT:
result = buildCatalog(
    source="gcmt",
    outputPath="data/gcmt-events.csv",
    latitude=-35.6,
    longitude=-73.25,
    maxRadiusKm=500,
    minMagnitude=5.0,
    startTime="2020-01-01",
    endTime="2020-12-31"
)
```

### Advanced Usage

For full control over configurations, use the low-level API:

### Basic Earthquake Map

```python
from kashima.mapper import EventMap, MapConfig, EventConfig, USGSCatalog
from datetime import datetime, timedelta

# Configure the map
map_config = MapConfig(
    project_name="Central California Seismicity",
    client="Research Project",
    latitude=36.7783,
    longitude=-119.4179,
    radius_km=200,
    base_zoom_level=8
)

event_config = EventConfig(
    color_palette="viridis",
    scaling_factor=3.0,
    show_events_default=True,
    show_heatmap_default=False
)

# Download USGS earthquake data
end_time = datetime.now()
start_time = end_time - timedelta(days=30)

catalog = USGSCatalog()
events_df = catalog.getEvents(
    start_date=start_time,
    end_date=end_time,
    latitude=map_config.latitude,
    longitude=map_config.longitude,
    maxradiuskm=map_config.radius_km,
    min_magnitude=2.0
)

# Save catalog to CSV
events_df.to_csv("events.csv", index=False)

# Create the map
event_map = EventMap(
    map_config=map_config,
    event_config=event_config,
    events_csv="events.csv"
)

event_map.loadData()
folium_map = event_map.getMap()
folium_map.save("earthquake_map.html")
```

### Mining Blast Analysis

```python
from kashima.mapper import EventMap, MapConfig, EventConfig, BlastCatalog, BlastConfig

# Configure blast data processing
blast_config = BlastConfig(
    blast_file_path="blast_data.csv",
    coordinate_system="EPSG:32722",  # UTM Zone 22S
    f_TNT=0.90,
    a_ML=0.75,
    b_ML=-1.0
)

# Process blast catalog
blast_catalog = BlastCatalog(blast_config)
blast_catalog.readBlastData()
blast_events = blast_catalog.buildCatalog()

# Save processed blast events
blast_events.to_csv("blast_catalog.csv", index=False)

# Create visualization
map_config = MapConfig(
    project_name="Mine Site Blasting",
    client="Mining Company",
    latitude=-23.5505,
    longitude=-46.6333,
    radius_km=50
)

event_config = EventConfig(
    show_events_default=True,
    show_heatmap_default=False
)

event_map = EventMap(
    map_config=map_config,
    event_config=event_config,
    events_csv="blast_catalog.csv"
)

event_map.loadData()
blast_map = event_map.getMap()
blast_map.save("blast_map.html")
```

### Advanced Multi-Layer Visualization

```python
from kashima.mapper import EventMap, MapConfig, EventConfig, FaultConfig, StationConfig, USGSCatalog
from datetime import datetime, timedelta

# Complete configuration
map_config = MapConfig(
    project_name="Comprehensive Seismic Analysis",
    client="Seismic Network",
    latitude=37.7749,
    longitude=-122.4194,
    radius_km=300,
    default_tile_layer="Esri.WorldImagery",
    epicentral_circles=7
)

event_config = EventConfig(
    color_palette="plasma",
    scaling_factor=2.5,
    show_events_default=True,
    show_heatmap_default=True,
    show_beachballs_default=True,
    beachball_min_magnitude=4.0,
    heatmap_radius=25
)

fault_config = FaultConfig(
    include_faults=True,
    faults_gem_file_path="faults.geojson",
    regional_faults_color="red",
    regional_faults_weight=2
)

station_config = StationConfig(
    station_file_path="stations.csv",
    layer_title="Seismic Network"
)

# Download catalog
catalog = USGSCatalog()
usgs_events = catalog.getEvents(
    start_date=datetime(2023, 1, 1),
    end_date=datetime(2023, 12, 31),
    latitude=37.7749,
    longitude=-122.4194,
    maxradiuskm=300,
    min_magnitude=3.0
)
usgs_events.to_csv("usgs_events.csv", index=False)

# Build comprehensive map
event_map = EventMap(
    map_config=map_config,
    event_config=event_config,
    events_csv="usgs_events.csv",
    fault_config=fault_config,
    station_config=station_config
)

event_map.loadData()
comprehensive_map = event_map.getMap()
comprehensive_map.save("comprehensive_map.html")
```

## Configuration Options

### MapConfig
Core map display settings:
```python
MapConfig(
    project_name="Project Name",
    client="Client Name", 
    latitude=40.0,
    longitude=-120.0,
    radius_km=100,
    base_zoom_level=8,
    default_tile_layer="OpenStreetMap",
    epicentral_circles=5,
    auto_fit_bounds=True
)
```

### EventConfig
Event visualization parameters:
```python
EventConfig(
    color_palette="magma",           # Color scheme: magma, viridis, plasma, etc.
    color_reversed=False,
    scaling_factor=2.0,              # Size scaling for magnitude
    legend_position="bottomright",
    show_events_default=True,        # Layer visibility on load
    show_heatmap_default=False,
    show_beachballs_default=False,
    heatmap_radius=20,
    heatmap_blur=15,
    beachball_min_magnitude=4.0
)
```

## Supported Tile Layers

Kashima supports numerous base map layers:
- **OpenStreetMap**: Standard OSM rendering
- **ESRI Layers**: Satellite imagery, terrain, streets, relief
- **CartoDB**: Positron, dark matter, voyager themes  
- **Stamen**: Terrain and toner artistic styles
- **OpenTopoMap**: Topographic mapping
- **CyclOSM**: Cycling-focused rendering

## Data Sources

### USGS Earthquake Catalog
```python
from datetime import datetime
from kashima.mapper import USGSCatalog

catalog = USGSCatalog()
events = catalog.getEvents(
    start_date=datetime(2023, 1, 1),
    end_date=datetime(2023, 12, 31),
    latitude=36.0,
    longitude=-120.0,
    maxradiuskm=200,
    min_magnitude=3.0,
    want_tensor=True  # Include moment tensor data
)
```

### Global CMT Catalog
Download moment tensor solutions from the Global CMT Project using the fast NDK method:
```python
from datetime import datetime
from kashima.mapper import GCMTCatalog

catalog = GCMTCatalog(verbose=True)

# NDK method (fast, recommended) - downloads from NDK text files
# Complete catalog: 68,718 events from 1962-present in ~30 seconds
events = catalog.getEventsFromNDK(
    start_date=datetime(1962, 1, 1),  # NDK starts in 1962
    end_date=datetime(2024, 12, 31),
    min_magnitude=4.5,
    max_magnitude=10.0
)

# Alternative: Web API method (slower, limited pagination)
# events = catalog.getEvents(
#     start_date=datetime(2020, 1, 1),
#     end_date=datetime(2020, 12, 31),
#     latitude=-35.6,
#     longitude=-73.25,
#     maxradiuskm=500,
#     min_magnitude=5.0
# )

# Events include complete moment tensor data:
# mrr, mtt, mpp, mrt, mrp, mtp
# strike1, dip1, rake1, strike2, dip2, rake2
# half_duration, time_shift, scalar_moment
```

### Custom Blast Data
For mining applications, process blast data with coordinate conversion:
```python
from kashima.mapper import BlastCatalog, BlastConfig

config = BlastConfig(
    blast_file_path="blasts.csv",
    coordinate_system="EPSG:32633",  # UTM Zone 33N
    f_TNT=0.85,     # TNT equivalency factor
    a_ML=0.75,      # Magnitude calculation parameters
    b_ML=-1.0
)
```

## Advanced Features

### Coordinate System Transformations
Automatic conversion between coordinate systems:
```python
# Input data in UTM, output in WGS84 for web mapping
blast_config = BlastConfig(
    coordinate_system="EPSG:32722"  # UTM Zone 22S
)
```

### Large Dataset Handling
Efficient processing of large catalogs:
```python
# Stream processing for large CSV files
from kashima.mapper.utils import stream_read_csv_bbox

bbox = great_circle_bbox(lon0, lat0, radius_km)
events = stream_read_csv_bbox(
    "large_catalog.csv", 
    bbox, 
    chunksize=50000
)
```

### Custom Layer Combinations
```python
from kashima.mapper.layers import (
    EventMarkerLayer, 
    HeatmapLayer, 
    BeachballLayer,
    EpicentralCirclesLayer
)

# Build custom layer combinations
event_layer = EventMarkerLayer(events, event_config)
heatmap_layer = HeatmapLayer(events, event_config) 
circles_layer = EpicentralCirclesLayer(map_config)
```

## Use Cases

- **Seismic Hazard Assessment**: Visualize historical earthquake activity
- **Mining Seismology**: Monitor and analyze blast-induced seismicity
- **Research Applications**: Academic earthquake research and publication
- **Emergency Response**: Real-time seismic event mapping
- **Geotechnical Engineering**: Site-specific seismic analysis
- **Education**: Teaching earthquake science and hazards
- **External Tool Integration**: Simple API for orchestration systems (TITO, workflows)

## Class Reference

### Simplified API Functions
- **`buildMap()`**: High-level function to create maps with sensible defaults
- **`buildCatalog()`**: Download and save seismic catalogs from various sources

### Core Classes
- **`EventMap`**: Main visualization class
- **`USGSCatalog`**: USGS earthquake data interface
- **`GCMTCatalog`**: Global CMT moment tensor data interface
- **`BlastCatalog`**: Mining blast data processor
- **`BaseMap`**: Foundation mapping functionality

### Configuration Classes
- **`MapConfig`**: Core map parameters
- **`EventConfig`**: Event visualization settings
- **`FaultConfig`**: Fault line display options
- **`StationConfig`**: Seismic station configuration
- **`BlastConfig`**: Blast data processing parameters

### Layer Classes  
- **`EventMarkerLayer`**: Individual event markers
- **`HeatmapLayer`**: Activity density visualization
- **`BeachballLayer`**: Moment tensor focal mechanisms
- **`FaultLayer`**: Geological fault lines
- **`StationLayer`**: Seismic station markers
- **`EpicentralCirclesLayer`**: Distance rings

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citation

If you use Kashima in your research, please cite:

```bibtex
@software{kashima,
  author = {Alejandro Verri Kozlowski},
  title = {Kashima: Machine Learning Tools for Geotechnical Earthquake Engineering},
  url = {https://github.com/averriK/kashima},
  version = {1.2.0.0},
  year = {2025}
}
```

## Contact

- **Author**: Alejandro Verri Kozlowski
- **Email**: averri@fi.uba.ar
- **GitHub**: [@averriK](https://github.com/averriK)

## Changelog

### Version 1.3.0 (Current)
- **MAJOR ENHANCEMENT**: Streamlined cache system
  - Removed obsolete `build_*_catalog` parameters from `buildMap()`
  - All catalogs (USGS, ISC, GCMT) now mandatory by default
  - Fresh cache snapshots copied to `./data/` on every run
  - No more stale data issues - always synchronized with cache
  - Added `keep_data` parameter to control `./data/` cleanup (default: False)
- **NEW EXAMPLES**:
  - `03_update_catalogs.py` - Update global cache catalogs
  - `04_rebuild_cache.py` - Rebuild corrupted cache from scratch
  - `05_custom_faults.py` - Use custom fault lines GeoJSON files
- **IMPROVEMENTS**:
  - Simplified data flow: Cache → ./data/ (temp) → Read → Cleanup
  - Better error messages for missing cache
  - Faults always copied fresh from cache (like catalogs)
- **DEPENDENCIES**: Same as v1.2.0.0

### Version 1.2.0.0
- **BREAKING CHANGE**: Refactored all public methods to use camelCase naming convention
  - `get_events()` → `getEvents()`
  - `load_data()` → `loadData()`
  - `get_map()` → `getMap()`
  - `read_blast_data()` → `readBlastData()`
  - `build_catalog()` → `buildCatalog()`
  - `to_feature_group()` → `toFeatureGroup()`
  - All layer classes updated
  - All examples and documentation updated
- **MAJOR ENHANCEMENT**: Global CMT catalog now uses fast NDK method
  - New `getEventsFromNDK()` method downloads from NDK text files
  - Complete historical catalog: 68,718 events from 1962-present
  - Download time: ~30 seconds for full catalog (vs hours with web API)
  - `buildGCMTCatalog()` now uses NDK method by default
  - Web API method still available via `getEvents()` for spatial filtering
- Added Global CMT (Global Centroid Moment Tensor) catalog support
  - New `GCMTCatalog` class for downloading moment tensor data
  - Integrated into `buildCatalog()` with `source="gcmt"`
  - Complete moment tensor components (Mrr, Mtt, Mpp, Mrt, Mrp, Mtp)
  - Nodal plane data (strike, dip, rake)
  - Source parameters (half_duration, time_shift, scalar_moment)
- Added global cache system for catalog data
  - `downloadAllCatalogs()` - Download all catalogs to cache once
  - `updateAllCatalogs()` - Incrementally update with new events
  - Cache location: `~/Library/Caches/kashima/` (macOS), `~/.cache/kashima/` (Linux)
  - Parquet format for efficient storage and fast loading
  - Added `pyarrow>=10.0.0` dependency
- Private methods and function arguments remain in snake_case

### Version 1.0.10.1
- Enhanced coordinate system support
- Improved large dataset handling
- Added beachball visualization
- Extended tile layer options
- Better error handling and logging
- Fixed directory creation bug in examples
- Updated SiteMarkerLayer export
- Corrected fault style typo