"""
Cache management for kashima.mapper catalogs
============================================

Provides a global cache system for earthquake catalogs so they only need
to be downloaded once per machine, regardless of where buildMap() is called.

Cache location:
  - Linux: ~/.cache/kashima/
  - macOS: ~/Library/Caches/kashima/
  - Windows: %LOCALAPPDATA%\\kashima\\Cache\\
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def get_cache_dir() -> Path:
    """
    Get kashima cache directory using platform-specific conventions.

    Returns
    -------
    Path
        Cache directory path (created if it doesn't exist)
    """
    try:
        import appdirs
        cache_dir = Path(appdirs.user_cache_dir("kashima", "kashima"))
    except ImportError:
        # Fallback if appdirs not installed
        import os
        if os.name == "nt":  # Windows
            base = Path(os.environ.get("LOCALAPPDATA", "~")).expanduser()
            cache_dir = base / "kashima" / "Cache"
        elif os.name == "posix":
            import platform
            if platform.system() == "Darwin":  # macOS
                cache_dir = Path.home() / "Library" / "Caches" / "kashima"
            else:  # Linux
                cache_dir = Path.home() / ".cache" / "kashima"
        else:
            cache_dir = Path.home() / ".kashima" / "cache"

    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def get_package_data_path(catalog: str) -> Optional[Path]:
    """
    Get path to catalog CSV bundled with kashima package.

    When kashima is installed via pip, it includes pre-downloaded catalogs
    in kashima/mapper/data/ to avoid initial download wait.

    Parameters
    ----------
    catalog : str
        Catalog name: "usgs", "gcmt", or "isc"

    Returns
    -------
    Path or None
        Path to catalog CSV in package data, or None if not found
    """
    try:
        # Get package data directory
        package_data_dir = Path(__file__).parent / "data"
        catalog_file = package_data_dir / f"{catalog}_catalog.csv"

        if catalog_file.exists():
            return catalog_file
        else:
            return None
    except Exception as e:
        logger.debug(f"Could not locate package data for {catalog}: {e}")
        return None


def get_auxiliary_file_path(file_name: str) -> Path:
    """
    Get path to auxiliary file in cache (e.g., gem_active_faults.geojson).

    Parameters
    ----------
    file_name : str
        Name of the auxiliary file (e.g., "gem_active_faults.geojson")

    Returns
    -------
    Path
        Path to auxiliary file in cache
    """
    cache_dir = get_cache_dir()
    return cache_dir / file_name


def auxiliary_file_exists(file_name: str) -> bool:
    """
    Check if auxiliary file exists in cache.

    Parameters
    ----------
    file_name : str
        Name of the auxiliary file (e.g., "gem_active_faults.geojson")

    Returns
    -------
    bool
        True if file exists in cache
    """
    return get_auxiliary_file_path(file_name).exists()


def initialize_cache_from_package_data() -> None:
    """
    Copy bundled catalog data from package to cache on first use.

    This runs automatically when downloadAllCatalogs() is called and no
    cache exists yet. It copies the pre-downloaded catalogs that ship
    with kashima to the user's cache directory.
    """
    import shutil
    cache_dir = get_cache_dir()
    cache_dir.mkdir(parents=True, exist_ok=True)

    # Copy catalogs
    for catalog in ["usgs", "gcmt", "isc"]:
        cache_path = get_catalog_path(catalog)

        # Skip if already in cache
        if cache_path.exists():
            continue

        # Try to copy from package data
        package_path = get_package_data_path(catalog)
        if package_path:
            logger.info(f"Initializing {catalog} cache from package data...")
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(package_path, cache_path)
            logger.info(f"  ✓ {catalog} ready ({cache_path.stat().st_size / 1024 / 1024:.1f} MB)")
        else:
            logger.debug(f"No package data found for {catalog}")

    # Copy auxiliary files (faults geojson)
    aux_files = ["gem_active_faults.geojson"]
    for aux_file in aux_files:
        cache_path = get_auxiliary_file_path(aux_file)

        # Skip if already in cache
        if cache_path.exists():
            continue

        # Try to copy from package data
        package_data_dir = Path(__file__).parent / "data"
        package_path = package_data_dir / aux_file

        if package_path.exists():
            logger.info(f"Initializing {aux_file} cache from package data...")
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(package_path, cache_path)
            logger.info(f"  ✓ {aux_file} ready ({cache_path.stat().st_size / 1024 / 1024:.1f} MB)")
        else:
            logger.debug(f"No package data found for {aux_file}")


def get_catalog_path(catalog: str) -> Path:
    """
    Get path to cached catalog file.

    Parameters
    ----------
    catalog : str
        Catalog name: "usgs", "gcmt", or "isc"

    Returns
    -------
    Path
        Path to catalog CSV file in cache
    """
    cache_dir = get_cache_dir()
    catalog_files = {
        "usgs": "usgs_catalog.csv",
        "gcmt": "gcmt_catalog.csv",
        "isc": "isc_catalog.csv",
    }

    if catalog not in catalog_files:
        raise ValueError(f"Unknown catalog: {catalog}. Must be 'usgs', 'gcmt', or 'isc'")

    return cache_dir / catalog_files[catalog]


def catalog_exists(catalog: str) -> bool:
    """
    Check if catalog exists in cache.

    Parameters
    ----------
    catalog : str
        Catalog name: "usgs", "gcmt", or "isc"

    Returns
    -------
    bool
        True if catalog exists in cache
    """
    return get_catalog_path(catalog).exists()


def downloadAllCatalogs(
    force_update: bool = False,
    usgs_min_mag: float = 4.5,
    gcmt_min_mag: float = 4.5,
    isc_min_mag: float = 5.0,
) -> dict:
    """
    Download all historical catalogs to global cache directory.

    This function downloads complete historical catalogs once and stores them
    in a platform-specific cache directory. Subsequent calls to buildMap() will
    use these cached catalogs, avoiding repeated downloads.

    When kashima is installed via pip, it includes pre-downloaded catalogs
    that are automatically copied to cache on first use (instant setup).

    Parameters
    ----------
    force_update : bool, optional
        If True, re-download even if cache exists (default: False)
    usgs_min_mag : float, optional
        Minimum magnitude for USGS catalog (default: 4.5)
    gcmt_min_mag : float, optional
        Minimum magnitude for GCMT catalog (default: 4.5)
    isc_min_mag : float, optional
        Minimum magnitude for ISC catalog (default: 5.0)

    Returns
    -------
    dict
        Paths to cached catalogs:
        {
            "usgs": str,    # Path to USGS catalog
            "gcmt": str,    # Path to GCMT catalog
            "isc": str,     # Path to ISC catalog
            "cache_dir": str,  # Cache directory location
        }

    Examples
    --------
    >>> # First time: uses bundled data from pip install (instant!)
    >>> from kashima.mapper import downloadAllCatalogs
    >>> catalogs = downloadAllCatalogs()
    Cache directory: /home/user/.cache/kashima
    Initializing usgs cache from package data...
      ✓ usgs ready (33.2 MB)
    Initializing gcmt cache from package data...
      ✓ gcmt ready (14.0 MB)
    Initializing isc cache from package data...
      ✓ isc ready (22.4 MB)

    >>> # Future calls: uses cache (instant)
    >>> catalogs = downloadAllCatalogs()
    Using cached catalogs from: /home/user/.cache/kashima

    >>> # Update catalogs with latest data (incremental)
    >>> catalogs = downloadAllCatalogs(force_update=True)
    """
    from .api import buildUSGSCatalog, buildGCMTCatalog, buildISCCatalog

    cache_dir = get_cache_dir()
    logger.info(f"Cache directory: {cache_dir}")

    # First, try to initialize cache from bundled package data
    initialize_cache_from_package_data()

    # If force_update=True and cache exists, use incremental update
    if force_update:
        usgs_exists = catalog_exists("usgs")
        gcmt_exists = catalog_exists("gcmt")
        isc_exists = catalog_exists("isc")

        if usgs_exists or gcmt_exists or isc_exists:
            logger.info("Performing incremental update (only new events)...")
            return updateAllCatalogs(
                usgs_min_mag=usgs_min_mag,
                gcmt_min_mag=gcmt_min_mag,
                isc_min_mag=isc_min_mag,
            )

    # USGS catalog
    usgs_path = get_catalog_path("usgs")
    if not usgs_path.exists():
        logger.info("Downloading USGS catalog (1800-present)...")
        result = buildUSGSCatalog(
            outputPath=str(usgs_path),
            minMagnitude=usgs_min_mag,
        )
        logger.info(f"✔ USGS: {result['event_count']:,} events cached")
    else:
        logger.info(f"Using cached USGS catalog: {usgs_path}")

    # GCMT catalog
    gcmt_path = get_catalog_path("gcmt")
    if not gcmt_path.exists():
        logger.info("Downloading GCMT catalog (1976-present)...")
        result = buildGCMTCatalog(
            outputPath=str(gcmt_path),
            minMagnitude=gcmt_min_mag,
        )
        logger.info(f"✔ GCMT: {result['event_count']:,} events cached")
    else:
        logger.info(f"Using cached GCMT catalog: {gcmt_path}")

    # ISC catalog
    isc_path = get_catalog_path("isc")
    if not isc_path.exists():
        logger.info("Downloading ISC catalog (1904-present, ~30 minutes)...")
        result = buildISCCatalog(
            outputPath=str(isc_path),
            minMagnitude=isc_min_mag,
        )
        logger.info(f"✔ ISC: {result['event_count']:,} events cached")
    else:
        logger.info(f"Using cached ISC catalog: {isc_path}")

    return {
        "usgs": str(usgs_path),
        "gcmt": str(gcmt_path),
        "isc": str(isc_path),
        "cache_dir": str(cache_dir),
    }


def clear_cache(catalog: Optional[str] = None) -> None:
    """
    Clear cached catalogs.

    Parameters
    ----------
    catalog : str, optional
        Specific catalog to clear ("usgs", "gcmt", "isc").
        If None, clears all catalogs.

    Examples
    --------
    >>> # Clear specific catalog
    >>> clear_cache("usgs")

    >>> # Clear all catalogs
    >>> clear_cache()
    """
    if catalog:
        path = get_catalog_path(catalog)
        if path.exists():
            path.unlink()
            logger.info(f"Cleared {catalog} cache: {path}")
        else:
            logger.info(f"No cached {catalog} catalog found")
    else:
        # Clear all catalogs
        for cat in ["usgs", "gcmt", "isc"]:
            clear_cache(cat)


# ════════════════════════════════════════════════════════════════════
#  Incremental Update Methods
# ════════════════════════════════════════════════════════════════════


def updateUSGSCatalog(minMagnitude: float = 4.5) -> dict:
    """
    Update USGS catalog with new events since last update.

    This function reads the cached USGS catalog, finds the most recent event,
    and downloads only new events from that date forward. Falls back to full
    download if no cache exists.

    Parameters
    ----------
    minMagnitude : float, optional
        Minimum magnitude threshold (default: 4.5)

    Returns
    -------
    dict
        {
            "csv": str,              # Path to updated catalog
            "event_count": int,      # Total events after update
            "new_events": int,       # Number of new events added
            "source": str,           # "usgs"
        }

    Examples
    --------
    >>> from kashima.mapper import updateUSGSCatalog
    >>> result = updateUSGSCatalog()
    ✔ USGS: Added 127 new events (total: 302,904)
    """
    from .api import buildUSGSCatalog
    from datetime import datetime, timedelta
    import pandas as pd

    usgs_path = get_catalog_path("usgs")

    # Fallback: full download if no cache
    if not usgs_path.exists():
        logger.info("No USGS cache found, downloading full catalog...")
        result = buildUSGSCatalog(
            outputPath=str(usgs_path),
            minMagnitude=minMagnitude,
        )
        return {
            "csv": result["csv"],
            "event_count": result["event_count"],
            "new_events": result["event_count"],
            "source": "usgs",
        }

    # Read existing catalog
    logger.info(f"Reading cached USGS catalog: {usgs_path}")
    df_existing = pd.read_csv(usgs_path)

    # Find most recent event
    df_existing["time"] = pd.to_datetime(df_existing["time"], errors="coerce")
    last_date = df_existing["time"].max()

    # Add 1 second to avoid duplicates
    start_date = last_date + timedelta(seconds=1)
    end_date = datetime.utcnow()

    logger.info(f"Updating USGS from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")

    # Download new events
    from .usgs_catalog import USGSCatalog
    catalog = USGSCatalog(min_magnitude=minMagnitude, verbose=True)
    df_new = catalog.getEvents(
        start_date=start_date,
        end_date=end_date,
        min_magnitude=minMagnitude,
    )

    # Append new events
    if len(df_new) > 0:
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        df_combined = df_combined.drop_duplicates(subset="event_id", keep="last").reset_index(drop=True)
        df_combined.to_csv(usgs_path, index=False)
        logger.info(f"✔ USGS: Added {len(df_new):,} new events (total: {len(df_combined):,})")
        return {
            "csv": str(usgs_path),
            "event_count": len(df_combined),
            "new_events": len(df_new),
            "source": "usgs",
        }
    else:
        logger.info("✔ USGS: No new events since last update")
        return {
            "csv": str(usgs_path),
            "event_count": len(df_existing),
            "new_events": 0,
            "source": "usgs",
        }


def updateGCMTCatalog(minMagnitude: float = 4.5) -> dict:
    """
    Update GCMT catalog with new events since last update.

    This function reads the cached GCMT catalog, finds the most recent event,
    and downloads only new events from that date forward. Falls back to full
    download if no cache exists.

    Parameters
    ----------
    minMagnitude : float, optional
        Minimum magnitude threshold (default: 4.5)

    Returns
    -------
    dict
        {
            "csv": str,              # Path to updated catalog
            "event_count": int,      # Total events after update
            "new_events": int,       # Number of new events added
            "source": str,           # "gcmt"
        }

    Examples
    --------
    >>> from kashima.mapper import updateGCMTCatalog
    >>> result = updateGCMTCatalog()
    ✔ GCMT: Added 42 new events (total: 54,863)
    """
    from .api import buildGCMTCatalog
    from datetime import datetime, timedelta
    import pandas as pd

    gcmt_path = get_catalog_path("gcmt")

    # Fallback: full download if no cache
    if not gcmt_path.exists():
        logger.info("No GCMT cache found, downloading full catalog...")
        result = buildGCMTCatalog(
            outputPath=str(gcmt_path),
            minMagnitude=minMagnitude,
        )
        return {
            "csv": result["csv"],
            "event_count": result["event_count"],
            "new_events": result["event_count"],
            "source": "gcmt",
        }

    # Read existing catalog
    logger.info(f"Reading cached GCMT catalog: {gcmt_path}")
    df_existing = pd.read_csv(gcmt_path)

    # Find most recent event
    df_existing["time"] = pd.to_datetime(df_existing["time"], errors="coerce")
    last_date = df_existing["time"].max()

    # Add 1 second to avoid duplicates
    start_date = last_date + timedelta(seconds=1)
    end_date = datetime.utcnow()

    logger.info(f"Updating GCMT from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")

    # Download new events
    from .gcmt_catalog import GCMTCatalog
    catalog = GCMTCatalog(verbose=True)
    df_new = catalog.getEvents(
        start_date=start_date,
        end_date=end_date,
        min_magnitude=minMagnitude,
        max_magnitude=10.0,
    )

    # Append new events
    if len(df_new) > 0:
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        df_combined = df_combined.drop_duplicates(subset="event_id", keep="last").reset_index(drop=True)
        df_combined.to_csv(gcmt_path, index=False)
        logger.info(f"✔ GCMT: Added {len(df_new):,} new events (total: {len(df_combined):,})")
        return {
            "csv": str(gcmt_path),
            "event_count": len(df_combined),
            "new_events": len(df_new),
            "source": "gcmt",
        }
    else:
        logger.info("✔ GCMT: No new events since last update")
        return {
            "csv": str(gcmt_path),
            "event_count": len(df_existing),
            "new_events": 0,
            "source": "gcmt",
        }


def updateISCCatalog(minMagnitude: float = 5.0) -> dict:
    """
    Update ISC catalog with new events since last update.

    This function reads the cached ISC catalog, finds the most recent event,
    and downloads only new events from that date forward. Falls back to full
    download if no cache exists.

    Parameters
    ----------
    minMagnitude : float, optional
        Minimum magnitude threshold (default: 5.0)

    Returns
    -------
    dict
        {
            "csv": str,              # Path to updated catalog
            "event_count": int,      # Total events after update
            "new_events": int,       # Number of new events added
            "source": str,           # "isc"
        }

    Examples
    --------
    >>> from kashima.mapper import updateISCCatalog
    >>> result = updateISCCatalog()
    ✔ ISC: Added 89 new events (total: 89,521)
    """
    from .api import buildISCCatalog
    from datetime import datetime, timedelta
    import pandas as pd

    isc_path = get_catalog_path("isc")

    # Fallback: full download if no cache
    if not isc_path.exists():
        logger.info("No ISC cache found, downloading full catalog...")
        result = buildISCCatalog(
            outputPath=str(isc_path),
            minMagnitude=minMagnitude,
        )
        return {
            "csv": result["csv"],
            "event_count": result["event_count"],
            "new_events": result["event_count"],
            "source": "isc",
        }

    # Read existing catalog
    logger.info(f"Reading cached ISC catalog: {isc_path}")
    df_existing = pd.read_csv(isc_path)

    # Find most recent event
    df_existing["time"] = pd.to_datetime(df_existing["time"], errors="coerce")
    last_date = df_existing["time"].max()

    # Add 1 day to avoid duplicates (ISC updates are slower)
    start_date = last_date + timedelta(days=1)
    end_date = datetime.utcnow()

    logger.info(f"Updating ISC from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")

    # Download new events
    from .isc_bulletin_catalog import ISCBulletinCatalog
    catalog = ISCBulletinCatalog(min_magnitude=minMagnitude, verbose=True)
    df_new = catalog.getEvents(
        start_date=start_date,
        end_date=end_date,
        min_magnitude=minMagnitude,
    )

    # Append new events
    if len(df_new) > 0:
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        df_combined = df_combined.drop_duplicates(subset="event_id", keep="last").reset_index(drop=True)
        df_combined.to_csv(isc_path, index=False)
        logger.info(f"✔ ISC: Added {len(df_new):,} new events (total: {len(df_combined):,})")
        return {
            "csv": str(isc_path),
            "event_count": len(df_combined),
            "new_events": len(df_new),
            "source": "isc",
        }
    else:
        logger.info("✔ ISC: No new events since last update")
        return {
            "csv": str(isc_path),
            "event_count": len(df_existing),
            "new_events": 0,
            "source": "isc",
        }


def updateAllCatalogs(
    usgs_min_mag: float = 4.5,
    gcmt_min_mag: float = 4.5,
    isc_min_mag: float = 5.0,
) -> dict:
    """
    Update all cached catalogs with new events since last update.

    This is the recommended way to keep catalogs up-to-date without
    re-downloading the entire historical dataset.

    Parameters
    ----------
    usgs_min_mag : float, optional
        Minimum magnitude for USGS catalog (default: 4.5)
    gcmt_min_mag : float, optional
        Minimum magnitude for GCMT catalog (default: 4.5)
    isc_min_mag : float, optional
        Minimum magnitude for ISC catalog (default: 5.0)

    Returns
    -------
    dict
        Paths and update statistics:
        {
            "usgs": str,           # Path to USGS catalog
            "gcmt": str,           # Path to GCMT catalog
            "isc": str,            # Path to ISC catalog
            "usgs_new": int,       # New USGS events added
            "gcmt_new": int,       # New GCMT events added
            "isc_new": int,        # New ISC events added
            "cache_dir": str,      # Cache directory
        }

    Examples
    --------
    >>> from kashima.mapper import updateAllCatalogs
    >>> result = updateAllCatalogs()
    ✔ USGS: Added 127 new events (total: 302,904)
    ✔ GCMT: Added 42 new events (total: 54,863)
    ✔ ISC: Added 89 new events (total: 89,521)
    """
    cache_dir = get_cache_dir()
    logger.info(f"Updating all catalogs in: {cache_dir}")

    # Update each catalog
    usgs_result = updateUSGSCatalog(minMagnitude=usgs_min_mag)
    gcmt_result = updateGCMTCatalog(minMagnitude=gcmt_min_mag)
    isc_result = updateISCCatalog(minMagnitude=isc_min_mag)

    return {
        "usgs": usgs_result["csv"],
        "gcmt": gcmt_result["csv"],
        "isc": isc_result["csv"],
        "usgs_new": usgs_result["new_events"],
        "gcmt_new": gcmt_result["new_events"],
        "isc_new": isc_result["new_events"],
        "cache_dir": str(cache_dir),
    }
