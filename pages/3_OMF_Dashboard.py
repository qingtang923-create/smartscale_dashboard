import streamlit as st
import plotly.express as px
from data_utils import load_project_data

st.set_page_config(
    page_title="OMF Dashboard",
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

st.title("OMF Dashboard")


@st.cache_data
def get_data():
    return load_project_data()


def add_count_labels(df, group_col):
    """
    Add sample size n to category labels for boxplots.
    Example: 'Arterial' -> 'Arterial (n=12)'
    """
    counts = df[group_col].value_counts(dropna=False).to_dict()
    df = df.copy()
    df[f"{group_col}_label"] = df[group_col].astype(str).map(
        lambda x: f"{x} (n={counts.get(x, 0)})"
    )
    return df, counts


df = get_data().copy()

# Keep valid rows
df = df[
    (df["AvgDelayBefore"] > 0) &
    (df["AvgSpeedBefore"] > 0) &
    (df["AvgSpeedAfter"] > 0)
].copy()

# Compute OMFs
# Delay OMF: After / Before -> <1 means improvement
df["OMF_delay"] = df["AvgDelayAfter"] / df["AvgDelayBefore"]

# Speed OMF: Before / After -> <1 means improvement
df["OMF_speed"] = df["AvgSpeedBefore"] / df["AvgSpeedAfter"]

# --------------------------------
# 1. Overall project-level summary
# --------------------------------
st.subheader("Overall Project-Level OMF Summary")

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Projects", len(df))
col2.metric("Median Delay OMF", f"{df['OMF_delay'].median():.3f}")
col3.metric("Mean Delay OMF", f"{df['OMF_delay'].mean():.3f}")
col4.metric("Median Speed OMF", f"{df['OMF_speed'].median():.3f}")
col5.metric("Mean Speed OMF", f"{df['OMF_speed'].mean():.3f}")

st.caption(
    "Delay OMF = AvgDelayAfter / AvgDelayBefore; "
    "Speed OMF = AvgSpeedBefore / AvgSpeedAfter. "
    "For both measures, values below 1 indicate improvement."
)

# --------------------------------
# 2. Overall OMF distributions
# --------------------------------
st.subheader("Overall OMF Distributions")

delay_col, delay_box_col = st.columns(2)

with delay_col:
    fig_overall_delay = px.histogram(
        df,
        x="OMF_delay",
        nbins=25,
        title="Distribution of Delay OMF Across All Projects"
    )
    fig_overall_delay.update_layout(
        xaxis_title="Delay OMF",
        yaxis_title="Count"
    )
    st.plotly_chart(fig_overall_delay, use_container_width=True)

with delay_box_col:
    fig_overall_delay_box = px.box(
        df,
        y="OMF_delay",
        points="all",
        title="Boxplot of Delay OMF Across All Projects"
    )
    fig_overall_delay_box.update_layout(
        xaxis_title="All Projects",
        yaxis_title="Delay OMF"
    )
    st.plotly_chart(fig_overall_delay_box, use_container_width=True)

speed_col, speed_box_col = st.columns(2)

with speed_col:
    fig_overall_speed = px.histogram(
        df,
        x="OMF_speed",
        nbins=25,
        title="Distribution of Speed OMF Across All Projects"
    )
    fig_overall_speed.update_layout(
        xaxis_title="Speed OMF",
        yaxis_title="Count"
    )
    st.plotly_chart(fig_overall_speed, use_container_width=True)

with speed_box_col:
    fig_overall_speed_box = px.box(
        df,
        y="OMF_speed",
        points="all",
        title="Boxplot of Speed OMF Across All Projects"
    )
    fig_overall_speed_box.update_layout(
        xaxis_title="All Projects",
        yaxis_title="Speed OMF"
    )
    st.plotly_chart(fig_overall_speed_box, use_container_width=True)

# ---------------------------------------------------
# 3. Delay / Speed OMF by Dominant Improvement Type
# ---------------------------------------------------
st.subheader("Delay OMF by Dominant Improvement Type")

if "DominantImprovementType" in df.columns and df["DominantImprovementType"].notna().any():
    df_dom, dom_counts = add_count_labels(df, "DominantImprovementType")

    fig1 = px.box(
        df_dom,
        x="DominantImprovementType_label",
        y="OMF_delay",
        points="all",
        hover_data=["AppID", "Title", "FacilityType", "DominantImprovementType"]
    )
    fig1.update_layout(
        xaxis_title="Dominant Improvement Type",
        yaxis_title="Delay OMF"
    )
    st.plotly_chart(fig1, use_container_width=True)

    st.write("Sample size by Dominant Improvement Type")
    st.dataframe(
        df["DominantImprovementType"]
        .value_counts()
        .rename_axis("DominantImprovementType")
        .reset_index(name="n"),
        use_container_width=True
    )
else:
    st.warning("DominantImprovementType data not available.")

st.subheader("Speed OMF by Dominant Improvement Type")

if "DominantImprovementType" in df.columns and df["DominantImprovementType"].notna().any():
    df_dom, dom_counts = add_count_labels(df, "DominantImprovementType")

    fig2 = px.box(
        df_dom,
        x="DominantImprovementType_label",
        y="OMF_speed",
        points="all",
        hover_data=["AppID", "Title", "FacilityType", "DominantImprovementType"]
    )
    fig2.update_layout(
        xaxis_title="Dominant Improvement Type",
        yaxis_title="Speed OMF"
    )
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.warning("DominantImprovementType data not available.")

# ----------------------------------------
# 4. Delay / Speed OMF by Facility Type
# ----------------------------------------
st.subheader("Delay OMF by Facility Type")

if "FacilityType" in df.columns and df["FacilityType"].notna().any():
    df_fac, fac_counts = add_count_labels(df, "FacilityType")

    fig3 = px.box(
        df_fac,
        x="FacilityType_label",
        y="OMF_delay",
        points="all",
        hover_data=["AppID", "Title", "FacilityType", "DominantImprovementType"]
    )
    fig3.update_layout(
        xaxis_title="Facility Type",
        yaxis_title="Delay OMF"
    )
    st.plotly_chart(fig3, use_container_width=True)

    st.write("Sample size by Facility Type")
    st.dataframe(
        df["FacilityType"]
        .value_counts()
        .rename_axis("FacilityType")
        .reset_index(name="n"),
        use_container_width=True
    )
else:
    st.warning("FacilityType data not available.")

st.subheader("Speed OMF by Facility Type")

if "FacilityType" in df.columns and df["FacilityType"].notna().any():
    df_fac, fac_counts = add_count_labels(df, "FacilityType")

    fig4 = px.box(
        df_fac,
        x="FacilityType_label",
        y="OMF_speed",
        points="all",
        hover_data=["AppID", "Title", "FacilityType", "DominantImprovementType"]
    )
    fig4.update_layout(
        xaxis_title="Facility Type",
        yaxis_title="Speed OMF"
    )
    st.plotly_chart(fig4, use_container_width=True)
else:
    st.warning("FacilityType data not available.")

# ----------------------------------------
# 5. Baseline Delay vs Delay OMF
# ----------------------------------------
st.subheader("Baseline Delay vs Delay OMF")

color_col = "FacilityType" if "FacilityType" in df.columns else None
fig5 = px.scatter(
    df,
    x="AvgDelayBefore",
    y="OMF_delay",
    color=color_col,
    hover_data=["AppID", "Title", "DominantImprovementType"]
)
fig5.update_layout(
    xaxis_title="Baseline Delay Before",
    yaxis_title="Delay OMF"
)
st.plotly_chart(fig5, use_container_width=True)

# ----------------------------------------
# 6. Single-Treatment Projects Only
# ----------------------------------------
st.subheader("Single-Treatment Projects Only")

if "SingleTreatmentProject" in df.columns:
    df_single = df[df["SingleTreatmentProject"] == "Yes"].copy()

    st.write(f"Single-treatment projects: {len(df_single)}")

    if len(df_single) > 0 and "DominantImprovementType" in df_single.columns:
        df_single_dom, single_counts = add_count_labels(df_single, "DominantImprovementType")

        fig6 = px.box(
            df_single_dom,
            x="DominantImprovementType_label",
            y="OMF_delay",
            points="all",
            hover_data=["AppID", "Title", "FacilityType"]
        )
        fig6.update_layout(
            xaxis_title="Dominant Improvement Type (Single-Treatment Only)",
            yaxis_title="Delay OMF"
        )
        st.plotly_chart(fig6, use_container_width=True)

        st.write("Sample size by Dominant Improvement Type (Single-Treatment Only)")
        st.dataframe(
            df_single["DominantImprovementType"]
            .value_counts()
            .rename_axis("DominantImprovementType")
            .reset_index(name="n"),
            use_container_width=True
        )
    else:
        st.info("No single-treatment projects available.")
else:
    st.warning("SingleTreatmentProject field not available.")
