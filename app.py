import streamlit as st
import pandas as pd
import plotly.express as px

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

def plot_telemetry(df, driver_name, frame=None):
    expected_cols = ['Speed', 'Throttle', 'Brake', 'Steering']
    available_cols = [col for col in expected_cols if col in df.columns]

    if 'SteeringWheelAngle' in df.columns and 'Steering' not in available_cols:
        available_cols.append('SteeringWheelAngle')

    if frame is not None:
        df = df.iloc[:frame+1]

    if available_cols:
        fig = px.line(df, x='LapDistPct', y=available_cols,
                      title=f"{driver_name} • Inputs vs. Lap %",
                      labels={'LapDistPct': 'Lap %'})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No telemetry columns found to plot. Please check your CSV file.")

def plot_gps_map(df, driver_name, frame=None):
    if 'Lat' in df.columns and 'Lon' in df.columns:
        if frame is not None:
            df = df.iloc[:frame+1]
        fig = px.line_mapbox(df, lat='Lat', lon='Lon', zoom=13, height=400,
                             title=f"{driver_name} • GPS Driving Line")
        fig.update_layout(mapbox_style="carto-darkmatter", margin={"r":0,"t":30,"l":0,"b":0})
        st.plotly_chart(fig, use_container_width=True)

def detect_braking_points(df):
    markers = df[df['Brake'] > 0.1][['LapDistPct']]
    return markers

def plot_comparison(merged_df, lap_name_1, lap_name_2, frame=None):
    if frame is not None:
        merged_df = merged_df.iloc[:frame+1]
    fig = px.line(merged_df, x='LapDistPct',
                  y=[f'Speed_{lap_name_1}', f'Speed_{lap_name_2}'],
                  title="Speed Comparison",
                  labels={'LapDistPct': 'Lap %'})
    fig.update_layout(legend_title_text="Driver")
    st.plotly_chart(fig, use_container_width=True)

# --- Main Logic ---
if uploaded_file1:
    df1 = pd.read_csv(uploaded_file1)
    df1 = standardize_columns(df1)
    driver1 = uploaded_file1.name.replace('.csv', '')

    st.subheader(f"📊 {driver1} Baseline Lap Telemetry")
    total_frames1 = len(df1)
    frame1 = st.slider(f"Playback Position for {driver1}", min_value=0, max_value=total_frames1-1, value=total_frames1-1)

    plot_telemetry(df1, driver1, frame1)
    plot_gps_map(df1, driver1, frame1)

    braking_points_1 = detect_braking_points(df1)
    st.write(f"**{len(braking_points_1)} braking zones detected in {driver1}.**")

if uploaded_file1 and uploaded_file2:
    df2 = pd.read_csv(uploaded_file2)
    df2 = standardize_columns(df2)
    driver2 = uploaded_file2.name.replace('.csv', '')

    st.subheader(f"🔁 Telemetry Comparison: {driver1} vs. {driver2}")

    if 'LapDistPct' in df1.columns and 'LapDistPct' in df2.columns:
        merged = pd.merge(df1, df2, on='LapDistPct', suffixes=(f'_{driver1}', f'_{driver2}'))
        total_frames_merged = len(merged)
        frame_merged = st.slider("Playback Position for Comparison", min_value=0, max_value=total_frames_merged-1, value=total_frames_merged-1)
        plot_comparison(merged, driver1, driver2, frame_merged)
    else:
        st.warning("Cannot compare laps – column 'LapDistPct' missing from one or both CSV files.")

    plot_gps_map(df2, driver2)
    braking_points_2 = detect_braking_points(df2)
    st.write(f"**{len(braking_points_2)} braking zones detected in {driver2}.**")

st.markdown("---")
st.markdown("<p style='text-align: center; font-size: 0.9em; color: gray;'>SimSplit is built by racers, for racers. 100% free.</p>", unsafe_allow_html=True)
