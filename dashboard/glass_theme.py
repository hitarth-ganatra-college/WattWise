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
    padding-bottom: 3rem !important;
    padding-left: 2.5rem !important;
    padding-right: 2.5rem !important;
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

/* --- Tailwind Top Navbar Banner --- */
.tw-navbar {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 12px 24px;
    margin-bottom: 16px;
    box-shadow: 0 1px 3px 0 rgba(15, 23, 42, 0.05), 0 1px 2px -1px rgba(15, 23, 42, 0.05);
    display: flex;
    justify-content: space-between;
    align-items: center;
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

/* --- Section Card with Modern Grey Shadow Border --- */
.tw-section-card {
    background: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 12px;
    box-shadow: 0 4px 6px -1px rgba(15, 23, 42, 0.04), 0 2px 4px -2px rgba(15, 23, 42, 0.03);
    padding: 20px 24px;
    margin-bottom: 24px;
}

.tw-section-header {
    font-size: 1.15rem;
    font-weight: 700;
    color: #0f172a;
    letter-spacing: -0.01em;
    padding-bottom: 12px;
    margin-bottom: 16px;
    border-bottom: 1px solid #e2e8f0;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

/* --- Tailwind Section Divider Line --- */
.tw-divider {
    height: 1px;
    background-color: #cbd5e1;
    margin: 20px 0;
    border: none;
}

/* --- Linear Filter Toolbar --- */
.linear-filter-bar {
    background: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 12px;
    padding: 14px 20px;
    margin-bottom: 24px;
    box-shadow: 0 1px 4px rgba(15, 23, 42, 0.05);
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

/* --- Navigation Tabs (Top Executive Navbar) --- */
.stTabs [data-baseweb="tab-list"] {
    background-color: #ffffff !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 12px !important;
    padding: 6px 12px !important;
    gap: 6px !important;
    margin-bottom: 20px !important;
    box-shadow: 0 1px 3px 0 rgba(15, 23, 42, 0.05) !important;
    width: 100% !important;
    justify-content: flex-start !important;
}

button[data-baseweb="tab"] {
    background-color: transparent !important;
    border: 1px solid transparent !important;
    border-radius: 8px !important;
    padding: 10px 20px !important;
    transition: all 0.15s ease-in-out !important;
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
    background-color: #f0f9ff !important;
    border: 1px solid #bae6fd !important;
    box-shadow: 0 1px 2px rgba(2, 132, 199, 0.1) !important;
}

button[aria-selected="true"] p,
button[aria-selected="true"] span {
    color: #0284c7 !important;
    font-weight: 700 !important;
}

/* --- Metric Cards with Greyish Modern Border --- */
.glass-metric {
    background: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 12px;
    padding: 18px 22px;
    box-shadow: 0 1px 3px 0 rgba(15, 23, 42, 0.06);
    margin-bottom: 12px;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.glass-metric:hover {
    box-shadow: 0 4px 12px rgba(15, 23, 42, 0.08);
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

def render_wattwise_logo(height: int = 42, width: int = 240) -> str:
    """Returns ultra-clean HTML/CSS flexbox logo badge for WattWise Predictive Engine."""
    return (
        '<div style="display: flex; align-items: center; gap: 12px; font-family: \'Inter\', system-ui, sans-serif;">'
        '<div style="width: 38px; height: 38px; background: linear-gradient(135deg, #0284c7, #10b981); border-radius: 10px; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 12px rgba(2, 132, 199, 0.25); flex-shrink: 0;">'
        '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">'
        '<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon>'
        '</svg>'
        '</div>'
        '<div>'
        '<div style="font-size: 1.45rem; font-weight: 800; color: #0f172a; line-height: 1.1; letter-spacing: -0.02em;">Watt<span style="color: #0284c7;">Wise</span></div>'
        '<div style="font-size: 0.68rem; font-weight: 700; color: #64748b; letter-spacing: 0.08em; text-transform: uppercase;">Solar &amp; Wind Predictive Engine</div>'
        '</div>'
        '</div>'
    )

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
