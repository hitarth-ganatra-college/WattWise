"""
Light Theme Configuration for Streamlit Dashboard
==================================================
Overrides Streamlit dark mode defaults with explicit high-contrast light styles.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

GLASS_CSS = """
<style>
/* --- Import Inter Font --- */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
    color: #0f172a !important;
}

/* --- Force Light App Background & Padding --- */
.stApp {
    background-color: #f8fafc !important;
}

.main .block-container {
    padding-top: 1.25rem !important;
    padding-bottom: 2rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    max-width: 100% !important;
}

/* --- Sidebar: Clean collapse / hide option --- */
section[data-testid="stSidebar"] {
    background-color: #ffffff !important;
    border-right: 1px solid #cbd5e1 !important;
}

section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] div,
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #0f172a !important;
    font-weight: 600 !important;
}

/* --- Header & Brand Banner --- */
.wattwise-header-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 12px 24px;
    margin-bottom: 16px;
    box-shadow: 0 2px 10px rgba(15, 23, 42, 0.03);
}

.wattwise-status-pill {
    display: flex;
    align-items: center;
    gap: 8px;
    background: #f1f5f9;
    border: 1px solid #cbd5e1;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 0.82rem;
    font-weight: 600;
    color: #334155;
}

.status-dot-green {
    width: 8px;
    height: 8px;
    background-color: #10b981;
    border-radius: 50%;
    box-shadow: 0 0 8px #10b981;
}

/* --- Linear Filter Toolbar --- */
.linear-filter-bar {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 12px 20px;
    margin-bottom: 20px;
    box-shadow: 0 1px 4px rgba(15, 23, 42, 0.04);
}

/* --- Fix Selectboxes & Inputs --- */
div[data-baseweb="select"] > div {
    background-color: #ffffff !important;
    color: #0f172a !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 8px !important;
}

div[data-baseweb="select"] * {
    color: #0f172a !important;
}

/* --- Navigation Tabs (Unified Top Navbar) --- */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px !important;
    background-color: transparent !important;
    padding: 0 !important;
    border: none !important;
    margin-bottom: 0 !important;
    align-items: center !important;
}

button[data-baseweb="tab"] {
    background: transparent !important;
    border: 1px solid transparent !important;
    border-radius: 6px !important;
    padding: 8px 14px !important;
    transition: all 0.2s ease-in-out !important;
}

button[data-baseweb="tab"]:hover {
    background-color: #f1f5f9 !important;
}

button[data-baseweb="tab"] p,
button[data-baseweb="tab"] span {
    color: #475569 !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
}

button[aria-selected="true"] {
    background-color: #ffffff !important;
    border: 1px solid #cbd5e1 !important;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.08) !important;
}

button[aria-selected="true"] p,
button[aria-selected="true"] span {
    color: #0284c7 !important;
    font-weight: 700 !important;
}

/* --- Metric Box --- */
.glass-metric {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 16px 20px;
    box-shadow: 0 2px 8px rgba(15, 23, 42, 0.05);
    text-align: left;
    margin-bottom: 12px;
}

.glass-metric-label {
    font-size: 0.8rem;
    font-weight: 700;
    color: #475569;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.glass-metric-value {
    font-size: 1.85rem;
    font-weight: 800;
    color: #0f172a;
    margin: 4px 0;
}

.glass-metric-sub {
    font-size: 0.8rem;
    font-weight: 600;
    color: #0284c7;
}

/* --- Badges --- */
.badge-healthy {
    background-color: #dcfce7;
    color: #166534;
    border: 1px solid #86efac;
    padding: 4px 12px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 0.85rem;
    display: inline-block;
}

.badge-warning {
    background-color: #fef3c7;
    color: #92400e;
    border: 1px solid #fcd34d;
    padding: 4px 12px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 0.85rem;
    display: inline-block;
}

.badge-critical {
    background-color: #fee2e2;
    color: #991b1b;
    border: 1px solid #fca5a5;
    padding: 4px 12px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 0.85rem;
    display: inline-block;
}
</style>
"""

def inject_glass_theme():
    """Inject clean light CSS into Streamlit."""
    st.markdown(GLASS_CSS, unsafe_allow_html=True)

import base64

def render_wattwise_logo(height: int = 42, width: int = 240) -> str:
    """Returns Base64 encoded SVG vector logo img tag for WattWise Predictive Engine."""
    raw_svg = (
        f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" fill="none" xmlns="http://www.w3.org/2000/svg">'
        f'<defs>'
        f'<linearGradient id="logoGrad" x1="0%" y1="0%" x2="100%" y2="100%">'
        f'<stop offset="0%" stop-color="#0284c7" />'
        f'<stop offset="100%" stop-color="#10b981" />'
        f'</linearGradient>'
        f'</defs>'
        f'<rect x="2" y="2" width="38" height="38" rx="10" fill="url(#logoGrad)" />'
        f'<path d="M22 9L15 22H21L19 33L28 19H22L24 9Z" fill="#FFFFFF" stroke="#FFFFFF" stroke-width="1.2" stroke-linejoin="round"/>'
        f'<circle cx="31" cy="11" r="2.5" fill="#38bdf8"/>'
        f'<circle cx="11" cy="31" r="2" fill="#34d399"/>'
        f'<text x="50" y="25" font-family="Inter, system-ui, -apple-system, sans-serif" font-weight="800" font-size="22" fill="#0f172a" letter-spacing="-0.5">Watt<tspan fill="#0284c7">Wise</tspan></text>'
        f'<text x="50" y="37" font-family="Inter, system-ui, -apple-system, sans-serif" font-weight="600" font-size="8.5" fill="#64748b" letter-spacing="0.8">SOLAR &amp; WIND PREDICTIVE ENGINE</text>'
        f'</svg>'
    )
    b64_svg = base64.b64encode(raw_svg.encode("utf-8")).decode("utf-8")
    return f'<img src="data:image/svg+xml;base64,{b64_svg}" height="{height}" style="vertical-align: middle; display: inline-block;" alt="WattWise Logo"/>'

def render_glass_card(title: str, value: str, subtitle: str = "", icon: str = "", color: str = "#0f172a"):
    """Render a crisp HTML metric card."""
    icon_html = f'<span style="font-size: 1.2rem;">{icon}</span>' if icon else ''
    html = f"""<div class="glass-metric"><div style="display: flex; justify-content: space-between; align-items: center;"><span class="glass-metric-label">{title}</span>{icon_html}</div><div class="glass-metric-value" style="color: {color};">{value}</div><div class="glass-metric-sub">{subtitle}</div></div>"""
    st.markdown(html, unsafe_allow_html=True)

def apply_plotly_glass_layout(fig):
    """Apply crisp light theme to Plotly figures."""
    fig.update_layout(
        paper_bgcolor='rgba(255,255,255,0.0)',
        plot_bgcolor='#ffffff',
        font=dict(family='Inter, sans-serif', color='#0f172a', size=13),
        xaxis=dict(
            gridcolor='#e2e8f0',
            zerolinecolor='#cbd5e1',
            showline=True,
            linecolor='#94a3b8'
        ),
        yaxis=dict(
            gridcolor='#e2e8f0',
            zerolinecolor='#cbd5e1',
            showline=True,
            linecolor='#94a3b8'
        ),
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(
            bgcolor='rgba(255,255,255,0.9)',
            bordercolor='#cbd5e1',
            borderwidth=1
        )
    )
    return fig
