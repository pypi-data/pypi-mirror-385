
"""
Voronoi cluster utilities for Cb_FloodDy.

Key functions:
- load_station_points(station_dir, start_idx, end_idx) -> list[(lon, lat)]
- load_floodmap(shapefile_path) -> (gdf, boundary_union)
- build_voronoi(stations, boundary_union) -> list[Polygon]
- combine_specified_polygons(polys, pairs) -> list[Polygon]
- plot_voronoi_on_floodmap(...)
- run_workflow(...)  # end-to-end helper

Import usage:
    from Cb_FloodDy.voronoi_clusters import run_workflow, combine_specified_polygons
or
    from Cb_FloodDy import voronoi_clusters as vc
    vc.run_workflow(...)
"""

from __future__ import annotations
import os
from typing import Iterable, List, Sequence, Tuple, Optional

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import Point, Polygon, MultiPolygon
from shapely.ops import unary_union, polygonize
from scipy.spatial import Voronoi
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
from pyproj import CRS

__all__ = [
    "load_station_points",
    "load_floodmap",
    "build_voronoi",
    "combine_specified_polygons",
    "plot_voronoi_on_floodmap",
    "save_polygons_as_shapefile",
    "run_workflow",
    "reorder_polygons_by_station",
]


# ------------------------------
# Reordering helper (match polygon index to station index)
# ------------------------------

def reorder_polygons_by_station(station_coords: Sequence[Tuple[float, float]],
                                polygons: Sequence[Polygon],
                                epsilon: float = 1e-9) -> List[Polygon]:
    """
    Reorder polygons so polygon i corresponds to station i (1-based in plotting, 0-based here).
    Strategy:
      1) Prefer polygons that contain (or nearly contain via small buffer) the station point.
      2) If none contain, choose the nearest remaining polygon by distance.
      3) Ensure polygons are not duplicated (one-to-one assignment).
    """
    from shapely.geometry import Point
    import numpy as np

    remaining = list(range(len(polygons)))
    ordered: List[Polygon] = []

    for (lon, lat) in station_coords:
        pt = Point(lon, lat)

        # First pass: containment check among remaining
        found_idx = None
        for idx in remaining:
            poly = polygons[idx]
            if poly.contains(pt) or poly.buffer(epsilon).contains(pt) or poly.covers(pt):
                found_idx = idx
                break

        # Fallback: nearest polygon among remaining
        if found_idx is None:
            dists = [(idx, polygons[idx].distance(pt)) for idx in remaining]
            dists.sort(key=lambda t: t[1])
            found_idx = dists[0][0]

        ordered.append(polygons[found_idx])
        remaining.remove(found_idx)

        if not remaining:
            # If stations > polygons, stop once we run out
            break

    return ordered
# ------------------------------
# Loading utilities
# ------------------------------

def _pick(series: pd.Series, names: Sequence[str]) -> pd.Series:
    for n in names:
        if n in series.index:
            return series[n]
    raise KeyError(f"None of expected columns {names} found in: {list(series.index)}")

def load_station_points(
    station_dir: str,
    start_idx: int,
    end_idx: int,
    lon_name: str | None = None,
    lat_name: str | None = None,
) -> List[Tuple[float, float]]:
    """
    Load station points from CSV files named station_#.csv (inclusive range).
    - Auto-detects lon/lat columns (case-insensitive, tolerant to variants).
    - You can force column names via lon_name/lat_name.
    """
    import re

    def normalize(name: str) -> str:
        # lower + strip spaces/punctuation so "Longitude (deg)" -> "longitudedeg"
        return re.sub(r"[^a-z0-9]+", "", name.lower())

    stations: List[Tuple[float, float]] = []
    for i in range(start_idx, end_idx + 1):
        path = os.path.join(station_dir, f"station_{i}.csv")
        if not os.path.exists(path):
            raise FileNotFoundError(f"Missing station file: {path}")

        df = pd.read_csv(path)

        # Build normalized map: "longitude" -> "Longitude (deg)" (original)
        norm_map = {normalize(c): c for c in df.columns}

        def find_col(preferred: list[str], fallback_contains: list[str]) -> str | None:
            # 1) exact (normalized) matches
            for key in preferred:
                key_n = normalize(key)
                if key_n in norm_map:
                    return norm_map[key_n]
            # 2) partial (normalized) contains
            for k_norm, orig in norm_map.items():
                if any(sub in k_norm for sub in fallback_contains):
                    return orig
            return None

        # If explicit names provided, try those first
        if lon_name:
            lon_col = df.columns[df.columns.str.lower() == lon_name.lower()]
            lon_col = lon_col[0] if len(lon_col) else None
        else:
            lon_col = find_col(
                preferred=["lon", "longitude", "x", "long"],
                fallback_contains=["lon", "long", "longitude", "coordx", "x"],
            )

        if lat_name:
            lat_col = df.columns[df.columns.str.lower() == lat_name.lower()]
            lat_col = lat_col[0] if len(lat_col) else None
        else:
            lat_col = find_col(
                preferred=["lat", "latitude", "y"],
                fallback_contains=["lat", "latitude", "coordy", "y"],
            )

        if not lon_col or not lat_col:
            raise KeyError(
                "Could not detect lon/lat columns in "
                f"{path}. Found columns: {list(df.columns)}. "
                "Try passing explicit lon_name=... and lat_name=...."
            )

        # Take the first row in each file (adjust if your CSVs have multiple rows per station)
        row = df.iloc[0]
        stations.append((float(row[lon_col]), float(row[lat_col])))

    return stations

def load_floodmap(shapefile_path: str):
    """Read a polygonal domain shapefile and return (GeoDataFrame, unary_union boundary polygon)."""
    gdf = gpd.read_file(shapefile_path)
    # dissolve to single geometry
    union = gdf.unary_union
    if union.geom_type == "MultiPolygon":
        boundary = MultiPolygon([p for p in union.geoms])
    else:
        boundary = union
    return gdf, boundary

# ------------------------------
# Voronoi construction & helpers
# ------------------------------

def _finite_polygons_2d(vor: Voronoi, radius: float = 1e6):
    """
    Reconstruct infinite Voronoi regions to finite regions.
    Adapted from https://stackoverflow.com/a/20678647
    """
    new_regions = []
    new_vertices = vor.vertices.tolist()

    center = vor.points.mean(axis=0)
    if vor.points.ptp().max() == 0:
        # all points identical—return empty
        return [], np.asarray(new_vertices)

    # Map ridge points to ridges
    all_ridges = {}
    for (p1, p2), (v1, v2) in zip(vor.ridge_points, vor.ridge_vertices):
        all_ridges.setdefault(p1, []).append((p2, v1, v2))
        all_ridges.setdefault(p2, []).append((p1, v1, v2))

    # Reconstruct each region
    for p1, region_idx in enumerate(vor.point_region):
        vertices = vor.regions[region_idx]
        if -1 not in vertices:
            # finite
            new_regions.append(vertices)
            continue

        # reconstruct non-finite region
        ridges = all_ridges[p1]
        new_region = [v for v in vertices if v != -1]

        for p2, v1, v2 in ridges:
            if v2 == -1 or v1 == -1:
                v_finite = v1 if v1 != -1 else v2
                t = vor.points[p2] - vor.points[p1]  # tangent
                t /= np.linalg.norm(t)
                n = np.array([-t[1], t[0]])  # normal
                midpoint = vor.points[[p1, p2]].mean(axis=0)
                direction = np.sign(np.dot(midpoint - center, n)) * n
                far_point = vor.vertices[v_finite] + direction * radius
                new_vertices.append(far_point.tolist())
                new_region.append(len(new_vertices) - 1)

        # sort region counterclockwise
        vs = np.asarray([new_vertices[v] for v in new_region])
        c = vs.mean(axis=0)
        angles = np.arctan2(vs[:, 1] - c[1], vs[:, 0] - c[0])
        new_region = [v for _, v in sorted(zip(angles, new_region))]
        new_regions.append(new_region)

    return new_regions, np.asarray(new_vertices)

def build_voronoi(stations: Sequence[Tuple[float, float]], boundary_union) -> List[Polygon]:
    """Compute Voronoi polygons from station points and clip them to boundary_union."""
    pts = np.array(stations)
    vor = Voronoi(pts)
    regions, vertices = _finite_polygons_2d(vor)
    polys: List[Polygon] = []
    for region in regions:
        polygon = Polygon(vertices[region])
        clipped = polygon.intersection(boundary_union)
        if not clipped.is_empty:
            if clipped.geom_type == "MultiPolygon":
                # keep the largest piece
                parts = list(clipped.geoms)
                parts.sort(key=lambda p: p.area, reverse=True)
                polys.append(parts[0])
            else:
                polys.append(clipped)
    return polys

def combine_specified_polygons(polygons: Sequence[Polygon],
                               pairs_to_combine: Sequence[Tuple[int, int]]) -> List[Polygon]:
    """
    Combine (union) specified polygon indices (1-based) into fewer polygons.
    Example pairs_to_combine = [(1, 19), (12, 21), (3, 18)]
    Any non-mentioned polygons remain as-is.
    """
    from collections import defaultdict
    n = len(polygons)
    used = set()
    buckets = defaultdict(list)

    # Build groups (1-based -> 0-based)
    for a, b in pairs_to_combine:
        buckets[min(a, b)].extend([a - 1, b - 1])
        used.update([a - 1, b - 1])

    combined: List[Polygon] = []
    # combine groups
    for _, idxs in buckets.items():
        geoms = [polygons[i] for i in sorted(set(idxs)) if 0 <= i < n]
        union = geoms[0]
        for g in geoms[1:]:
            union = union.union(g)
        combined.append(union)

    # keep leftovers
    for i, poly in enumerate(polygons):
        if i not in used:
            combined.append(poly)
    return combined

# ------------------------------
# Output helpers
# ------------------------------

def save_polygons_as_shapefile(polygons: Sequence[Polygon],
                               crs: CRS,
                               out_path: str):
    gdf = gpd.GeoDataFrame({"id": list(range(1, len(polygons) + 1))},
                           geometry=polygons, crs=crs)
    gdf.to_file(out_path)

def plot_voronoi_on_floodmap(stations: Sequence[Tuple[float, float]],
                             flood_gdf: gpd.GeoDataFrame,
                             polygons: Sequence[Polygon],
                             src_crs: CRS,
                             x_ticks: Optional[Sequence[float]] = None,
                             y_ticks: Optional[Sequence[float]] = None,
                             save_path: Optional[str] = None):
    fig, ax = plt.subplots(figsize=(10, 10))
    flood_gdf.plot(ax=ax, facecolor="none", edgecolor="black", linewidth=0.6)

    # draw voronoi cells
    patches = [plt.Polygon(np.asarray(p.exterior.coords)) for p in polygons]
    pc = PatchCollection(patches, alpha=0.3, edgecolor="red", facecolor="lightblue", linewidths=0.8)
    ax.add_collection(pc)

    # draw stations
    xs = [p[0] for p in stations]
    ys = [p[1] for p in stations]
    ax.scatter(xs, ys, s=10, marker="o")

    # label stations (1-based)
    for i, (x, y) in enumerate(stations, start=1):
        ax.text(x, y, str(i), fontsize=12, ha="center", va="top")

    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")

    if x_ticks is not None:
        ax.set_xticks(list(x_ticks))
    if y_ticks is not None:
        ax.set_yticks(list(y_ticks))

    ax.set_aspect("equal", adjustable="box")
    if save_path:
        out_dir = os.path.dirname(save_path)
        if out_dir and not os.path.exists(out_dir):
            os.makedirs(out_dir, exist_ok=True)
        fig.savefig(save_path, dpi=300, bbox_inches="tight")
    return fig, ax

# ------------------------------
# End-to-end workflow
# ------------------------------

def run_workflow(
    src_crs: CRS,
    station_dir: str,
    station_range: Tuple[int, int],
    shapefile_path: str,
    combine_pairs: Optional[Sequence[Tuple[int, int]]] = None,
    x_ticks: Optional[Sequence[float]] = None,
    y_ticks: Optional[Sequence[float]] = None,
    out_shapefile: Optional[str] = None,
    out_fig: Optional[str] = None,
    reorder_by_station: bool = True,
    lon_name: str | None = None,   
    lat_name: str | None = None,
):
    """
    Execute the full workflow and return artifacts for further use.
    """
    # load inputs
    stations = load_station_points(station_dir, station_range[0], station_range[1], lon_name=lon_name, lat_name=lat_name)
    flood_gdf, boundary = load_floodmap(shapefile_path)

    # build voronoi
    polys = build_voronoi(stations, boundary)

    # optionally combine
    if combine_pairs:
        polys = combine_specified_polygons(polys, combine_pairs)

    # optional reorder so polygon index matches station index
    if reorder_by_station:
        polys = reorder_polygons_by_station(stations, polys)

    # save outputs
    if out_shapefile:
        save_polygons_as_shapefile(polys, crs=src_crs, out_path=out_shapefile)
    fig = None
    if out_fig:
        fig, _ = plot_voronoi_on_floodmap(
            stations, flood_gdf, polys, src_crs, x_ticks, y_ticks, save_path=out_fig
        )
    return {
        "stations": stations,
        "polygons": polys,
        "flood_gdf": flood_gdf,
        "figure_saved": out_fig if out_fig else None,
        "shapefile_saved": out_shapefile if out_shapefile else None,
    }

if __name__ == "__main__":
    # Example (adjust paths before running as a script)
    _src_crs = CRS.from_epsg(4326)
    _station_dir = "training_water_level"
    _shapefile_path = "GBay_cells_polygon.shp"
    _combine_pairs = [(1, 19), (12, 21), (3, 18)]
    _longitudes = [-95.5, -95.0, -94.5]
    _latitudes = [29.0, 29.4, 29.8]

    run_workflow(
        src_crs=_src_crs,
        station_dir=_station_dir,
        station_range=(1, 21),  # inclusive
        shapefile_path=_shapefile_path,
        combine_pairs=_combine_pairs,
        x_ticks=_longitudes,
        y_ticks=_latitudes,
        out_shapefile="voronoi_clusters.shp",
        out_fig="voronoi_map.png",
    )
