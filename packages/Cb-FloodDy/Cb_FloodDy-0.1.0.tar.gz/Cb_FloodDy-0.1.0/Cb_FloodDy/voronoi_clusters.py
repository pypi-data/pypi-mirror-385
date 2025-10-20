# Voronoi clusters
import geopandas as gpd
from shapely.geometry import Point, Polygon, MultiPolygon
from shapely.ops import unary_union, cascaded_union
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
import numpy as np
from scipy.spatial import Voronoi
import pandas as pd
import os
from pyproj import CRS

# Set the font to Times New Roman and STIX math font for annotations
plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams["font.size"] = 16
plt.rcParams["mathtext.fontset"] = "stix"
plt.rcParams["font.family"] = "STIXGeneral"

# Function to generate Voronoi polygons and extract empty space polygons within the floodmap boundary
def generate_voronoi_clusters_and_empty_areas(station_coords, floodmap_union):
    vor = Voronoi(station_coords)
    voronoi_polygons = []
    for region_idx in vor.regions:
        if not region_idx or -1 in region_idx:
            continue
        polygon_points = [vor.vertices[i] for i in region_idx]
        voronoi_polygons.append(Polygon(polygon_points))
    clipped_voronoi_polygons = [poly.intersection(floodmap_union) for poly in voronoi_polygons if poly.intersects(floodmap_union)]
    remaining_area = floodmap_union.difference(cascaded_union(clipped_voronoi_polygons))
    if isinstance(remaining_area, MultiPolygon):
        empty_areas = list(remaining_area.geoms)
    else:
        empty_areas = [remaining_area] if not remaining_area.is_empty else []
    return clipped_voronoi_polygons + empty_areas

# Function to reorder polygons so that the polygon number matches the station number
def reorder_polygons_by_station(station_coords, polygons):
    reordered_polygons = []
    for station in station_coords:
        for polygon in polygons:
            if polygon.contains(Point(station)):
                reordered_polygons.append(polygon)
                break
    return reordered_polygons

# Function to combine specified polygons
def combine_specified_polygons(polygons, pairs_to_combine):
    new_polygons = polygons.copy()
    # Sort pairs to combine in reverse order to avoid indexing issues after deletion
    pairs_to_combine = sorted(pairs_to_combine, key=lambda pair: max(pair), reverse=True)
    
    for pair in pairs_to_combine:
        # Perform the union operation
        polygon_union = unary_union([new_polygons[pair[0] - 1], new_polygons[pair[1] - 1]])
        
        # If the result is a MultiPolygon, convert it to individual polygons
        if isinstance(polygon_union, MultiPolygon):
            # Replace the original polygons with individual polygons from the union
            new_polygons[pair[0] - 1] = list(polygon_union.geoms)
        else:
            new_polygons[pair[0] - 1] = polygon_union
        
        # Remove the polygon from the list, ensuring index consistency
        del new_polygons[pair[1] - 1]
    
    # Flatten the list in case we have nested lists
    flat_polygons = []
    for poly in new_polygons:
        if isinstance(poly, list):
            flat_polygons.extend(poly)
        else:
            flat_polygons.append(poly)
    
    return flat_polygons


# Function to save polygons as a shapefile
def save_polygons_as_shapefile(polygons, save_path="reordered_polygons.shp"):
    gdf = gpd.GeoDataFrame(geometry=polygons, crs=CRS.from_epsg(4326))
    gdf.to_file(save_path, driver='ESRI Shapefile')
    print(f"Polygons saved to {save_path}")

# Function to plot the floodmap with Voronoi clusters, empty areas, and labels for each polygon
def plot_floodmap_with_voronoi_and_labels(station_coords, floodmap_union, polygons, longitudes, latitudes, save_path=None):
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_aspect('equal')
    ax.plot(*floodmap_union.exterior.xy, color='black', label='Floodmap Boundary', linewidth=0.75)

    valid_polygons = [polygon for polygon in polygons if polygon.is_valid and not polygon.is_empty]
    total_polygons = len(valid_polygons)
    print(f'Total number of individual polygons in the shapefile: {total_polygons}')

    patches = []
    polygon_counter = 1  # To ensure unique labels for each part of MultiPolygon
    for polygon in valid_polygons:
        # Check if the polygon is a MultiPolygon
        if isinstance(polygon, MultiPolygon):
            # Iterate over its constituent polygons
            for sub_polygon in polygon:
                patches.append(plt.Polygon(list(sub_polygon.exterior.coords)))
                centroid = sub_polygon.centroid
                ax.text(centroid.x, centroid.y, str(polygon_counter), fontsize=12, ha='center', color='black')
                polygon_counter += 1
        else:
            # If it is a single Polygon
            patches.append(plt.Polygon(list(polygon.exterior.coords)))
            centroid = polygon.centroid
            ax.text(centroid.x, centroid.y, str(polygon_counter), fontsize=12, ha='center', color='black')
            polygon_counter += 1

    p = PatchCollection(patches, alpha=0.4, edgecolor='blue', facecolor='lightblue')
    ax.add_collection(p)
    ax.scatter(station_coords[:, 0], station_coords[:, 1], color='red', marker='x', label='Stations')
    ax.set_xticks(longitudes)
    ax.set_yticks(latitudes)
    ax.set_xticklabels([f'{lon:.1f}' for lon in longitudes])
    ax.set_yticklabels([f'{lat:.1f}' for lat in latitudes])

    plt.xlabel('Longitude')
    plt.ylabel('Latitude')

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')

    plt.show()

# Define source CRS (WGS84)
src_crs = CRS.from_epsg(4326)

# Custom ticks for longitude and latitude
longitudes = [-95.5, -95.0, -94.5]
latitudes = [29.0, 29.4, 29.8]

# Directory containing station CSV files
station_dir = 'observation_points'

# Load station data from the station directory (assumed to be in WGS84)
station_files = [os.path.join(station_dir, f'station_{i}.csv') for i in range(1, 22)] 
stations = []
for file in station_files:
    df = pd.read_csv(file)
    stations.append((df['x'].iloc[0], df['y'].iloc[0]))

# Convert station coordinates to a NumPy array
station_coords = np.array(stations)

# Load the floodmap shapefile using geopandas
shapefile_path = 'GBay_cells_polygon.shp'
floodmap = gpd.read_file(shapefile_path)
floodmap_union = unary_union(floodmap.geometry)

# Generate Voronoi clusters and identify empty areas (no unioned polygons)
all_polygons = generate_voronoi_clusters_and_empty_areas(station_coords, floodmap_union)

# If you like to combine specified polygons
# combined_polygons = combine_specified_polygons(all_polygons, [(1, 19), (12, 21), (3, 18)])

# Reorder polygons so that the polygon number corresponds to the station number
reordered_polygons = reorder_polygons_by_station(station_coords, combined_polygons)

# Save the reordered polygons as a shapefile
save_polygons_as_shapefile(reordered_polygons)

# Plot floodmap with reordered polygons, empty areas, and labeled polygons
plot_floodmap_with_voronoi_and_labels(station_coords, floodmap_union, reordered_polygons, longitudes, latitudes, save_path='floodmap_with_voronoi_and_labels_reordered.png')

