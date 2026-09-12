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

/* --- Force Light App Background --- */
.stApp {
    background-color: #f8fafc !important;
}

/* --- Sidebar: Crisp Dark Text on Light Surface --- */
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

/* --- Fix Tab Text --- */
button[data-baseweb="tab"] {
    background: transparent !important;
    border: none !important;
    padding: 8px 16px !important;
}

button[data-baseweb="tab"] p,
button[data-baseweb="tab"] span {
    color: #475569 !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
}

button[aria-selected="true"] p,
button[aria-selected="true"] span {
    color: #0284c7 !important;
    font-weight: 800 !important;
}

button[aria-selected="true"] {
    border-bottom: 3px solid #0284c7 !important;
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
