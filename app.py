import streamlit as st
from pathlib import Path
from PIL import Image, ImageOps

st.set_page_config(
    page_title="NEA Master Protection Tool",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ------------------ GLOBAL CSS ------------------
st.markdown(
    """
    <style>
    /* Hide Streamlit sidebar */
    [data-testid="stSidebar"] {display:none !important;}
    [data-testid="stSidebarNav"] {display:none !important;}

    /* Overall spacing */
    .block-container {padding-top: 1.2rem; padding-bottom: 1rem; max-width: 1200px;}

    /* Remove default hr if any */
    hr {display:none !important;}

    /* Header spacing */
    .nea-header-wrap{
        margin-top: 10px;
        margin-bottom: 14px;
    }

    /* Card container */
    .nea-card{
        border: 1px solid rgba(0,0,0,0.08);
        border-radius: 18px;
        padding: 18px;
        background: #ffffff;
        box-shadow: 0 10px 30px rgba(0,0,0,0.06);
    }

    /* Tool tiles grid */
    .tiles{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 18px;
        margin-top: 14px;
    }

    /* A tool tile */
    .tile{
        display: flex;
        align-items: center;
        justify-content: center;
        height: 92px;
        border-radius: 18px;
        color: white;
        font-size: 20px;
        font-weight: 900;
        text-decoration: none !important;
        box-shadow: 0 14px 30px rgba(2,132,199,0.20);
        border: 1px solid rgba(255,255,255,0.18);
        transition: transform 120ms ease, box-shadow 120ms ease, filter 120ms ease;
        user-select: none;
    }
    .tile:hover{
        transform: translateY(-2px);
        box-shadow: 0 18px 40px rgba(2,132,199,0.30);
        filter: brightness(1.03);
    }

    /* 4 blue shades */
    .b1{ background: linear-gradient(135deg, #0b5bd3 0%, #0ea5e9 100%); }
    .b2{ background: linear-gradient(135deg, #1d4ed8 0%, #3b82f6 55%, #60a5fa 100%); }
    .b3{ background: linear-gradient(135deg, #075985 0%, #0284c7 55%, #38bdf8 100%); }
    .b4{ background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 55%, #0b5bd3 100%); }

    /* Emoji spacing */
    .tile span{
        display:inline-flex;
        gap: 10px;
        align-items:center;
    }

    /* Make it mobile-friendly */
    @media (max-width: 900px){
        .tiles{ grid-template-columns: 1fr; }
        .tile{ height: 84px; font-size: 18px; }
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ------------------ NAV HANDLER ------------------
# We navigate using query param ?go=tcc / ocef / theory / working
qp = st.query_params
go = qp.get("go", None)

if go == "tcc":
    st.query_params.clear()
    st.switch_page("pages/2_GUI_Final5_TCC.py")
elif go == "ocef":
    st.query_params.clear()
    st.switch_page("pages/3_OC_EF_GOD.py")
elif go == "theory":
    st.query_params.clear()
    st.switch_page("pages/4_Theory.py")
elif go == "working":
    st.query_params.clear()
    st.switch_page("pages/5_Working.py")

# ------------------ LOGO (IMPORTANT NOTE) ------------------
# If your logo file itself is cropped, Streamlit cannot "fix" it.
# Replace logo.jpg in GitHub with the FULL original logo image for perfect result.
logo_path = Path(__file__).parent / "logo.jpg"

def load_logo(path: Path, target_w: int = 150) -> Image.Image | None:
    if not path.exists():
        return None
    img = Image.open(path).convert("RGBA")

    # Add padding around logo so it never "touches" the edges visually
    img = ImageOps.expand(img, border=10, fill=(255, 255, 255, 255))

    # Keep full image visible (no cropping)
    img = ImageOps.contain(img, (target_w, target_w))

    return img

# ------------------ HEADER ------------------
st.markdown("<div class='nea-header-wrap'>", unsafe_allow_html=True)

c1, c2 = st.columns([1.1, 5.0], vertical_alignment="center")
with c1:
    logo = load_logo(logo_path, target_w=150)
    if logo is not None:
        st.image(logo, width=150)
    else:
        st.warning("logo.jpg not found in repo root")

with c2:
    st.markdown(
        "<h1 style='margin:0; padding:0; font-size:46px; font-weight:900;'>NEA Master Protection Tool</h1>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<div style='margin-top:6px; color:#4b5563; font-weight:700; font-size:16px;'>Select a tool below. (Navigation is here)</div>",
        unsafe_allow_html=True
    )

st.markdown("</div>", unsafe_allow_html=True)

# ------------------ MAIN CARD ------------------
st.markdown("<div class='nea-card'>", unsafe_allow_html=True)
st.markdown("<h3 style='margin:0; font-size:26px; font-weight:900;'>Open a tool</h3>", unsafe_allow_html=True)

# Clickable tiles (stable colors + stable layout)
st.markdown(
    """
    <div class="tiles">
        <a class="tile b1" href="?go=tcc"><span>⚡ TCC Plot Tool (Q1–Q5)</span></a>
        <a class="tile b2" href="?go=ocef"><span>🧮 OC/EF Grid Tool</span></a>
        <a class="tile b3" href="?go=theory"><span>📘 Theory</span></a>
        <a class="tile b4" href="?go=working"><span>🛠️ Working</span></a>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("</div>", unsafe_allow_html=True)
