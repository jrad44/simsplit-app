import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import json

# --- Page Setup ---
st.set_page_config(page_title="SimSplit Telemetry Analyzer", layout="wide")
st.markdown("<h1 style='text-align: center; color: #00ffcc;'>SimSplit • Advanced Telemetry Visualizer</h1>", unsafe_allow_html=True)

# --- File Uploads ---
col1, col2 = st.columns(2)
with col1:
    uploaded_file1 = st.file_uploader("📥 Upload the Garage61 lap you want to compare your time to (CSV file only)", type="csv", key="baseline")
with col2:
    uploaded_file2 = st.file_uploader("📥 Upload your Garage61 lap here (CSV file only)", type="csv", key="comparison")

# --- Helper Functions ---
def standardize_columns(df):
    df.columns = [col.strip() for col in df.columns]
    return df

def plot_overlaid_telemetry(df1, df2, driver1, driver2, frame=None):
    expected_cols = ['Speed', 'Throttle', 'Brake', 'Steering']
    fig = px.line()

    for df, driver in zip([df1, df2], [driver1, driver2]):
        available_cols = [col for col in expected_cols if col in df.columns]
        if 'SteeringWheelAngle' in df.columns and 'Steering' not in available_cols:
            available_cols.append('SteeringWheelAngle')

        if frame is not None:
            df = df.iloc[:frame+1]

        for col in available_cols:
            fig.add_scatter(x=df['LapDistPct'], y=df[col], mode='lines', name=f"{col} ({driver})")

    fig.update_layout(title="Telemetry Inputs Comparison", xaxis_title="Lap %", yaxis_title="Value")
    st.plotly_chart(fig, use_container_width=True)

def plot_overlaid_gps_map(df1, df2, driver1, driver2, frame=None):
    if 'Lat' in df1.columns and 'Lon' in df1.columns and 'Lat' in df2.columns and 'Lon' in df2.columns:
        if frame is not None:
            df1 = df1.iloc[:frame+1]
            df2 = df2.iloc[:frame+1]
        fig = px.line_mapbox(df1, lat='Lat', lon='Lon', zoom=13, height=400, color_discrete_sequence=["red"])
        fig.add_trace(px.line_mapbox(df2, lat='Lat', lon='Lon').data[0])
        fig.data[1].line.color = "blue"
        fig.update_layout(title="Driving Line Comparison", mapbox_style="carto-darkmatter", margin={"r":0,"t":30,"l":0,"b":0})
        st.plotly_chart(fig, use_container_width=True)

def detect_braking_points(df):
    if 'Brake' in df.columns:
        markers = df[df['Brake'] > 0.1][['LapDistPct']]
        return markers
    else:
        return pd.DataFrame()

def generate_ghost_json(df1, df2, driver1, driver2):
    frames = []
    total_frames = min(len(df1), len(df2))
    for i in range(total_frames):
        frame_data = {
            "frame": i,
            driver1: {
                "lat": df1.iloc[i]['Lat'] if 'Lat' in df1.columns else None,
                "lon": df1.iloc[i]['Lon'] if 'Lon' in df1.columns else None,
                "speed": df1.iloc[i]['Speed'] if 'Speed' in df1.columns else None
            },
            driver2: {
                "lat": df2.iloc[i]['Lat'] if 'Lat' in df2.columns else None,
                "lon": df2.iloc[i]['Lon'] if 'Lon' in df2.columns else None,
                "speed": df2.iloc[i]['Speed'] if 'Speed' in df2.columns else None
            }
        }
        frames.append(frame_data)
    return frames

# --- Main Logic ---
if uploaded_file1 and uploaded_file2:
    df1 = pd.read_csv(uploaded_file1)
    df2 = pd.read_csv(uploaded_file2)
    df1 = standardize_columns(df1)
    df2 = standardize_columns(df2)
    driver1 = uploaded_file1.name.replace('.csv', '')
    driver2 = uploaded_file2.name.replace('.csv', '')

    st.subheader(f"📊 {driver1} vs {driver2} Telemetry Overlaid")

    total_frames = min(len(df1), len(df2))
    frame = st.slider("Playback Position", min_value=0, max_value=total_frames-1, value=total_frames-1)

    plot_overlaid_telemetry(df1, df2, driver1, driver2, frame)
    plot_overlaid_gps_map(df1, df2, driver1, driver2, frame)

    braking_points_1 = detect_braking_points(df1)
    braking_points_2 = detect_braking_points(df2)

    st.write(f"**{len(braking_points_1)} braking zones detected in {driver1}.**")
    st.write(f"**{len(braking_points_2)} braking zones detected in {driver2}.**")

    # JSON Export Section
    st.subheader("⬇️ Export Ghost Replay JSON")
    ghost_data = generate_ghost_json(df1, df2, driver1, driver2)
    json_str = json.dumps(ghost_data)
    st.download_button(label="Download Ghost Replay JSON", data=json_str, file_name="ghost_replay.json", mime="application/json")

st.markdown("---")
st.markdown("<p style='text-align: center; font-size: 0.9em; color: gray;'>SimSplit is built by racers, for racers. 100% free.</p>", unsafe_allow_html=True)
