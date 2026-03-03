import streamlit as st

st.set_page_config(page_title="Working Manual", layout="wide")

st.title("NEA Protection Suite - Comprehensive User Manual")

tab1, tab2, tab3 = st.tabs(["📈 TCC Plotter Guide", "⚡ OC/EF Grid Guide", "🛠️ Troubleshooting & Tips"])

with tab1:
    st.markdown(
        """
## SECTION 1: TCC PLOTTER
This tool visualizes how your relays will react during a fault.

### 1.1 Input Field Definitions
- **Pickup Current (Ip):** Current where relay starts timing.
- **TMS:** Moves curve vertically (lower = faster).
- **Curve:** Standard Inverse for most NEA feeders.

### 1.2 Coordination Workflow
1. Enter Q1 first (feeder).
2. Ensure Q4 is above Q1 by at least CTI margin.
3. Enable stages (IDMT/DT) to show on plot.

### 1.3 Understanding the Plot
If curves intersect, you have a race condition—adjust TMS/pickups.
"""
    )

with tab2:
    st.markdown(
        """
## SECTION 2: OC/EF GRID TOOL
Automates grading for a substation based on transformer data.

### 2.1 Required Data Entry
- Transformer MVA, %Z (nameplate)
- CT primary values (e.g., 400 for 400/1A)

### 2.2 Calculate Button
Checks:
1. Total feeder load vs transformer FLC
2. CTI grading upstream (Q4/Q5)
3. EF sensitivity

### 2.3 Exporting Results
Use **Save PDF** and **Save CSV** and review alerts.
"""
    )

with tab3:
    st.markdown(
        """
## COMMON ISSUES & SOLUTIONS

### Q: The plot looks messy.
A: Ensure Ip values increase upstream (Q1 smallest → Q5 largest).

### Q: Why are there alerts?
A: Safety interlocks: CT smaller than load or transformer overload.

**PRO TIP:** Reset before a new substation calculation.
"""
    )

st.caption("NEA Protection & Automation Division - Kathmandu, Nepal")
