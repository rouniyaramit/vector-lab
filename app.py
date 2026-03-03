import os
import streamlit as st
from PIL import Image

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

st.set_page_config(
    page_title="NEA Protection Suite",
    layout="wide",
)

col1, col2 = st.columns([1, 5], vertical_alignment="center")

with col1:
    logo_path = os.path.join(BASE_DIR, "logo.jpg")
    if os.path.exists(logo_path):
        st.image(Image.open(logo_path), width=140)

with col2:
    st.title("NEA Protection & Coordination Tools")
    st.caption("Protection and Automation Division, GOD • Nepal Electricity Authority")

st.divider()

st.subheader("Open Modules")

# Streamlit multipage: pages appear automatically in sidebar.
# This home page provides quick navigation links.

try:
    # Available in newer Streamlit
    st.page_link("pages/1_TCC_Tool.py", label="Open Protection Coordination Tool (TCC Plot)", icon="📈")
    st.page_link("pages/2_OC_EF_Grid.py", label="Open OC / EF Grid Coordination Tool", icon="⚡")
    st.page_link("pages/3_Theory.py", label="Open Protection Theory Guide", icon="📘")
    st.page_link("pages/4_Working.py", label="Open Working Methodology / Manual", icon="🛠️")
except Exception:
    st.info("Use the left sidebar to open pages (Streamlit multipage).")

st.divider()
st.markdown(
    """
    **Notes**
    - Put `logo.jpg` and `sld.png` in the project root (same folder as `app.py`).
    - Run locally: `streamlit run app.py`
    """
)
