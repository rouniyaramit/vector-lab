import os
import streamlit as st
from PIL import Image, ImageEnhance

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

st.set_page_config(
    page_title="NEA Protection Master Launcher",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -------------------- CSS: remove sidebar, header (share/menu), and the "red dot" artifacts --------------------
st.markdown(
    """
    <style>
    /* Hide sidebar completely */
    [data-testid="stSidebar"] {display: none !important;}
    [data-testid="collapsedControl"] {display: none !important;}

    /* Hide Streamlit Cloud top bar (Share, GitHub, menu) */
    [data-testid="stHeader"] {display: none !important;}
    header {display: none !important;}

    /* Hide footer + menu */
    footer {display: none !important;}
    #MainMenu {visibility: hidden;}

    /* Fix top spacing so logo never gets cut */
    .block-container {
        padding-top: 2.6rem !important;
        padding-bottom: 2.4rem !important;
        max-width: 1150px;
    }

    /* Remove weird anchor/link icons (sometimes appear near top) */
    a[href^="#"] {display: none !important;}
    [data-testid="stDecoration"] {display:none !important;}

    /* Center everything */
    .nea-center {text-align: center;}

    /* Logo styling (no fade) */
    .nea-logo-wrap{
        display:flex;
        justify-content:center;
        align-items:center;
        margin-top: 4px;
        margin-bottom: 16px;
    }
    .nea-logo-frame{
        display:inline-flex;
        padding: 10px;
        border-radius: 16px;
        border: 2px solid rgba(220, 38, 38, 0.85);
        background: #ffffff;
        box-shadow: 0 14px 30px rgba(0,0,0,0.10);
    }

    /* Title */
    .nea-title {
        font-size: 46px;
        font-weight: 900;
        margin: 6px 0 12px 0;
        color: #111827;
        letter-spacing: 0.2px;
    }

    /* Divider spacing */
    hr {margin: 18px 0 24px 0 !important;}

    /* TAB container */
    .tabs-grid{
        display:flex;
        flex-direction:column;
        gap:18px;
        align-items:center;
        margin-top: 10px;
        margin-bottom: 54px;
    }

    /* Make buttons look like premium tabs */
    div.stButton > button {
        width: 600px !important;
        height: 62px !important;
        border-radius: 16px !important;
        font-size: 16px !important;
        font-weight: 900 !important;
        border: 1px solid rgba(255,255,255,0.20) !important;
        box-shadow: 0 14px 28px rgba(0,0,0,0.10) !important;
        transition: transform 0.08s ease, filter 0.14s ease, box-shadow 0.14s ease;
        text-align: left !important;
        padding-left: 18px !important;
        letter-spacing: 0.1px;
    }
    div.stButton > button:hover{
        transform: translateY(-2px);
        filter: brightness(1.06);
        box-shadow: 0 16px 34px rgba(0,0,0,0.14) !important;
    }
    div.stButton > button:active{transform: translateY(0px);}

    /* Footer */
    .nea-footer{
        margin-top: 90px;
        text-align:center;
        color:#6b7280;
        font-style: italic;
        font-size: 14px;
        line-height: 1.5;
    }

    /* Responsive */
    @media (max-width: 720px){
        div.stButton > button {width: 94vw !important;}
        .nea-title{font-size: 34px;}
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------- Navigation --------------------
def go(page_path: str):
    try:
        st.switch_page(page_path)
    except Exception:
        # If older Streamlit: keep silent (or show a small message)
        st.info("Navigation needs Streamlit multipage support. Use the pages menu or upgrade Streamlit.")

# -------------------- Logo (centered above title, enhanced) --------------------
logo_path = os.path.join(BASE_DIR, "logo.jpg")
logo_img = None
if os.path.exists(logo_path):
    img = Image.open(logo_path).convert("RGB")
    # Enhance to avoid "faded" look
    img = ImageEnhance.Contrast(img).enhance(1.18)
    img = ImageEnhance.Color(img).enhance(1.10)
    img = ImageEnhance.Sharpness(img).enhance(1.40)
    logo_img = img

st.markdown('<div class="nea-logo-wrap">', unsafe_allow_html=True)
if logo_img is not None:
    st.markdown('<div class="nea-logo-frame">', unsafe_allow_html=True)
    st.image(logo_img, width=125)
    st.markdown("</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# -------------------- Title (subtitle REMOVED as requested) --------------------
st.markdown('<div class="nea-center">', unsafe_allow_html=True)
st.markdown('<div class="nea-title">NEA Protection &amp; Coordination Tools</div>', unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

st.divider()

# -------------------- 4 attractive "tabs" (different blue shades + gradient) --------------------
# We apply per-button styling using nth-of-type selectors.
# IMPORTANT: keep button order fixed.

pad_l, center, pad_r = st.columns([1, 2, 1])

with center:
    st.markdown('<div class="tabs-grid">', unsafe_allow_html=True)

    # Tab 1: bright blue gradient
    st.markdown(
        """
        <style>
        div.stButton:nth-of-type(1) > button{
            background: linear-gradient(135deg, #0B5ED7 0%, #2563EB 50%, #1D4ED8 100%) !important;
            color: white !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    if st.button("📈  Protection Coordination Tool (TCC Plot)"):
        go("pages/1_TCC_Tool.py")

    # Tab 2: deeper azure
    st.markdown(
        """
        <style>
        div.stButton:nth-of-type(2) > button{
            background: linear-gradient(135deg, #0A58CA 0%, #1D4ED8 55%, #1E40AF 100%) !important;
            color: white !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    if st.button("⚡  OC / EF Grid Coordination Tool"):
        go("pages/2_OC_EF_Grid.py")

    # Tab 3: navy-blue elegant
    st.markdown(
        """
        <style>
        div.stButton:nth-of-type(3) > button{
            background: linear-gradient(135deg, #1D4ED8 0%, #1E40AF 60%, #1E3A8A 100%) !important;
            color: white !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    if st.button("📘  Protection Theory Guide"):
        go("pages/3_Theory.py")

    # Tab 4: midnight blue premium
    st.markdown(
        """
        <style>
        div.stButton:nth-of-type(4) > button{
            background: linear-gradient(135deg, #1E40AF 0%, #1E3A8A 55%, #172554 100%) !important;
            color: white !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    if st.button("🛠️  Working Methodology / Manual"):
        go("pages/4_Working.py")

    st.markdown("</div>", unsafe_allow_html=True)

# Optional footer (you can delete if you want fully clean)
st.markdown(
    """
    <div class="nea-footer">
        Protection and Automation Division, GOD<br/>
        Nepal Electricity Authority
    </div>
    """,
    unsafe_allow_html=True,
)
