import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import random
import numpy as np
from datetime import datetime, timedelta
import time

# Page configuration
st.set_page_config(
    page_title="🔋 EV Battery Dashboard",
    page_icon="🔋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark theme CSS with black background and white text
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .stApp {
        background-color: #000000 !important;
        color: #ffffff !important;
        font-family: 'Inter', sans-serif;
    }
    
    .main .block-container {
        background-color: #000000 !important;
        color: #ffffff !important;
    }
    
    .metric-card {
        background-color: #111111 !important;
        color: #ffffff !important;
        border-radius: 16px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        border: 1px solid #333333;
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        background-color: #1a1a1a !important;
        border-color: #555555;
    }
    
    .stButton > button {
        background-color: #333333 !important;
        color: #ffffff !important;
        border: 1px solid #555555;
        padding: 0.75rem 2rem;
        border-radius: 12px;
        font-weight: 600;
        font-size: 16px;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: #444444 !important;
        border-color: #777777 !important;
    }
    
    .stSelectbox > div > div {
        background-color: #111111 !important;
        color: #ffffff !important;
        border: 1px solid #333333 !important;
        border-radius: 10px;
    }
    
    .stSelectbox label {
        color: #ffffff !important;
    }
    
    .stDataFrame, .stDataFrame > div, .stDataFrame table {
        background-color: #111111 !important;
        color: #ffffff !important;
        border: 1px solid #333333;
        border-radius: 12px;
    }
    
    .stMetric {
        background-color: #111111 !important;
        color: #ffffff !important;
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid #333333;
    }
    
    .stMetric label {
        color: #ffffff !important;
    }
    
    .stMetric > div > div {
        color: #ffffff !important;
    }
    
    .alert-success {
        background-color: #1a4d1a !important;
        color: #ffffff !important;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border: 1px solid #2d7d2d;
    }
    
    .alert-warning {
        background-color: #4d3d1a !important;
        color: #ffffff !important;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border: 1px solid #7d6d2d;
    }
    
    .alert-danger {
        background-color: #4d1a1a !important;
        color: #ffffff !important;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border: 1px solid #7d2d2d;
    }
    
    .sidebar-header {
        background-color: #222222 !important;
        color: #ffffff !important;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        text-align: center;
        font-weight: 600;
        border: 1px solid #444444;
    }
    
    .chart-container {
        background-color: #111111 !important;
        border-radius: 15px;
        padding: 1rem;
        margin: 1rem 0;
        border: 1px solid #333333;
    }
    
    .title-header {
        text-align: center;
        color: #ffffff !important;
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 2rem;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #111111 !important;
    }
    
    .stSidebar > div {
        background-color: #111111 !important;
        color: #ffffff !important;
    }
    
    .stSidebar label {
        color: #ffffff !important;
    }
    
    /* Tab styling */
    .stTabs [role="tab"] {
        background-color: #222222 !important;
        color: #ffffff !important;
        border: 1px solid #444444;
        margin: 4px;
        padding: 10px 16px;
        border-radius: 8px;
    }
    
    .stTabs [role="tab"][aria-selected="true"] {
        background-color: #333333 !important;
        color: #ffffff !important;
        border-color: #555555;
    }
    
    .stTabs [role="tabpanel"] {
        background-color: #000000 !important;
        color: #ffffff !important;
    }
    
    /* Text elements */
    h1, h2, h3, h4, h5, h6, p, div, span, label {
        color: #ffffff !important;
    }
    
    /* Input elements */
    .stSlider label {
        color: #ffffff !important;
    }
    
    .stCheckbox label {
        color: #ffffff !important;
    }
    
    .stToggle label {
        color: #ffffff !important;
    }
    
    /* Plotly charts dark theme */
    .js-plotly-plot {
        background-color: #111111 !important;
        border-radius: 10px;
        border: 1px solid #333333;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'cells_data' not in st.session_state:
    st.session_state.cells_data = {}
if 'monitoring_active' not in st.session_state:
    st.session_state.monitoring_active = False
if 'last_update' not in st.session_state:
    st.session_state.last_update = datetime.now()

# Cell specifications with realistic parameters
CELL_SPECS = {
    "LFP": {"nominal_voltage": 3.2, "max_voltage": 3.6, "min_voltage": 2.5, "capacity": 100, "color": "#4CAF50"},
    "NMC": {"nominal_voltage": 3.7, "max_voltage": 4.2, "min_voltage": 3.0, "capacity": 120, "color": "#2196F3"},
    "NCA": {"nominal_voltage": 3.6, "max_voltage": 4.2, "min_voltage": 2.8, "capacity": 110, "color": "#FF9800"},
    "LCO": {"nominal_voltage": 3.7, "max_voltage": 4.2, "min_voltage": 3.0, "capacity": 140, "color": "#9C27B0"},
    "LTO": {"nominal_voltage": 2.4, "max_voltage": 2.8, "min_voltage": 1.5, "capacity": 80, "color": "#F44336"}
}

def generate_realistic_data(cell_type, cell_id):
    """Generate realistic cell data based on cell type"""
    specs = CELL_SPECS[cell_type]
    
    # Generate voltage within realistic range
    voltage_variance = 0.1
    voltage = specs["nominal_voltage"] + random.uniform(-voltage_variance, voltage_variance)
    voltage = max(specs["min_voltage"], min(specs["max_voltage"], voltage))
    
    # Generate current (0-5A typical range)
    current = round(random.uniform(0.1, 5.0), 2)
    
    # Generate temperature (20-50°C operational range)
    temp = round(random.uniform(20, 50), 1)
    
    # Calculate SOC based on voltage
    voltage_range = specs["max_voltage"] - specs["min_voltage"]
    soc = ((voltage - specs["min_voltage"]) / voltage_range) * 100
    soc = round(max(0, min(100, soc)), 1)
    
    # Calculate power and capacity
    power = round(voltage * current, 2)
    capacity = specs["capacity"]
    
    # Health status based on various factors
    health = round(random.uniform(85, 100), 1)
    
    # Status determination
    if voltage < specs["min_voltage"] * 1.1 or temp > 45 or health < 90:
        status = "Critical"
    elif voltage < specs["nominal_voltage"] * 0.9 or temp > 40 or health < 95:
        status = "Warning"
    else:
        status = "Good"
    
    return {
        "voltage": voltage,
        "current": current,
        "temperature": temp,
        "soc": soc,
        "power": power,
        "capacity": capacity,
        "health": health,
        "status": status,
        "type": cell_type
    }

def create_gauge_chart(value, title, max_value=100, color_ranges=None):
    """Create a professional gauge chart with dark theme"""
    if color_ranges is None:
        color_ranges = [
            {"range": [0, 30], "color": "#4d1a1a"},
            {"range": [30, 70], "color": "#4d3d1a"}, 
            {"range": [70, 100], "color": "#1a4d1a"}
        ]
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = value,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {
            'text': title, 
            'font': {'size': 18, 'color': '#ffffff', 'family': 'Inter'}
        },
        number = {
            'font': {
                'color': '#ffffff', 
                'size': 32, 
                'family': 'Inter',
                'weight': 'bold'
            },
            'valueformat': '.1f',
            'suffix': '%' if 'SOC' in title or 'Health' in title else ('°C' if 'Temperature' in title else '')
        },
        gauge = {
            'axis': {
                'range': [None, max_value], 
                'tickwidth': 1, 
                'tickcolor': "#ffffff", 
                'tickfont': {'color': '#ffffff', 'size': 12, 'family': 'Inter'}
            },
            'bar': {'color': "#ffffff", 'thickness': 0.25},
            'bgcolor': "#111111",
            'borderwidth': 2,
            'bordercolor': "#333333",
            'steps': color_ranges,
            'threshold': {
                'line': {'color': "#ffffff", 'width': 3},
                'thickness': 0.75,
                'value': max_value * 0.9
            }
        }
    ))
    
    fig.update_layout(
        paper_bgcolor="#000000",
        plot_bgcolor="#111111",
        font={'color': "#ffffff", 'family': "Inter"},
        height=320,
        margin=dict(l=30, r=30, t=80, b=30),
        showlegend=False
    )
    return fig

def create_status_indicator(status):
    """Create status indicator with colors"""
    if status == "Good":
        return f'<div class="alert-success">✅ {status}</div>'
    elif status == "Warning":
        return f'<div class="alert-warning">⚠️ {status}</div>'
    else:
        return f'<div class="alert-danger">🚨 {status}</div>'

# Main title
st.markdown('<h1 class="title-header">🔋 EV Battery Dashboard</h1>', unsafe_allow_html=True)

# Sidebar configuration
with st.sidebar:
    st.markdown('<div class="sidebar-header">⚙️ System Configuration</div>', unsafe_allow_html=True)
    
    # Cell configuration
    st.subheader("🔧 Cell Setup")
    num_cells = st.slider("Number of Cells", min_value=1, max_value=12, value=6, step=1)
    
    cell_types = []
    for i in range(num_cells):
        cell_type = st.selectbox(
            f"Cell {i+1} Type", 
            options=list(CELL_SPECS.keys()), 
            key=f"cell_type_{i}",
            index=i % len(CELL_SPECS)
        )
        cell_types.append(cell_type)
    
    st.divider()
    
    # Monitoring controls
    st.subheader("📡 Monitoring")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("▶️ Start" if not st.session_state.monitoring_active else "⏸️ Pause"):
            st.session_state.monitoring_active = not st.session_state.monitoring_active
    
    with col2:
        if st.button("🔄 Refresh"):
            st.session_state.last_update = datetime.now()
            st.rerun()
    
    # Auto-refresh toggle
    auto_refresh = st.toggle("🔄 Auto Refresh (5s)", value=False)
    
    st.divider()
    
    # System info
    st.subheader("ℹ️ System Info")
    st.info(f"**Cells:** {num_cells}")
    st.info(f"**Last Update:** {st.session_state.last_update.strftime('%H:%M:%S')}")
    st.success("**Status:** Online" if st.session_state.monitoring_active else "**Status:** Standby")

# Generate or update cell data
cells_data = {}
for i, cell_type in enumerate(cell_types):
    cell_id = f"cell_{i+1}"
    cells_data[cell_id] = generate_realistic_data(cell_type, cell_id)

# Main dashboard
tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "🔍 Detailed View", "📈 Analytics", "⚙️ Settings"])

with tab1:
    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    avg_voltage = np.mean([data['voltage'] for data in cells_data.values()])
    avg_temp = np.mean([data['temperature'] for data in cells_data.values()])
    avg_soc = np.mean([data['soc'] for data in cells_data.values()])
    total_power = sum([data['power'] for data in cells_data.values()])
    
    with col1:
        st.metric(
            label="⚡ Average Voltage", 
            value=f"{avg_voltage:.2f}V",
            delta=f"{random.uniform(-0.1, 0.1):.2f}V"
        )
    
    with col2:
        st.metric(
            label="🌡️ Average Temperature", 
            value=f"{avg_temp:.1f}°C",
            delta=f"{random.uniform(-2, 2):.1f}°C"
        )
    
    with col3:
        st.metric(
            label="🔋 Average SOC", 
            value=f"{avg_soc:.1f}%",
            delta=f"{random.uniform(-5, 5):.1f}%"
        )
    
    with col4:
        st.metric(
            label="⚡ Total Power", 
            value=f"{total_power:.1f}W",
            delta=f"{random.uniform(-10, 10):.1f}W"
        )
    
    # Gauge charts
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    gauge_col1, gauge_col2, gauge_col3 = st.columns(3)
    
    with gauge_col1:
        st.plotly_chart(
            create_gauge_chart(avg_soc, "State of Charge (%)", 100), 
            use_container_width=True
        )
    
    with gauge_col2:
        st.plotly_chart(
            create_gauge_chart(avg_temp, "Temperature (°C)", 60, [
                {"range": [0, 30], "color": "#4caf50"},
                {"range": [30, 45], "color": "#ff9800"},
                {"range": [45, 60], "color": "#f44336"}
            ]), 
            use_container_width=True
        )
    
    with gauge_col3:
        avg_health = np.mean([data['health'] for data in cells_data.values()])
        st.plotly_chart(
            create_gauge_chart(avg_health, "Battery Health (%)", 100), 
            use_container_width=True
        )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Status overview
    st.subheader("🚦 System Status")
    status_col1, status_col2, status_col3 = st.columns(3)
    
    good_cells = sum(1 for data in cells_data.values() if data['status'] == 'Good')
    warning_cells = sum(1 for data in cells_data.values() if data['status'] == 'Warning')
    critical_cells = sum(1 for data in cells_data.values() if data['status'] == 'Critical')
    
    with status_col1:
        st.markdown(f'<div class="alert-success">✅ Good Cells: {good_cells}</div>', unsafe_allow_html=True)
    
    with status_col2:
        st.markdown(f'<div class="alert-warning">⚠️ Warning Cells: {warning_cells}</div>', unsafe_allow_html=True)
    
    with status_col3:
        st.markdown(f'<div class="alert-danger">🚨 Critical Cells: {critical_cells}</div>', unsafe_allow_html=True)

with tab2:
    st.subheader("🔍 Detailed Cell Analysis")
    
    # Create detailed dataframe
    df_detailed = pd.DataFrame.from_dict(cells_data, orient='index')
    df_detailed.index.name = 'Cell ID'
    df_detailed = df_detailed.reset_index()
    
    # Display enhanced dataframe with black background and white text
    def highlight_status(row):
        if row['status'] == 'Good':
            return ['background-color: #1a4d1a; color: #ffffff; font-weight: bold'] * len(row)
        elif row['status'] == 'Warning':
            return ['background-color: #4d3d1a; color: #ffffff; font-weight: bold'] * len(row)
        elif row['status'] == 'Critical':
            return ['background-color: #4d1a1a; color: #ffffff; font-weight: bold'] * len(row)
        return ['background-color: #111111; color: #ffffff; font-weight: 500'] * len(row)
    
    # Create styled dataframe with dark theme
    styled_df = df_detailed.style.format({
        'voltage': '{:.2f}V',
        'current': '{:.2f}A', 
        'temperature': '{:.1f}°C',
        'soc': '{:.1f}%',
        'power': '{:.2f}W',
        'capacity': '{:.0f}Ah',
        'health': '{:.1f}%'
    }).apply(highlight_status, axis=1).set_properties(**{
        'text-align': 'center',
        'font-size': '14px',
        'padding': '8px',
        'border': '1px solid #333333',
        'background-color': '#111111',
        'color': '#ffffff'
    })
    
    st.dataframe(
        styled_df,
        use_container_width=True,
        height=400
    )
    
    # Individual cell selector
    st.subheader("🔧 Individual Cell Analysis")
    selected_cell = st.selectbox("Select Cell for Detailed View", list(cells_data.keys()))
    
    if selected_cell:
        cell_data = cells_data[selected_cell]
        
        # Cell detail cards
        detail_col1, detail_col2, detail_col3, detail_col4 = st.columns(4)
        
        with detail_col1:
            st.markdown(f"""
            <div class="metric-card">
                <h4>⚡ Electrical</h4>
                <p><strong>Voltage:</strong> {cell_data['voltage']:.2f}V</p>
                <p><strong>Current:</strong> {cell_data['current']:.2f}A</p>
                <p><strong>Power:</strong> {cell_data['power']:.2f}W</p>
            </div>
            """, unsafe_allow_html=True)
        
        with detail_col2:
            st.markdown(f"""
            <div class="metric-card">
                <h4>🌡️ Thermal</h4>
                <p><strong>Temperature:</strong> {cell_data['temperature']:.1f}°C</p>
                <p><strong>Status:</strong> {cell_data['status']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with detail_col3:
            st.markdown(f"""
            <div class="metric-card">
                <h4>🔋 Capacity</h4>
                <p><strong>SOC:</strong> {cell_data['soc']:.1f}%</p>
                <p><strong>Capacity:</strong> {cell_data['capacity']:.0f}Ah</p>
            </div>
            """, unsafe_allow_html=True)
        
        with detail_col4:
            st.markdown(f"""
            <div class="metric-card">
                <h4>🏥 Health</h4>
                <p><strong>Health:</strong> {cell_data['health']:.1f}%</p>
                <p><strong>Type:</strong> {cell_data['type']}</p>
            </div>
            """, unsafe_allow_html=True)

with tab3:
    st.subheader("📈 Battery Analytics")
    
    # Create comprehensive charts
    df_chart = pd.DataFrame.from_dict(cells_data, orient='index')
    df_chart.index.name = 'Cell'
    df_chart = df_chart.reset_index()
    
    # Chart selection
    chart_type = st.selectbox("Select Visualization Type", 
                             ["2D Charts", "3D Surface", "3D Bar Chart"])
    
    if chart_type == "2D Charts":
        # Voltage distribution with dark theme
        fig_voltage = px.bar(
            df_chart, 
            x='Cell', 
            y='voltage', 
            color='type',
            title="🔋 Cell Voltage Distribution",
            color_discrete_map={cell_type: CELL_SPECS[cell_type]['color'] for cell_type in CELL_SPECS}
        )
        fig_voltage.update_layout(
            plot_bgcolor='#111111',
            paper_bgcolor='#000000',
            font_color='#ffffff',
            title_font_color='#ffffff'
        )
        st.plotly_chart(fig_voltage, use_container_width=True)
        
        # Multi-metric comparison
        fig_multi = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Current Distribution', 'Temperature Profile', 'SOC Levels', 'Power Output'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # Current
        fig_multi.add_trace(
            go.Bar(x=df_chart['Cell'], y=df_chart['current'], name="Current", marker_color='#2196F3'),
            row=1, col=1
        )
        
        # Temperature
        fig_multi.add_trace(
            go.Scatter(x=df_chart['Cell'], y=df_chart['temperature'], mode='lines+markers', 
                      name="Temperature", line=dict(color='#FF5722', width=3)),
            row=1, col=2
        )
        
        # SOC
        fig_multi.add_trace(
            go.Bar(x=df_chart['Cell'], y=df_chart['soc'], name="SOC", marker_color='#4CAF50'),
            row=2, col=1
        )
        
        # Power
        fig_multi.add_trace(
            go.Bar(x=df_chart['Cell'], y=df_chart['power'], name="Power", marker_color='#FF9800'),
            row=2, col=2
        )
        
        fig_multi.update_layout(
            height=600, 
            showlegend=False,
            plot_bgcolor='#111111',
            paper_bgcolor='#000000',
            font_color='#ffffff',
            title_text="📊 Comprehensive Cell Metrics",
            title_font_color='#ffffff'
        )
        st.plotly_chart(fig_multi, use_container_width=True)
    
    elif chart_type == "3D Surface":
        # Create 3D surface plot
        st.subheader("🌊 3D Surface Analysis")
        
        # Create meshgrid for surface plot
        x = np.arange(len(df_chart))
        y = np.array([df_chart['voltage'], df_chart['current'], df_chart['temperature']])
        z_voltage = np.array([df_chart['voltage']] * 3)
        z_current = np.array([df_chart['current']] * 3)
        z_temp = np.array([df_chart['temperature']] * 3)
        
        fig_3d_surface = go.Figure()
        
        # Add voltage surface
        fig_3d_surface.add_trace(go.Surface(
            z=z_voltage,
            x=x,
            y=['Voltage', 'Current', 'Temperature'],
            colorscale='Viridis',
            name='Voltage Surface',
            opacity=0.8
        ))
        
        fig_3d_surface.update_layout(
            title='🔋 3D Battery Parameter Surface',
            scene=dict(
                xaxis_title='Cell Index',
                yaxis_title='Parameter Type',
                zaxis_title='Value',
                bgcolor='#111111',
                xaxis=dict(backgroundcolor='#111111', gridcolor='#333333', color='#ffffff'),
                yaxis=dict(backgroundcolor='#111111', gridcolor='#333333', color='#ffffff'),
                zaxis=dict(backgroundcolor='#111111', gridcolor='#333333', color='#ffffff')
            ),
            paper_bgcolor='#000000',
            plot_bgcolor='#111111',
            font_color='#ffffff',
            title_font_color='#ffffff',
            height=600
        )
        
        st.plotly_chart(fig_3d_surface, use_container_width=True)
    
    elif chart_type == "3D Bar Chart":
        # Create 3D bar chart
        st.subheader("📊 3D Bar Analysis")
        
        # Create 3D bar chart
        fig_3d_bar = go.Figure()
        
        # Add 3D bars for different parameters
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
        parameters = ['voltage', 'current', 'temperature', 'soc', 'power']
        param_names = ['Voltage', 'Current', 'Temperature', 'SOC', 'Power']
        
        for i, (param, name, color) in enumerate(zip(parameters, param_names, colors)):
            fig_3d_bar.add_trace(go.Scatter3d(
                x=df_chart.index,
                y=[i] * len(df_chart),
                z=df_chart[param],
                mode='markers',
                marker=dict(
                    size=10,
                    color=color,
                    symbol='square'
                ),
                name=name,
                text=df_chart['Cell'],
                textfont=dict(color='#ffffff')
            ))
            
            # Add bars (lines from base to value)
            for j, cell_idx in enumerate(df_chart.index):
                fig_3d_bar.add_trace(go.Scatter3d(
                    x=[cell_idx, cell_idx],
                    y=[i, i],
                    z=[0, df_chart[param].iloc[j]],
                    mode='lines',
                    line=dict(color=color, width=8),
                    showlegend=False
                ))
        
        fig_3d_bar.update_layout(
            title='📊 3D Multi-Parameter Bar Chart',
            scene=dict(
                xaxis_title='Cell Index',
                yaxis_title='Parameter Type',
                zaxis_title='Value',
                bgcolor='#111111',
                xaxis=dict(backgroundcolor='#111111', gridcolor='#333333', color='#ffffff'),
                yaxis=dict(
                    backgroundcolor='#111111', 
                    gridcolor='#333333', 
                    color='#ffffff',
                    tickmode='array',
                    tickvals=list(range(len(param_names))),
                    ticktext=param_names
                ),
                zaxis=dict(backgroundcolor='#111111', gridcolor='#333333', color='#ffffff')
            ),
            paper_bgcolor='#000000',
            plot_bgcolor='#111111',
            font_color='#ffffff',
            title_font_color='#ffffff',
            height=600,
            legend=dict(font=dict(color='#ffffff'))
        )
        
        st.plotly_chart(fig_3d_bar, use_container_width=True)
    
    # Correlation heatmap
    st.subheader("🔗 Parameter Correlations")
    numeric_cols = ['voltage', 'current', 'temperature', 'soc', 'power', 'health']
    corr_matrix = df_chart[numeric_cols].corr()
    
    fig_heatmap = px.imshow(
        corr_matrix,
        title="Parameter Correlation Matrix",
        color_continuous_scale='RdBu_r',
        aspect="auto"
    )
    fig_heatmap.update_layout(
        plot_bgcolor='#111111',
        paper_bgcolor='#000000',
        font_color='#ffffff',
        title_font_color='#ffffff'
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)
    
    # Advanced 3D Analysis Section
    st.subheader("🧊 Advanced 3D Analysis")
    
    col_3d1, col_3d2 = st.columns(2)
    
    with col_3d1:
        # 3D Mesh plot
        fig_mesh = go.Figure(data=[go.Mesh3d(
            x=df_chart['voltage'],
            y=df_chart['current'], 
            z=df_chart['temperature'],
            alphahull=5,
            opacity=0.4,
            color='lightblue'
        )])
        
        fig_mesh.update_layout(
            title='🔷 3D Mesh Visualization',
            scene=dict(
                bgcolor='#111111',
                xaxis=dict(backgroundcolor='#111111', gridcolor='#333333', color='#ffffff', title='Voltage'),
                yaxis=dict(backgroundcolor='#111111', gridcolor='#333333', color='#ffffff', title='Current'),
                zaxis=dict(backgroundcolor='#111111', gridcolor='#333333', color='#ffffff', title='Temperature')
            ),
            paper_bgcolor='#000000',
            font_color='#ffffff',
            title_font_color='#ffffff',
            height=400
        )
        
        st.plotly_chart(fig_mesh, use_container_width=True)
    
    with col_3d2:
        # 3D Cone plot for vector fields
        fig_cone = go.Figure(data=go.Cone(
            x=df_chart['voltage'],
            y=df_chart['current'],
            z=df_chart['temperature'],
            u=df_chart['soc']/100,
            v=df_chart['power']/100,
            w=df_chart['health']/100,
            colorscale='Viridis',
            sizemode="absolute",
            sizeref=0.5
        ))
        
        fig_cone.update_layout(
            title='🌪️ 3D Vector Field (SOC/Power/Health)',
            scene=dict(
                bgcolor='#111111',
                xaxis=dict(backgroundcolor='#111111', gridcolor='#333333', color='#ffffff', title='Voltage'),
                yaxis=dict(backgroundcolor='#111111', gridcolor='#333333', color='#ffffff', title='Current'),
                zaxis=dict(backgroundcolor='#111111', gridcolor='#333333', color='#ffffff', title='Temperature')
            ),
            paper_bgcolor='#000000',
            font_color='#ffffff',
            title_font_color='#ffffff',
            height=400
        )
        
        st.plotly_chart(fig_cone, use_container_width=True)

with tab4:
    st.subheader("⚙️ System Settings")
    
    settings_col1, settings_col2 = st.columns(2)
    
    with settings_col1:
        st.markdown("### 🔧 Monitoring Settings")
        
        # Thresholds
        voltage_threshold = st.slider("Low Voltage Threshold (V)", 2.0, 4.0, 3.0, 0.1)
        temp_threshold = st.slider("High Temperature Threshold (°C)", 30, 60, 45, 1)
        soc_threshold = st.slider("Low SOC Threshold (%)", 10, 50, 20, 5)
        
        # Alert settings
        st.markdown("### 🚨 Alert Settings")
        email_alerts = st.checkbox("Enable Email Alerts")
        sound_alerts = st.checkbox("Enable Sound Alerts")
        
    with settings_col2:
        st.markdown("### 📊 Data Export")
        
        # Export options
        export_format = st.selectbox("Export Format", ["CSV", "Excel", "JSON"])
        
        if st.button("📥 Export Current Data"):
            if export_format == "CSV":
                csv_data = df_detailed.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv_data,
                    file_name=f"battery_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        
        st.markdown("### 🔄 System Actions")
        
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("🔄 Reset System"):
                st.session_state.cells_data = {}
                st.success("System reset successfully!")
        
        with col_b:
            if st.button("🧹 Clear History"):
                st.success("History cleared!")

# Auto-refresh functionality
if auto_refresh and st.session_state.monitoring_active:
    time.sleep(5)
    st.rerun()

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; padding: 20px;'>"
    "🔋 EV Battery Dashboard By Krish Ujeniya | "
    f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
    "Status: ✅ Online"
    "</div>", 
    unsafe_allow_html=True
)
