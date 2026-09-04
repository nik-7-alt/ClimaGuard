import streamlit as st
import pandas as pd
import time
from pathlib import Path

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="ClimaGuard | Live AWS Monitoring",
    page_icon="🌦️",
    layout="wide"
)

BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "climaguard_dashboard_data.csv"

# =========================================================
# LOAD DATA
# =========================================================
@st.cache_data
def load_data():
    data = pd.read_csv(DATA_FILE)

    if "timestamp" in data.columns:
        data["timestamp"] = pd.to_datetime(data["timestamp"])

    return data


if not DATA_FILE.exists():
    st.error("climaguard_dashboard_data.csv not found.")
    st.stop()

df = load_data()

# =========================================================
# SESSION STATE
# =========================================================
if "running" not in st.session_state:
    st.session_state.running = False

if "index" not in st.session_state:
    st.session_state.index = 0

if "speed" not in st.session_state:
    st.session_state.speed = 1.0

# =========================================================
# CSS
# =========================================================
st.markdown("""
<style>

.main-title {
    font-size: 42px;
    font-weight: 800;
}

.subtitle {
    font-size: 17px;
    color: #64748b;
}

.live {
    color: #16a34a;
    font-weight: 700;
}

.alert {
    padding: 20px;
    border-radius: 14px;
    background: #fff7ed;
    border-left: 7px solid #f97316;
}

.normal {
    padding: 20px;
    border-radius: 14px;
    background: #ecfdf5;
    border-left: 7px solid #22c55e;
}

.weather {
    padding: 20px;
    border-radius: 14px;
    background: #eff6ff;
    border-left: 7px solid #3b82f6;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# HEADER
# =========================================================
st.markdown(
    '<div class="main-title">🌦️ ClimaGuard</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'AI-Powered Intelligent Anomaly Detection for Automatic Weather Stations'
    '</div>',
    unsafe_allow_html=True
)

st.caption(
    "Smart India Hackathon 2026 • SIH26073 • CodeYoddhas"
)

# =========================================================
# SIDEBAR CONTROLS
# =========================================================
st.sidebar.title("🎛️ Monitoring Control")

st.sidebar.markdown("### System")

if st.session_state.running:
    st.sidebar.success("🟢 LIVE MONITORING")
else:
    st.sidebar.info("⏸️ MONITORING PAUSED")

speed = st.sidebar.selectbox(
    "Simulation Speed",
    [0.5, 1.0, 1.5, 2.0],
    index=1,
    format_func=lambda x: f"{x}×"
)

st.session_state.speed = speed

st.sidebar.markdown("---")

st.sidebar.markdown("### Controls")

col_a, col_b = st.sidebar.columns(2)

with col_a:
    if st.button("▶ Start"):
        st.session_state.running = True
        st.rerun()

with col_b:
    if st.button("⏸ Pause"):
        st.session_state.running = False
        st.rerun()

if st.sidebar.button("🔄 Reset"):
    st.session_state.index = 0
    st.session_state.running = False
    st.rerun()

st.sidebar.markdown("---")

st.sidebar.markdown("### AWS Station")

st.sidebar.info(
    """
**AWS-001**

📍 Nellore Region

🟢 Sensor connection active

📡 3 parameters monitored

🌡 Temperature  
💧 Humidity  
🌪 Pressure
"""
)

# =========================================================
# CURRENT READING
# =========================================================
current = df.iloc[st.session_state.index]

status = str(current.get("status", "Normal"))

confidence = float(
    current.get("confidence_percent", 0)
)

temperature = float(current["temperature"])
humidity = float(current["humidity"])
pressure = float(current["pressure"])

affected_sensor = current.get(
    "affected_sensor",
    "Multiple"
)

severity = current.get(
    "severity",
    "Normal"
)

explanation = current.get(
    "explanation",
    "No significant anomaly detected."
)

timestamp = current.get(
    "timestamp",
    ""
)

# =========================================================
# LIVE STATUS
# =========================================================
st.markdown("### 📡 Live Monitoring")

if status == "Normal":

    st.markdown(
        """
        <div class="normal">
        <h3>🟢 SYSTEM NORMAL</h3>
        All monitored AWS parameters are behaving normally.
        </div>
        """,
        unsafe_allow_html=True
    )

elif "Weather Event" in status:

    st.markdown(
        f"""
        <div class="weather">
        <h3>🌦️ GENUINE WEATHER EVENT</h3>
        ClimaGuard detected a coordinated change across multiple
        atmospheric parameters.
        </div>
        """,
        unsafe_allow_html=True
    )

else:

    st.markdown(
        f"""
        <div class="alert">
        <h3>🚨 SENSOR ANOMALY DETECTED</h3>
        <b>{status}</b><br>
        ClimaGuard has detected abnormal sensor behavior.
        </div>
        """,
        unsafe_allow_html=True
    )

# =========================================================
# SENSOR VALUES
# =========================================================
st.markdown("### 🌡️ Current Sensor Readings")

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric(
        "Temperature",
        f"{temperature:.2f} °C"
    )

with c2:
    st.metric(
        "Humidity",
        f"{humidity:.2f} %"
    )

with c3:
    st.metric(
        "Pressure",
        f"{pressure:.2f} hPa"
    )

with c4:
    st.metric(
        "AI Confidence",
        f"{confidence:.1f}%"
    )

# =========================================================
# AI DECISION
# =========================================================
st.markdown("---")
st.markdown("### 🤖 ClimaGuard AI Decision")

d1, d2, d3 = st.columns(3)

with d1:
    st.write("**Detection**")
    st.write(status)

with d2:
    st.write("**Affected Sensor**")
    st.write(affected_sensor)

with d3:
    st.write("**Severity**")
    st.write(severity)

st.markdown("#### 🧠 Why did ClimaGuard make this decision?")

st.info(explanation)

st.caption(
    f"Latest AWS reading: {timestamp}"
)

# =========================================================
# LIVE GRAPH
# =========================================================
st.markdown("---")
st.markdown("### 📈 Live Sensor Stream")

start = max(
    0,
    st.session_state.index - 80
)

graph_df = df.iloc[start:st.session_state.index + 1].copy()

if len(graph_df) > 0:

    graph_df = graph_df.set_index("timestamp")

    st.line_chart(
        graph_df[
            [
                "temperature",
                "humidity",
                "pressure"
            ]
        ]
    )

# =========================================================
# ALERT LOG
# =========================================================
st.markdown("---")
st.markdown("### 🚨 Recent Alerts")

past = df.iloc[:st.session_state.index + 1]

alerts = past[
    past["status"] != "Normal"
].tail(10)

if len(alerts) == 0:

    st.success(
        "No anomalies detected in the current monitoring period."
    )

else:

    alert_columns = [
        "timestamp",
        "status",
        "affected_sensor",
        "severity",
        "confidence_percent"
    ]

    alert_columns = [
        c for c in alert_columns
        if c in alerts.columns
    ]

    st.dataframe(
        alerts[alert_columns],
        use_container_width=True,
        hide_index=True
    )

# =========================================================
# SYSTEM STATISTICS
# =========================================================
st.markdown("---")
st.markdown("### 📊 Monitoring Statistics")

observed = df.iloc[:st.session_state.index + 1]

total = len(observed)

normal_count = int(
    (observed["status"] == "Normal").sum()
)

alert_count = total - normal_count

s1, s2, s3, s4 = st.columns(4)

with s1:
    st.metric(
        "Readings Processed",
        total
    )

with s2:
    st.metric(
        "Normal",
        normal_count
    )

with s3:
    st.metric(
        "Alerts",
        alert_count
    )

with s4:
    st.metric(
        "Avg Confidence",
        f"{observed['confidence_percent'].mean():.1f}%"
    )

# =========================================================
# DEMO SCENARIOS
# =========================================================
st.markdown("---")
st.markdown("### 🎯 SIH Demo Scenarios")

st.write(
    "Use these readings during your presentation to demonstrate "
    "different ClimaGuard capabilities."
)

scenario_data = {
    "Temperature Spike": 100,
    "Frozen Sensor": 505,
    "Sensor Drift": 717,
    "Pressure Spike": 850,
    "Genuine Weather Event": 902,
    "Weather Event Recovery": 906
}

cols = st.columns(3)

for i, (name, idx) in enumerate(scenario_data.items()):

    with cols[i % 3]:

        if st.button(
            name,
            key=f"scenario_{idx}"
        ):

            st.session_state.index = idx
            st.session_state.running = False
            st.rerun()

# =========================================================
# AUTO PLAY
# =========================================================
if st.session_state.running:

    if st.session_state.index < len(df) - 1:

        time.sleep(
            max(0.2, 1.0 / st.session_state.speed)
        )

        st.session_state.index += 1

        st.rerun()

    else:

        st.session_state.running = False

        st.success(
            "Live simulation completed."
        )

# =========================================================
# FOOTER
# =========================================================
st.markdown("---")

st.markdown(
    """
    <div style="text-align:center; padding:20px; color:#64748b;">
    <b>ClimaGuard</b> — Intelligent AWS Anomaly Detection<br>
    Smart India Hackathon 2026 | SIH26073 | CodeYoddhas
    </div>
    """,
    unsafe_allow_html=True
)