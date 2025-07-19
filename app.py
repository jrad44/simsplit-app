import streamlit as st
import pandas as pd
import plotly.express as px

# --- Page setup ---
st.set_page_config(page_title="SimSplit Telemetry Analyzer", layout="wide")
st.markdown("<h1 style='text-align: center; color: #00ffcc;'>SimSplit • Telemetry Visualizer</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>Upload Garage61 or iRacing CSV telemetry files to compare your racing lines and inputs</p>", unsafe_allow_html=True)

# --- File uploads ---
col1, col2 = st.columns(2)
with col1:
    uploaded_file1 = st.file_uploader("📥 Upload Baseline Lap (CSV)", type="csv", key="baseline")
with col2:
    uploaded_file2 = st.file_uploader("📥 Upload Lap to Compare (Optional)", type="csv", key="comparison")

# --- Helper function to clean & detect columns ---
def standardize_columns(df):
    df.columns = [col.strip() for col in df.columns]
    return df

# --- Display Baseline Data ---
if uploaded_file1:
    df1 = pd.read_csv(uploaded_file1)
    df1 = standardize_columns(df1)

    st.subheader("📊 Baseline Lap Telemetry")
    try:
        fig1 = px.line(df1, x='LapDistPct', y=['Speed', 'Throttle', 'Brake', 'Steering'],
                       labels={'LapDistPct': 'Lap Distance (%)'},
                       title="Speed, Throttle, Brake, Steering vs Lap %")
        st.plotly_chart(fig1, use_container_width=True)
    except Exception as e:
        st.warning("Couldn't plot baseline telemetry. Please check CSV format.")

    if 'Lat' in df1.columns and 'Lon' in df1.columns:
        st.subheader("🗺️ Baseline GPS Driving Line")
        fig_map = px.line_mapbox(df1, lat='Lat', lon='Lon', zoom=13, height=400)
        fig_map.update_layout(mapbox_style="carto-darkmatter", margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig_map)

# --- Comparison Plot ---
if uploaded_file1 and uploaded_file2:
    df2 = pd.read_csv(uploaded_file2)
    df2 = standardize_columns(df2)

    st.subheader("🔁 Telemetry Comparison")

    try:
        merged = pd.merge(df1, df2, on='LapDistPct', suffixes=('_base', '_comp'))
        fig_comp = px.line(merged, x='LapDistPct',
                           y=['Speed_base', 'Speed_comp'],
                           labels={'LapDistPct': 'Lap Distance (%)'},
                           title="Speed Comparison")
        fig_comp.update_layout(legend_title_text="Lap Source")
        st.plotly_chart(fig_comp, use_container_width=True)
    except Exception as e:
        st.warning("Could not merge/compare files. Please ensure both files contain 'LapDistPct'.")

# --- Footer ---
st.markdown("---")
st.markdown("<p style='text-align: center; font-size: 0.9em; color: gray;'>SimSplit is built by racers, for racers. 100% free.</p>", unsafe_allow_html=True)
