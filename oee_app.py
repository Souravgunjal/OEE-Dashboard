import streamlit as st
import pandas as pd
import numpy as np
import datetime
import plotly.graph_objects as go

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
st.markdown("Professional interactive tool for **Availability, Performance, Quality, and OEE** analysis.")

# --- SIDEBAR INPUTS ---
st.sidebar.header("⚙️ Production Inputs")
st.sidebar.markdown("---")
planned_production_time = st.sidebar.number_input("⏱ Planned Production Time (min)", min_value=1.0, value=480.0)
downtime = st.sidebar.number_input("🛑 Downtime (min)", min_value=0.0, value=60.0)
ideal_cycle_time = st.sidebar.number_input("⚙️ Ideal Cycle Time/unit (min)", min_value=0.01, value=0.5)
total_units = st.sidebar.number_input("📦 Total Units Produced", min_value=1, value=800)
good_units = st.sidebar.number_input("✅ Good Units Produced", min_value=0, value=780)
st.sidebar.markdown("---")
st.sidebar.info("Input production parameters to calculate OEE metrics.")

# --- CALCULATIONS ---
running_time = planned_production_time - downtime
availability = running_time / planned_production_time if planned_production_time > 0 else 0
performance = (ideal_cycle_time * total_units) / running_time if running_time > 0 else 0
quality = good_units / total_units if total_units > 0 else 0
oee = availability * performance * quality

# --- KPI COLORS ---
def color_value(value):
    if value < 0.6: return "🔴"
    elif value < 0.85: return "🟡"
    else: return "🟢"

# --- TABS ---
tab1, tab2, tab3, tab4 = st.tabs(["📊 KPIs", "📈 Trends", "📅 Daily Log", "📥 Export Data"])

# --- TAB 1: KPIs ---
with tab1:
    st.subheader("Key Performance Indicators")
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("⚡ Availability", f"{availability*100:.2f}% {color_value(availability)}")
    kpi2.metric("🚀 Performance", f"{performance*100:.2f}% {color_value(performance)}")
    kpi3.metric("✅ Quality", f"{quality*100:.2f}% {color_value(quality)}")
    kpi4.metric("🏆 OEE", f"{oee*100:.2f}% {color_value(oee)}")

    st.markdown("---")
    st.subheader("OEE Gauge")
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=oee*100,
        number={'suffix': "%"},
        title={'text': "Overall Equipment Effectiveness"},
        delta={'reference': 80, 'relative': True, 'position': "top"},
        gauge={
            'axis': {'range':[0,100]},
            'bar': {'color':'darkblue'},
            'steps': [
                {'range':[0,40], 'color':'#ff4d4d'},
                {'range':[40,60], 'color':'#ffd11a'},
                {'range':[60,85], 'color':'#85e085'},
                {'range':[85,100], 'color':'#33cc33'}
            ],
        },
    ))
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("""
    **Legend:**  
    🔴 0–40% : Poor  
    🟡 40–60% : Average  
    🟢 60–85% : Good  
    🟢 85–100% : Excellent
    """)

# --- TAB 2: Trends ---
with tab2:
    st.subheader("📈 OEE & Components Trend")
    if "log" in st.session_state and len(st.session_state.log) > 0:
        trend_fig = go.Figure()
        trend_fig.add_trace(go.Scatter(x=st.session_state.log["Date"], y=st.session_state.log["Availability"], mode="lines+markers", name="Availability", line=dict(color="#1f77b4")))
        trend_fig.add_trace(go.Scatter(x=st.session_state.log["Date"], y=st.session_state.log["Performance"], mode="lines+markers", name="Performance", line=dict(color="#ff7f0e")))
        trend_fig.add_trace(go.Scatter(x=st.session_state.log["Date"], y=st.session_state.log["Quality"], mode="lines+markers", name="Quality", line=dict(color="#2ca02c")))
        trend_fig.add_trace(go.Scatter(x=st.session_state.log["Date"], y=st.session_state.log["OEE"], mode="lines+markers", name="OEE", line=dict(color="#d62728", width=4)))
        trend_fig.update_layout(xaxis_title="Date", yaxis_title="%", yaxis_range=[0,100])
        st.plotly_chart(trend_fig, use_container_width=True)
    else:
        st.info("No historical data yet. Save today's OEE first!")

# --- TAB 3: Daily Log ---
with tab3:
    st.subheader("📅 Daily OEE Log")
    if "log" not in st.session_state:
        st.session_state.log = pd.DataFrame(columns=["Date","Availability","Performance","Quality","OEE"])
    
    if st.button("💾 Save Today's OEE"):
        new_entry = {
            "Date": datetime.date.today().strftime("%Y-%m-%d"),
            "Availability": availability*100,
            "Performance": performance*100,
            "Quality": quality*100,
            "OEE": oee*100
        }
        st.session_state.log = pd.concat([st.session_state.log, pd.DataFrame([new_entry])], ignore_index=True)
        st.success("Saved!")
    
    st.dataframe(st.session_state.log)

# --- TAB 4: Export Data ---
with tab4:
    st.subheader("📥 Download OEE Log")
    if "log" in st.session_state and len(st.session_state.log) > 0:
        csv = st.session_state.log.to_csv(index=False).encode()
        st.download_button("Download CSV", csv, "oee_log.csv", "text/csv", key="download-csv")
    else:
        st.info("No data available yet to download.")


