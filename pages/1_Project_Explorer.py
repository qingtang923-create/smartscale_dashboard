import streamlit as st
from data_utils import load_project_data

st.set_page_config(
    page_title="SMART SCALE Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .block-container {
        max-width: 100% !important;
        padding-top: 1rem;
        padding-right: 1rem;
        padding-left: 1rem;
        padding-bottom: 0.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Project Explorer")


@st.cache_data
def get_data():
    return load_project_data()


def get_all_improvement_type_options(df):
    """
    Build a unique sorted list of all improvement types from the
    semicolon-separated AllImprovementTypes column.
    """
    if "AllImprovementTypes" not in df.columns:
        return []

    values = (
        df["AllImprovementTypes"]
        .dropna()
        .astype(str)
        .tolist()
    )

    items = []
    for val in values:
        parts = [x.strip() for x in val.split(";") if x.strip()]
        items.extend(parts)

    return sorted(set(items))


df = get_data()

st.sidebar.header("Filters")

# District
districts = sorted(df["District"].dropna().astype(str).unique()) if "District" in df.columns else []
selected_districts = st.sidebar.multiselect("District", districts)

# Facility Type
facility_types = sorted(df["FacilityType"].dropna().astype(str).unique()) if "FacilityType" in df.columns else []
selected_facility_types = st.sidebar.multiselect("Facility Type", facility_types)

# Dominant Improvement Type
dominant_types = sorted(df["DominantImprovementType"].dropna().astype(str).unique()) if "DominantImprovementType" in df.columns else []
selected_dominant_types = st.sidebar.multiselect("Dominant Improvement Type", dominant_types)

# Contains Improvement Type
all_type_options = get_all_improvement_type_options(df)
selected_contains_types = st.sidebar.multiselect("Contains Improvement Type", all_type_options)

# Improvement Type Count
if "ImprovementTypeCount" in df.columns:
    count_values = sorted(df["ImprovementTypeCount"].dropna().astype(int).unique().tolist())
else:
    count_values = []
selected_counts = st.sidebar.multiselect("Improvement Type Count", count_values)

# Data Quality
quality = sorted(df["DataQualityFlag"].dropna().astype(str).unique()) if "DataQualityFlag" in df.columns else []
selected_quality = st.sidebar.multiselect("Data Quality", quality)

filtered = df.copy()

if selected_districts:
    filtered = filtered[filtered["District"].astype(str).isin(selected_districts)]

if selected_facility_types:
    filtered = filtered[filtered["FacilityType"].astype(str).isin(selected_facility_types)]

if selected_dominant_types:
    filtered = filtered[filtered["DominantImprovementType"].astype(str).isin(selected_dominant_types)]

if selected_counts:
    filtered = filtered[filtered["ImprovementTypeCount"].astype("Int64").isin(selected_counts)]

if selected_quality:
    filtered = filtered[filtered["DataQualityFlag"].astype(str).isin(selected_quality)]

# Filter by whether AllImprovementTypes contains ALL selected types
if selected_contains_types and "AllImprovementTypes" in filtered.columns:
    def contains_all_types(val):
        if val is None:
            return False
        val_str = str(val)
        item_set = {x.strip() for x in val_str.split(";") if x.strip()}
        return all(t in item_set for t in selected_contains_types)

    filtered = filtered[filtered["AllImprovementTypes"].apply(contains_all_types)]

st.write(f"Projects shown: {len(filtered)}")

display_cols = [
    "AppID",
    "Title",
    "District",
    "FacilityType",
    "AllImprovementTypes",
    "DominantImprovementType",
    "ImprovementTypeCount",
    "AvgDelayChange",
    "AvgSpeedChange",
    "PTIChange",
    "DataQualityFlag",
    "ConfounderFlag"
]

display_cols = [col for col in display_cols if col in filtered.columns]

st.dataframe(filtered[display_cols], use_container_width=True)
