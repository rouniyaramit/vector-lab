import streamlit as st
from PIL import Image, ImageOps
from pathlib import Path
import uuid

st.set_page_config(
    page_title="NEA Master Protection Tool",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------- CSS (hide sidebar + style big colored buttons) ----------
st.markdown(
    """
    <style>
    /* Hide Streamlit sidebar (left panel) */
    [data-testid="stSidebar"] {display:none !important;}
    [data-testid="stSidebarNav"] {display:none !important;}

    /* Reduce top padding to avoid any accidental clipping space issues */
    .block-container {padding-top: 0.6rem; padding-bottom: 0.6rem;}

    /* Remove any HR lines */
    hr {display:none !important;}

    /* Make subheader spacing tighter */
    h3 {margin-top: 0.5rem !important;}

    /* BIG button base */
    div.stButton > button {
        width: 100%;
        height: 78px;                 /* bigger */
        border-radius: 18px;
        border: 1px solid rgba(0,0,0,0.10);
        font-size: 20px;              /* bolder text */
        font-weight: 900;             /* extra bold */
        color: #ffffff;
        letter-spacing: 0.2px;
        box-shadow: 0 12px 26px rgba(2, 132, 199, 0.20);
        transition: transform 120ms ease, box-shadow 120ms ease;
        margin: 0 !important;
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 16px 34px rgba(2, 132, 199, 0.30);
        filter: brightness(1.02);
    }

    /* Target specific buttons by key (stable trick using aria-label contains) */
    button[aria-label="⚡  TCC Plot Tool (Q1–Q5)"] { 
        background: linear-gradient(135deg, #0b5bd3 0%, #0ea5e9 100%) !important;
    }
    button[aria-label="🧮  OC/EF Grid Tool"] { 
        background: linear-gradient(135deg, #1d4ed8 0%, #3b82f6 55%, #60a5fa 100%) !important;
    }
    button[aria-label="📘  Theory"] { 
        background: linear-gradient(135deg, #075985 0%, #0284c7 55%, #38bdf8 100%) !important;
    }
    button[aria-label="🛠️  Working"] { 
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 55%, #0b5bd3 100%) !important;
    }

    /* Card look */
    .card{
        border: 1px solid rgba(0,0,0,0.08);
        border-radius: 18px;
        padding: 18px 18px 10px 18px;
        background: #ffffff;
        box-shadow: 0 10px 30px rgba(0,0,0,0.06);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Load logo safely (no cropping) ----------
logo_path = Path(__file__).parent / "logo.jpg"

def load_logo_safe(path: Path, target: int = 170) -> Image.Image | None:
    """
    Ensures the logo is fully visible by:
    - loading safely
    - fitting into a square canvas without cropping
    - adding small padding so top never gets clipped visually
    """
    if not path.exists():
        return None

    img = Image.open(path).convert("RGBA")
    # Add small white border/padding to avoid perceived clipping
    img = ImageOps.expand(img, border=8, fill=(255, 255, 255, 255))
    # Fit into target x target without cropping
    img = ImageOps.contain(img, (target, target))
    return img

# ---------- Header ----------
left, right = st.columns([1.0, 5.0], vertical_alignment="center")

with left:
    logo = load_logo_safe(logo_path, target=170)  # smaller and fully visible
    if logo is not None:
        st.image(logo, width=170)  # fixed width prevents Streamlit weird scaling

with right:
    st.markdown(
        "<h1 style='margin-bottom:0.15rem;'>NEA Master Protection Tool</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div style='color:#4b5563;font-weight:700;margin-top:0.25rem;'>Select a tool below. (Navigation is here)</div>",
        unsafe_allow_html=True,
    )

# ---------- Tools grid ----------
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.subheader("Open a tool")

r1c1, r1c2 = st.columns(2, gap="large")
with r1c1:
    if st.button("⚡  TCC Plot Tool (Q1–Q5)", use_container_width=True, key="btn_tcc"):
        st.switch_page("pages/2_GUI_Final5_TCC.py")

with r1c2:
    if st.button("🧮  OC/EF Grid Tool", use_container_width=True, key="btn_ocef"):
        st.switch_page("pages/3_OC_EF_GOD.py")

r2c1, r2c2 = st.columns(2, gap="large")
with r2c1:
    if st.button("📘  Theory", use_container_width=True, key="btn_theory"):
        st.switch_page("pages/4_Theory.py")

with r2c2:
    if st.button("🛠️  Working", use_container_width=True, key="btn_working"):
        st.switch_page("pages/5_Working.py")

st.markdown("</div>", unsafe_allow_html=True)
