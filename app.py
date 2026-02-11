import streamlit as st
import pandas as pd
import plotly.express as px
import joblib
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="Hydrawall-X", layout="wide")
st.title("🛡️ Hydrawall-X | Kernel AI Monitor")

# 1. LOAD THE BRAIN
model = None
try:
    if os.path.exists('hydrawall_model.pkl'):
        model = joblib.load('hydrawall_model.pkl')
        st.sidebar.success("✅ AI Brain Online")
    else:
        st.sidebar.warning("⚠️ Model file not found.")
except Exception as e:
    st.sidebar.error(f"❌ Error loading model: {e}")

# 2. FILE UPLOAD
uploaded_file = st.file_uploader("Upload Kernel Data (CSV)", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    
    if model is not None:
        # 3. PREDICT ANOMALIES
        # Ensure the CSV has PID and PPID columns
        df['is_anomaly'] = model.predict(df[['PID', 'PPID']])
        df['Status'] = df['is_anomaly'].map({1: 'Normal', -1: 'ANOMALY'})
        
        # 4. DEFINE ANOMALIES FOR METRICS
        anomalies = df[df['is_anomaly'] == -1]

        # 5. INTEGRITY METRIC
        st.metric(
            label="System Integrity Score", 
            value="98%" if anomalies.empty else "42%", 
            delta="-56%" if not anomalies.empty else "0%"
        )

        # 6. ALERT LOGIC
        if not anomalies.empty:
            st.error(f"🚨 ALERT: {len(anomalies)} suspicious processes detected!")
            st.dataframe(anomalies[['PID', 'PPID', 'COMM', 'Status']])
        else:
            st.success("✅ System Status: Secure")

        # 7. VISUAL MAPPING
        fig = px.scatter(
            df, x="PID", y="PPID", color="Status", 
            hover_data=['COMM'],
            title="Kernel Process Distribution",
            color_discrete_map={'Normal': '#00CC96', 'ANOMALY': '#EF553B'}
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("Please ensure 'hydrawall_model.pkl' is in the directory to begin analysis.")
