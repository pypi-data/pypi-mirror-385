# kashima/mapper/event_map.py   •   2025‑06‑24 stable
from __future__ import annotations
import logging
import math
from pathlib import Path

import folium
import branca
import numpy as np
import pandas as pd
from pyproj import Transformer
from .layers.site_marker import SiteMarkerLayer  # ← add this line

from .config import (
    MapConfig,
    EventConfig,
    FaultConfig,
    StationConfig,
    TILE_LAYER_CONFIGS,
)
from .utils import (
    great_circle_bbox,
    stream_read_csv_bbox,
    load_faults,
    load_stations_csv,
    calculate_distances_vectorized,
    classify_fault_style,
)
from .isc_catalog import load_isc
from .layers import (
    EventMarkerLayer,
    BeachballLayer,
    HeatmapLayer,
    FaultLayer,
    StationLayer,
    EpicentralCirclesLayer,
)

logger = logging.getLogger(__name__)


class EventMap:
    """
    Folium map builder — includes coloured circles, heatmap, beachballs,
    distances, faults, stations, and tile‑layer control.

    *XY back‑compat*: pass `x_col`, `y_col`, `location_crs` if your CSV
    stores projected coordinates (e.g. blasting events).
    """

    # ────────────────────────────────────────────────────────────────
    def __init__(
        self,
        map_config: MapConfig,
        event_config: EventConfig,
        *,
        events_csv: str | Path,
        legend_map: dict[str, str] | None = None,
        isc_csv: str | None = None,
        gcmt_csv: str | None = None,
        mandatory_mag_col: str = "mag",
        calculate_distance: bool = True,
        fault_config: FaultConfig | None = None,
        station_config: StationConfig | None = None,
        tooltip_fields: list[str] | None = None,
        # XY → lat/lon support
        x_col: str | None = None,
        y_col: str | None = None,
        location_crs: str = "EPSG:4326",
        log_level: int = logging.INFO,
    ):
        logger.setLevel(log_level)

        # configs & paths
        self.mc, self.ec = map_config, event_config
        self.fc, self.sc = fault_config, station_config
        self.events_csv = Path(events_csv)
        self.isc_csv = Path(isc_csv) if isc_csv else None
        self.gcmt_csv = Path(gcmt_csv) if gcmt_csv else None
        self.legend_map = legend_map or {}

        # behaviour
        self.mandatory_mag_col = mandatory_mag_col
        self.calculate_distance = calculate_distance
        self.tooltip_fields = tooltip_fields or ["place"]

        # XY support
        self.x_col, self.y_col = x_col, y_col
        self.location_crs = location_crs

        # runtime holders
        self.events_df: pd.DataFrame = pd.DataFrame()
        self.faults_gdf = None
        self.stations_df = pd.DataFrame()
        self.color_map = None
        self._loaded = False

    # ======================= PUBLIC API ==============================
    def loadData(self):
        if not self._loaded:
            self._load_everything()


    # -----------------------------------------------------------------
    #  Public: build the Folium map with all configured layers
    # -----------------------------------------------------------------
    def getMap(self) -> folium.Map:
        """
        Assemble and return a Folium map that contains every layer
        specified by the current EventMap configuration:

        • Circle markers (USGS / ISC events)                     – EventMarkerLayer
        • Beach‑ball focal mechanisms                            – BeachballLayer
        • Magnitude‑weighted heat‑map                            – HeatmapLayer
        • Active faults (GEM)                                    – FaultLayer
        • Seismic stations (optional)                            – StationLayer
        • Concentric epicentral distance rings                   – EpicentralCirclesLayer
        • Site (project centre) marker                           – SiteMarkerLayer
        • Full base‑map tile set + magnitude legend + layer ctrl
        """
        # ------------------------------------------------------ data
        if not self._loaded:                # lazy initialisation
            self._load_everything()

        # ------------------------------------------------------ base map
        m = folium.Map(
            location=[self.mc.latitude, self.mc.longitude],
            zoom_start=self.mc.base_zoom_level,
            min_zoom=self.mc.min_zoom_level,
            max_zoom=self.mc.max_zoom_level,
            control_scale=True,
        )

        # ------------------------------------------------------ markers
        EventMarkerLayer(
            self.events_df,
            event_cfg=self.ec,
            legend_map=self.legend_map,
            tooltip_fields=self.tooltip_fields,
            clustered=self.ec.show_cluster_default,
            show=self.ec.show_events_default,
        ).toFeatureGroup().add_to(m)

        # -------------------- beach‑balls ----------------------------------
        bb_df = self.events_df
        if self.ec.beachball_min_magnitude is not None:
            bb_df = bb_df[bb_df[self.mandatory_mag_col] >= self.ec.beachball_min_magnitude]

        BeachballLayer(
            bb_df,
            show=self.ec.show_beachballs_default,
            fault_style_meta=self.ec.fault_style_meta,  # ← NEW
            mag_bins=self.ec.mag_bins,
            size_map=self.ec.beachball_sizes,
            vmin=self.ec.vmin,
            scaling_factor=self.ec.scaling_factor,
        ).toFeatureGroup().add_to(m)

        # ------------------------------------------------------ heat‑map
        HeatmapLayer(
            self.events_df,
            radius=self.ec.heatmap_radius,
            blur=self.ec.heatmap_blur,
            min_opacity=self.ec.heatmap_min_opacity,
            show=self.ec.show_heatmap_default,
        ).toFeatureGroup().add_to(m)

        # ------------------------------------------------------ faults & stations
        if self.faults_gdf is not None:
            FaultLayer(
                self.faults_gdf,
                color=self.fc.regional_faults_color,
                weight=self.fc.regional_faults_weight,
                show=self.fc.include_faults,
            ).toFeatureGroup().add_to(m)

        if not self.stations_df.empty:
            StationLayer(self.stations_df).toFeatureGroup().add_to(m)

        # ------------------------------------------------------ epicentral rings + site marker
        EpicentralCirclesLayer(
            self.mc.latitude,
            self.mc.longitude,
            self.mc.radius_km,
            n_circles=self.mc.epicentral_circles,
            show=self.ec.show_epicentral_circles_default,
        ).toFeatureGroup().add_to(m)

        SiteMarkerLayer(
            self.mc.latitude,
            self.mc.longitude,
            self.mc.project_name,
            self.mc.client,
        ).toFeatureGroup().add_to(m)

        # ------------------------------------------------------ tiles, legend, control
        self._add_tile_layers(m)
        if self.color_map is not None:
            self.color_map.position = self.ec.legend_position.lower()
            self.color_map.caption = self.ec.legend_title
            self.color_map.add_to(m)

        folium.LayerControl().add_to(m)
        return m

    # ======================= INTERNALS ===============================
    def _load_everything(self):
        logger.info("Loading catalogues and auxiliary data …")

        bbox = great_circle_bbox(
            self.mc.longitude,
            self.mc.latitude,
            self.mc.radius_km * (self.ec.event_radius_multiplier or 1.0),
        )

        frames: list[pd.DataFrame] = []
        if self.events_csv.exists():
            df = stream_read_csv_bbox(self.events_csv, bbox=bbox)
            if not df.empty and "time" in df.columns:
                df["time"] = pd.to_datetime(df["time"], format='mixed')
                frames.append(df)
        if self.isc_csv and self.isc_csv.exists():
            df = stream_read_csv_bbox(self.isc_csv, bbox=bbox)
            if not df.empty and "time" in df.columns:
                df["time"] = pd.to_datetime(df["time"], format='mixed')
                frames.append(df)
        if self.gcmt_csv and self.gcmt_csv.exists():
            df = stream_read_csv_bbox(self.gcmt_csv, bbox=bbox)
            if not df.empty and "time" in df.columns:
                df["time"] = pd.to_datetime(df["time"], format='mixed')
                frames.append(df)

        if not frames:
            raise RuntimeError("No catalogue data found.")

        self.events_df = pd.concat(frames, ignore_index=True)

        # ---- XY → lat/lon conversion (if requested) ------------------
        if (
            self.x_col
            and self.y_col
            and "latitude" not in self.events_df.columns
            and self.x_col in self.events_df.columns
            and self.y_col in self.events_df.columns
        ):
            logger.info(
                "Converting %s/%s from %s to WGS84 …",
                self.x_col,
                self.y_col,
                self.location_crs,
            )
            tf = Transformer.from_crs(self.location_crs, "EPSG:4326", always_xy=True)
            lon, lat = tf.transform(
                self.events_df[self.x_col].values,
                self.events_df[self.y_col].values,
            )
            self.events_df["longitude"] = lon
            self.events_df["latitude"] = lat

        self._postprocess_events()
        self._build_colormap()
        self._load_faults()
        self._load_stations()
        self._loaded = True
        logger.info("Data loaded: %d events", len(self.events_df))

    # -----------------------------------------------------------------
    def _postprocess_events(self):
        # numeric magnitude
        self.events_df[self.mandatory_mag_col] = pd.to_numeric(
            self.events_df[self.mandatory_mag_col], errors="coerce"
        )
        self.events_df.dropna(subset=[self.mandatory_mag_col], inplace=True)

        # distance filter
        if self.calculate_distance:
            calculate_distances_vectorized(
                self.events_df,
                self.mc.latitude,
                self.mc.longitude,
                out_col="Repi",
            )
            lim = self.mc.radius_km * (self.ec.event_radius_multiplier or 1.0)
            self.events_df = self.events_df[self.events_df["Repi"] <= lim]

        # magnitude filter
        if self.ec.vmin is not None:
            self.events_df = self.events_df[
                self.events_df[self.mandatory_mag_col] >= self.ec.vmin
            ]
        if self.ec.vmax is not None:
            self.events_df = self.events_df[
                self.events_df[self.mandatory_mag_col] <= self.ec.vmax
            ]

        # fault‑style classification
        self.events_df["fault_style"] = self.events_df.apply(
            lambda r: classify_fault_style(
                r.mrr, r.mtt, r.mpp, r.mrt, r.mrp, r.mtp, source=r.get("source")
            ),
            axis=1,
        )

    # -----------------------------------------------------------------
    def _build_colormap(self):
        import matplotlib.pyplot as plt

        mags = self.events_df[self.mandatory_mag_col]
        vmin = self.ec.vmin or math.floor(mags.min() * 2) / 2
        vmax = self.ec.vmax or math.ceil(mags.max() * 2) / 2
        cmap = plt.get_cmap(self.ec.color_palette)
        if self.ec.color_reversed:
            cmap = cmap.reversed()
        colors = [cmap(i / cmap.N) for i in range(cmap.N)]
        self.color_map = branca.colormap.LinearColormap(colors, vmin=vmin, vmax=vmax)
        self.color_map.caption = self.ec.legend_title or "Magnitude"

    # -----------------------------------------------------------------
    def _load_faults(self):
        if not (self.fc and self.fc.include_faults):
            return
        try:
            self.faults_gdf = load_faults(
                self.fc.faults_gem_file_path, self.fc.coordinate_system
            )
        except Exception as e:
            logger.warning("Faults loading failed: %s", e)

    # -----------------------------------------------------------------
    def _load_stations(self):
        if not (self.sc and self.sc.station_file_path):
            return
        try:
            self.stations_df = load_stations_csv(
                self.sc.station_file_path, self.sc.coordinate_system
            )
        except Exception as e:
            logger.warning("Stations loading failed: %s", e)

    # -----------------------------------------------------------------
    def _add_tile_layers(self, m: folium.Map):
        default = self.mc.default_tile_layer
        for name, cfg in TILE_LAYER_CONFIGS.items():
            folium.TileLayer(
                tiles=cfg["tiles"],
                attr=cfg["attr"],
                name=name,
                control=True,
                max_zoom=self.mc.max_zoom_level,
                min_zoom=self.mc.min_zoom_level,
                show=(name == default),
            ).add_to(m)
