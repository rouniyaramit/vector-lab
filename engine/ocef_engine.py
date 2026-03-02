"""
OC/EF Grid Engine (logic-only)

Refactors the calculation logic from OC_EF_GOD.py into pure functions.
Streamlit UI must call compute_ocef() and must NOT implement formulas itself.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List
import math


@dataclass(frozen=True)
class SystemInputs:
    mva: float
    hv_kv: float
    lv_kv: float
    z_pct: float
    cti_ms: float
    q4_ct: float
    q5_ct: float


@dataclass(frozen=True)
class FeederInputs:
    load_a: float
    ct_a: float


@dataclass(frozen=True)
class SystemResults:
    flc_lv: float
    flc_hv: float
    isc_lv: float
    if_lv: float
    if_hv: float
    total_load: float
    hv_load: float


@dataclass(frozen=True)
class OCEFResults:
    system: SystemResults
    oc_report_text: str
    ef_report_text: str
    ct_alerts: List[str]
    critical_overload: bool


def compute_ocef(sys: SystemInputs, feeders: List[FeederInputs]) -> OCEFResults:
    cti_ms = float(sys.cti_ms)
    if cti_ms < 120:
        raise ValueError("CTI must be greater than or equal to 120ms.")

    mva, hv_v, lv_v = float(sys.mva), float(sys.hv_kv), float(sys.lv_kv)
    z_pct = float(sys.z_pct)
    q4_ct, q5_ct = float(sys.q4_ct), float(sys.q5_ct)
    cti_s = cti_ms / 1000.0

    flc_lv = round((mva * 1000) / (math.sqrt(3) * lv_v), 2)
    flc_hv = round((mva * 1000) / (math.sqrt(3) * hv_v), 2)
    isc_lv = round(flc_lv / (z_pct / 100), 2)

    if_lv = round(isc_lv * 0.9, 2)
    if_hv = round(if_lv / (hv_v / lv_v), 2)

    total_load = 0.0
    max_t_oc = 0.0
    max_t_ef = 0.0

    f_oc_txt = ""
    f_ef_txt = ""
    ct_alerts: List[str] = []

    # Feeders Q1..Qn
    for i, fd in enumerate(feeders):
        l = float(fd.load_a)
        ct = float(fd.ct_a)
        total_load += l

        if ct < l:
            ct_alerts.append(f"ALERT: Feeder Q{i+1} CT ({ct}A) is less than Load ({l}A)\n")

        # OC calculations
        p_oc = round(1.1 * l, 2)
        r1 = round(p_oc / ct, 2)
        t_oc = round(0.025 * (0.14 / (math.pow(max(1.05, if_lv / p_oc), 0.02) - 1)), 3)
        max_t_oc = max(max_t_oc, t_oc)

        p2 = round(3 * l, 2)
        r2 = round(p2 / ct, 2)

        f_oc_txt += (
            f"FEEDER Q{i+1}: Load={l}A, CT={ct}\n"
            f" - S1 (IDMT): Pickup={p_oc}A ({r1}*In), TMS=0.025, Time={t_oc}s\n"
            f" - S2 (DT):   Pickup={p2}A ({r2}*In), Time=0.0s\n\n"
        )

        # EF calculations
        p_ef = round(0.15 * l, 2)
        r_ef1 = round(p_ef / ct, 2)
        t_ef = round(0.025 * (0.14 / (math.pow(max(1.05, if_lv / p_ef), 0.02) - 1)), 3)
        max_t_ef = max(max_t_ef, t_ef)

        p_ef2 = round(1.0 * l, 2)
        r_ef2 = round(p_ef2 / ct, 2)

        f_ef_txt += (
            f"FEEDER Q{i+1}: Load={l}A, CT={ct}\n"
            f" - S1 (IDMT): Pickup={p_ef}A ({r_ef1}*In), TMS=0.025, Time={t_ef}s\n"
            f" - S2 (DT):   Pickup={p_ef2}A ({r_ef2}*In), Time=0.0s\n\n"
        )

    hv_load = total_load / (hv_v / lv_v)

    if q4_ct < total_load:
        ct_alerts.append(f"ALERT: Q4 Incomer CT ({q4_ct}A) is less than Total Load ({total_load}A)\n")
    if q5_ct < hv_load:
        ct_alerts.append(f"ALERT: Q5 HV CT ({q5_ct}A) is less than HV Load ({round(hv_load,2)}A)\n")

    # Q4 + Q5 coordination
    coord_data = [
        ("INCOMER Q4 (LV)", q4_ct, if_lv, 1, round(0.9 * isc_lv, 2), cti_ms, max_t_oc, max_t_ef),
        ("HV SIDE Q5 (HV)", q5_ct, if_hv, hv_v / lv_v, round(if_hv, 2), cti_ms * 2, max_t_oc + cti_s, max_t_ef + cti_s)
    ]

    i_oc = ""
    i_ef = ""

    for name, ct_v, fault, scale, s3, dt_ms, t_prev_oc, t_prev_ef in coord_data:
        l_cur = total_load / scale

        t_req_oc = round(t_prev_oc + cti_s, 3)
        t_req_ef = round(t_prev_ef + cti_s, 3)

        # OC incomer/hv side
        p_oc = round(1.1 * l_cur, 2)
        r1 = round(p_oc / ct_v, 2)
        tms_oc = round(t_req_oc / (0.14 / (math.pow(max(1.05, fault / p_oc), 0.02) - 1)), 3)

        p2 = round(3 * l_cur, 2)
        r2 = round(p2 / ct_v, 2)
        r3 = round(s3 / ct_v, 2)

        i_oc += (
            f"{name}: Load={round(l_cur,2)}A, CT={ct_v}\n"
            f" - S1 (IDMT): Pickup={p_oc}A ({r1}*In), TMS={tms_oc}, Time={t_req_oc}s\n"
            f" - S2 (DT):   Pickup={p2}A ({r2}*In), Time={dt_ms/1000}s\n"
            f" - S3 (DT):   Pickup={s3}A ({r3}*In), Time=0.0s\n\n"
        )

        # EF incomer/hv side
        p_ef = round(0.15 * l_cur, 2)
        r_ef1 = round(p_ef / ct_v, 2)
        tms_ef = round(t_req_ef / (0.14 / (math.pow(max(1.05, fault / p_ef), 0.02) - 1)), 3)

        p_ef2 = round(1.0 * l_cur, 2)
        r_ef2 = round(p_ef2 / ct_v, 2)
        r_ef3 = round(s3 / ct_v, 2)

        i_ef += (
            f"{name}: Load={round(l_cur,2)}A, CT={ct_v}\n"
            f" - S1 (IDMT): Pickup={p_ef}A ({r_ef1}*In), TMS={tms_ef}, Time={t_req_ef}s\n"
            f" - S2 (DT):   Pickup={p_ef2}A ({r_ef2}*In), Time={dt_ms/1000}s\n"
            f" - S3 (DT):   Pickup={s3}A ({r_ef3}*In), Time=0.0s\n\n"
        )

    head = f"FLC LV: {flc_lv}A | FLC HV: {flc_hv}A | Short Circuit: {isc_lv}A\n" + "=" * 60 + "\n"

    critical_overload = (total_load > flc_lv)
    prefix = ""
    if critical_overload:
        prefix += f"CRITICAL ALERT: TRANSFORMER OVERLOAD ({total_load}A > {flc_lv}A)\n"
    for a in ct_alerts:
        prefix += a

    oc_report_text = prefix + head + f_oc_txt + i_oc
    ef_report_text = prefix + head + f_ef_txt + i_ef

    sys_res = SystemResults(
        flc_lv=flc_lv,
        flc_hv=flc_hv,
        isc_lv=isc_lv,
        if_lv=if_lv,
        if_hv=if_hv,
        total_load=total_load,
        hv_load=hv_load,
    )

    return OCEFResults(
        system=sys_res,
        oc_report_text=oc_report_text,
        ef_report_text=ef_report_text,
        ct_alerts=ct_alerts,
        critical_overload=critical_overload,
    )
