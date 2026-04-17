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

st.title("Project Detail")

@st.cache_data
def get_data():
    return load_project_data()

df = get_data()

project_ids = df["AppID"].dropna().astype(str).unique().tolist()
selected_id = st.selectbox("Select AppID", sorted(project_ids))

row = df[df["AppID"].astype(str) == selected_id].iloc[0]

st.subheader("Basic Information")
st.write({
    "AppID": row.get("AppID", ""),
    "UPC": row.get("UPC", ""),
    "Title": row.get("Title", ""),
    "Description": row.get("Description", ""),
    "SMART SCALE Round": row.get("SMARTSCALE_Round", ""),
    "Area Type": row.get("AreaType", ""),
    "District": row.get("District", ""),
    "Jurisdiction": row.get("Jurisdiction", ""),
    "Road System": row.get("RoadSystem", ""),
    "Project Category": row.get("ProjectCategory", ""),
    "Construction Begin": row.get("ConstructionBegin", ""),
    "Construction End": row.get("ConstructionEnd", ""),
    "Before Year": row.get("BeforeYear", ""),
    "After Year": row.get("AfterYear", ""),
    "Peak Period": row.get("PeakPeriod", "")
})

st.subheader("Treatment Information")
st.write({
    "Facility Type": row.get("FacilityType", ""),
    "Principal Improvement Type": row.get("PrincipalImprovementType", ""),
    "All Improvement Types": row.get("AllImprovementTypes", ""),
    "Dominant Improvement Type": row.get("DominantImprovementType", ""),
    "Improvement Type Count": row.get("ImprovementTypeCount", ""),
    "Single Treatment Project": row.get("SingleTreatmentProject", "")
})

st.subheader("Traffic and Screening")
st.write({
    "AADT": row.get("AADT", ""),
    "Peak Hour Volume": row.get("PeakHourVolume", ""),
    "Directional Volume": row.get("DirectionalVolume", ""),
    "Data Quality Flag": row.get("DataQualityFlag", ""),
    "Confounder Flag": row.get("ConfounderFlag", ""),
    "Notes": row.get("Notes", "")
})

st.subheader("Observed Before-After Results")
st.write({
    "Average Delay Before": row.get("AvgDelayBefore", ""),
    "Average Delay After": row.get("AvgDelayAfter", ""),
    "Average Delay Change": row.get("AvgDelayChange", ""),
    "Average Speed Before": row.get("AvgSpeedBefore", ""),
    "Average Speed After": row.get("AvgSpeedAfter", ""),
    "Average Speed Change": row.get("AvgSpeedChange", ""),
    "PTI Before": row.get("PTIBefore", ""),
    "PTI After": row.get("PTIAfter", ""),
    "PTI Change": row.get("PTIChange", ""),
    "BTI Before": row.get("BTIBefore", ""),
    "BTI After": row.get("BTIAfter", ""),
    "BTI Change": row.get("BTIChange", ""),
    "TTI Before": row.get("TTIBefore", ""),
    "TTI After": row.get("TTIAfter", ""),
    "TTI Change": row.get("TTIChange", ""),
    "LOTTR Before": row.get("LOTTRBefore", ""),
    "LOTTR After": row.get("LOTTRAfter", ""),
    "LOTTR Change": row.get("LOTTRChange", "")
})

st.subheader("Improvement Matrix")
matrix_cols = [col for col in df.columns if col.startswith(("F_", "A_")) and not col.endswith("_features")]
if matrix_cols:
    st.dataframe(row[matrix_cols].to_frame(name="Value"), use_container_width=True)

st.subheader("Improvement Features")
feature_cols = [col for col in df.columns if col.endswith("_features")]
feature_data = {col: row.get(col, "") for col in feature_cols if str(row.get(col, "")).strip() not in ["", "nan", "None"]}
if feature_data:
    st.write(feature_data)
else:
    st.info("No feature descriptions available for this project.")
