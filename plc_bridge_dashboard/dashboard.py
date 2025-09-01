import time
import streamlit as st
import pandas as pd

from src.bridge import load_data, window
from src.kpis import throughput_pph, scrap_rate, oee_simple, availability, quality
from src.alarms import evaluate_alarms

st.set_page_config(page_title="PLC Bridge Dashboard", layout="wide")
st.title("PLC Bridge Dashboard (Simplified OEE)")

# Sidebar controls
auto_refresh = st.sidebar.checkbox("Auto-refresh", value=True)
refresh_sec = st.sidebar.slider("Refresh every (sec)", 1, 10, 3)
win_minutes = st.sidebar.slider("Window (minutes)", 5, 120, 60, step=5)

mt_max = st.sidebar.number_input("Motor Temp Max (°C)", value=80.0, step=0.5)
vb_max = st.sidebar.number_input("Vibration Max (mm/s)", value=7.5, step=0.1)

df = load_data()
if df.empty:
    st.warning("No data found yet. Generate some:\n\n"
               "`python src/generator.py --seconds 1800` (batch)\n\n"
               "`python src/generator.py --live --seconds 600` (live append)")
else:
    dfw = window(df, minutes=win_minutes)

    # KPIs
    tpph = throughput_pph(dfw)
    sr = scrap_rate(dfw)
    oee, A, Q = oee_simple(dfw)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Throughput (pph)", f"{tpph:,.1f}")
    c2.metric("Scrap Rate", f"{sr*100:.1f}%")
    c3.metric("OEE (A×Q)", f"{oee*100:.1f}%")
    c4.metric("A | Q", f"{A*100:.0f}% | {Q*100:.0f}%")

    # Charts
    left, right = st.columns(2)
    with left:
        st.subheader("Line Speed (units/min)")
        st.line_chart(dfw.set_index("timestamp")[["line_speed"]])

        st.subheader("Motor Temp (°C)")
        st.line_chart(dfw.set_index("timestamp")[["motor_temp"]])

    with right:
        st.subheader("Vibration (mm/s)")
        st.line_chart(dfw.set_index("timestamp")[["vibration_rms"]])

        st.subheader("Work Orders (count in window)")
        wo_counts = dfw["work_order"].value_counts().rename_axis("work_order").reset_index(name="count")
        if not wo_counts.empty:
            st.bar_chart(wo_counts.set_index("work_order"))
        else:
            st.info("No WO data in current window.")

    # Alarms
    st.subheader("Alarms")
    events = evaluate_alarms(dfw, motor_temp_max=mt_max, vibration_max=vb_max)
    if not events:
        st.success("No active alarms.")
    else:
        for sev, msg in events:
            if sev == "CRITICAL":
                st.error(f"[{sev}] {msg}")
            elif sev == "WARNING":
                st.warning(f"[{sev}] {msg}")
            else:
                st.info(f"[{sev}] {msg}")

    # Raw window + export
    with st.expander("Raw data (windowed)"):
        st.dataframe(dfw.tail(500))
        st.download_button("Download CSV (window)", data=dfw.to_csv(index=False),
                           file_name="plc_window.csv", mime="text/csv")

# simple auto-refresh
if auto_refresh:
    time.sleep(refresh_sec)
    st.rerun()
