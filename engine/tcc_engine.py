import numpy as np

# ---------------- CTI VALUES ----------------
CTI_Q1_Q4 = 0.150
CTI_Q1_Q5 = 0.300
CTI_Q4_Q5 = 0.150


# ---------------- IEC CURVE ----------------
def iec_curve(I: float, Ip: float, TMS: float, curve: str) -> float:
    if I <= Ip:
        return np.nan
    curves = {
        "Standard Inverse": (0.14, 0.02),
        "Very Inverse": (13.5, 1.0),
        "Extremely Inverse": (80.0, 2.0),
    }
    k, alpha = curves[curve]
    M = I / Ip
    return TMS * (k / ((M ** alpha) - 1.0))


def transformer_calculations(MVA: float, LV: float, HV: float, Z: float):
    """
    Returns:
      FLC_LV (A), Isc_LV (A), HV_factor (HV/LV)
    """
    FLC_LV = (MVA * 1000.0) / (np.sqrt(3.0) * LV)
    Isc_LV = FLC_LV / (Z / 100.0)
    HV_factor = HV / LV
    return FLC_LV, Isc_LV, HV_factor


def compute_tcc_plot(
    MVA: float,
    LV: float,
    HV: float,
    Z: float,
    fault_current: float | None,
    relays: list[dict],
):
    """
    relays: list of 5 dicts for Q1..Q5:
      {
        "idmt_on": bool,
        "dt1_on": bool,
        "dt2_on": bool,
        "pickup": float,
        "tms": float,
        "dt1_pickup": float,
        "dt1_time": float,
        "dt2_pickup": float,
        "dt2_time": float,
        "curve": str,
      }
    Returns:
      currents, merged_curves(list[np.ndarray]), trip_times(dict), flc_lv, isc_lv, fault_current_clamped
    """
    currents = np.logspace(1, 5, 800)
    flc_lv, isc_lv, hv_factor = transformer_calculations(MVA, LV, HV, Z)

    # Clamp fault if above Isc_LV (same behavior as Tkinter warning)
    fault_clamped = fault_current
    if isc_lv and fault_current and fault_current > isc_lv:
        fault_clamped = float(isc_lv)

    merged_curves = []
    trip_times: dict[str, float] = {}

    for i in range(5):
        r = relays[i]

        current_scaling = hv_factor if i == 4 else 1.0  # Q5 on HV side
        curve_vals = []

        for I in currents:
            I_scaled = I / current_scaling
            times = []

            if r["idmt_on"]:
                t_idmt = iec_curve(I_scaled, r["pickup"], r["tms"], r["curve"])
                if not np.isnan(t_idmt):
                    times.append(t_idmt)

            if r["dt1_on"]:
                try:
                    if I_scaled >= r["dt1_pickup"]:
                        times.append(r["dt1_time"])
                except Exception:
                    pass

            if i >= 3 and r["dt2_on"]:
                try:
                    if I_scaled >= r["dt2_pickup"]:
                        times.append(r["dt2_time"])
                except Exception:
                    pass

            curve_vals.append(min(times) if times else np.nan)

        merged = np.array(curve_vals, dtype=float)
        merged_curves.append(merged)

        # Intersection at fault
        if fault_clamped:
            I_fault_scaled = fault_clamped / current_scaling
            intersection_times = []

            if r["idmt_on"]:
                t_f = iec_curve(I_fault_scaled, r["pickup"], r["tms"], r["curve"])
                if not np.isnan(t_f):
                    intersection_times.append(t_f)

            if r["dt1_on"]:
                try:
                    if I_fault_scaled >= r["dt1_pickup"]:
                        intersection_times.append(r["dt1_time"])
                except Exception:
                    pass

            if i >= 3 and r["dt2_on"]:
                try:
                    if I_fault_scaled >= r["dt2_pickup"]:
                        intersection_times.append(r["dt2_time"])
                except Exception:
                    pass

            if intersection_times:
                trip_times[f"Q{i+1}"] = round(float(min(intersection_times)), 3)

    return currents, merged_curves, trip_times, flc_lv, isc_lv, fault_clamped


def build_coordination_report(trip_times: dict[str, float], flc_lv: float | None, isc_lv: float | None, fault: float | None):
    lines = []
    lines.append("Coordination Report")
    lines.append("=" * 20)
    if flc_lv is not None and isc_lv is not None:
        lines.append(f"LV FLC: {flc_lv:.3f} A | LV Isc: {isc_lv:.3f} A")
    if fault is not None:
        lines.append(f"Fault Current: {fault:.3f} A")
    lines.append("")

    for q in sorted(trip_times.keys()):
        lines.append(f"{q} Trip: {trip_times[q]:.3f} s")

    lines.append("")
    lines.append("Coordination Results:")

    checks = [
        ("Q1", "Q4", CTI_Q1_Q4), ("Q2", "Q4", CTI_Q1_Q4), ("Q3", "Q4", CTI_Q1_Q4),
        ("Q1", "Q5", CTI_Q1_Q5), ("Q2", "Q5", CTI_Q1_Q5), ("Q3", "Q5", CTI_Q1_Q5),
        ("Q4", "Q5", CTI_Q4_Q5),
    ]

    results = []
    for d, u, cti in checks:
        if d in trip_times and u in trip_times:
            margin = trip_times[u] - trip_times[d]
            ok = margin >= cti
            results.append((d, u, margin, cti, ok))
            lines.append(f"{d}->{u}: {margin:.3f}s {'OK' if ok else 'NOT OK'}")

    return "\n".join(lines), results
