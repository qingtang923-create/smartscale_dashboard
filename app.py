import streamlit as st

st.set_page_config(
    page_title="SMART SCALE Dashboard",
    layout="wide"
)

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

st.title("SMART SCALE Project Dashboard")
st.markdown("""
This dashboard is used to:
- explore projects,
- review before-after results,
- compare observed outcomes with SMART SCALE estimates,
- examine OMF patterns.
""")

st.info("Use the pages in the left sidebar to navigate.")
