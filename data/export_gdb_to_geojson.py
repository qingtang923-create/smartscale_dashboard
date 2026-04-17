from pathlib import Path
import geopandas as gpd
from pyogrio import list_layers

gdb_path = Path("data/Cohort3_CongestionSegments.gdb")
layer_name = "Cohort3onXD2501"
out_path = Path("data/Cohort3onXD2501.geojson")

print("Checking GDB:", gdb_path.resolve())
print("Available layers:")
print(list_layers(gdb_path))

gdf = gpd.read_file(gdb_path, layer=layer_name)

print("Rows:", len(gdf))
print("CRS before:", gdf.crs)

if gdf.crs is not None and str(gdf.crs) != "EPSG:4326":
    gdf = gdf.to_crs(epsg=4326)

print("CRS after:", gdf.crs)

gdf.to_file(out_path, driver="GeoJSON")

print(f"Done. Exported to: {out_path.resolve()}")