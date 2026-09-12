"""
WattWise Executive Dashboard — Modern Enterprise UI (v3.0)
===========================================================
Fin/Lovable/Mintlify-inspired navbar, clean sections, refined typography.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from pymongo import MongoClient
import pandas as pd
from datetime import datetime, timezone, timedelta
import sys
import os
import time
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from business_logic.health_index import AssetHealthCalculator
from business_logic.financial_engine import FinancialEngine
from dashboard.glass_theme import inject_glass_theme, render_glass_card, apply_plotly_glass_layout, render_wattwise_logo, render_topbar
import importlib
import dashboard.three_asset_viewer as tav
importlib.reload(tav)
render_3d_wind_turbine = tav.render_3d_wind_turbine
render_3d_solar_panel = tav.render_3d_solar_panel

# ─── Page Config ──────────────────────────────────────────────
st.set_page_config(
    layout="wide",
    page_title="WattWise | Predictive Maintenance Platform",
    page_icon="⚡",
    initial_sidebar_state="collapsed"
)

# Inject Light Design System
inject_glass_theme()

# ─── DB Connection ────────────────────────────────────────────
@st.cache_resource
def get_db():
    client = MongoClient(config.MONGO_URI)
    return client[config.DB_NAME]

# ─── Data Fetchers ────────────────────────────────────────────
@st.cache_data(ttl=3)
def fetch_all_assets():
    db = get_db()
    return list(db[config.COLLECTION_ASSETS].find({'status': {'$in': ['active', 'pending']}}))

@st.cache_data(ttl=3)
def fetch_latest_telemetry(asset_ids: tuple):
    db = get_db()
    results = []
    col = db[config.COLLECTION_TELEMETRY]
    for aid in asset_ids:
        doc = col.find_one({'asset_id': aid}, sort=[('timestamp', -1)])
        if doc:
            results.append(doc)
    return results

@st.cache_data(ttl=3)
def fetch_history(asset_id: str, limit: int = 150):
    db = get_db()
    docs = list(
        db[config.COLLECTION_TELEMETRY]
        .find({'asset_id': asset_id})
        .sort('timestamp', -1)
        .limit(limit)
    )
    docs.reverse()
    return docs

@st.cache_data(ttl=5)
def fetch_command_history(limit: int = 30):
    db = get_db()
    return list(
        db[config.COLLECTION_COMMANDS]
        .find()
        .sort('created_at', -1)
        .limit(limit)
    )

@st.cache_data(ttl=3)
def fetch_repair_history(limit: int = 50):
    db = get_db()
    col_name = getattr(config, 'COLLECTION_REPAIR_HISTORY', 'repair_history')
    return list(
        db[col_name]
        .find()
        .sort('repaired_at', -1)
        .limit(limit)
    )

@st.cache_data(ttl=3)
def fetch_alert_notifications(limit: int = 50):
    db = get_db()
    col_name = getattr(config, 'COLLECTION_ALERTS', 'alert_notifications')
    return list(
        db[col_name]
        .find()
        .sort('dispatched_at', -1)
        .limit(limit)
    )

def generate_work_order_pdf(asset_row):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#0284c7')
    )
    
    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#0f172a')
    )

    bold_style = ParagraphStyle(
        'BodyBold',
        parent=body_style,
        fontName='Helvetica-Bold'
    )
    
    elements = []
    aid = asset_row['asset_id']
    elements.append(Paragraph(f"WORK ORDER TICKET: #{aid}-WO", title_style))
    elements.append(Paragraph("Renewables Predictive Maintenance Platform | Technical Service Dispatch", body_style))
    elements.append(Spacer(1, 8))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#0284c7'), spaceAfter=12))
    
    lead_days = asset_row.get('lead_time_days', 30)
    daily_loss = asset_row.get('estimated_daily_revenue_loss', 0)
    repair_cost = asset_row.get('estimated_repair_cost', 5000)
    ahi = asset_row.get('ahi', 100)
    
    catastrophic_loss_avoided = (daily_loss * lead_days) + (config.EMERGENCY_REPLACEMENT_COST if ahi < 50 else config.PREVENTIVE_MAINTENANCE_COST * 2)
    net_savings = max(0.0, catastrophic_loss_avoided - repair_cost)
    
    data = [
        [Paragraph("<b>Field</b>", bold_style), Paragraph("<b>Value</b>", bold_style)],
        [Paragraph("<b>Equipment Asset ID</b>", body_style), Paragraph(str(aid), body_style)],
        [Paragraph("<b>Asset Type</b>", body_style), Paragraph(str(asset_row.get('asset_type', '')).upper().replace('_', ' '), body_style)],
        [Paragraph("<b>OEM Manufacturer</b>", body_style), Paragraph(str(asset_row.get('oem', '')), body_style)],
        [Paragraph("<b>Climate Region</b>", body_style), Paragraph(str(asset_row.get('region', '')), body_style)],
        [Paragraph("<b>Health Index (AHI)</b>", body_style), Paragraph(f"{ahi:.1f} / 100 ({asset_row.get('health_status', '')})", body_style)],
        [Paragraph("<b>Primary Fault Detected</b>", body_style), Paragraph(f"<font color='#b91c1c'><b>{asset_row.get('top_issue', '')}</b></font>", body_style)],
        [Paragraph("<b>Parts Lead Time</b>", body_style), Paragraph(f"{lead_days} Days", body_style)],
        [Paragraph("<b>Est. Servicing Cost</b>", body_style), Paragraph(f"${repair_cost:,.2f}", body_style)],
        [Paragraph("<b>Avoided Catastrophic Loss</b>", body_style), Paragraph(f"${catastrophic_loss_avoided:,.2f}", body_style)],
        [Paragraph("<b>NET MONEY SAVED (ROI)</b>", bold_style), Paragraph(f"<font color='#166534'><b>${net_savings:,.2f}</b></font>", bold_style)],
        [Paragraph("<b>Urgency Level</b>", body_style), Paragraph(str(asset_row.get('urgency', '')), body_style)],
    ]
    
    t = Table(data, colWidths=[180, 340])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f172a')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('TOPPADDING', (0,0), (-1,0), 6),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#f8fafc')),
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('BACKGROUND', (0,10), (1,10), colors.HexColor('#dcfce7')),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 12))
    
    elements.append(Paragraph("<b>Recommended Technical Dispatch Action:</b>", bold_style))
    elements.append(Paragraph(f"{asset_row.get('recommended_action', '')}", body_style))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(f"<b>Ticket Generated At:</b> {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}", body_style))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()

REGIONS = list(config.REGIONAL_MODIFIERS.keys())

# ─── Session state defaults ──────────────────────────────────
if "toolbar_asset_type" not in st.session_state:
    st.session_state["toolbar_asset_type"] = "All"
if "toolbar_region" not in st.session_state:
    st.session_state["toolbar_region"] = "All"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TOP NAVBAR — Logo left | Status right (single clean bar)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.markdown(render_topbar(), unsafe_allow_html=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# NAVIGATION TABS — Styled as clean text links via CSS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Fleet Overview",
    "Asset Deep Dive",
    "Maintenance Queue",
    "Financial Impact",
    "Asset Manager",
    "Command Center"
])

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FILTER TOOLBAR — Compact inline row (rendered outside tabs,
# visible on every page)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# ─── Helpers ──────────────────────────────────────────────────
hc = AssetHealthCalculator()
fe = FinancialEngine()

def safe_ahi(scores):
    if not scores or not isinstance(scores, dict):
        return 100.0
    return hc.calculate_ahi(scores)

def process_assets(assets, telemetry_docs):
    processed = []
    for t in telemetry_docs:
        aid = t['asset_id']
        atype = t.get('asset_type', 'unknown')
        region = t.get('region', 'Unknown')
        scores = t.get('anomaly_scores', {})
        ahi = safe_ahi(scores)
        status_id = t.get('status_type_id', 0)

        # Region metadata with deterministic GPS jitter per asset ID
        reg_info = config.REGIONAL_MODIFIERS.get(region, {})
        base_lat = reg_info.get('lat', 25.0)
        base_lon = reg_info.get('lon', 70.0)

        # Hash asset_id to create deterministic lat/lon jitter offset
        h = abs(hash(aid))
        lat_jitter = ((h % 100) - 50) * 0.04  # ~ +/- 2 degrees offset
        lon_jitter = (((h // 100) % 100) - 50) * 0.04
        lat = round(base_lat + lat_jitter, 4)
        lon = round(base_lon + lon_jitter, 4)

        oem = reg_info.get('oem_wind' if atype == 'wind_turbine' else 'oem_solar', 'Generic Manufacturer')

        cap = config.WIND_TURBINE_CAPACITY_KW if atype == 'wind_turbine' else config.SOLAR_PANEL_CAPACITY_KW
        actual = t.get('active_power') or t.get('power_output_kw') or 0
        expected = t.get('expected_power_kw')

        # Apply Curtailment Guard to power loss calculation
        loss_kw = fe.estimate_hourly_power_loss(cap, actual if actual else 0, expected, status_type_id=status_id, ahi=ahi)
        rev_loss = fe.estimate_revenue_loss(loss_kw)

        rec = fe.generate_recommendation(aid, atype, ahi, scores if isinstance(scores, dict) else {}, rev_loss)
        rec['region'] = region
        rec['lat'] = lat
        rec['lon'] = lon
        rec['oem'] = oem
        
        # Calculate RUL hours & degradation velocity
        history_data = fetch_history(aid, limit=30)
        rul_info = hc.estimate_rul_hours(ahi, history_data)
        rec['rul_hours'] = rul_info['rul_hours']
        rec['velocity'] = rul_info['velocity']
        
        if rul_info['is_collapsing'] and ahi < 50:
            rec['urgency'] = 'Immediate'
            rec['recommended_action'] = f"RAPID COLLAPSE ALERT: {rec['recommended_action']}"

        # HTML Badge without emojis
        if rec['health_status'] == 'Healthy':
            badge = '<span class="badge-healthy">Healthy</span>'
        elif rec['health_status'] in ['Warning', 'Scheduled']:
            badge = '<span class="badge-warning">Warning</span>'
        else:
            badge = '<span class="badge-critical">Critical</span>'
            
        rec['status_badge'] = badge
        simple_status = 'Healthy' if rec['health_status'] == 'Healthy' else 'Warning' if rec['health_status'] in ['Warning', 'Scheduled'] else 'Critical'
        rec['asset_type_label'] = 'Wind Turbine' if atype == 'wind_turbine' else 'Solar Panel'
        rec['asset_health_category'] = f"{rec['asset_type_label']} - {simple_status}"
        processed.append(rec)

    return processed

# ─── Data Filtering ───────────────────────────────────────────
# Read filter values from session state (set by selectboxes rendered below)
asset_type_filter = st.session_state.get("toolbar_asset_type", "All")
region_filter = st.session_state.get("toolbar_region", "All")

all_assets = fetch_all_assets()

filtered_assets = all_assets
if asset_type_filter == "Wind Turbine":
    filtered_assets = [a for a in filtered_assets if a.get('asset_type') == 'wind_turbine']
elif asset_type_filter == "Solar Panel":
    filtered_assets = [a for a in filtered_assets if a.get('asset_type') == 'solar_panel']
if region_filter != "All":
    filtered_assets = [a for a in filtered_assets if a.get('region') == region_filter]

asset_ids = tuple(a['asset_id'] for a in filtered_assets)
latest_tel = fetch_latest_telemetry(asset_ids) if asset_ids else []

processed = process_assets(filtered_assets, latest_tel) if latest_tel else []
df_assets = pd.DataFrame(processed) if processed else pd.DataFrame()
if not df_assets.empty:
    df_assets = df_assets.sort_values(by='priority_score', ascending=False)

# ── Tab 1: Fleet Overview ────────────────────────────────────
with tab1:
    # Compact filter bar at the top of the tab
    ft1, ft2, ft3, ft4 = st.columns([2, 2, 3, 3])
    with ft1:
        asset_type_filter = st.selectbox("Asset Type", ["All", "Wind Turbine", "Solar Panel"], key="toolbar_asset_type")
    with ft2:
        region_filter = st.selectbox("Region", ["All"] + REGIONS, key="toolbar_region")
    with ft3:
        auto_refresh = st.checkbox("Auto-refresh", value=True, key="toolbar_auto_refresh")
    with ft4:
        st.markdown(
            '<div style="font-size:0.75rem;color:#9ca3af;padding-top:6px;">'
            '<b>Telemetry:</b> Live SCADA Stream &middot; 2s interval'
            '</div>',
            unsafe_allow_html=True
        )

    st.markdown("<hr class='ww-divider'/>", unsafe_allow_html=True)

    if df_assets.empty:
        st.markdown("""
        <div class="glass-metric" style="text-align:center; padding: 40px;">
            <h3 style="color:#0f172a;">No Active Telemetry Streams Found</h3>
            <p style="color:#64748b;">Go to <b>Asset Manager</b> to register an asset or start the simulator with <code>python simulator/run_simulation.py --seed-defaults</code>.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        total = len(df_assets)
        at_risk = len(df_assets[df_assets['ahi'] < 50])
        total_loss = df_assets['estimated_daily_revenue_loss'].sum()
        healthy_pct = ((total - at_risk) / total) * 100.0

        # ── KPI Summary Cards ──
        st.markdown('<div class="ww-section-title">Key Metrics</div>', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            render_glass_card("Total Managed Assets", str(total), "Solar & Wind Units", "", "#0f172a")
        with c2:
            render_glass_card("Fleet Health Score", f"{healthy_pct:.0f}%", "Units > 50 AHI", "", "#10b981")
        with c3:
            render_glass_card("At-Risk Assets", str(at_risk), "Requires Inspection", "", "#f59e0b" if at_risk > 0 else "#10b981")
        with c4:
            render_glass_card("Est. Daily Rev Loss", f"${total_loss:,.2f}", "Cost of Inaction", "", "#ef4444" if total_loss > 100 else "#0284c7")

        st.markdown("<hr class='ww-divider'/>", unsafe_allow_html=True)

        # ── Satellite Map Section ──
        st.markdown('<div class="ww-section-title">Fleet Satellite Map & 3D Inspection</div>', unsafe_allow_html=True)
        
        map_col1, map_col2 = st.columns([3, 1])
        with map_col2:
            st.markdown("<b style='color:#0f172a; font-size:1.05rem;'>Map Controls & Legend</b>", unsafe_allow_html=True)
            focus_asset = st.selectbox(
                "FOCUS MAP & 3D INSPECTOR",
                ["All Assets"] + df_assets['asset_id'].tolist(),
                key="map_focus_asset"
            )
            proj_choice = st.radio(
                "Map Mode",
                ["Google Earth Satellite View", "3D Globe", "Flat Vector Map"],
                index=0,
                key="map_proj_choice"
            )
            st.markdown("""
            <div style='margin-top:12px; font-size:0.82rem; color:#475569; line-height:1.5; background: #f8fafc; padding: 14px; border-radius: 10px; border: 1px solid #e2e8f0;'>
                <b>Asset Marker Symbols:</b><br/>
                &#9650; <b>Triangles</b> = Wind Turbines<br/>
                &#9632; <b>Squares / Dots</b> = Solar Panels<br/><br/>
                <b>Health Status Colors:</b><br/>
                <span style='color:#10b981; font-weight:bold;'>&#9632; Green</span> = Healthy (&ge;80 AHI)<br/>
                <span style='color:#f59e0b; font-weight:bold;'>&#9632; Yellow</span> = Warning (50-79 AHI)<br/>
                <span style='color:#ef4444; font-weight:bold;'>&#9632; Red</span> = Critical / Failure (&lt;50 AHI)
            </div>
            """, unsafe_allow_html=True)

        with map_col1:
            color_map = {
                'Wind Turbine - Healthy': '#10b981',
                'Wind Turbine - Warning': '#f59e0b',
                'Wind Turbine - Critical': '#ef4444',
                'Wind Turbine - Failure Imminent': '#991b1b',
                'Solar Panel - Healthy': '#06b6d4',
                'Solar Panel - Warning': '#f97316',
                'Solar Panel - Critical': '#dc2626',
                'Solar Panel - Failure Imminent': '#7f1d1d'
            }

            if proj_choice == "Google Earth Satellite View":
                center_dict = dict(lat=20.0, lon=0.0)
                zoom_val = 1.2

                if focus_asset != "All Assets":
                    asset_row = df_assets[df_assets['asset_id'] == focus_asset].iloc[0]
                    center_dict = dict(lat=float(asset_row['lat']), lon=float(asset_row['lon']))
                    zoom_val = 13.5  # Satellite close-up focus!

                scatter_map_func = getattr(px, 'scatter_map', None) or getattr(px, 'scatter_mapbox', None)
                fig_map = scatter_map_func(
                    df_assets,
                    lat='lat',
                    lon='lon',
                    hover_name='asset_id',
                    hover_data={
                        'asset_type_label': True,
                        'health_status': True,
                        'ahi': ':.1f',
                        'region': True,
                        'oem': True,
                        'lat': ':.4f',
                        'lon': ':.4f'
                    },
                    color='asset_health_category',
                    color_discrete_map=color_map,
                    size_max=18,
                    zoom=zoom_val,
                    center=center_dict,
                    title="Google Earth Satellite View (Divided by Asset Type & Health)"
                )

                style_key = "map_style" if hasattr(px, 'scatter_map') else "mapbox_style"
                layers_key = "map_layers" if hasattr(px, 'scatter_map') else "mapbox_layers"
                
                layout_kwargs = {
                    style_key: "white-bg",
                    layers_key: [
                        {
                            "below": 'traces',
                            "sourcetype": "raster",
                            "source": ["https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"]
                        }
                    ],
                    "margin": dict(l=0, r=0, t=30, b=0)
                }
                fig_map.update_layout(**layout_kwargs)
                fig_map.update_traces(marker=dict(size=14, opacity=0.9))
                st.plotly_chart(fig_map, use_container_width=True)

            else:
                proj = "orthographic" if proj_choice == "3D Globe" else "natural earth"
                fig_map = px.scatter_geo(
                    df_assets,
                    lat='lat',
                    lon='lon',
                    hover_name='asset_id',
                    hover_data={
                        'asset_type_label': True,
                        'health_status': True,
                        'ahi': ':.1f',
                        'region': True,
                        'oem': True,
                        'lat': ':.4f',
                        'lon': ':.4f'
                    },
                    color='asset_health_category',
                    symbol='asset_type_label',
                    symbol_map={'Wind Turbine': 'triangle-up', 'Solar Panel': 'square'},
                    color_discrete_map=color_map,
                    size_max=18,
                    projection=proj,
                    title="3D Globe Fleet View (Triangles = Wind, Squares = Solar)"
                )
                
                geo_config = dict(
                    projection_type=proj,
                    showcountries=True,
                    showcoastlines=True,
                    showland=True,
                    landcolor="#e2e8f0",
                    oceancolor="#f0f9ff",
                    lakecolor="#f0f9ff",
                    bgcolor="rgba(0,0,0,0)"
                )
                
                if focus_asset != "All Assets":
                    asset_row = df_assets[df_assets['asset_id'] == focus_asset].iloc[0]
                    geo_config['center'] = dict(lat=float(asset_row['lat']), lon=float(asset_row['lon']))
                    geo_config['projection_scale'] = 3.5 if proj == "orthographic" else 4.0
                
                fig_map.update_geos(**geo_config)
                fig_map.update_traces(marker=dict(size=14, line=dict(width=1.5, color='white')))
                apply_plotly_glass_layout(fig_map)
                st.plotly_chart(fig_map, use_container_width=True)

        # Render 3D WebGL Asset Model Inspector when an asset is focused
        if focus_asset != "All Assets":
            st.divider()
            asset_row = df_assets[df_assets['asset_id'] == focus_asset].iloc[0]
            atype = asset_row.get('asset_type', 'unknown')
            ahi_val = asset_row.get('ahi', 100.0)
            status_val = asset_row.get('health_status', 'Healthy')

            st.markdown(f"<h4 style='color:#0f172a;'>Interactive 3D Asset Model Inspector: {focus_asset}</h4>", unsafe_allow_html=True)
            st.caption("Rotatable 3D WebGL asset visualization driven by real-time SCADA telemetry.")

            latest_tel_list = fetch_history(focus_asset, limit=1)
            latest_doc = latest_tel_list[0] if latest_tel_list else {}

            if atype == 'wind_turbine':
                rpm_val = latest_doc.get('generator_rpm') or 1500.0
                gb_temp = latest_doc.get('gearbox_bearing_temp') or 60.0
                render_3d_wind_turbine(rpm=rpm_val, gearbox_temp=gb_temp, health_status=status_val, height=460)
            else:
                soiling_val = latest_doc.get('soiling_factor') or 1.0
                irradiance_val = latest_doc.get('solar_irradiance') or 850.0
                panel_temp_val = latest_doc.get('panel_temp') or 45.0
                render_3d_solar_panel(soiling_factor=soiling_val, irradiance=irradiance_val, panel_temp=panel_temp_val, health_status=status_val, height=400)

        st.markdown("<h4 style='color:#0f172a; margin-top:20px;'>Fleet Status Overview</h4>", unsafe_allow_html=True)
        
        display_df = df_assets[['asset_id', 'asset_type', 'region', 'oem', 'ahi', 'health_status', 'priority_score']].copy()
        display_df.columns = ['Asset ID', 'Asset Type', 'Region', 'OEM Manufacturer', 'Health (AHI)', 'Status', 'Risk Priority (RPN)']
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)

# ── Tab 2: Asset Deep Dive ───────────────────────────────────
with tab2:
    if df_assets.empty:
        st.info("No assets to inspect.")
    else:
        selected = st.selectbox("Select Asset for Deep Diagnostics", df_assets['asset_id'].tolist())
        if selected:
            history = fetch_history(selected)
            if history:
                df_h = pd.DataFrame(history)
                atype = history[0].get('asset_type', 'unknown')

                df_h['ahi'] = [safe_ahi(d.get('anomaly_scores', {})) for d in history]
                latest_ahi = df_h['ahi'].iloc[-1]
                status = hc.classify_health(latest_ahi)

                c1, c2 = st.columns([1, 3])
                with c1:
                    render_glass_card("Asset Health Index", f"{latest_ahi:.1f} / 100", f"Status: {status}", "", "#0284c7")
                with c2:
                    fig_ahi = px.area(df_h, x='timestamp', y='ahi', title='Asset Health Index (AHI) Trend', range_y=[0, 105])
                    fig_ahi.add_hline(y=50, line_dash="dash", line_color="#f59e0b", annotation_text="Warning (50 AHI)")
                    fig_ahi.add_hline(y=20, line_dash="dash", line_color="#ef4444", annotation_text="Critical (20 AHI)")
                    
                    # Fetch repair history to mark repair events on chart
                    db = get_db()
                    col_repair = getattr(config, 'COLLECTION_REPAIR_HISTORY', 'repair_history')
                    repairs = list(db[col_repair].find({'asset_id': selected}))
                    for rep in repairs:
                        rep_time = rep.get('repaired_at')
                        if rep_time:
                            fig_ahi.add_vline(x=rep_time, line_dash="dot", line_color="#10b981", annotation_text="Technician Repair")

                    apply_plotly_glass_layout(fig_ahi)
                    st.plotly_chart(fig_ahi, use_container_width=True)

                st.markdown("<h4 style='color:#0f172a; margin-top:16px;'>Live Sensor Telemetry and Residual Diagnostics</h4>", unsafe_allow_html=True)
                
                if atype == 'wind_turbine':
                    cols_to_plot = ['gearbox_bearing_temp', 'gearbox_oil_temp', 'generator_bearing_de_temp']
                    avail = [c for c in cols_to_plot if c in df_h.columns]
                    if avail:
                        fig1 = px.line(df_h, x='timestamp', y=avail, title='Component Temperatures (deg C) [EMA Smoothed]')
                        apply_plotly_glass_layout(fig1)
                        st.plotly_chart(fig1, use_container_width=True)

                    # Thermal Delta (T_bearing - T_oil)
                    if 'gearbox_bearing_temp' in df_h.columns and 'gearbox_oil_temp' in df_h.columns:
                        df_h['delta_t_gearbox'] = df_h['gearbox_bearing_temp'] - df_h['gearbox_oil_temp']
                        fig_dt = px.line(df_h, x='timestamp', y='delta_t_gearbox', title='Bearing-to-Oil Temperature Delta (dT = T_bearing - T_oil deg C)')
                        fig_dt.add_hline(y=20, line_dash="dash", line_color="#ef4444", annotation_text="Friction Threshold (20 deg C dT)")
                        apply_plotly_glass_layout(fig_dt)
                        st.plotly_chart(fig_dt, use_container_width=True)

                    # 3-Phase Electrical Imbalance
                    if 'current_phase_1' in df_h.columns and 'current_phase_2' in df_h.columns and 'current_phase_3' in df_h.columns:
                        df_h['i_avg'] = (df_h['current_phase_1'] + df_h['current_phase_2'] + df_h['current_phase_3']) / 3.0
                        df_h['imbalance_pct'] = df_h.apply(
                            lambda r: (max(abs(r['current_phase_1'] - r['i_avg']), abs(r['current_phase_2'] - r['i_avg']), abs(r['current_phase_3'] - r['i_avg'])) / r['i_avg'] * 100.0) if r['i_avg'] > 5 else 0.0, axis=1
                        )
                        fig_elec = px.line(df_h, x='timestamp', y='imbalance_pct', title='3-Phase Current Imbalance (dI %)')
                        fig_elec.add_hline(y=5.0, line_dash="dash", line_color="#ef4444", annotation_text="Imbalance Alarm Threshold (5%)")
                        apply_plotly_glass_layout(fig_elec)
                        st.plotly_chart(fig_elec, use_container_width=True)

                    vib_cols = ['generator_rpm_std', 'rotor_rpm_std']
                    avail_v = [c for c in vib_cols if c in df_h.columns]
                    if avail_v:
                        fig2 = px.line(df_h, x='timestamp', y=avail_v, title='Vibration Proxies (RPM Std Deviation)')
                        apply_plotly_glass_layout(fig2)
                        st.plotly_chart(fig2, use_container_width=True)

                    if 'active_power' in df_h.columns:
                        fig3 = px.line(df_h, x='timestamp', y='active_power', title='Active Power Generation (kW)')
                        apply_plotly_glass_layout(fig3)
                        st.plotly_chart(fig3, use_container_width=True)

                elif atype == 'solar_panel':
                    solar_cols = ['power_output_kw', 'expected_power_kw']
                    avail_s = [c for c in solar_cols if c in df_h.columns]
                    if avail_s:
                        fig1 = px.line(df_h, x='timestamp', y=avail_s, title='Power: Actual vs. ML Expected Baseline (kW)')
                        apply_plotly_glass_layout(fig1)
                        st.plotly_chart(fig1, use_container_width=True)

                    # IEC 61724 Solar Performance Ratio (PR)
                    if 'power_output_kw' in df_h.columns and 'solar_irradiance' in df_h.columns:
                        cap = history[0].get('capacity_kw', 10)
                        df_h['pr'] = df_h.apply(
                            lambda r: (r['power_output_kw'] / ((r['solar_irradiance'] / 1000.0) * cap)) if r.get('solar_irradiance', 0) > 200 else 0.85, axis=1
                        )
                        fig_pr = px.line(df_h, x='timestamp', y='pr', title='IEC 61724 Solar Performance Ratio (PR)', range_y=[0.0, 1.05])
                        fig_pr.add_hline(y=0.80, line_dash="dash", line_color="#10b981", annotation_text="Target PR (0.80)")
                        fig_pr.add_hline(y=0.70, line_dash="dash", line_color="#ef4444", annotation_text="Soiling / Fault Threshold (0.70 PR)")
                        apply_plotly_glass_layout(fig_pr)
                        st.plotly_chart(fig_pr, use_container_width=True)

                    if 'soiling_factor' in df_h.columns:
                        fig2 = px.area(df_h, x='timestamp', y='soiling_factor', title='Panel Soiling Ratio (1.0 = Clean)', range_y=[0.5, 1.05])
                        apply_plotly_glass_layout(fig2)
                        st.plotly_chart(fig2, use_container_width=True)

                    other_s = ['solar_irradiance', 'panel_temp', 'ambient_temp']
                    avail_o = [c for c in other_s if c in df_h.columns]
                    if avail_o:
                        fig3 = px.line(df_h, x='timestamp', y=avail_o, title='Solar Irradiance and Temperatures')
                        apply_plotly_glass_layout(fig3)
                        st.plotly_chart(fig3, use_container_width=True)

# ── Tab 3: Maintenance Queue ─────────────────────────────────
with tab3:
    if df_assets.empty:
        st.info("No maintenance items.")
    else:
        st.markdown("<h3 style='color:#0f172a;'>Actionable Maintenance Queue</h3>", unsafe_allow_html=True)
        st.caption("Assets ordered by Risk Priority Number (RPN = Failure Probability x Daily Financial Loss x Supply Chain Lead Time Factor).")

        display_cols = ['asset_id', 'asset_type', 'oem', 'region', 'health_status', 'top_issue',
                        'recommended_action', 'rul_hours', 'lead_time_days', 'velocity', 'estimated_daily_revenue_loss', 'estimated_repair_cost', 'urgency']
        avail_m = [c for c in display_cols if c in df_assets.columns]
        
        m_df = df_assets[avail_m].copy()
        m_df.columns = ['Asset ID', 'Type', 'OEM Hardware', 'Region', 'Health Status', 'Primary Fault', 
                        'Recommended Action', 'RUL (Hours)', 'Parts Lead Time (Days)', 'Degradation Velocity', 'Daily Loss ($)', 'Est Repair Cost ($)', 'Urgency']
        
        st.dataframe(m_df, use_container_width=True, hide_index=True)

        st.divider()
        c_wo, c_rep = st.columns(2)
        
        with c_wo:
            st.markdown("### Export Technician Work Order")
            degraded_wo_assets = df_assets[df_assets['ahi'] < 95]['asset_id'].tolist()
            if not degraded_wo_assets:
                st.info("No active work orders required. All fleet assets are healthy!")
            else:
                selected_wo_asset = st.selectbox("Select Asset for Work Order Ticket", degraded_wo_assets, key="wo_select")
                if selected_wo_asset:
                    asset_row = df_assets[df_assets['asset_id'] == selected_wo_asset].iloc[0]
                    
                    # Calculate financial savings figure
                    lead_days = asset_row.get('lead_time_days', 30)
                    daily_loss = asset_row.get('estimated_daily_revenue_loss', 0)
                    repair_cost = asset_row.get('estimated_repair_cost', 5000)
                    ahi = asset_row.get('ahi', 100)
                    
                    catastrophic_loss_avoided = (daily_loss * lead_days) + (config.EMERGENCY_REPLACEMENT_COST if ahi < 50 else config.PREVENTIVE_MAINTENANCE_COST * 2)
                    net_savings = max(0.0, catastrophic_loss_avoided - repair_cost)

                    with st.expander(f"View Ticket: {selected_wo_asset}", expanded=True):
                        ticket_html = f"""
                        <div style="background:#ffffff; border:2px solid #0f172a; padding:20px; border-radius:12px; color:#0f172a;">
                            <h3 style="margin:0 0 10px 0; color:#0284c7;">WORK ORDER #{selected_wo_asset}-WO</h3>
                            <p style="margin:4px 0;"><b>Equipment:</b> {asset_row['asset_id']} ({asset_row['oem']})</p>
                            <p style="margin:4px 0;"><b>Primary Fault:</b> <span style="color:#b91c1c; font-weight:700;">{asset_row['top_issue']}</span></p>
                            <p style="margin:4px 0;"><b>Parts Lead Time:</b> {lead_days} Days</p>
                            <p style="margin:4px 0;"><b>Estimated Servicing Cost:</b> ${repair_cost:,.2f}</p>
                            <p style="margin:4px 0;"><b>Estimated Financial Savings (ROI):</b> <span style="color:#166534; font-weight:800; font-size:1.05rem;">${net_savings:,.2f}</span></p>
                            <p style="margin:4px 0;"><b>Recommended Action:</b> {asset_row['recommended_action']}</p>
                        </div>
                        """
                        st.markdown(ticket_html, unsafe_allow_html=True)
                        
                        # Generate PDF bytes
                        pdf_data = generate_work_order_pdf(asset_row)
                        st.download_button(
                            label="Download Work Order (PDF)",
                            data=pdf_data,
                            file_name=f"Work_Order_{selected_wo_asset}.pdf",
                            mime="application/pdf",
                            key=f"dl_pdf_{selected_wo_asset}"
                        )

        with c_rep:
            st.markdown("### Perform Technician Repair")
            degraded_assets = df_assets[df_assets['ahi'] < 95]['asset_id'].tolist()
            if not degraded_assets:
                st.success("All fleet assets are currently operating at nominal 100% health!")
            else:
                repair_target = st.selectbox("Select Asset to Repair", degraded_assets, key="repair_select")
                if st.button("Perform Complete Repair and Reset Asset", use_container_width=True, key="repair_btn"):
                    db = get_db()
                    target_row = df_assets[df_assets['asset_id'] == repair_target].iloc[0]
                    
                    lead_days = target_row.get('lead_time_days', 30)
                    daily_loss = target_row.get('estimated_daily_revenue_loss', 0)
                    repair_cost = target_row.get('estimated_repair_cost', 5000)
                    ahi = target_row.get('ahi', 100)
                    catastrophic_loss_avoided = (daily_loss * lead_days) + (config.EMERGENCY_REPLACEMENT_COST if ahi < 50 else config.PREVENTIVE_MAINTENANCE_COST * 2)
                    net_savings = max(0.0, catastrophic_loss_avoided - repair_cost)

                    # 1. Send Simulation Command to clear overrides
                    cmd = {
                        'asset_id': repair_target,
                        'action': 'clear_overrides',
                        'parameters': {'clean_panels': True, 'repair_all': True},
                        'status': 'pending',
                        'created_at': datetime.now(timezone.utc)
                    }
                    db[config.COLLECTION_COMMANDS].insert_one(cmd)

                    # 2. Heals ONLY the latest telemetry document for instant responsiveness, keeping historical records intact!
                    latest_doc = db[config.COLLECTION_TELEMETRY].find_one(
                        {'asset_id': repair_target},
                        sort=[('timestamp', -1)]
                    )
                    if latest_doc:
                        db[config.COLLECTION_TELEMETRY].update_one(
                            {'_id': latest_doc['_id']},
                            {'$set': {'anomaly_scores': {}, 'status_type_id': 0, 'has_diode_fault': False, 'soiling_factor': 1.0}}
                        )

                    # 3. Insert Permanent Repair History Record into MongoDB
                    repair_record = {
                        'asset_id': repair_target,
                        'asset_type': target_row.get('asset_type', 'unknown'),
                        'region': target_row.get('region', 'Unknown'),
                        'oem': target_row.get('oem', 'Generic'),
                        'repaired_at': datetime.now(timezone.utc),
                        'primary_fault_fixed': target_row.get('top_issue', 'General Wear'),
                        'ahi_before': float(ahi),
                        'ahi_after': 100.0,
                        'repair_cost': float(repair_cost),
                        'financial_savings': float(net_savings),
                        'status': 'Completed & Health Restored'
                    }
                    col_repair = getattr(config, 'COLLECTION_REPAIR_HISTORY', 'repair_history')
                    db[col_repair].insert_one(repair_record)

                    # Reset session state selections for repaired asset
                    if "wo_select" in st.session_state and st.session_state["wo_select"] == repair_target:
                        del st.session_state["wo_select"]
                    if "repair_select" in st.session_state and st.session_state["repair_select"] == repair_target:
                        del st.session_state["repair_select"]

                    st.success(f"Maintenance completed on **{repair_target}**! Repair logged to MongoDB fix history. Health restored to 100% (Saved ${net_savings:,.2f}).")
                    st.cache_data.clear()
                    time.sleep(0.3)
                    st.rerun()

        # Render Live Fix History from MongoDB
        st.divider()
        st.markdown("### Completed Repair & Servicing History (MongoDB Log)")
        repair_history = fetch_repair_history()
        if not repair_history:
            st.caption("No repairs recorded yet in MongoDB.")
        else:
            df_rep = pd.DataFrame(repair_history)
            df_rep_display = df_rep[['repaired_at', 'asset_id', 'asset_type', 'oem', 'primary_fault_fixed', 'ahi_before', 'ahi_after', 'repair_cost', 'financial_savings', 'status']].copy()
            df_rep_display.columns = ['Repaired Timestamp (UTC)', 'Asset ID', 'Type', 'OEM Hardware', 'Fault Serviced', 'AHI Before', 'AHI After', 'Repair Cost ($)', 'Net Money Saved ($)', 'Status']
            st.dataframe(df_rep_display, use_container_width=True, hide_index=True)

        # Email Notification Settings Form
        st.divider()
        st.markdown("### Email Alert Dispatch Configuration & Recipient Settings")
        st.caption("Configure the destination email address and optional SMTP server credentials for automated critical equipment alerts.")

        db = get_db()
        current_cfg = db['settings'].find_one({'key': 'email_config'}) or {}
        saved_email = current_cfg.get('recipient_email', 'operator@energycorp.com')
        saved_smtp_h = current_cfg.get('smtp_host', 'smtp.gmail.com')
        saved_smtp_p = current_cfg.get('smtp_port', 587)
        saved_smtp_u = current_cfg.get('smtp_user', '')

        with st.form("email_settings_form"):
            col_e1, col_e2 = st.columns([2, 2])
            with col_e1:
                recipient_input = st.text_input("Alert Recipient Email Address", value=saved_email, help="All automated HTML failure alerts (<50 AHI) will be sent to this email address.")
                smtp_user_input = st.text_input("SMTP Outbound User / Email", value=saved_smtp_u, placeholder="e.g., alert-dispatcher@yourcompany.com")
            with col_e2:
                smtp_host_input = st.text_input("SMTP Host Server", value=saved_smtp_h)
                col_p1, col_p2 = st.columns(2)
                with col_p1:
                    smtp_port_input = st.number_input("SMTP Port", value=int(saved_smtp_p), min_value=1, max_value=65535)
                with col_p2:
                    smtp_pass_input = st.text_input("SMTP App Password", type="password", placeholder="App Password")

            if st.form_submit_button("Save Email Preferences", use_container_width=True):
                new_settings = {
                    'key': 'email_config',
                    'recipient_email': recipient_input.strip(),
                    'smtp_host': smtp_host_input.strip(),
                    'smtp_port': int(smtp_port_input),
                    'smtp_user': smtp_user_input.strip(),
                    'smtp_pass': smtp_pass_input if smtp_pass_input else current_cfg.get('smtp_pass', ''),
                    'updated_at': datetime.now(timezone.utc)
                }
                db['settings'].update_one({'key': 'email_config'}, {'$set': new_settings}, upsert=True)
                st.success(f"Email preferences saved successfully! Automated alerts will now be dispatched to **{recipient_input.strip()}**.")
                st.cache_data.clear()

        # Render Dispatched Email & System Alert Inbox from MongoDB
        st.divider()
        st.markdown("### Dispatched HTML Email Alerts & System Notices (MongoDB Log)")
        alerts = fetch_alert_notifications()
        if not alerts:
            st.caption("No email alerts or system notifications triggered yet.")
        else:
            df_alt = pd.DataFrame(alerts)
            df_alt_display = df_alt[['dispatched_at', 'severity', 'asset_id', 'asset_type', 'primary_fault', 'ahi', 'resolution_lead_days', 'daily_revenue_loss', 'recipient', 'delivery_status']].copy()
            df_alt_display.columns = ['Dispatched Timestamp (UTC)', 'Severity', 'Asset ID', 'Type', 'Primary Fault', 'AHI Score', 'Resolution Window (Days)', 'Daily Loss ($)', 'Recipient Email', 'Dispatch Status']
            st.dataframe(df_alt_display, use_container_width=True, hide_index=True)
            
            with st.expander("Preview Dispatched HTML Email Layout", expanded=False):
                latest_alert = alerts[0]
                st.markdown(f"<b>Previewing HTML Email for Alert #{latest_alert.get('asset_id')}</b> ({latest_alert.get('severity')})", unsafe_allow_html=True)
                st.components.v1.html(latest_alert.get('html_content', ''), height=500, scrolling=True)

# ── Tab 4: Financial Impact ──────────────────────────────────
with tab4:
    if df_assets.empty:
        st.info("No financial data.")
    else:
        st.markdown("<h3 style='color:#0f172a;'>Revenue Loss and Maintenance ROI</h3>", unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            fig_bar = px.bar(df_assets, x='asset_id', y='estimated_daily_revenue_loss', color='urgency',
                             title='Daily Revenue Loss by Asset ($)',
                             color_discrete_map={'Immediate': '#ef4444', 'This Week': '#f59e0b',
                                                 'Scheduled': '#10b981', 'Monitor': '#0284c7'})
            apply_plotly_glass_layout(fig_bar)
            st.plotly_chart(fig_bar, use_container_width=True)
        with c2:
            fig_pie = px.pie(df_assets, names='region', values='estimated_daily_revenue_loss', title='Loss Distribution by Climate Region')
            apply_plotly_glass_layout(fig_pie)
            st.plotly_chart(fig_pie, use_container_width=True)

        st.divider()
        at_risk_df = df_assets[df_assets['ahi'] < 50]
        cost_inaction = at_risk_df['estimated_daily_revenue_loss'].sum() * 30 + (len(df_assets[df_assets['ahi'] < 20]) * config.EMERGENCY_REPLACEMENT_COST)
        cost_pm = at_risk_df['estimated_repair_cost'].sum()
        savings = cost_inaction - cost_pm

        c1, c2, c3 = st.columns(3)
        with c1:
            render_glass_card("30-Day Cost of Inaction", f"${cost_inaction:,.0f}", "Projected Cumulative Loss", "", "#ef4444")
        with c2:
            render_glass_card("Preventive Servicing Cost", f"${cost_pm:,.0f}", "Scheduled Repairs", "", "#f59e0b")
        with c3:
            render_glass_card("Net Potential ROI", f"${max(0, savings):,.0f}", "Saved by Early Action", "", "#10b981")

# ── Tab 5: Asset Manager ─────────────────────────────────────
with tab5:
    st.markdown("<h3 style='color:#0f172a;'>Provision and Register New Assets</h3>", unsafe_allow_html=True)
    st.caption("New assets are registered to MongoDB and auto-discovered by the running IoT simulator engine.")

    with st.form("create_asset_form"):
        col_a, col_b = st.columns(2)
        with col_a:
            new_id = st.text_input("Asset ID", placeholder="e.g., WT-Nordic-05 or SP-Desert-08")
            new_type = st.selectbox("Asset Type", ["wind_turbine", "solar_panel"])
            new_region = st.selectbox("Climate Region", REGIONS)
        with col_b:
            if new_type == "wind_turbine":
                fault_options = [
                    "Healthy (100% Nominal)",
                    "Overheated Gearbox (50% Health)",
                    "Critical Generator Bearing (20% Health)"
                ]
            else:
                fault_options = [
                    "Healthy (100% Nominal)",
                    "Blown Solar Diode (33% Power Drop)",
                    "Heavy Solar Dust Soiling (0.70 Ratio)"
                ]
            initial_condition = st.selectbox("Initial Health / Fault Condition", fault_options)
            
            if new_type == "solar_panel":
                new_lat = st.number_input("Latitude", value=28.6, min_value=-90.0, max_value=90.0)
                new_soiling_rate = st.number_input("Soiling Degradation Rate (/tick)", value=0.001, format="%.4f")
                new_inverter_eff = st.number_input("Inverter Baseline Efficiency", value=0.96, min_value=0.5, max_value=1.0)
            else:
                st.info("Wind turbines auto-assign dataset CSV data streams from Kaggle.")
                new_lat = None
                new_soiling_rate = None
                new_inverter_eff = None

        submitted = st.form_submit_button("Register Asset into Fleet", use_container_width=True)

        if submitted:
            if not new_id:
                st.error("Asset ID is required.")
            else:
                db = get_db()
                existing = db[config.COLLECTION_ASSETS].find_one({'asset_id': new_id})
                if existing:
                    st.error(f"Asset '{new_id}' already exists!")
                else:
                    custom_params = {}
                    if "Overheated Gearbox" in initial_condition:
                        custom_params['initial_fault'] = 'overheated_gearbox'
                    elif "Critical Generator" in initial_condition:
                        custom_params['initial_fault'] = 'critical_generator'
                    elif "Blown Solar Diode" in initial_condition:
                        custom_params['initial_fault'] = 'diode_fault'
                    elif "Heavy Solar Dust" in initial_condition:
                        custom_params['initial_fault'] = 'heavy_soiling'

                    if new_type == 'solar_panel':
                        custom_params.update({
                            'latitude': new_lat,
                            'soiling_rate': new_soiling_rate,
                            'inverter_efficiency': new_inverter_eff,
                        })

                    doc = {
                        'asset_id': new_id,
                        'asset_type': new_type,
                        'region': new_region,
                        'capacity_kw': config.WIND_TURBINE_CAPACITY_KW if new_type == 'wind_turbine' else config.SOLAR_PANEL_CAPACITY_KW,
                        'custom_params': custom_params,
                        'status': 'pending',
                        'registered_at': datetime.now(timezone.utc),
                    }
                    db[config.COLLECTION_ASSETS].insert_one(doc)
                    st.success(f"Asset **{new_id}** created with condition: **{initial_condition}**! The IoT simulator will activate it within ~5 seconds.")
                    st.cache_data.clear()

    st.divider()
    st.markdown("#### Registered Asset Inventory")
    all_reg = fetch_all_assets()
    if all_reg:
        df_reg = pd.DataFrame(all_reg)
        avail_reg = [c for c in ['asset_id', 'asset_type', 'region', 'status', 'capacity_kw'] if c in df_reg.columns]
        st.dataframe(df_reg[avail_reg], use_container_width=True, hide_index=True)

# ── Tab 6: Command Center ────────────────────────────────────
with tab6:
    st.markdown("<h3 style='color:#0f172a;'>Operational Command Center</h3>", unsafe_allow_html=True)
    st.caption("Domain-aware dispatch console: inject live faults, schedule panel cleaning, or apply sensor overrides to running fleet assets.")

    all_asset_map = {a['asset_id']: a.get('asset_type', 'unknown') for a in all_assets} if all_assets else {}
    all_asset_ids = list(all_asset_map.keys())

    wind_asset_ids = [aid for aid, atype in all_asset_map.items() if atype == 'wind_turbine']
    solar_asset_ids = [aid for aid, atype in all_asset_map.items() if atype == 'solar_panel']

    if not all_asset_ids:
        st.warning("No running assets available. Register assets in the Asset Manager tab.")
    else:
        target_options = []
        if wind_asset_ids:
            target_options.append("ALL WIND TURBINES")
        if solar_asset_ids:
            target_options.append("ALL SOLAR PANELS")
        target_options.extend(all_asset_ids)

        target_asset = st.selectbox("Target Equipment", target_options, key="cmd_target_asset")
        
        # Determine target asset type
        if target_asset == "ALL WIND TURBINES":
            selected_type = "wind_turbine"
            st.info(f"Target Selected: **ALL WIND TURBINES** ({len(wind_asset_ids)} Units)")
        elif target_asset == "ALL SOLAR PANELS":
            selected_type = "solar_panel"
            st.info(f"Target Selected: **ALL SOLAR PANELS** ({len(solar_asset_ids)} Units)")
        else:
            selected_type = all_asset_map.get(target_asset, "unknown")
            st.info(f"Target Selected: **{target_asset}** (Type: **{selected_type.upper().replace('_', ' ')}**)")

        with st.form("command_form"):
            if selected_type == "wind_turbine":
                action_options = [
                    "inject_fault - Inject Gearbox Bearing Overheat (+25 deg C)",
                    "inject_fault - Inject Generator Bearing Friction Failure (+35 deg C)",
                    "inject_fault - Inject 3-Phase Current Imbalance (15% Deviation)",
                    "override - Custom Telemetry Sensor Offset",
                    "clear_overrides - Perform Service Maintenance & Reset Asset",
                    "stop - Emergency Stop Wind Turbine"
                ]
            else:  # solar_panel
                action_options = [
                    "inject_fault - Inject Blown Bypass Diode (33% Power Drop)",
                    "inject_fault - Inject Heavy Dust Soiling (0.70 Soiling Ratio)",
                    "override - Schedule Panel Cleaning Crew (Reset Soiling to 1.0)",
                    "override - Custom Telemetry Sensor Offset",
                    "clear_overrides - Perform Service Maintenance & Reset Asset",
                    "stop - Emergency Stop Solar Array"
                ]

            action = st.selectbox("Action / Fault Scenario", action_options, key="cmd_action_select")

            param_col1, param_col2 = st.columns(2)
            
            with param_col1:
                if selected_type == "wind_turbine":
                    temp_offset = st.number_input("Thermal Fault Offset (deg C)", value=25.0, key="cmd_temp_offset")
                    elec_imbalance = st.number_input("Current Imbalance (%)", value=15.0, min_value=0.0, max_value=100.0, key="cmd_imbalance")
                    diode_loss = 33.0
                    soiling_val = 0.70
                else:  # solar_panel
                    diode_loss = st.number_input("Diode Power Loss (%)", value=33, min_value=0, max_value=100, key="cmd_diode_loss")
                    soiling_val = st.number_input("Dust Soiling Ratio (1.0 = Clean)", value=0.70, min_value=0.1, max_value=1.0, key="cmd_soiling_val")
                    temp_offset = 25.0
                    elec_imbalance = 15.0

            with param_col2:
                custom_key = st.text_input("Custom Telemetry Key", placeholder="e.g., ambient_temp", key="cmd_custom_key")
                custom_value = st.number_input("Custom Telemetry Value", value=0.0, key="cmd_custom_val")

            send = st.form_submit_button("Dispatch Real-time Command", use_container_width=True)

            if send:
                db = get_db()
                action_type = action.split(" - ")[0]

                if target_asset == "ALL WIND TURBINES":
                    targets = wind_asset_ids
                elif target_asset == "ALL SOLAR PANELS":
                    targets = solar_asset_ids
                else:
                    targets = [target_asset]
                
                for tid in targets:
                    parameters = {}
                    
                    if "Gearbox" in action:
                        parameters = {'gearbox_bearing_temp': temp_offset, 'gearbox_oil_temp': temp_offset * 0.8}
                    elif "Generator Bearing" in action:
                        parameters = {'generator_bearing_de_temp': temp_offset + 10, 'generator_bearing_nde_temp': temp_offset + 5}
                    elif "Current Imbalance" in action:
                        parameters = {'current_phase_1': elec_imbalance}
                    elif "Diode" in action:
                        parameters = {'inject_diode_fault': True, 'diode_fault_loss': diode_loss / 100.0}
                    elif "Heavy Dust" in action:
                        parameters = {'soiling_factor': soiling_val}
                    elif "Cleaning" in action:
                        parameters = {'clean_panels': True}
                    elif "Custom Telemetry" in action and custom_key:
                        parameters = {custom_key: custom_value}
                    elif "clear_overrides" in action_type:
                        parameters = {'clean_panels': True, 'repair_all': True}

                    cmd = {
                        'asset_id': tid,
                        'action': action_type,
                        'parameters': parameters,
                        'status': 'pending',
                        'created_at': datetime.now(timezone.utc)
                    }
                    db[config.COLLECTION_COMMANDS].insert_one(cmd)

                st.success(f"Command **{action_type}** successfully dispatched to {len(targets)} equipment unit(s)!")
                st.cache_data.clear()

    st.divider()
    st.markdown("#### Command Dispatch Audit Log")
    cmd_hist = fetch_command_history()
    if cmd_hist:
        df_cmd = pd.DataFrame(cmd_hist)
        avail_cmd = [c for c in ['asset_id', 'action', 'parameters', 'status', 'created_at'] if c in df_cmd.columns]
        st.dataframe(df_cmd[avail_cmd], use_container_width=True, hide_index=True)

# ─── Auto Refresh Loop (Default ON) ───────────────────────────
if st.session_state.get("toolbar_auto_refresh", True):
    time.sleep(2)
    st.rerun()
