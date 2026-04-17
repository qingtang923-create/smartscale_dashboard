import json
from pathlib import Path

import pandas as pd
import pydeck as pdk
import streamlit as st

from data_utils import load_project_data

st.title("Congestion Segments Map")

GEOJSON_PATH = Path("data/Cohort3onXD2501.geojson")


@st.cache_data
def load_geojson():
    if not GEOJSON_PATH.exists():
        raise FileNotFoundError(f"GeoJSON not found: {GEOJSON_PATH}")

    with open(GEOJSON_PATH, "r", encoding="utf-8") as f:
        geojson_data = json.load(f)

    return geojson_data


@st.cache_data
def load_feature_table():
    geojson_data = load_geojson()

    rows = []
    for feature in geojson_data.get("features", []):
        props = feature.get("properties", {}).copy()
        rows.append(props)

    df = pd.DataFrame(rows)

    if "SMART_SCALE_ID" in df.columns:
        df["SMART_SCALE_ID"] = df["SMART_SCALE_ID"].astype(str).str.strip()

    return df


@st.cache_data
def load_joined_table():
    gis_df = load_feature_table()
    project_df = load_project_data().copy()

    if "AppID" in project_df.columns:
        project_df["AppID"] = project_df["AppID"].astype(str).str.strip()

    keep_cols = [
        "AppID",
        "Title",
        "District",
        "FacilityType",
        "DominantImprovementType",
        "AllImprovementTypes",
        "ImprovementTypeCount",
        "AvgDelayBefore",
        "AvgDelayAfter",
        "AvgDelayChange",
        "AvgSpeedBefore",
        "AvgSpeedAfter",
        "AvgSpeedChange",
        "PTIChange",
        "DataQualityFlag",
        "ConfounderFlag",
    ]
    keep_cols = [c for c in keep_cols if c in project_df.columns]

    project_info = project_df[keep_cols].drop_duplicates(subset=["AppID"])

    if "SMART_SCALE_ID" in gis_df.columns and "AppID" in project_info.columns:
        gis_df = gis_df.merge(
            project_info,
            left_on="SMART_SCALE_ID",
            right_on="AppID",
            how="left"
        )

    return gis_df


def filter_geojson_by_ids(geojson_data, selected_ids):
    if not selected_ids:
        return geojson_data

    selected_ids = {str(x).strip() for x in selected_ids}

    filtered_features = []
    for feature in geojson_data.get("features", []):
        props = feature.get("properties", {})
        seg_id = str(props.get("SMART_SCALE_ID", "")).strip()
        if seg_id in selected_ids:
            filtered_features.append(feature)

    return {
        "type": "FeatureCollection",
        "features": filtered_features
    }


def extract_bounds(geojson_data):
    minx, miny = float("inf"), float("inf")
    maxx, maxy = float("-inf"), float("-inf")

    for feature in geojson_data.get("features", []):
        geom = feature.get("geometry", {})
        coords = geom.get("coordinates", [])
        geom_type = geom.get("type", "")

        if geom_type == "LineString":
            lines = [coords]
        elif geom_type == "MultiLineString":
            lines = coords
        else:
            continue

        for line in lines:
            for pt in line:
                x, y = pt[0], pt[1]
                minx = min(minx, x)
                miny = min(miny, y)
                maxx = max(maxx, x)
                maxy = max(maxy, y)

    if minx == float("inf"):
        return None

    return [minx, miny, maxx, maxy]


try:
    geojson_data = load_geojson()
    gis_df = load_joined_table()
except Exception as e:
    st.error(f"Failed to load GIS data: {e}")
    st.stop()

st.sidebar.header("GIS Controls")

project_ids = []
if "SMART_SCALE_ID" in gis_df.columns:
    project_ids = sorted(gis_df["SMART_SCALE_ID"].dropna().astype(str).unique().tolist())

selected_project_ids = st.sidebar.multiselect("Project ID", project_ids)

line_width = st.sidebar.slider("Line width", min_value=1, max_value=12, value=4)
show_table = st.sidebar.checkbox("Show attribute table", value=False)
show_no_basemap = st.sidebar.checkbox("Use no basemap (debug)", value=False)

filtered_geojson = filter_geojson_by_ids(geojson_data, selected_project_ids)

filtered_df = gis_df.copy()
if selected_project_ids and "SMART_SCALE_ID" in filtered_df.columns:
    filtered_df = filtered_df[
        filtered_df["SMART_SCALE_ID"].astype(str).isin(selected_project_ids)
    ]

st.write(f"Filtered features: **{len(filtered_geojson.get('features', []))}**")

if len(filtered_geojson.get("features", [])) == 0:
    st.warning("No features match the current filter.")
    st.stop()

bounds = extract_bounds(filtered_geojson)
if bounds is None:
    st.warning("Could not determine bounds from GeoJSON.")
    st.stop()

st.subheader("Debug Information")
st.write(f"Bounds: {bounds}")

minx, miny, maxx, maxy = bounds
center_lon = (minx + maxx) / 2
center_lat = (miny + maxy) / 2

st.write("Map center:", {"latitude": center_lat, "longitude": center_lon})

tooltip_text = "\n".join([
    "Project ID: {SMART_SCALE_ID}",
    "Title: {Title}",
    "District: {District}",
    "FacilityType: {FacilityType}",
    "Dominant Type: {DominantImprovementType}",
    "All Types: {AllImprovementTypes}",
    "Type Count: {ImprovementTypeCount}",
    "Delay Change: {AvgDelayChange}",
    "Speed Change: {AvgSpeedChange}",
    "PTI Change: {PTIChange}",
    "Data Quality: {DataQualityFlag}",
    "Confounder: {ConfounderFlag}",
])

layer = pdk.Layer(
    "GeoJsonLayer",
    data=filtered_geojson,
    pickable=True,
    stroked=True,
    filled=False,
    get_line_color=[255, 0, 0],
    get_line_width=line_width,
    line_width_min_pixels=2,
)

view_state = pdk.ViewState(
    latitude=center_lat,
    longitude=center_lon,
    zoom=6 if not selected_project_ids else 9,
    pitch=0,
)

deck = pdk.Deck(
    map_style=None if show_no_basemap else "light",
    layers=[layer],
    initial_view_state=view_state,
    tooltip={"text": tooltip_text},
)

st.pydeck_chart(deck, use_container_width=True)

if show_table:
    st.subheader("Attribute Table Preview")
    preview_cols = [
        "SMART_SCALE_ID",
        "Title",
        "District",
        "FacilityType",
        "DominantImprovementType",
        "AllImprovementTypes",
        "ImprovementTypeCount",
        "AvgDelayChange",
        "AvgSpeedChange",
        "PTIChange",
    ]
    preview_cols = [c for c in preview_cols if c in filtered_df.columns]
    st.dataframe(filtered_df[preview_cols].head(50), use_container_width=True)
