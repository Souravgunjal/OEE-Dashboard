import streamlit as st
import pandas as pd
import datetime

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="OEE Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- THEME / STYLING (clean, professional, color-coded) ---
st.markdown(
    """
<style>
/* App background */
.stApp { background-color: #F6F7FB; }

/* Sidebar */
section[data-testid="stSidebar"]{
  background: #FFFFFF;
  border-right: 1px solid #E6E8F0;
}

/* Header */
.app-title { font-size: 30px; font-weight: 700; margin: 0 0 4px 0; color: #111827; }
.app-subtitle { margin: 0 0 14px 0; color: #6B7280; }

/* Card container */
.card {
  background: #FFFFFF;
  border: 1px solid #E6E8F0;
  border-radius: 14px;
  padding: 14px 16px;
  box-shadow: 0 1px 2px rgba(16,24,40,0.04);
}

/* KPI label/value */
.kpi-label { font-size: 12px; color: #6B7280; margin-bottom: 6px; text-transform: uppercase; letter-spacing: .04em; }
.kpi-value { font-size: 28px; font-weight: 800; color: #111827; margin: 0; }
.kpi-badge {
  display: inline-block;
  margin-top: 10px;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
}

/* Badges (status) */
.badge-good { background: rgba(16,185,129,0.12); color: #065F46; }
.badge-warn { background: rgba(245,158,11,0.14); color: #92400E; }
.badge-bad  { background: rgba(239,68,68,0.12); color: #991B1B; }

/* Buttons */
.stButton>button {
  background: #1F4FFF;
  color: white;
  border-radius: 10px;
  border: 1px solid #1F4FFF;
  padding: 8px 14px;
  font-weight: 600;
}
.stButton>button:hover {
  background: #173ED6;
  border: 1px solid #173ED6;
}

/* Tabs */
button[data-baseweb="tab"] {
  font-weight: 600;
}
</style>
""",
    unsafe_allow_html=True,
)

# --- HELPERS ---
def status_label(value: float):
    """
    Thresholds:
    - Good: >= 0.85
    - Watch: 0.60–0.85
    - Needs attention: < 0.60
    """
    if value >= 0.85:
        return "GOOD", "badge-good"
    elif value >= 0.60:
        return "WATCH", "badge-warn"
    else:
        return "NEEDS ATTENTION", "badge-bad"


def clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


# --- HEADER ---
st.markdown('<div class="app-title">OEE Dashboard</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="app-subtitle">Track Availability, Performance, Quality, and Overall Equipment Effectiveness with a clean daily log and trend view.</div>',
    unsafe_allow_html=True,
)

# --- SIDEBAR INPUTS ---
st.sidebar.markdown("### Production Inputs")
st.sidebar.caption("Enter shift values. Results update instantly.")
st.sidebar.markdown("---")

planned_production_time = st.sidebar.number_input(
    "Planned Production Time (min)", min_value=1.0, value=480.0, step=10.0
)
downtime = st.sidebar.number_input(
    "Downtime (min)", min_value=0.0, value=60.0, step=5.0
)
ideal_cycle_time = st.sidebar.number_input(
    "Ideal Cycle Time (min/unit)", min_value=0.01, value=0.50, step=0.01
)
total_units = st.sidebar.number_input(
    "Total Units Produced", min_value=1, value=800, step=10
)
good_units = st.sidebar.number_input(
    "Good Units Produced", min_value=0, value=780, step=10
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Targets")
target_oee = st.sidebar.slider("OEE Target", min_value=0.50, max_value=0.95, value=0.85, step=0.01)

# --- CALCULATIONS (guard rails) ---
running_time = max(planned_production_time - downtime, 0.0001)
availability = clamp01(running_time / planned_production_time)

# Performance can exceed 1 if ideal cycle time assumption is off; keep for transparency, but clamp for KPI gauge.
raw_performance = (ideal_cycle_time * total_units) / running_time
performance = raw_performance  # show real value
quality = clamp01(good_units / total_units)

oee = availability * clamp01(performance) * quality  # clamp perf for OEE consistency

# Status tags
a_txt, a_cls = status_label(availability)
p_txt, p_cls = status_label(clamp01(performance))
q_txt, q_cls = status_label(quality)
o_txt, o_cls = status_label(oee)

# --- TABS ---
tab1, tab2, tab3, tab4 = st.tabs(["KPIs", "Trends", "Daily Log", "Export"])

# --- TAB 1: KPIs ---
with tab1:
    st.markdown("#### Key Performance Indicators")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(
            f"""
            <div class="card">
              <div class="kpi-label">Availability</div>
              <div class="kpi-value">{availability*100:.1f}%</div>
              <span class="kpi-badge {a_cls}">{a_txt}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            f"""
            <div class="card">
              <div class="kpi-label">Performance</div>
              <div class="kpi-value">{clamp01(performance)*100:.1f}%</div>
              <span class="kpi-badge {p_cls}">{p_txt}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.caption(f"Raw Performance (unclamped): {raw_performance*100:.1f}%")

    with c3:
        st.markdown(
            f"""
            <div class="card">
              <div class="kpi-label">Quality</div>
              <div class="kpi-value">{quality*100:.1f}%</div>
              <span class="kpi-badge {q_cls}">{q_txt}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c4:
        st.markdown(
            f"""
            <div class="card">
              <div class="kpi-label">OEE</div>
              <div class="kpi-value">{oee*100:.1f}%</div>
              <span class="kpi-badge {o_cls}">{o_txt}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("")

    # OEE gauge-style progress with target marker
    st.markdown("#### OEE Indicator")
    st.progress(clamp01(oee))
    st.caption(f"OEE Target: **{target_oee*100:.0f}%** • Current: **{oee*100:.1f}%**")

    # Small action hints (clean, not emoji-heavy)
    st.markdown("#### Quick focus")
    focus = []
    if availability < 0.85:
        focus.append("Reduce unplanned downtime and speed up recovery/startup.")
    if clamp01(performance) < 0.85:
        focus.append("Address minor stops and stabilize cycle time vs ideal.")
    if quality < 0.98:
        focus.append("Reduce defects/rework and improve first-pass yield.")
    if not focus:
        focus.append("Maintain controls and standard work; monitor for drift.")
    st.write("• " + "\n• ".join(focus))

# --- TAB 2: Trends ---
with tab2:
    st.markdown("#### OEE & Components Trend")
    if "log" in st.session_state and len(st.session_state.log) > 0:
        chart_df = st.session_state.log.copy()
        chart_df["Date"] = pd.to_datetime(chart_df["Date"])
        chart_df = chart_df.sort_values("Date").set_index("Date")

        # Display line chart (Streamlit default styling)
        st.line_chart(chart_df[["Availability", "Performance", "Quality", "OEE"]])
        st.caption("Tip: Consistent dips often correlate to downtime clusters or unstable operating windows.")
    else:
        st.info("No historical data yet. Save a few entries in the Daily Log to view trends.")

# --- TAB 3: Daily Log ---
with tab3:
    st.markdown("#### Daily OEE Log")

    if "log" not in st.session_state:
        st.session_state.log = pd.DataFrame(
            columns=["Date", "Availability", "Performance", "Quality", "OEE"]
        )

    colA, colB = st.columns([1, 3])
    with colA:
        log_date = st.date_input("Log date", value=datetime.date.today())

        if st.button("Save Entry"):
            new_entry = {
                "Date": log_date.strftime("%Y-%m-%d"),
                "Availability": availability,
                "Performance": clamp01(performance),
                "Quality": quality,
                "OEE": oee,
            }
            st.session_state.log = pd.concat(
                [st.session_state.log, pd.DataFrame([new_entry])],
                ignore_index=True,
            )
            st.success("Entry saved.")

    with colB:
        # Display as percentages for readability
        if len(st.session_state.log) > 0:
            display_df = st.session_state.log.copy()
            for col in ["Availability", "Performance", "Quality", "OEE"]:
                display_df[col] = (display_df[col] * 100).round(2)
            st.dataframe(display_df, use_container_width=True)
        else:
            st.info("No entries saved yet.")

# --- TAB 4: Export Data ---
with tab4:
    st.markdown("#### Export OEE Log")

    if "log" in st.session_state and len(st.session_state.log) > 0:
        export_df = st.session_state.log.copy()
        export_df["Date"] = pd.to_datetime(export_df["Date"]).dt.strftime("%Y-%m-%d")

        csv = export_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download CSV",
            csv,
            "oee_log.csv",
            "text/csv",
        )
        st.caption("Exports the stored log (Availability, Performance, Quality, OEE).")
    else:
        st.info("No data available yet. Save entries in the Daily Log first.")

    else:
        st.info("No data available yet.")


