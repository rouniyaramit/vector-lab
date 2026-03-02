import streamlit as st
from pathlib import Path
import base64

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="NEA Master Protection Tool",
    page_icon="⚡",
    layout="wide",
)

# -------------------------------------------------
# HELPERS
# -------------------------------------------------
def get_base64(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

logo_base64 = get_base64("logo.jpg")

# -------------------------------------------------
# CSS STYLING
# -------------------------------------------------
st.markdown(
f"""
<style>

/* Background */
.stApp {{
    background-color: #dfe3e8;
}}

/* Hide Streamlit menu + footer */
#MainMenu {{visibility:hidden;}}
footer {{visibility:hidden;}}

/* Main container */
.block-container {{
    padding-top: 2rem;
    max-width: 1200px;
}}

/* Title section */
.title-box {{
    display:flex;
    align-items:center;
    gap:30px;
}}

.logo-img {{
    width:180px;
    border-radius:12px;
}}

.main-title {{
    font-size:56px;
    font-weight:800;
    color:#0d1b34;
}}

/* Tool buttons */
.tool-btn button {{
    width:100%;
    height:120px;
    border-radius:18px;
    font-size:38px;
    font-weight:700;
    color:white !important;
    border:none;
    box-shadow:0 10px 30px rgba(0,0,0,0.10);
}}

.tool1 button {{
    background: linear-gradient(90deg,#1565d8,#1ea0e0);
}}

.tool2 button {{
    background: linear-gradient(90deg,#2c56d8,#5a96ea);
}}

.tool3 button {{
    background: linear-gradient(90deg,#0f6a9a,#34a7df);
}}

.tool4 button {{
    background: linear-gradient(90deg,#2c61e0,#1d4fcf);
}}

/* Footer */
.footer {{
    text-align:center;
    margin-top:40px;
    font-size:32px;
    color:#5a6475;
    font-style:italic;
}}

</style>
""",
unsafe_allow_html=True,
)

# -------------------------------------------------
# HEADER
# -------------------------------------------------
st.markdown(
f"""
<div class="title-box">
    <img src="data:image/jpg;base64,{logo_base64}" class="logo-img">
    <div class="main-title">NEA Master Protection Tool</div>
</div>
""",
unsafe_allow_html=True,
)

st.markdown("<br>", unsafe_allow_html=True)

# -------------------------------------------------
# OPEN TOOL TITLE
# -------------------------------------------------
st.markdown("## Open a tool")

# -------------------------------------------------
# BUTTON GRID
# -------------------------------------------------
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown('<div class="tool-btn tool1">', unsafe_allow_html=True)
    if st.button("⚡  TCC Plot Tool (Q1–Q5)", key="tcc"):
        st.switch_page("pages/2_GUI_Final5_TCC.py")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="tool-btn tool3">', unsafe_allow_html=True)
    if st.button("📘  Theory", key="theory"):
        st.switch_page("pages/4_Theory.py")
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown('<div class="tool-btn tool2">', unsafe_allow_html=True)
    if st.button("🧮  OC/EF Grid Tool", key="ocef"):
        st.switch_page("pages/3_OC_EF_GOD.py")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="tool-btn tool4">', unsafe_allow_html=True)
    if st.button("🛠️  Working", key="working"):
        st.switch_page("pages/5_Working.py")
    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------
# FOOTER
# -------------------------------------------------
st.markdown(
"""
<div class="footer">
Protection and Automation Division, GOD<br>
Nepal Electricity Authority
</div>
""",
unsafe_allow_html=True,
)
