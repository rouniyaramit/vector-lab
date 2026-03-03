import os
import io
import csv
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from PIL import Image

from engine.tcc_engine import (
    compute_tcc_plot,
    transformer_calculations,
    build_coordination_report,
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

st.set_page_config(page_title="TCC Plot Tool", layout="wide")

# ---------- Session defaults ----------
def _init_state():
    if "tcc_initialized" in st.session_state:
        return

    st.session_state.tcc = {
        "mva": 16.6,
        "hv": 33.0,
        "lv": 11.0,
        "z": 10.0,
        "fault": 7900.0,
        "relays": [
            {"idmt_on": True, "dt1_on": True, "dt2_on": True, "pickup": 220.0, "tms": 0.025, "dt1_pickup": 600.0, "dt1_time": 0.0, "dt2_pickup": 0.0, "dt2_time": 0.0, "curve": "Standard Inverse"},
            {"idmt_on": True, "dt1_on": True, "dt2_on": True, "pickup": 275.0, "tms": 0.025, "dt1_pickup": 750.0, "dt1_time": 0.0, "dt2_pickup": 0.0, "dt2_time": 0.0, "curve": "Standard Inverse"},
            {"idmt_on": True, "dt1_on": True, "dt2_on": True, "pickup": 330.0, "tms": 0.025, "dt1_pickup": 900.0, "dt1_time": 0.0, "dt2_pickup": 0.0, "dt2_time": 0.0, "curve": "Standard Inverse"},
            {"idmt_on": True, "dt1_on": True, "dt2_on": True, "pickup": 825.0, "tms": 0.07,  "dt1_pickup": 2250.0, "dt1_time": 0.15, "dt2_pickup": 8000.0, "dt2_time": 0.0, "curve": "Standard Inverse"},
            {"idmt_on": True, "dt1_on": True, "dt2_on": True, "pickup": 275.0, "tms": 0.12,  "dt1_pickup": 750.0, "dt1_time": 0.3,  "dt2_pickup": 2666.67, "dt2_time": 0.0, "curve": "Standard Inverse"},
        ],
        "last_fig": None,
        "last_report_text": "",
        "last_results_table": [],
        "warning_fault_clamped": False,
        "flc_lv": None,
        "isc_lv": None,
        "fault_used": None,
        "trip_times": {},
    }

    st.session_state.tcc_initialized = True


def reset_all():
    st.session_state.pop("tcc_initialized", None)
    _init_state()


_init_state()

# ---------- Header ----------
h1, h2 = st.columns([4, 1], vertical_alignment="center")
with h1:
    st.title("NEA Protection Coordination Tool (TCC Plot)")
    st.caption("Streamlit web version (Tkinter-equivalent layout and logic).")
with h2:
    logo_path = os.path.join(BASE_DIR, "logo.jpg")
    if os.path.exists(logo_path):
        st.image(Image.open(logo_path), width=110)

st.divider()

left, right = st.columns([1.05, 1.95], gap="large")

# ---------- LEFT PANEL ----------
with left:
    st.subheader("Transformer Data")
    c1, c2 = st.columns(2)
    with c1:
        st.session_state.tcc["mva"] = st.number_input("Rating (MVA)", value=float(st.session_state.tcc["mva"]), step=0.1)
        st.session_state.tcc["lv"] = st.number_input("LV (kV)", value=float(st.session_state.tcc["lv"]), step=0.1)
    with c2:
        st.session_state.tcc["hv"] = st.number_input("HV (kV)", value=float(st.session_state.tcc["hv"]), step=0.1)
        st.session_state.tcc["z"] = st.number_input("Impedance (%)", value=float(st.session_state.tcc["z"]), step=0.1)

    try:
        flc_lv, isc_lv, hv_factor = transformer_calculations(
            float(st.session_state.tcc["mva"]),
            float(st.session_state.tcc["lv"]),
            float(st.session_state.tcc["hv"]),
            float(st.session_state.tcc["z"]),
        )
        st.session_state.tcc["flc_lv"] = flc_lv
        st.session_state.tcc["isc_lv"] = isc_lv
        st.info(f"FLC (LV) = {flc_lv:.3f} A")
        st.info(f"Isc (LV) = {isc_lv:.3f} A")
    except Exception:
        st.warning("Enter valid transformer inputs.")

    st.subheader("Fault Data")
    st.session_state.tcc["fault"] = st.number_input("Fault (A)", value=float(st.session_state.tcc["fault"]), step=100.0)

    st.subheader("Relay Settings")
    st.caption("Q1–Q5 (IDMT + DT1 + DT2)")

    curve_opts = ["Standard Inverse", "Very Inverse", "Extremely Inverse"]

    for i in range(5):
        r = st.session_state.tcc["relays"][i]
        with st.expander(f"Q{i+1} Settings", expanded=(i < 2)):
            a, b, c = st.columns([1, 1, 1])
            with a:
                r["idmt_on"] = st.checkbox("IDMT", value=bool(r["idmt_on"]), key=f"idmt_{i}")
                r["pickup"] = st.number_input("Pick (A)", value=float(r["pickup"]), step=1.0, key=f"pick_{i}")
                r["curve"] = st.selectbox("Curve", curve_opts, index=curve_opts.index(r["curve"]), key=f"curve_{i}")
            with b:
                r["tms"] = st.number_input("TMS", value=float(r["tms"]), step=0.005, format="%.3f", key=f"tms_{i}")
                r["dt1_on"] = st.checkbox("DT1", value=bool(r["dt1_on"]), key=f"dt1_{i}")
                r["dt1_pickup"] = st.number_input("P1 (A)", value=float(r["dt1_pickup"]), step=1.0, key=f"p1_{i}")
                r["dt1_time"] = st.number_input("T1 (s)", value=float(r["dt1_time"]), step=0.01, format="%.3f", key=f"t1_{i}")
            with c:
                r["dt2_on"] = st.checkbox("DT2 (Q4/Q5 only)", value=bool(r["dt2_on"]), key=f"dt2_{i}")
                r["dt2_pickup"] = st.number_input("P2 (A)", value=float(r["dt2_pickup"]), step=1.0, key=f"p2_{i}")
                r["dt2_time"] = st.number_input("T2 (s)", value=float(r["dt2_time"]), step=0.01, format="%.3f", key=f"t2_{i}")

            st.session_state.tcc["relays"][i] = r

    st.divider()
    b1, b2, b3 = st.columns(3)
    with b1:
        if st.button("Plot Coordination", type="primary", use_container_width=True):
            try:
                currents, merged_curves, trip_times, flc_lv, isc_lv, fault_used = compute_tcc_plot(
                    float(st.session_state.tcc["mva"]),
                    float(st.session_state.tcc["lv"]),
                    float(st.session_state.tcc["hv"]),
                    float(st.session_state.tcc["z"]),
                    float(st.session_state.tcc["fault"]) if st.session_state.tcc["fault"] else None,
                    st.session_state.tcc["relays"],
                )

                # Matplotlib figure
                fig = plt.figure(figsize=(10, 6))
                ax = fig.add_subplot(111)
                ax.set_title("Time-Current Characteristics", fontsize=14, fontweight="bold")
                ax.set_xscale("log")
                ax.set_yscale("log")
                ax.set_xlabel("Current (A)", fontsize=12)
                ax.set_ylabel("Time (s)", fontsize=12)
                ax.grid(True, which="both", linestyle="--", alpha=0.7)

                colors = ["blue", "green", "red", "purple", "orange"]

                for i in range(5):
                    ax.plot(currents, merged_curves[i], color=colors[i], linewidth=2.5, label=f"Q{i+1}")

                    if fault_used is not None and f"Q{i+1}" in trip_times:
                        t_res = trip_times[f"Q{i+1}"]
                        ax.plot(fault_used, t_res, "o", color=colors[i])
                        ax.text(fault_used, t_res, f"{t_res:.3f}s", fontsize=9)

                if fault_used is not None:
                    ax.axvline(fault_used, linestyle="dotted", color="black", linewidth=2, label="Fault Level")

                ax.legend()

                report_text, results_table = build_coordination_report(trip_times, flc_lv, isc_lv, fault_used)

                st.session_state.tcc["last_fig"] = fig
                st.session_state.tcc["last_report_text"] = report_text
                st.session_state.tcc["last_results_table"] = results_table
                st.session_state.tcc["trip_times"] = trip_times
                st.session_state.tcc["fault_used"] = fault_used
                st.session_state.tcc["warning_fault_clamped"] = (
                    st.session_state.tcc["fault"] is not None and fault_used is not None and float(st.session_state.tcc["fault"]) > float(isc_lv)
                )

                if st.session_state.tcc["warning_fault_clamped"]:
                    st.warning("Warning: Fault current exceeded LV short circuit current; it was clamped to Isc (LV).")
            except Exception as e:
                st.error(f"Plot failed: {e}")

    with b2:
        if st.button("Prefill Defaults", use_container_width=True):
            reset_all()
    with b3:
        if st.button("New Project (Reset All)", use_container_width=True):
            reset_all()

    # SLD image + footer (like Tkinter)
    sld_path = os.path.join(BASE_DIR, "sld.png")
    if os.path.exists(sld_path):
        st.image(Image.open(sld_path), width=260)

    st.markdown(
        "<div style='color:red; font-weight:700;'>Protection and Automation Division, GOD</div>",
        unsafe_allow_html=True,
    )

# ---------- RIGHT PANEL ----------
with right:
    st.subheader("Plot")
    if st.session_state.tcc["last_fig"] is not None:
        st.pyplot(st.session_state.tcc["last_fig"], clear_figure=False)
    else:
        st.info("Click **Plot Coordination** to generate the TCC plot.")

    st.subheader("Coordination Report")
    report = st.session_state.tcc["last_report_text"] or ""
    st.text_area("Report Output", value=report, height=260)

    # Export buttons (PDF + CSV) like Tkinter menu items
    cexp1, cexp2 = st.columns(2)

    with cexp1:
        if st.session_state.tcc["last_fig"] is not None:
            # Build PDF with plot page + summary page (same concept as Tkinter)
            def build_pdf_bytes():
                buf = io.BytesIO()
                with PdfPages(buf) as pdf:
                    pdf.savefig(st.session_state.tcc["last_fig"])

                    fig_rep, ax_rep = plt.subplots(figsize=(11, 8.5))
                    ax_rep.axis("off")
                    ax_rep.text(0.5, 0.95, "Relay Settings & Coordination Report", fontsize=16, weight="bold", ha="center")

                    headers = ["Relay", "IDMT", "Pick", "TMS", "DT1", "P1", "T1", "DT2", "P2", "T2", "Curve"]
                    rows = []
                    for i in range(5):
                        r = st.session_state.tcc["relays"][i]
                        rows.append([
                            f"Q{i+1}",
                            "ON" if r["idmt_on"] else "OFF",
                            f"{float(r['pickup']):.3f}",
                            f"{float(r['tms']):.3f}",
                            "ON" if r["dt1_on"] else "OFF",
                            f"{float(r['dt1_pickup']):.3f}",
                            f"{float(r['dt1_time']):.3f}",
                            "ON" if r["dt2_on"] else "OFF",
                            f"{float(r['dt2_pickup']):.3f}",
                            f"{float(r['dt2_time']):.3f}",
                            r["curve"],
                        ])

                    table = ax_rep.table(
                        cellText=rows,
                        colLabels=headers,
                        loc="center",
                        cellLoc="center",
                        bbox=[0.03, 0.52, 0.94, 0.35],
                    )
                    table.auto_set_font_size(False)
                    table.set_fontsize(9)

                    ax_rep.text(0.03, 0.47, "Results Summary:", fontsize=12, weight="bold")
                    ax_rep.text(0.03, 0.45, report, fontsize=9, family="monospace", va="top")

                    pdf.savefig(fig_rep)
                    plt.close(fig_rep)

                return buf.getvalue()

            st.download_button(
                "Save Report (PDF)",
                data=build_pdf_bytes(),
                file_name="NEA_TCC_Report.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        else:
            st.download_button(
                "Save Report (PDF)",
                data=b"",
                file_name="NEA_TCC_Report.pdf",
                mime="application/pdf",
                disabled=True,
                use_container_width=True,
            )

    with cexp2:
        def build_csv_bytes():
            out = io.StringIO()
            writer = csv.writer(out)
            writer.writerow(["NEA PROTECTION TOOL REPORT"])
            writer.writerow([])
            writer.writerow(["--- Transformer Data ---"])
            writer.writerow(["Rating (MVA)", st.session_state.tcc["mva"]])
            writer.writerow(["HV Voltage (kV)", st.session_state.tcc["hv"]])
            writer.writerow(["LV Voltage (kV)", st.session_state.tcc["lv"]])
            writer.writerow(["Impedance (%)", st.session_state.tcc["z"]])
            if st.session_state.tcc["flc_lv"] is not None:
                writer.writerow(["FLC (LV)", f"{st.session_state.tcc['flc_lv']:.3f} A"])
            if st.session_state.tcc["isc_lv"] is not None:
                writer.writerow(["Isc (LV)", f"{st.session_state.tcc['isc_lv']:.3f} A"])
            writer.writerow([])
            writer.writerow(["--- Relay Settings ---"])
            writer.writerow(["Relay", "IDMT", "Pickup", "TMS", "DT1", "P1", "T1", "DT2", "P2", "T2", "Curve"])
            for i in range(5):
                r = st.session_state.tcc["relays"][i]
                writer.writerow([
                    f"Q{i+1}",
                    int(r["idmt_on"]),
                    r["pickup"],
                    r["tms"],
                    int(r["dt1_on"]),
                    r["dt1_pickup"],
                    r["dt1_time"],
                    int(r["dt2_on"]),
                    r["dt2_pickup"],
                    r["dt2_time"],
                    r["curve"],
                ])
            return out.getvalue().encode("utf-8")

        st.download_button(
            "Export to Excel (CSV)",
            data=build_csv_bytes(),
            file_name="NEA_TCC_Report.csv",
            mime="text/csv",
            use_container_width=True,
        )
