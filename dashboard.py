import streamlit as st
import plotly.graph_objects as go
import json
from web3 import Web3
from weather_fetcher import get_weather
from disaster_detector import DisasterDetector

st.set_page_config(page_title="AI Crop Insurance", layout="wide")
st.title("🌾 AI Crop Insurance Agent")
st.caption("Autonomous weather monitoring + automatic payouts on Flare")

# ===== CONFIG =====
CONTRACT_ADDRESS = "0x6A0088D3885b0Ea10a0bCF9bb9938140DfeD1Dad"
RPC_URL = "https://coston2-api.flare.network/ext/C/rpc"

# ===== SIDEBAR =====
st.sidebar.header("📍 Select Location")
locations = {
    "Nairobi, Kenya": (-1.286, 36.817),
    "Mumbai, India": (19.076, 72.877),
    "Oxford, UK": (51.752, -1.258),
    "São Paulo, Brazil": (-23.550, -46.633),
}
selected = st.sidebar.selectbox("Location", list(locations.keys()))
lat, lon = locations[selected]

# ===== FETCH WEATHER =====
weather = get_weather(lat, lon)
current = weather["current"]
daily = weather["daily"]

# ===== CURRENT CONDITIONS =====
st.subheader(f"Current Conditions — {selected}")
col1, col2, col3, col4 = st.columns(4)
col1.metric("🌡️ Temperature", f"{current['temperature_2m']}°C")
col2.metric("🌧️ Rainfall", f"{current['rain']}mm")
col3.metric("💧 Humidity", f"{current['relative_humidity_2m']}%")
col4.metric("💨 Wind", f"{current['wind_speed_10m']} km/h")

# ===== AI DETECTION =====
st.subheader("🤖 AI Disaster Detection")
detector = DisasterDetector()
detector.train(daily)
result = detector.detect(current, daily)

if result["disaster"]:
    st.error(f"🚨 DISASTER DETECTED: {result['type']} (confidence: {result['confidence']:.2f})")
else:
    st.success("✅ No disaster detected — conditions normal")

col_a, col_b = st.columns(2)
col_a.info(f"📏 Rule-based detector: **{result['rule_detector']['result']}**\n\n{result['rule_detector']['reason']}")
col_b.info(f"🧠 ML detector (Isolation Forest): **{result['ml_detector']['result']}**\n\nAnomaly score: {result['ml_detector']['score']:.3f}")

# ===== SIMULATE DISASTER =====
st.subheader("🔴 Demo: Simulate Disaster")
sim_col1, sim_col2, sim_col3 = st.columns(3)

if sim_col1.button("🏜️ Simulate DROUGHT"):
    fake_daily = {**daily, "rain_sum": [0]*len(daily["rain_sum"])}
    fake_current = {**current, "temperature_2m": 40, "rain": 0, "relative_humidity_2m": 10, "wind_speed_10m": 30}
    det = DisasterDetector()
    det.train(fake_daily)
    r = det.detect(fake_current, fake_daily)
    st.error(f"🚨 Simulated result: {r['type']} | Rule: {r['rule_detector']['result']} | ML: {r['ml_detector']['result']}")

if sim_col2.button("🌊 Simulate FLOOD"):
    fake_current = {**current, "temperature_2m": 20, "rain": 85, "relative_humidity_2m": 98, "wind_speed_10m": 45}
    r = detector.detect(fake_current, daily)
    st.error(f"🚨 Simulated result: {r['type']} | Rule: {r['rule_detector']['result']} | ML: {r['ml_detector']['result']}")

if sim_col3.button("🥶 Simulate FROST"):
    fake_current = {**current, "temperature_2m": -3, "rain": 0, "relative_humidity_2m": 85, "wind_speed_10m": 5}
    r = detector.detect(fake_current, daily)
    st.error(f"🚨 Simulated result: {r['type']} | Rule: {r['rule_detector']['result']} | ML: {r['ml_detector']['result']}")

# ===== CHARTS =====
st.subheader("📊 14-Day Weather History")

fig_rain = go.Figure()
rain_vals = [r if r is not None else 0 for r in daily["rain_sum"]]
dates = daily.get("time", list(range(len(rain_vals))))
fig_rain.add_trace(go.Bar(x=dates, y=rain_vals, marker_color="#3b82f6", name="Rainfall"))
fig_rain.update_layout(title="Daily Rainfall (mm)", yaxis_title="mm", height=300)
st.plotly_chart(fig_rain, use_container_width=True)

fig_temp = go.Figure()
fig_temp.add_trace(go.Scatter(x=dates, y=daily["temperature_2m_max"], name="Max", line=dict(color="#ef4444")))
fig_temp.add_trace(go.Scatter(x=dates, y=daily["temperature_2m_min"], name="Min", line=dict(color="#3b82f6")))
fig_temp.update_layout(title="Temperature Range (°C)", yaxis_title="°C", height=300)
st.plotly_chart(fig_temp, use_container_width=True)

# ===== BLOCKCHAIN INFO =====
st.subheader("⛓️ Smart Contract on Flare")
st.code(f"Contract Address: {CONTRACT_ADDRESS}\nNetwork: Flare Testnet Coston2\nExplorer: https://coston2-explorer.flare.network/address/{CONTRACT_ADDRESS}")

try:
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    contract_abi = json.load(open("CropInsurance.json"))["abi"]
    contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=contract_abi)
    count = contract.functions.policyCount().call()
    st.metric("Active Policies", count)
except Exception as e:
    st.warning(f"Could not connect to contract: {e}")
