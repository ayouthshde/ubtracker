from pathlib import Path
import geopandas as gpd
import pandas as pd

def preprocess_roads():
    shp_path = Path("data/gis_osm_roads_free_1.shp")

    if not shp_path.exists():
        print(f"File not found: {shp_path}")
        print("Download from: https://download.geofabrik.de/")
        return

    print("Loading shapefile...")
    roads = gpd.read_file(shp_path)
    print(f"Total roads loaded: {len(roads)}")

    if roads.crs is None:
        print("Setting CRS to WGS84 (EPSG:4326)...")
        roads = roads.set_crs("EPSG:4326")

    print("\nFiltering to Ulaanbaatar...")
    if roads.crs.to_string() != "EPSG:4326":
        roads_latlon = roads.to_crs("EPSG:4326")
    else:
        roads_latlon = roads

    ub_minlon = 106.65
    ub_maxlon = 107.15
    ub_minlat = 47.80
    ub_maxlat = 48.00

    bounds = roads_latlon.geometry.bounds

    in_ub = (
        (bounds["minx"] >= ub_minlon)
        & (bounds["maxx"] <= ub_maxlon)
        & (bounds["miny"] >= ub_minlat)
        & (bounds["maxy"] <= ub_maxlat)
    )

    roads = roads[in_ub].copy()
    print(f"Roads in UB: {len(roads)}")
    print("Converting to metric projection (EPSG:3857)...")
    roads = roads.to_crs("EPSG:3857")

    roads["length_m"] = roads.geometry.length

    print("\nFiltering road types...")
    if "fclass" in roads.columns:
        pedestrian = ["footway", "path", "cycleway", "steps", "pedestrian"]
        before = len(roads)
        roads = roads[~roads["fclass"].isin(pedestrian)].copy()
        print(f"Removed pedestrian roads: {before} -> {len(roads)}")

    if "access" in roads.columns:
        before = len(roads)
        roads = roads[roads["access"] != "no"].copy()
        roads = roads[roads["access"] != "private"].copy()
        print(f"Removed restricted roads: {before} -> {len(roads)}")

    if "oneway" in roads.columns:
        print("\nOneway column values:")
        print(roads["oneway"].value_counts(dropna=False))

        roads["is_oneway"] = False
        roads.loc[roads["oneway"] == "F", "is_oneway"] = True

        roads.loc[roads["oneway"] == "yes", "is_oneway"] = True
        roads.loc[roads["oneway"] == "1", "is_oneway"] = True
        roads.loc[roads["oneway"] == "T", "is_oneway"] = True

        print(f"One-way roads: {roads['is_oneway'].sum()}")
    else:
        roads["is_oneway"] = False

    if "maxspeed" in roads.columns:
        roads["speed_kmh"] = pd.to_numeric(roads["maxspeed"], errors="coerce")

        if "fclass" in roads.columns:
            roads.loc[
                (roads["fclass"] == "motorway") & roads["speed_kmh"].isna(),
                "speed_kmh",
            ] = 100
            roads.loc[
                (roads["fclass"] == "trunk") & roads["speed_kmh"].isna(), "speed_kmh"
            ] = 80
            roads.loc[
                (roads["fclass"] == "primary") & roads["speed_kmh"].isna(), "speed_kmh"
            ] = 60
            roads.loc[
                (roads["fclass"] == "secondary") & roads["speed_kmh"].isna(),
                "speed_kmh",
            ] = 50
            roads.loc[
                (roads["fclass"] == "tertiary") & roads["speed_kmh"].isna(), "speed_kmh"
            ] = 40
            roads.loc[
                (roads["fclass"] == "residential") & roads["speed_kmh"].isna(),
                "speed_kmh",
            ] = 30

        roads["speed_kmh"] = roads["speed_kmh"].fillna(30)
    else:
        roads["speed_kmh"] = 30

    columns_to_keep = ["is_oneway", "speed_kmh", "length_m", "geometry"]
    if "fclass" in roads.columns:
        columns_to_keep.insert(0, "fclass")
    if "name" in roads.columns:
        columns_to_keep.insert(0, "name")

    roads = roads[columns_to_keep].copy()
    roads = roads.reset_index(drop=True)

    print("\n" + "=" * 50)
    print("Final Statistics:")
    print("=" * 50)
    print(f"Total roads: {len(roads)}")
    print(f"Total length: {roads['length_m'].sum() / 1000:.1f} km")
    print(f"Average road length: {roads['length_m'].mean():.1f} m")

    if "fclass" in roads.columns:
        print("\nRoad types count:")
        print(roads["fclass"].value_counts())

    print("\nFirst few rows:")
    print(roads.head())

    output_path = Path("data/roads_clean.gpkg")
    output_path.parent.mkdir(exist_ok=True)
    roads.to_file(output_path, driver="GPKG")
    print(f"\nSaved to: {output_path}")

    return roads

if __name__ == "__main__":
    preprocess_roads()