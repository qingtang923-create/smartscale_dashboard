import streamlit as st

st.set_page_config(
    page_title="SMART SCALE Dashboard",
    layout="wide"
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