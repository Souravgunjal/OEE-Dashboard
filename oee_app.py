Now edit this code to make dashboard more appealing, professioanl dont add too many  emojis and all, clean but color coded, my code: import streamlit as st
import pandas as pd
import numpy as np
import datetime

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="OEE Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- STYLING ---
st.markdown("""
    <style>
    .stApp {background-color: #f9f9f9;}
    .stButton>button {background-color:#0047ab;color:white;border-radius:5px;}
    .stMetric {background-color:#e6f0ff;padding:15px;border-radius:10px;}
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.title("🏭 OEE Dashboard - Manufacturing Performance")
st.markdown("Professional tool for **Availability, Performance, Quality, and OEE** analysis.")

# --- SIDEBAR INPUTS ---
st.sidebar.header("⚙️ Production Inputs")
st.sidebar.markdown("---")
planned_production_time = st.sidebar.number_input("⏱ Planned Production Time (min)", min_value=1.0, value=480.0)
downtime = st.sidebar.number_input("🛑 Downtime (min)", min_value=0.0, value=60.0)
ideal_cycle_time = st.sidebar.number_input("⚙️ Ideal Cycle Time/unit (min)", min_value=0.01, value=0.5)
total_units = st.sidebar.number_input("📦 Total Units Produced", min_value=1, value=800)
good_units = st.sidebar.number_input("✅ Good Units Produced", min_value=0, value=780)

# --- CALCULATIONS ---
running_time = planned_production_time - downtime
availability = running_time / planned_production_time
performance = (ideal_cycle_time * total_units) / running_time
quality = good_units / total_units
oee = availability * performance * quality

# --- KPI COLORS ---
def color_value(value):
    if value < 0.6:
        return "🔴"
    elif value < 0.85:
        return "🟡"
    else:
        return "🟢"

# --- TABS ---
tab1, tab2, tab3, tab4 = st.tabs(["📊 KPIs", "📈 Trends", "📅 Daily Log", "📥 Export Data"])

# --- TAB 1: KPIs ---
with tab1:
    st.subheader("Key Performance Indicators")
    c1, c2, c3, c4 = st.columns(4)

    c1.metric("⚡ Availability", f"{availability*100:.2f}% {color_value(availability)}")
    c2.metric("🚀 Performance", f"{performance*100:.2f}% {color_value(performance)}")
    c3.metric("✅ Quality", f"{quality*100:.2f}% {color_value(quality)}")
    c4.metric("🏆 OEE", f"{oee*100:.2f}% {color_value(oee)}")

    st.markdown("---")
    st.subheader("OEE Indicator")

    st.progress(min(oee, 1.0))
    st.caption(f"Overall Equipment Effectiveness: **{oee*100:.2f}%**")

# --- TAB 2: Trends ---
with tab2:
    st.subheader("📈 OEE & Components Trend")

    if "log" in st.session_state and len(st.session_state.log) > 0:
        chart_df = st.session_state.log.set_index("Date")
        st.line_chart(chart_df)
    else:
        st.info("No historical data yet. Save today's OEE first!")

# --- TAB 3: Daily Log ---
with tab3:
    st.subheader("📅 Daily OEE Log")

    if "log" not in st.session_state:
        st.session_state.log = pd.DataFrame(
            columns=["Date", "Availability", "Performance", "Quality", "OEE"]
        )

    if st.button("💾 Save Today's OEE"):
        new_entry = {
            "Date": datetime.date.today().strftime("%Y-%m-%d"),
            "Availability": availability * 100,
            "Performance": performance * 100,
            "Quality": quality * 100,
            "OEE": oee * 100
        }
        st.session_state.log = pd.concat(
            [st.session_state.log, pd.DataFrame([new_entry])],
            ignore_index=True
        )
        st.success("Saved!")

    st.dataframe(st.session_state.log)

# --- TAB 4: Export Data ---
with tab4:
    st.subheader("📥 Download OEE Log")

    if "log" in st.session_state and len(st.session_state.log) > 0:
        csv = st.session_state.log.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download CSV",
            csv,
            "oee_log.csv",
            "text/csv"
        )
    else:
        st.info("No data available yet.")

