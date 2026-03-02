import streamlit as st
from PIL import Image
from pathlib import Path

st.set_page_config(
    page_title="NEA Master Protection Tool",
    layout="wide",
    initial_sidebar_state="collapsed",
)

def inject_css():
    st.markdown(
        """
        <style>
        /* Hide Streamlit sidebar (left panel) */
        [data-testid="stSidebar"] {display:none !important;}
        [data-testid="stSidebarNav"] {display:none !important;}

        /* Page padding */
        .block-container {padding-top: 1.0rem;}

        /* Logo box: prevent crop and keep full image visible */
        .logo-wrap{
            width: 260px;
            max-width: 260px;
        }

        /* Uniform "tile" buttons */
        .tile .stButton > button{
            width: 100%;
            height: 64px;                 /* equal height for all 4 */
            border-radius: 16px;
            border: 1px solid rgba(0,0,0,0.10);
            font-size: 16px;
            font-weight: 800;
            color: white;
            background: linear-gradient(135deg, #0b5bd3 0%, #0ea5e9 100%);
            box-shadow: 0 8px 20px rgba(11, 91, 211, 0.18);
            margin: 0 !important;
        }
        .tile .stButton > button:hover{
            transform: translateY(-1px);
            box-shadow: 0 10px 24px rgba(11, 91, 211, 0.28);
        }

        /* Different attractive gradients for each tile */
        .tile-green  .stButton > button{background: linear-gradient(135deg,#0f766e 0%,#22c55e 100%);}
        .tile-purple .stButton > button{background: linear-gradient(135deg,#7c3aed 0%,#ec4899 100%);}
        .tile-orange .stButton > button{background: linear-gradient(135deg,#ea580c 0%,#f59e0b 100%);}

        /* Card container */
        .card{
            border: 1px solid rgba(0,0,0,0.08);
            border-radius: 18px;
            padding: 18px 18px 8px 18px;
            background: #ffffff;
            box-shadow: 0 8px 26px rgba(0,0,0,0.06);
        }

        /* Tighten vertical gaps between rows */
        div[data-testid="column"] {padding-top: 0px;}
        </style>
        """,
        unsafe_allow_html=True
    )

inject_css()

logo_path = Path(__file__).parent / "logo.jpg"

# --- Header row (logo + title) ---
left, right = st.columns([1.2, 3.8], vertical_alignment="center")

with left:
    if logo_path.exists():
        img = Image.open(logo_path)
        # Show full logo without cropping
        st.markdown("<div class='logo-wrap'>", unsafe_allow_html=True)
        st.image(img, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown(
        "<h1 style='margin-bottom:0.2rem;'>NEA Master Protection Tool</h1>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<div style='color:#4b5563;font-weight:600;'>Select a tool below. (Sidebar hidden — navigation is here)</div>",
        unsafe_allow_html=True
    )

st.markdown("<hr/>", unsafe_allow_html=True)

# --- Buttons in a true 2x2 grid (equal layout) ---
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.subheader("Open a tool")

row1_c1, row1_c2 = st.columns(2, gap="large")
with row1_c1:
    st.markdown("<div class='tile'>", unsafe_allow_html=True)
    if st.button("⚡  TCC Plot Tool (Q1–Q5)", use_container_width=True):
        st.switch_page("pages/2_GUI_Final5_TCC.py")
    st.markdown("</div>", unsafe_allow_html=True)

with row1_c2:
    st.markdown("<div class='tile tile-green'>", unsafe_allow_html=True)
    if st.button("🧮  OC/EF Grid Tool", use_container_width=True):
        st.switch_page("pages/3_OC_EF_GOD.py")
    st.markdown("</div>", unsafe_allow_html=True)

row2_c1, row2_c2 = st.columns(2, gap="large")
with row2_c1:
    st.markdown("<div class='tile tile-orange'>", unsafe_allow_html=True)
    if st.button("📘  Theory", use_container_width=True):
        st.switch_page("pages/4_Theory.py")
    st.markdown("</div>", unsafe_allow_html=True)

with row2_c2:
    st.markdown("<div class='tile tile-purple'>", unsafe_allow_html=True)
    if st.button("🛠️  Working", use_container_width=True):
        st.switch_page("pages/5_Working.py")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)
