import io
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from engine.tcc_engine import (
    TransformerInputs, StageSettings, TCCInputs, compute_tcc
)

st.set_page_config(page_title="TCC Plot Tool", layout="wide")
st.title("TCC Plot Tool (Q1–Q5)")
st.caption("Streamlit UI only. All calculations are in engine/tcc_engine.py")

# Defaults (same as your Tkinter prefill style)
DEFAULTS = {
    "mva": 16.6, "hv": 33.0, "lv": 11.0, "z": 10.0, "fault": 2000.0,
    "pickups": [400, 500, 600, 800, 200],
    "tms":     [0.025, 0.05, 0.08, 0.2, 0.25],
    "curve":   ["Standard Inverse"]*5,
    "idmt":    [1,1,1,1,1],
    "dt1":     [1,1,1,1,1],
    "dt1_p":   [1200,1500,1800,2400,600],
    "dt1_t":   [0.0,0.0,0.0,0.1,0.2],
    "dt2":     [0,0,0,1,1],
    "dt2_p":   [0,0,0,3000,900],
    "dt2_t":   [0,0,0,0.0,0.0],
}

with st.sidebar:
    st.header("Transformer Inputs")
    mva = st.number_input("MVA", value=float(DEFAULTS["mva"]), step=0.1, format="%.3f")
    hv  = st.number_input("HV (kV)", value=float(DEFAULTS["hv"]), step=0.1, format="%.3f")
    lv  = st.number_input("LV (kV)", value=float(DEFAULTS["lv"]), step=0.1, format="%.3f")
    z   = st.number_input("Impedance Z (%)", value=float(DEFAULTS["z"]), step=0.1, format="%.3f")
    fault = st.number_input("Fault Current (A)", value=float(DEFAULTS["fault"]), step=10.0, format="%.3f")

st.subheader("Relay Settings (Q1–Q5)")
curves = ["Standard Inverse", "Very Inverse", "Extremely Inverse"]

relays = []
cols = st.columns(5)
for i in range(5):
    with cols[i]:
        st.markdown(f"### Q{i+1}")

        idmt = st.checkbox("IDMT enable", value=bool(DEFAULTS["idmt"][i]), key=f"idmt_{i}")
        pickup = st.number_input("Pickup Ip (A)", value=float(DEFAULTS["pickups"][i]), step=1.0, format="%.3f", key=f"ip_{i}")
        tms = st.number_input("TMS", value=float(DEFAULTS["tms"][i]), step=0.001, format="%.3f", key=f"tms_{i}")
        curve = st.selectbox("Curve", curves, index=curves.index(DEFAULTS["curve"][i]), key=f"curve_{i}")

        dt1 = st.checkbox("DT1 enable", value=bool(DEFAULTS["dt1"][i]), key=f"dt1_{i}")
        dt1_p = st.number_input("DT1 Pickup (A)", value=float(DEFAULTS["dt1_p"][i]), step=1.0, format="%.3f", key=f"dt1p_{i}")
        dt1_t = st.number_input("DT1 Time (s)", value=float(DEFAULTS["dt1_t"][i]), step=0.001, format="%.3f", key=f"dt1t_{i}")

        dt2 = st.checkbox("DT2 enable (Q4/Q5 only)", value=bool(DEFAULTS["dt2"][i]), key=f"dt2_{i}")
        dt2_p = st.number_input("DT2 Pickup (A)", value=float(DEFAULTS["dt2_p"][i]), step=1.0, format="%.3f", key=f"dt2p_{i}")
        dt2_t = st.number_input("DT2 Time (s)", value=float(DEFAULTS["dt2_t"][i]), step=0.001, format="%.3f", key=f"dt2t_{i}")

        relays.append(StageSettings(
            idmt_enabled=idmt,
            pickup_ip=float(pickup),
            tms=float(tms),
            curve=str(curve),
            dt1_enabled=dt1,
            dt1_pickup=float(dt1_p),
            dt1_time=float(dt1_t),
            dt2_enabled=dt2,
            dt2_pickup=float(dt2_p),
            dt2_time=float(dt2_t),
        ))

st.divider()

if st.button("Plot + Generate Report", type="primary"):
    inp = TCCInputs(
        transformer=TransformerInputs(mva=float(mva), hv_kv=float(hv), lv_kv=float(lv), z_pct=float(z)),
        fault_current_a=float(fault) if fault else None,
        relays=relays,
    )

    res = compute_tcc(inp)

    for w in res.warnings:
        st.warning(w)

    # Plot
    fig, ax = plt.subplots()
    ax.set_title("Time-Current Characteristics", fontsize=14, fontweight="bold")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Current (A)")
    ax.set_ylabel("Time (s)")
    ax.grid(True, which="both", linestyle="--", alpha=0.7)

    colors = ["blue", "green", "red", "purple", "orange"]
    for i in range(5):
        q = f"Q{i+1}"
        ax.plot(res.currents, res.curves[q], color=colors[i], linewidth=2.5, label=q)

        if res.fault_current_used_a is not None and q in res.trip_times:
            t = res.trip_times[q]
            ax.plot(res.fault_current_used_a, t, "o", color=colors[i])
            ax.text(res.fault_current_used_a, t, f"{t:.3f}s", fontsize=9)

    if res.fault_current_used_a is not None:
        ax.axvline(res.fault_current_used_a, linestyle="dotted", color="black", linewidth=2, label="Fault Level")

    ax.legend()

    c1, c2 = st.columns([3, 2], vertical_alignment="top")
    with c1:
        st.pyplot(fig, clear_figure=False)
    with c2:
        st.text(res.report_text)
        if res.trip_times:
            df = pd.DataFrame([{"Relay": k, "Trip (s)": v} for k, v in sorted(res.trip_times.items())])
            st.dataframe(df, use_container_width=True)

    # PDF Download (plot + settings + report)
    pdf_buf = io.BytesIO()
    with PdfPages(pdf_buf) as pdf:
        pdf.savefig(fig)

        fig2, ax2 = plt.subplots(figsize=(11, 8.5))
        ax2.axis("off")
        ax2.text(0.5, 0.95, "Relay Settings & Coordination Report", fontsize=16, weight="bold", ha="center")

        headers = ["Relay", "IDMT", "Pick", "TMS", "DT1", "P1", "T1", "DT2", "P2", "T2"]
        rows = []
        for i in range(5):
            s = relays[i]
            rows.append([
                f"Q{i+1}",
                "ON" if s.idmt_enabled else "OFF",
                f"{s.pickup_ip:.3f}",
                f"{s.tms:.3f}",
                "ON" if s.dt1_enabled else "OFF",
                f"{s.dt1_pickup:.3f}",
                f"{s.dt1_time:.3f}",
                "ON" if s.dt2_enabled else "OFF",
                f"{s.dt2_pickup:.3f}",
                f"{s.dt2_time:.3f}",
            ])

        table = ax2.table(cellText=rows, colLabels=headers, loc="center", cellLoc="center", bbox=[0.05, 0.5, 0.9, 0.35])
        table.auto_set_font_size(False)
        table.set_fontsize(10)

        ax2.text(0.05, 0.45, "Results Summary:", fontsize=12, weight="bold")
        ax2.text(0.05, 0.43, res.report_text, fontsize=10, family="monospace", va="top")

        pdf.savefig(fig2)
        plt.close(fig2)

    pdf_buf.seek(0)
    st.download_button(
        "Download PDF Report",
        data=pdf_buf,
        file_name="tcc_report.pdf",
        mime="application/pdf",
        use_container_width=True,
    )
