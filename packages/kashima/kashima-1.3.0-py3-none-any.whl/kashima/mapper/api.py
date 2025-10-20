#!/usr/bin/env python
"""
Simplified API for kashima.mapper - encapsulates complexity.
"""

from pathlib import Path
import logging
from typing import Optional

from kashima.mapper.config import (
    MapConfig,
    EventConfig,
    FaultConfig,
    DEFAULT_FAULT_STYLE_META,
)
from kashima.mapper.usgs_catalog import USGSCatalog
from kashima.mapper.gcmt_catalog import GCMTCatalog
from kashima.mapper.isc_bulletin_catalog import ISCBulletinCatalog
from kashima.mapper.event_map import EventMap


logger = logging.getLogger(__name__)


# ── Constants (extracted from examples/mapper/run.py) ──────────────
MAG_BINS = [4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0]

DOT_PALETTE = {
    "4.5-5.0": "#ffffb2",
    "5.0-5.5": "#fed976",
    "5.5-6.0": "#feb24c",
    "6.0-6.5": "#fd8d3c",
    "6.5-7.0": "#fc4e2a",
    "7.0-7.5": "#e31a1c",
    "7.5-8.0": "#bd0026",
    "8.0-8.5": "#800026",
    "8.5-9.0": "#4d0026",
}

DOT_SIZES = {
    "4.5-5.0": 6,
    "5.0-5.5": 7,
    "5.5-6.0": 8,
    "6.0-6.5": 9,
    "6.5-7.0": 10,
    "7.0-7.5": 14,
    "7.5-8.0": 18,
    "8.0-8.5": 22,
    "≥8.5": 30,
}

BEACHBALL_SIZES = {
    "4.5-5.0": 18,
    "5.0-5.5": 24,
    "5.5-6.0": 26,
    "6.0-6.5": 30,
    "6.5-7.0": 34,
    "7.0-7.5": 38,
    "7.5-8.0": 42,
    "8.0-8.5": 46,
    ">=8.5": 54,
}

USER_FAULT_STYLE = {
    "N":   {"label": "Normal",                 "color": "#3182bd"},
    "R":   {"label": "Reverse",                "color": "#de2d26"},
    "SS":  {"label": "Strike-slip",            "color": "#31a354"},
    "NSS": {"label": "Normal-Strike-slip",     "color": "#6baed6"},
    "RSS": {"label": "Reverse-Strike-slip",    "color": "#fc9272"},
    "O":   {"label": "Oblique",                "color": "#bdbdbd"},
    "U":   {"label": "Undetermined",           "color": "#969696"},
}

FAULT_STYLE = {**DEFAULT_FAULT_STYLE_META, **USER_FAULT_STYLE}

# ── Default legend mapping (field name → display label) ────────────
DEFAULT_LEGEND_MAP = {
    "latitude": "Latitude",
    "longitude": "Longitude",
    "mag": "Magnitude",
    "depth": "Hypocentral Depth",
    "time": "Date",
    "place": "Location",
    "event_id": "ID",
    "source": "Catalog Source",
}


def buildMap(
    latitude: float,
    longitude: float,
    output_dir: str = ".",
    radius_km: float = 500,
    # Magnitude filtering
    vmin: float = 4.5,
    vmax: float = 9.0,
    # Project metadata
    project_name: str = "",
    client: str = "",
    # User-provided events
    user_events_csv: Optional[str] = None,
    # Layer visibility
    show_events_default: bool = True,
    show_cluster_default: bool = False,
    show_heatmap_default: bool = False,
    show_beachballs_default: bool = True,
    show_epicentral_circles_default: bool = True,
    # Zoom configuration
    base_zoom_level: int = 9,
    min_zoom_level: int = 7,
    max_zoom_level: int = 15,
    # Tile layer
    default_tile_layer: str = "Esri.WorldImagery",
    # Map behavior
    auto_fit_bounds: bool = False,
    lock_pan: bool = True,
    epicentral_circles: int = 10,
    # Visual customization - Palettes & Sizes
    mag_bins: Optional[list] = None,
    dot_palette: Optional[dict] = None,
    dot_sizes: Optional[dict] = None,
    beachball_sizes: Optional[dict] = None,
    fault_style_meta: Optional[dict] = None,
    legend_map: Optional[dict] = None,
    # Visual customization - Colors
    color_palette: str = "magma",
    color_reversed: bool = False,
    # Visual customization - Scaling
    scaling_factor: float = 2.0,
    event_radius_multiplier: float = 1.0,
    # Heatmap configuration
    heatmap_radius: int = 30,
    heatmap_blur: int = 15,
    heatmap_min_opacity: float = 0.50,
    # Legend configuration
    legend_title: str = "Magnitude (Mw)",
    legend_position: str = "bottomright",
    # Beachball configuration
    beachball_min_magnitude: Optional[float] = None,
    # File paths
    faults_geojson_path: Optional[str] = None,
    station_csv_path: Optional[str] = None,
    # Fault configuration
    regional_faults_color: str = "darkgreen",
    regional_faults_weight: int = 4,
    faults_coordinate_system: str = "EPSG:4326",
    # Station configuration
    station_coordinate_system: str = "EPSG:4326",
    station_layer_title: str = "Seismic Stations",
    # Advanced: XY coordinate support
    x_col: Optional[str] = None,
    y_col: Optional[str] = None,
    location_crs: str = "EPSG:4326",
    # Advanced: tooltip customization
    tooltip_fields: Optional[list] = None,
    # Data management
    keep_data: bool = False,
) -> dict:
    """
    Build an interactive seismic event map using kashima.mapper.

    This function encapsulates all the complexity of configuring MapConfig, EventConfig,
    and FaultConfig with sensible defaults. Only the parameters that typically vary
    per task are exposed.

    Parameters
    ----------
    latitude : float
        Center latitude for the map (-90 to 90) - REQUIRED
    longitude : float
        Center longitude for the map (-180 to 180) - REQUIRED
    output_dir : str, optional
        Directory where data/ and maps/ subdirectories will be created.
        Default: "." (current directory)
        Example: "/path/to/project/session"
    radius_km : float, optional
        Search radius in kilometers (default: 500)
    vmin : float, optional
        Minimum magnitude to display (default: 4.5)
    vmax : float, optional
        Maximum magnitude to display (default: 9.0)
    project_name : str, optional
        Project name for metadata (default: "")
    client : str, optional
        Client name for metadata (default: "")
    show_events_default : bool, optional
        Show event dots by default (default: True)
    show_cluster_default : bool, optional
        Show clustered view by default (default: False)
    show_heatmap_default : bool, optional
        Show heatmap layer by default (default: False)
    show_beachballs_default : bool, optional
        Show beachball focal mechanisms by default (default: True)
    show_epicentral_circles_default : bool, optional
        Show distance rings by default (default: True)
    base_zoom_level : int, optional
        Initial zoom level (default: 9)
    min_zoom_level : int, optional
        Minimum allowed zoom level (default: 7)
    max_zoom_level : int, optional
        Maximum allowed zoom level (default: 15)
    faults_geojson_path : str, optional
        Path to GeoJSON file with fault lines (default: None)
    legend_map : dict, optional
        Custom legend mapping (field name → display label). If None, uses DEFAULT_LEGEND_MAP.
        Example: {"mag": "Magnitude", "depth": "Depth (km)"}
    keep_data : bool, optional
        Keep temporary data files in ./data/ after completion (default: False).
        If False, ./data/ directory is removed after map generation.
        Set to True to preserve catalog snapshots for documentation.

    Returns
    -------
    dict
        Dictionary with paths to generated artifacts:
        {
            "html": str,          # Path to generated HTML map
            "csv": str,           # Path to epicenters CSV
            "event_count": int,   # Number of events in map
        }

    Examples
    --------
    >>> # Minimal call - only coordinates required
    >>> result = buildMap(latitude=-32.8908, longitude=-68.8272)
    >>> print(result["html"])
    ./maps/index.html

    >>> # With custom output directory and parameters
    >>> result = buildMap(
    ...     latitude=-32.8908,
    ...     longitude=-68.8272,
    ...     output_dir="/path/to/session",
    ...     radius_km=600,
    ...     vmin=5.5,
    ...     show_heatmap_default=False
    ... )
    >>> print(result["html"])
    /path/to/session/maps/index.html
    """

    # ── 1. Setup directories ────────────────────────────────────────
    root = Path(output_dir)
    input_dir = root / "data"
    output_map_dir = root / "maps"

    # FIX: Create both directories
    input_dir.mkdir(parents=True, exist_ok=True)
    output_map_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"Output directory: {root}")
    logger.info(f"Data directory: {input_dir}")
    logger.info(f"Maps directory: {output_map_dir}")

    # ── 2. Load catalogs from cache (always fresh snapshot) ─────────
    # Always copy fresh from cache to ./data/ - this ensures:
    # 1. ./data/ is never stale
    # 2. ./data/ documents exactly what data was used for this project
    # Use build*Catalog() or update*Catalog() to refresh the global cache

    from .cache import get_catalog_path, catalog_exists, get_auxiliary_file_path, auxiliary_file_exists
    import shutil

    # 2a. USGS Catalog (always mandatory)
    if not catalog_exists("usgs"):
        raise RuntimeError(
            "USGS catalog not found in cache. Please reinstall kashima or run:\n"
            "  from kashima.mapper import buildUSGSCatalog\n"
            "  buildUSGSCatalog()"
        )

    usgs_local = input_dir / "usgs-events.csv"
    cache_path = get_catalog_path("usgs")
    logger.info(f"Copying USGS catalog from cache: {cache_path}")
    shutil.copy(cache_path, usgs_local)
    usgs_path = usgs_local

    # 2b. ISC Bulletin Catalog (always mandatory)
    if not catalog_exists("isc"):
        raise RuntimeError(
            "ISC catalog not found in cache. Please reinstall kashima or run:\n"
            "  from kashima.mapper import buildISCCatalog\n"
            "  buildISCCatalog()"
        )

    isc_local = input_dir / "isc-events.csv"
    cache_path = get_catalog_path("isc")
    logger.info(f"Copying ISC catalog from cache: {cache_path}")
    shutil.copy(cache_path, isc_local)
    isc_path = isc_local

    # 2c. GCMT Catalog (only if beachballs enabled)
    gcmt_path = None
    if show_beachballs_default:
        if not catalog_exists("gcmt"):
            raise RuntimeError(
                "GCMT catalog not found in cache (required for beachballs). Please reinstall kashima or run:\n"
                "  from kashima.mapper import buildGCMTCatalog\n"
                "  buildGCMTCatalog()"
            )

        gcmt_local = input_dir / "gcmt-events.csv"
        cache_path = get_catalog_path("gcmt")
        logger.info(f"Copying GCMT catalog from cache: {cache_path}")
        shutil.copy(cache_path, gcmt_local)
        gcmt_path = gcmt_local

    # ── 3. Setup catalog paths for EventMap ────────────────────────
    # Use user-provided CSV if available, otherwise use cached catalogs
    events_csv = user_events_csv if user_events_csv else str(usgs_path)
    isc_csv = str(isc_path)
    gcmt_csv = str(gcmt_path) if gcmt_path else None

    # ── 7. Build configurations ─────────────────────────────────────
    map_cfg = MapConfig(
        project_name=project_name,
        client=client,
        latitude=latitude,
        longitude=longitude,
        radius_km=radius_km,
        base_zoom_level=base_zoom_level,
        min_zoom_level=min_zoom_level,
        max_zoom_level=max_zoom_level,
        default_tile_layer=default_tile_layer,
        auto_fit_bounds=auto_fit_bounds,
        lock_pan=lock_pan,
        epicentral_circles=epicentral_circles,
    )

    event_cfg = EventConfig(
        # Use custom bins/palettes if provided, otherwise defaults
        mag_bins=mag_bins or MAG_BINS,
        dot_palette=dot_palette or DOT_PALETTE,
        dot_sizes=dot_sizes or DOT_SIZES,
        beachball_sizes=beachball_sizes or BEACHBALL_SIZES,
        fault_style_meta=fault_style_meta or FAULT_STYLE,
        # Color configuration
        color_palette=color_palette,
        color_reversed=color_reversed,
        # Scaling
        scaling_factor=scaling_factor,
        event_radius_multiplier=event_radius_multiplier,
        # Heatmap
        heatmap_radius=heatmap_radius,
        heatmap_blur=heatmap_blur,
        heatmap_min_opacity=heatmap_min_opacity,
        # Legend
        legend_title=legend_title,
        legend_position=legend_position,
        # Magnitude filters
        vmin=vmin,
        vmax=vmax,
        # Layer visibility
        show_events_default=show_events_default,
        show_cluster_default=show_cluster_default,
        show_heatmap_default=show_heatmap_default,
        show_beachballs_default=show_beachballs_default,
        show_epicentral_circles_default=show_epicentral_circles_default,
        # Beachball
        beachball_min_magnitude=beachball_min_magnitude,
    )

    # ── 2d. Faults GeoJSON (conditional on no custom path) ────────────
    fault_cfg = None
    if faults_geojson_path:
        # User specified custom faults file
        fault_cfg = FaultConfig(
            include_faults=True,
            faults_gem_file_path=faults_geojson_path,
            regional_faults_color=regional_faults_color,
            regional_faults_weight=regional_faults_weight,
            coordinate_system=faults_coordinate_system,
        )
    elif auxiliary_file_exists("gem_active_faults.geojson"):
        # Copy from cache (always fresh copy, like catalogs)
        cache_path = get_auxiliary_file_path("gem_active_faults.geojson")
        faults_local = input_dir / "gem_active_faults.geojson"
        logger.info(f"Copying faults file from cache: {cache_path}")
        shutil.copy(cache_path, faults_local)
        fault_cfg = FaultConfig(
            include_faults=True,
            faults_gem_file_path=str(faults_local),
            regional_faults_color=regional_faults_color,
            regional_faults_weight=regional_faults_weight,
            coordinate_system=faults_coordinate_system,
        )

    station_cfg = None
    if station_csv_path:
        from kashima.mapper.config import StationConfig
        station_cfg = StationConfig(
            station_file_path=station_csv_path,
            coordinate_system=station_coordinate_system,
            layer_title=station_layer_title,
        )

    # ── 4. Build the map ────────────────────────────────────────────
    events_map = EventMap(
        map_config=map_cfg,
        event_config=event_cfg,
        events_csv=events_csv,  # Main catalog (USGS or user-provided)
        isc_csv=isc_csv,  # ISC Bulletin events (optional)
        gcmt_csv=gcmt_csv,  # GCMT moment tensors (optional)
        legend_map=legend_map or DEFAULT_LEGEND_MAP,  # Use custom or default legend
        mandatory_mag_col="mag",
        calculate_distance=True,
        fault_config=fault_cfg,
        station_config=station_cfg,
        tooltip_fields=tooltip_fields,
        # XY coordinate support
        x_col=x_col,
        y_col=y_col,
        location_crs=location_crs,
    )

    events_map.loadData()
    folium_map = events_map.getMap()

    # ── 8. Save artifacts ───────────────────────────────────────────
    html_out = output_map_dir / "index.html"
    csv_out = output_map_dir / "epicenters.csv"

    folium_map.save(str(html_out))
    events_map.events_df.to_csv(csv_out, index=False)

    logger.info(f"✔ Map  → {html_out}")
    logger.info(f"✔ Data → {csv_out}")

    # ── 9. Cleanup temporary data (if requested) ────────────────────
    if not keep_data and input_dir.exists():
        import shutil
        shutil.rmtree(input_dir)
        logger.info(f"✓ Cleaned up temporary data: {input_dir}")

    # ── 10. Return results ──────────────────────────────────────────
    return {
        "html": str(html_out),
        "csv": str(csv_out),
        "event_count": len(events_map.events_df),
    }


def buildCatalog(
    source: str,
    output_path: str,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    max_radius_km: Optional[float] = None,
    min_magnitude: float = 4.5,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    event_type: str = "earthquake",
    **kwargs
) -> dict:
    """
    Build a seismic event catalog from various sources (USGS, GCMT, Blast).

    Parameters
    ----------
    source : str
        Catalog source: "usgs", "gcmt", or "blast"
    output_path : str
        Path where the catalog CSV will be saved
    latitude : float, optional
        Center latitude for radial search (required for radial search)
    longitude : float, optional
        Center longitude for radial search (required for radial search)
    max_radius_km : float, optional
        Search radius in kilometers (requires lat/lon)
    min_magnitude : float, optional
        Minimum magnitude threshold (default: 4.5)
    start_time : str, optional
        Start time in ISO format "YYYY-MM-DD" (default: 1800-01-01)
    end_time : str, optional
        End time in ISO format "YYYY-MM-DD" (default: now)
    event_type : str, optional
        Event type filter (default: "earthquake")
    **kwargs
        Additional source-specific parameters

    Returns
    -------
    dict
        Dictionary with catalog information:
        {
            "csv": str,           # Path to saved CSV
            "event_count": int,   # Number of events retrieved
            "source": str,        # Catalog source
        }

    Examples
    --------
    >>> # Download USGS catalog for a region
    >>> result = buildCatalog(
    ...     source="usgs",
    ...     output_path="data/usgs-events.csv",
    ...     latitude=-32.8,
    ...     longitude=-68.8,
    ...     max_radius_km=500,
    ...     min_magnitude=5.0
    ... )
    >>> print(f"Downloaded {result['event_count']} events")

    >>> # Download full USGS catalog
    >>> result = buildCatalog(
    ...     source="usgs",
    ...     output_path="data/usgs-full.csv",
    ...     event_type="earthquake"
    ... )
    """

    from datetime import datetime

    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    source = source.lower()

    if source == "usgs":
        logger.info(f"Building USGS catalog...")

        catalog = USGSCatalog(min_magnitude=min_magnitude, verbose=True)

        # Parse time parameters
        start_date = datetime.fromisoformat(start_time) if start_time else datetime(1800, 1, 1)
        end_date = datetime.fromisoformat(end_time) if end_time else datetime.utcnow()

        # Build query parameters
        query_params = {
            "start_date": start_date,
            "end_date": end_date,
            "min_magnitude": min_magnitude,
            "event_type": event_type,
            **kwargs
        }

        # Add radial search if coordinates provided
        if latitude is not None and longitude is not None and max_radius_km is not None:
            query_params.update({
                "latitude": latitude,
                "longitude": longitude,
                "maxradiuskm": max_radius_km,
            })

        # Fetch data
        df = catalog.getEvents(**query_params)
        df.to_csv(output_path, index=False)

        logger.info(f"✔ USGS catalog saved → {output_path}")
        logger.info(f"✔ Events: {len(df)}")

        return {
            "csv": str(output_path),
            "event_count": len(df),
            "source": "usgs",
        }

    elif source == "gcmt":
        logger.info(f"Building Global CMT catalog...")

        catalog = GCMTCatalog(verbose=True)

        # Parse time parameters
        start_date = datetime.fromisoformat(start_time) if start_time else datetime(1976, 1, 1)
        end_date = datetime.fromisoformat(end_time) if end_time else datetime.utcnow()

        # Build query parameters
        query_params = {
            "start_date": start_date,
            "end_date": end_date,
            "min_magnitude": min_magnitude,
            "max_magnitude": kwargs.get("max_magnitude", 10.0),
            **kwargs
        }

        # Add radial search if coordinates provided
        if latitude is not None and longitude is not None and max_radius_km is not None:
            query_params.update({
                "latitude": latitude,
                "longitude": longitude,
                "maxradiuskm": max_radius_km,
            })

        # Fetch data
        df = catalog.getEvents(**query_params)

        if len(df) == 0:
            logger.warning("No events found matching the criteria")

        df.to_csv(output_path, index=False)

        logger.info(f"✔ Global CMT catalog saved → {output_path}")
        logger.info(f"✔ Events: {len(df)}")

        return {
            "csv": str(output_path),
            "event_count": len(df),
            "source": "gcmt",
        }

    elif source == "isc":
        logger.info(f"Building ISC Bulletin catalog...")

        catalog = ISCBulletinCatalog(min_magnitude=min_magnitude, verbose=True)

        # Parse time parameters
        start_date = datetime.fromisoformat(start_time) if start_time else datetime(1904, 1, 1)
        end_date = datetime.fromisoformat(end_time) if end_time else datetime.utcnow()

        # Build query parameters
        query_params = {
            "start_date": start_date,
            "end_date": end_date,
            "min_magnitude": min_magnitude,
            **kwargs
        }

        # Add radial search if coordinates provided
        if latitude is not None and longitude is not None and max_radius_km is not None:
            query_params.update({
                "latitude": latitude,
                "longitude": longitude,
                "maxradiuskm": max_radius_km,
            })

        # Fetch data
        df = catalog.getEvents(**query_params)

        if len(df) == 0:
            logger.warning("No events found matching the criteria")

        df.to_csv(output_path, index=False)

        logger.info(f"✔ ISC Bulletin catalog saved → {output_path}")
        logger.info(f"✔ Events: {len(df)}")

        return {
            "csv": str(output_path),
            "event_count": len(df),
            "source": "isc",
        }

    elif source == "blast":
        raise NotImplementedError(
            "Blast catalog builder not yet implemented. "
            "Use kashima.mapper.BlastCatalog() directly."
        )

    else:
        raise ValueError(
            f"Unknown catalog source: '{source}'. "
            f"Supported sources: 'usgs', 'isc', 'gcmt', 'blast'"
        )


# ════════════════════════════════════════════════════════════════════
#  Specialized Catalog Builders
# ════════════════════════════════════════════════════════════════════


def buildUSGSCatalog(
    output_path: Optional[str] = None,
    min_magnitude: float = 4.5,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    event_type: str = "earthquake",
    **kwargs
) -> dict:
    """
    Download USGS ComCat earthquake catalog and update cache.

    By default, updates the global cache at ~/.cache/kashima/usgs_catalog.csv
    This cache is automatically used by all projects via buildMap().

    Parameters
    ----------
    output_path : str, optional
        If None (default): Updates global cache
        If provided: Saves to specified path (for project-specific catalogs)
    min_magnitude : float, optional
        Minimum magnitude threshold (default: 4.5)
    start_time : str, optional
        Start time in ISO format "YYYY-MM-DD" (default: 1800-01-01)
    end_time : str, optional
        End time in ISO format "YYYY-MM-DD" (default: now)
    event_type : str, optional
        Event type filter (default: "earthquake")
    **kwargs
        Additional USGS-specific parameters

    Returns
    -------
    dict
        {
            "csv": str,           # Path to saved CSV
            "event_count": int,   # Number of events retrieved
            "source": str,        # "usgs"
        }

    Examples
    --------
    >>> # Update global cache (run once, all projects benefit)
    >>> buildUSGSCatalog()

    >>> # Save to specific path with custom filters
    >>> buildUSGSCatalog(
    ...     output_path="./data/usgs-custom.csv",
    ...     start_time="2020-01-01",
    ...     min_magnitude=6.0
    ... )
    """
    from datetime import datetime
    from .cache import get_catalog_path

    # Determine output path
    if output_path is None:
        # Default: update global cache
        out_path = get_catalog_path("usgs")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        logger.info("Updating global USGS cache...")
    else:
        # Custom path specified
        out_path = Path(output_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        logger.info(f"Downloading USGS catalog to: {out_path}")

    logger.info("Downloading USGS catalog (global, no spatial filters)...")

    catalog = USGSCatalog(min_magnitude=min_magnitude, verbose=True)

    start_date = datetime.fromisoformat(start_time) if start_time else datetime(1800, 1, 1)
    end_date = datetime.fromisoformat(end_time) if end_time else datetime.utcnow()

    df = catalog.getEvents(
        start_date=start_date,
        end_date=end_date,
        min_magnitude=min_magnitude,
        event_type=event_type,
        **kwargs
    )

    # Save catalog
    df.to_csv(out_path, index=False)
    logger.info(f"✔ USGS catalog saved → {out_path}")
    logger.info(f"✔ Events: {len(df):,}")

    return {
        "csv": str(out_path),
        "event_count": len(df),
        "source": "usgs",
    }


def buildISCCatalog(
    output_path: Optional[str] = None,
    min_magnitude: float = 5.0,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    **kwargs
) -> dict:
    """
    Download ISC Bulletin catalog and update cache.

    By default, updates the global cache at ~/.cache/kashima/isc_catalog.csv
    This cache is automatically used by all projects via buildMap().

    Performance Note
    ----------------
    ISC Bulletin API is inherently slow (~15 seconds per year of data).
    For faster testing, use explicit start_time/end_time to limit the time range.
    Default: 1904-present (full catalog)

    Parameters
    ----------
    output_path : str, optional
        If None (default): Updates global cache
        If provided: Saves to specified path (for project-specific catalogs)
    min_magnitude : float, optional
        Minimum magnitude threshold (default: 5.0)
    start_time : str, optional
        Start time in ISO format "YYYY-MM-DD" (default: 1904-01-01)
    end_time : str, optional
        End time in ISO format "YYYY-MM-DD" (default: now)
    **kwargs
        Additional ISC-specific parameters

    Returns
    -------
    dict
        {
            "csv": str,           # Path to saved CSV
            "event_count": int,   # Number of events retrieved
            "source": str,        # "isc"
        }

    Examples
    --------
    >>> # Update global cache (run once, all projects benefit)
    >>> buildISCCatalog()

    >>> # Save to specific path with custom filters
    >>> buildISCCatalog(
    ...     output_path="./data/isc-custom.csv",
    ...     start_time="2015-01-01",
    ...     min_magnitude=6.0
    ... )
    """
    from datetime import datetime
    from .cache import get_catalog_path

    # Determine output path
    if output_path is None:
        # Default: update global cache
        out_path = get_catalog_path("isc")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        logger.info("Updating global ISC cache...")
    else:
        # Custom path specified
        out_path = Path(output_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        logger.info(f"Downloading ISC catalog to: {out_path}")

    logger.info("Downloading ISC Bulletin catalog (global, no spatial filters)...")

    catalog = ISCBulletinCatalog(min_magnitude=min_magnitude, verbose=True)

    start_date = datetime.fromisoformat(start_time) if start_time else datetime(1904, 1, 1)
    end_date = datetime.fromisoformat(end_time) if end_time else datetime.utcnow()

    df = catalog.getEvents(
        start_date=start_date,
        end_date=end_date,
        min_magnitude=min_magnitude,
        **kwargs
    )

    if len(df) == 0:
        logger.warning("No ISC events found matching the criteria")

    # Save catalog
    df.to_csv(out_path, index=False)
    logger.info(f"✔ ISC Bulletin catalog saved → {out_path}")
    logger.info(f"✔ Events: {len(df):,}")

    return {
        "csv": str(out_path),
        "event_count": len(df),
        "source": "isc",
    }


def buildGCMTCatalog(
    output_path: Optional[str] = None,
    min_magnitude: float = 4.5,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    **kwargs
) -> dict:
    """
    Download Global CMT catalog with moment tensors and update cache.

    By default, updates the global cache at ~/.cache/kashima/gcmt_catalog.csv
    This cache is automatically used by all projects via buildMap().

    Note: GCMT catalog is only downloaded when show_beachballs_default=True in buildMap().

    Parameters
    ----------
    output_path : str, optional
        If None (default): Updates global cache
        If provided: Saves to specified path (for project-specific catalogs)
    min_magnitude : float, optional
        Minimum magnitude threshold (default: 4.5)
    start_time : str, optional
        Start time in ISO format "YYYY-MM-DD" (default: 1962-01-01)
    end_time : str, optional
        End time in ISO format "YYYY-MM-DD" (default: now)
    **kwargs
        Additional GCMT-specific parameters

    Returns
    -------
    dict
        {
            "csv": str,           # Path to saved CSV
            "event_count": int,   # Number of events retrieved
            "source": str,        # "gcmt"
        }

    Examples
    --------
    >>> # Update global cache (run once, all projects benefit)
    >>> buildGCMTCatalog()

    >>> # Save to specific path with custom filters
    >>> buildGCMTCatalog(
    ...     output_path="./data/gcmt-custom.csv",
    ...     start_time="2010-01-01",
    ...     min_magnitude=6.0
    ... )
    """
    from datetime import datetime
    from .cache import get_catalog_path

    # Determine output path
    if output_path is None:
        # Default: update global cache
        out_path = get_catalog_path("gcmt")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        logger.info("Updating global GCMT cache...")
    else:
        # Custom path specified
        out_path = Path(output_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        logger.info(f"Downloading GCMT catalog to: {out_path}")

    logger.info("Downloading Global CMT catalog (global, no spatial filters)...")

    catalog = GCMTCatalog(verbose=True)

    start_date = datetime.fromisoformat(start_time) if start_time else datetime(1962, 1, 1)  # NDK starts 1962
    end_date = datetime.fromisoformat(end_time) if end_time else datetime.utcnow()

    df = catalog.getEventsFromNDK(
        start_date=start_date,
        end_date=end_date,
        min_magnitude=min_magnitude,
        max_magnitude=kwargs.get("max_magnitude", 10.0),
        **kwargs
    )

    if len(df) == 0:
        logger.warning("No GCMT events found matching the criteria")

    # Save catalog
    df.to_csv(out_path, index=False)
    logger.info(f"✔ Global CMT catalog saved → {out_path}")
    logger.info(f"✔ Events: {len(df):,}")

    return {
        "csv": str(out_path),
        "event_count": len(df),
        "source": "gcmt",
    }
