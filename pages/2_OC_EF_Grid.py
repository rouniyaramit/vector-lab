import io
import csv
import streamlit as st
import pandas as pd
from engine.grid_engine import calculate_grid, validate_cti_ms
from engine.pdf_utils import text_to_pdf_bytes

st.set_page_config(page_title="OC/EF Grid Tool", layout="wide")

st.title("Nepal Electricity Authority (NEA) Grid Protection Coordination Tool")
st.caption("Streamlit web version (same calculation logic as Tkinter).")

# ---------- State ----------
def init_grid_state():
    if "grid_initialized" in st.session_state:
        return

    st.session_state.grid = {
        "mva": 16.6,
        "hv": 33.0,
        "lv": 11.0,
        "z": 10.0,
        "cti": 150.0,
        "q4": 900.0,
        "q5": 300.0,
        "feeders": pd.DataFrame(
            [{"Load (A)": 200.0, "CT (A)": 400.0},
             {"Load (A)": 250.0, "CT (A)": 400.0},
             {"Load (A)": 300.0, "CT (A)": 400.0}]
        ),
        "last": None,
    }
    st.session_state.grid_initialized = True


def preload_defaults():
    st.session_state.grid["mva"] = 16.6
    st.session_state.grid["hv"] = 33.0
    st.session_state.grid["lv"] = 11.0
    st.session_state.grid["z"] = 10.0
    st.session_state.grid["cti"] = 150.0
    st.session_state.grid["q4"] = 900.0
    st.session_state.grid["q5"] = 300.0
    st.session_state.grid["feeders"] = pd.DataFrame(
        [{"Load (A)": 200.0, "CT (A)": 400.0},
         {"Load (A)": 250.0, "CT (A)": 400.0},
         {"Load (A)": 300.0, "CT (A)": 400.0}]
    )
    st.session_state.grid["last"] = None


def reset_grid():
    st.session_state.pop("grid_initialized", None)
    init_grid_state()


init_grid_state()

# ---------- Inputs ----------
with st.container(border=True):
    st.subheader("Transformer & System Data (Inputs)")

    c1, c2, c3, c4 = st.columns(4)
    st.session_state.grid["mva"] = c1.number_input("MVA", value=float(st.session_state.grid["mva"]), step=0.1)
    st.session_state.grid["hv"] = c2.number_input("HV (kV)", value=float(st.session_state.grid["hv"]), step=0.1)
    st.session_state.grid["lv"] = c3.number_input("LV (kV)", value=float(st.session_state.grid["lv"]), step=0.1)
    st.session_state.grid["z"] = c4.number_input("Z%", value=float(st.session_state.grid["z"]), step=0.1)

    c5, c6, c7 = st.columns(3)
    st.session_state.grid["cti"] = c5.number_input("CTI (ms)", value=float(st.session_state.grid["cti"]), step=10.0)
    st.session_state.grid["q4"] = c6.number_input("Q4 CT", value=float(st.session_state.grid["q4"]), step=10.0)
    st.session_state.grid["q5"] = c7.number_input("Q5 CT", value=float(st.session_state.grid["q5"]), step=10.0)

with st.container(border=True):
    st.subheader("Feeder Configuration")

    # Editable table (replaces dynamic Tkinter rows)
    df = st.session_state.grid["feeders"]
    edited = st.data_editor(
        df,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
    )
    st.session_state.grid["feeders"] = edited

    total_load = float(edited["Load (A)"].fillna(0).sum()) if len(edited) else 0.0
    st.markdown(f"**Total Connected Load: {total_load:.2f} A**")

# ---------- Actions ----------
a1, a2, a3 = st.columns(3)
with a1:
    run = st.button("RUN CALCULATION", type="primary", use_container_width=True)
with a2:
    if st.button("Preload Default Data", use_container_width=True):
        preload_defaults()
with a3:
    if st.button("Reset", use_container_width=True):
        reset_grid()

# ---------- Run ----------
if run:
    ok, msg = validate_cti_ms(float(st.session_state.grid["cti"]))
    if not ok:
        st.warning(msg)
    else:
        feeders_list = []
        for _, row in st.session_state.grid["feeders"].fillna(0).iterrows():
            feeders_list.append({"load": float(row["Load (A)"]), "ct": float(row["CT (A)"])})

        try:
            result = calculate_grid(
                mva=float(st.session_state.grid["mva"]),
                hv_kv=float(st.session_state.grid["hv"]),
                lv_kv=float(st.session_state.grid["lv"]),
                z_pct=float(st.session_state.grid["z"]),
                cti_ms=float(st.session_state.grid["cti"]),
                q4_ct=float(st.session_state.grid["q4"]),
                q5_ct=float(st.session_state.grid["q5"]),
                feeders=feeders_list,
            )
            st.session_state.grid["last"] = result
        except Exception as e:
            st.error(f"Invalid Inputs: {e}")

# ---------- Outputs ----------
last = st.session_state.grid["last"]
if last:
    if last["critical_overload"]:
        st.error(f"CRITICAL ALERT: TRANSFORMER OVERLOAD ({last['total_load']}A > {last['flc_lv']}A)")

    if last["alerts"]:
        st.warning("\n".join(last["alerts"]))

    tab1, tab2 = st.tabs(["Overcurrent (Phase)", "Earth Fault (Neutral)"])

    with tab1:
        st.text_area("OC Report", value=last["oc_report"], height=360)
    with tab2:
        st.text_area("EF Report", value=last["ef_report"], height=360)

    # Exports
    st.subheader("Exports")

    def build_tabulated_csv_bytes():
        out = io.StringIO()
        writer = csv.writer(out)
        writer.writerow(["EQUIPMENT", "FAULT TYPE", "STAGE", "PICKUP (A)", "RATIO (*In)", "TMS/DELAY", "TIME (s)"])

        def parse(txt: str, label: str):
            curr = ""
            for line in txt.split("\n"):
                if ":" in line and "Load" in line:
                    curr = line.split(":")[0]
                elif "- S" in line:
                    p = line.split(":")
                    stage = p[0].strip("- ")
                    details = p[1].split(",")
                    pick_raw = details[0].split("=")[1].strip()
                    val = pick_raw.split("(")[0].strip()
                    rat = pick_raw.split("(")[1].replace("*In)", "").strip()
                    tms = details[1].split("=")[1].strip()
                    op = details[2].split("=")[1].strip() if len(details) > 2 else "0.0s"
                    writer.writerow([curr, label, stage, val, rat, tms, op.replace("s", "")])

        parse(last["oc_report"], "Overcurrent")
        parse(last["ef_report"], "Earth Fault")
        return out.getvalue().encode("utf-8")

    cexp1, cexp2 = st.columns(2)
    with cexp1:
        st.download_button(
            "Save Tabulated CSV",
            data=build_tabulated_csv_bytes(),
            file_name="NEA_Grid_Tabulated.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with cexp2:
        combined = last["oc_report"] + "\n\n" + last["ef_report"]
        pdf_bytes = text_to_pdf_bytes("NEA Grid Coordination Report", combined)
        st.download_button(
            "Save PDF",
            data=pdf_bytes,
            file_name="NEA_Grid_Report.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

st.caption("By Protection and Automation Division, GOD")
