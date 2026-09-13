"""
WattWise Design System ΓÇö Modern Enterprise UI
================================================
Inspired by Fin (Intercom), Lovable, Mintlify navbars.
Clean single-row navbar, subtle section containers, refined typography.
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

/* --- Force Solid Background & Prevent Option-Change Whitening / Dimming --- */
html, body, .stApp, section[data-testid="stMain"],
div[data-testid="stAppViewContainer"], div[data-testid="stMainBlockContainer"] {
    background-color: #fafafa !important;
    background: #fafafa !important;
}

.stApp,
.stApp *,
[data-test-script-state="running"],
[data-test-script-state="running"] *,
[data-st-mode="running"],
[data-st-mode="running"] *,
div[data-testid="stAppViewContainer"],
div[data-testid="stAppViewContainer"] *,
section[data-testid="stMain"],
section[data-testid="stMain"] *,
div[data-testid="stMainBlockContainer"],
div[data-testid="stMainBlockContainer"] * {
    opacity: 1 !important;
    filter: none !important;
    backdrop-filter: none !important;
    transition: none !important;
}

/* --- Kill Streamlit default chrome UI, toolbars, menus, status badges, and rerun overlays --- */
#MainMenu, footer, header, 
[data-testid="stHeader"], 
[data-testid="stToolbar"], 
[data-testid="stDecoration"], 
[data-testid="stStatusWidget"],
div[class*="stStatusWidget"],
div[data-test-script-state="running"],
[data-testid="stSidebarNav"],
.viewerBadge_container__1S-5D,
button[title="View fullscreen"],
.stActionButton,
div[class*="stActionButton"] {
    display: none !important;
    visibility: hidden !important;
    height: 0 !important;
    width: 0 !important;
    opacity: 0 !important;
    pointer-events: none !important;
}

/* --- Eliminate iframe component background flashes --- */
iframe,
[data-testid="stCustomComponentV1"],
.element-container iframe {
    background-color: transparent !important;
    border: none !important;
}

/* Remove transforms/containment from Streamlit ancestors so position:fixed works */
.stApp, .main, .main > div, section[data-testid="stMain"],
section[data-testid="stMainBlockContainer"], .block-container,
[data-testid="stAppViewContainer"], [data-testid="stVerticalBlock"],
[data-testid="stElementContainer"], [data-testid="stTabs"], .stTabs {
    transform: none !important;
    will-change: auto !important;
    contain: none !important;
    isolation: auto !important;
    perspective: none !important;
    filter: none !important;
    backdrop-filter: none !important;
}

/* --- Main content area --- */
.main .block-container {
    padding-top: 52px !important;
    padding-bottom: 2rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    max-width: 100% !important;
}

/* --- Sidebar: Force collapse --- */
section[data-testid="stSidebar"] {
    display: none !important;
}

/* ================================================================
   NAVBAR ΓÇö Truly fixed to viewport top
   ================================================================ */
.ww-topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: #ffffff;
    border-bottom: 1px solid #e5e7eb;
    padding: 0 32px;
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    z-index: 999999;
    height: 48px;
    box-sizing: border-box;
}

.ww-topbar-logo {
    display: flex;
    align-items: center;
    gap: 10px;
    flex-shrink: 0;
}

.ww-topbar-logo-icon {
    width: 32px;
    height: 32px;
    background: linear-gradient(135deg, #0284c7, #10b981);
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}

.ww-topbar-brand {
    font-size: 1.15rem;
    font-weight: 800;
    color: #0f172a;
    letter-spacing: -0.02em;
    line-height: 1;
}

.ww-topbar-brand span {
    color: #0284c7;
}

.ww-topbar-right {
    display: flex;
    align-items: center;
    gap: 16px;
    flex-shrink: 0;
}

.ww-status-pill {
    display: flex;
    align-items: center;
    gap: 6px;
    background: #f0fdf4;
    border: 1px solid #bbf7d0;
    padding: 5px 12px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    color: #166534;
}

.ww-status-dot {
    width: 7px;
    height: 7px;
    background-color: #22c55e;
    border-radius: 50%;
    animation: ww-pulse 2s ease-in-out infinite;
}

@keyframes ww-pulse {
    0%, 100% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.4); }
    50% { box-shadow: 0 0 0 4px rgba(34, 197, 94, 0); }
}

/* ================================================================
   NAVIGATION TABS ΓÇö Positioned directly in the Top Navigation Bar beside Logo
   ================================================================ */
.stTabs {
    margin-top: 0 !important;
}

[data-testid="stTabList"],
[role="tablist"],
.stTabs [data-baseweb="tab-list"],
.stTabs > div:first-child {
    position: fixed !important;
    top: 0 !important;
    left: 175px !important;
    height: 48px !important;
    z-index: 9999999 !important;
    background-color: transparent !important;
    border: none !important;
    border-bottom: none !important;
    border-radius: 0 !important;
    padding: 0 !important;
    gap: 2px !important;
    margin: 0 !important;
    box-shadow: none !important;
    width: auto !important;
    display: flex !important;
    align-items: center !important;
    justify-content: flex-start !important;
}

/* Remove default tab highlight lines and borders */
[data-testid="stTabList"] + div,
.stTabs [data-baseweb="tab-highlight"],
.stTabs [data-baseweb="tab-border"] {
    display: none !important;
}

[data-testid="stTab"],
button[role="tab"],
.stTabs [data-baseweb="tab"],
.stTabs button {
    background-color: transparent !important;
    border: none !important;
    border-radius: 0 !important;
    padding: 0 14px !important;
    height: 48px !important;
    margin: 0 !important;
    transition: all 0.15s ease !important;
    border-bottom: 2px solid transparent !important;
    display: flex !important;
    align-items: center !important;
}

[data-testid="stTab"]:hover,
button[role="tab"]:hover,
.stTabs [data-baseweb="tab"]:hover,
.stTabs button:hover {
    background-color: transparent !important;
    border-bottom: 2px solid #0284c7 !important;
}

[data-testid="stTab"] p,
[data-testid="stTab"] span,
button[role="tab"] p,
button[role="tab"] span,
.stTabs button p,
.stTabs button span {
    color: #64748b !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
    letter-spacing: -0.01em !important;
}

[data-testid="stTab"][aria-selected="true"],
button[role="tab"][aria-selected="true"],
.stTabs button[aria-selected="true"] {
    background-color: transparent !important;
    border: none !important;
    border-bottom: 2px solid #0284c7 !important;
    box-shadow: none !important;
}

[data-testid="stTab"][aria-selected="true"] p,
[data-testid="stTab"][aria-selected="true"] span,
button[role="tab"][aria-selected="true"] p,
button[role="tab"][aria-selected="true"] span,
.stTabs button[aria-selected="true"] p,
.stTabs button[aria-selected="true"] span {
    color: #0284c7 !important;
    font-weight: 700 !important;
}

/* ================================================================
   FILTER BAR ΓÇö Compact inline row
   ================================================================ */
.ww-filter-bar {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 10px 0;
    margin-top: 12px;
    margin-bottom: 4px;
}

/* Selectbox refinements */
div[data-baseweb="select"] > div {
    background-color: #ffffff !important;
    color: #0f172a !important;
    border: 1px solid #e5e7eb !important;
    border-radius: 8px !important;
    font-size: 0.85rem !important;
    min-height: 38px !important;
}

div[data-baseweb="select"] > div:hover {
    border-color: #9ca3af !important;
}

div[data-baseweb="select"] * {
    color: #0f172a !important;
}

/* Selectbox labels */
.stSelectbox label, .stCheckbox label, .stSlider label {
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    color: #6b7280 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.04em !important;
}

/* ================================================================
   DIVIDER
   ================================================================ */
.ww-divider {
    height: 1px;
    background: #e5e7eb;
    border: none;
    margin: 16px 0;
}

/* ================================================================
   SECTION CONTAINERS ΓÇö Subtle bordered cards
   ================================================================ */
.ww-section {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 20px;
    box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.03);
}

.ww-section:hover {
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.06);
}

.ww-section-title {
    font-size: 0.78rem;
    font-weight: 700;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 16px;
}

/* ================================================================
   METRIC CARDS ΓÇö Clean, minimal
   ================================================================ */
.glass-metric {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 20px 22px;
    box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.03);
    margin-bottom: 12px;
    transition: box-shadow 0.15s ease;
}

.glass-metric:hover {
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.glass-metric-label {
    font-size: 0.72rem;
    font-weight: 700;
    color: #9ca3af;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}

.glass-metric-value {
    font-size: 1.75rem;
    font-weight: 800;
    color: #0f172a;
    margin: 6px 0 2px 0;
    line-height: 1.1;
}

.glass-metric-sub {
    font-size: 0.78rem;
    font-weight: 500;
    color: #0284c7;
}

/* ================================================================
   BADGES
   ================================================================ */
.badge-healthy {
    background-color: #f0fdf4;
    color: #166534;
    border: 1px solid #bbf7d0;
    padding: 3px 10px;
    border-radius: 20px;
    font-weight: 600;
    font-size: 0.78rem;
    display: inline-block;
}

.badge-warning {
    background-color: #fffbeb;
    color: #92400e;
    border: 1px solid #fde68a;
    padding: 3px 10px;
    border-radius: 20px;
    font-weight: 600;
    font-size: 0.78rem;
    display: inline-block;
}

.badge-critical {
    background-color: #fef2f2;
    color: #991b1b;
    border: 1px solid #fecaca;
    padding: 3px 10px;
    border-radius: 20px;
    font-weight: 600;
    font-size: 0.78rem;
    display: inline-block;
}

/* ================================================================
   STREAMLIT OVERRIDES ΓÇö Tables, expanders, etc.
   ================================================================ */
.stDataFrame, .stTable {
    border: 1px solid #e5e7eb !important;
    border-radius: 8px !important;
    overflow: hidden !important;
}

div[data-testid="stExpander"] {
    border: 1px solid #e5e7eb !important;
    border-radius: 10px !important;
    background: #ffffff !important;
}

div[data-testid="stExpander"] summary {
    font-weight: 600 !important;
    color: #374151 !important;
}

/* Button styling */
.stButton > button {
    border: 1px solid #e5e7eb !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    color: #374151 !important;
    background: #ffffff !important;
    padding: 8px 16px !important;
    transition: all 0.15s ease !important;
}

.stButton > button:hover {
    border-color: #9ca3af !important;
    background: #f9fafb !important;
}

/* Streamlit markdown H3/H4 refinements */
h3 { color: #111827 !important; font-weight: 700 !important; font-size: 1.1rem !important; }
h4 { color: #374151 !important; font-weight: 600 !important; font-size: 0.95rem !important; }

</style>
"""

def inject_glass_theme():
    """Inject clean light CSS into Streamlit."""
    st.markdown(GLASS_CSS, unsafe_allow_html=True)

def render_topbar() -> str:
    """Render the full top navigation bar HTML ΓÇö logo left, status right."""
    return (
        '<div class="ww-topbar">'
        # Left: Logo
        '<div class="ww-topbar-logo">'
        '<div class="ww-topbar-logo-icon">'
        '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">'
        '<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon>'
        '</svg>'
        '</div>'
        '<span class="ww-topbar-brand">Watt<span>Wise</span></span>'
        '</div>'
        # Right: Status pill
        '<div class="ww-topbar-right">'
        '<div class="ww-status-pill"><span class="ww-status-dot"></span>System Online</div>'
        '</div>'
        '</div>'
    )

def render_wattwise_logo(height: int = 42, width: int = 240) -> str:
    """Legacy compatibility ΓÇö returns inline logo HTML."""
    return (
        '<div style="display:flex;align-items:center;gap:10px;">'
        '<div style="width:32px;height:32px;background:linear-gradient(135deg,#0284c7,#10b981);border-radius:8px;display:flex;align-items:center;justify-content:center;">'
        '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">'
        '<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon>'
        '</svg>'
        '</div>'
        '<span style="font-size:1.15rem;font-weight:800;color:#0f172a;letter-spacing:-0.02em;">Watt<span style="color:#0284c7;">Wise</span></span>'
        '</div>'
    )

def render_glass_card(title: str, value: str, subtitle: str = "", icon: str = "", color: str = "#0f172a"):
    """Render a crisp HTML metric card."""
    icon_html = f'<span style="font-size: 1.1rem;">{icon}</span>' if icon else ''
    html = (
        f'<div class="glass-metric">'
        f'<div class="glass-metric-label">{title}</div>'
        f'<div class="glass-metric-value" style="color: {color};">{value}</div>'
        f'<div class="glass-metric-sub">{subtitle}</div>'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)

def apply_plotly_glass_layout(fig):
    """Apply crisp light theme to Plotly figures."""
    fig.update_layout(
        paper_bgcolor='rgba(255,255,255,0.0)',
        plot_bgcolor='#ffffff',
        font=dict(family='Inter, sans-serif', color='#0f172a', size=13),
        xaxis=dict(
            gridcolor='#f3f4f6',
            zerolinecolor='#e5e7eb',
            showline=True,
            linecolor='#d1d5db'
        ),
        yaxis=dict(
            gridcolor='#f3f4f6',
            zerolinecolor='#e5e7eb',
            showline=True,
            linecolor='#d1d5db'
        ),
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(
            bgcolor='rgba(255,255,255,0.95)',
            bordercolor='#e5e7eb',
            borderwidth=1
        )
    )
    return fig
