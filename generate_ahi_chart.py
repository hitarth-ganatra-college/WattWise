import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# Set overall style
plt.style.use('default')
fig = plt.figure(figsize=(12, 6), dpi=300, facecolor='#F8FAFC')
gs = gridspec.GridSpec(1, 2, width_ratios=[1, 2.5], wspace=0.3)

# -------------------------------------------------------------
# 1. Left Subplot: Vertical AHI Health Index Scale / Thermometer
# -------------------------------------------------------------
ax1 = fig.add_subplot(gs[0])
ax1.set_facecolor('#FFFFFF')
ax1.set_xlim(0, 10)
ax1.set_ylim(0, 100)
ax1.axis('off')

# Title
ax1.text(5, 96, "ASSET HEALTH INDEX (AHI)", fontsize=11, fontweight='bold', ha='center', color='#1E293B')

# Draw AHI Gradient Bands (Green -> Yellow -> Orange -> Red)
# 80-100: Healthy (Green #10B981)
ax1.fill_between([3.5, 6.5], 80, 100, color='#10B981', alpha=0.9)
# 50-80: Warning (Yellow #F59E0B)
ax1.fill_between([3.5, 6.5], 50, 80, color='#F59E0B', alpha=0.9)
# 20-50: Critical (Orange #F97316)
ax1.fill_between([3.5, 6.5], 20, 50, color='#F97316', alpha=0.9)
# 0-20: Failure Imminent (Red #EF4444)
ax1.fill_between([3.5, 6.5], 0, 20, color='#EF4444', alpha=0.9)

# Border box around AHI scale bar
ax1.plot([3.5, 3.5, 6.5, 6.5, 3.5], [0, 100, 100, 0, 0], color='#CBD5E1', lw=1.5)

# Text labels on left side of scale
ax1.text(3.1, 90, "HEALTHY\n(80-100)", fontsize=8, fontweight='bold', color='#059669', ha='right', va='center')
ax1.text(3.1, 65, "WARNING\n(50-79)", fontsize=8, fontweight='bold', color='#D97706', ha='right', va='center')
ax1.text(3.1, 35, "CRITICAL\n(20-49)", fontsize=8, fontweight='bold', color='#EA580C', ha='right', va='center')
ax1.text(3.1, 10, "FAILURE IMMINENT\n(0-19)", fontsize=8, fontweight='bold', color='#DC2626', ha='right', va='center')

# Current Asset Pointer (Current AHI = 34)
current_ahi = 34
ax1.annotate(
    f"  CURRENT AHI: {current_ahi}%\n  (Critical Degradation)",
    xy=(6.5, current_ahi),
    xytext=(7.2, current_ahi + 2),
    arrowprops=dict(facecolor='#EF4444', shrink=0.08, width=3, headwidth=8),
    fontsize=9,
    fontweight='bold',
    color='#B91C1C',
    va='center'
)

# -------------------------------------------------------------
# 2. Right Subplot: RUL Linear Regression Scatter Plot
# -------------------------------------------------------------
ax2 = fig.add_subplot(gs[1])
ax2.set_facecolor('#FFFFFF')

# Generate realistic degradation SCADA telemetry points
np.random.seed(42)
operating_hours = np.linspace(0, 500, 60)
# Baseline anomaly score growing linearly with noise
anomaly_score = 5 + 0.132 * operating_hours + np.random.normal(0, 3.5, size=60)
ahi_series = np.maximum(0, 100 - anomaly_score)

# Polynomial linear regression fit (polyfit deg 1)
slope, intercept = np.polyfit(operating_hours, ahi_series, 1)
trend_hours = np.linspace(0, 650, 100)
trend_ahi = slope * trend_hours + intercept

# Intersection with AHI = 0 (RUL limit)
rul_zero_hour = (0 - intercept) / slope
current_operating_hour = operating_hours[-1]
estimated_rul_hours = max(0, rul_zero_hour - current_operating_hour)

# Plot historical scatter points
ax2.scatter(operating_hours, ahi_series, color='#06B6D4', alpha=0.7, edgecolors='#0284C7', s=45, label='Historical SCADA Telemetry (AHI)')

# Plot linear regression trendline
ax2.plot(trend_hours, trend_ahi, color='#EF4444', lw=2.5, linestyle='--', label=f'Linear Polyfit Trend (Rate: {abs(slope):.2f} pts/hr)')

# Threshold lines
ax2.axhline(y=80, color='#10B981', linestyle=':', alpha=0.6, label='Warning Limit (AHI 80)')
ax2.axhline(y=20, color='#EF4444', linestyle=':', alpha=0.6, label='Critical Limit (AHI 20)')
ax2.axvline(x=current_operating_hour, color='#64748B', linestyle='-', alpha=0.5)

# Forecast Projection Highlight
ax2.plot([current_operating_hour, rul_zero_hour], [ahi_series[-1], 0], color='#DC2626', lw=3.0)
ax2.scatter([rul_zero_hour], [0], color='#991B1B', s=100, zorder=5)

# Annotation for RUL
ax2.annotate(
    f"FAILURE THRESHOLD (0 AHI)\nESTIMATED RUL: ~{estimated_rul_hours:.1f} Hours",
    xy=(rul_zero_hour, 0),
    xytext=(rul_zero_hour - 180, 22),
    arrowprops=dict(facecolor='#991B1B', shrink=0.08, width=2, headwidth=7),
    fontsize=9,
    fontweight='bold',
    color='#7F1D1D',
    bbox=dict(boxstyle='round,pad=0.4', facecolor='#FEF2F2', edgecolor='#FCA5A5', alpha=0.95)
)

# Styling and Labels
ax2.set_title("REMAINING USEFUL LIFE (RUL) LINEAR REGRESSION FORECAST", fontsize=11, fontweight='bold', color='#1E293B', pad=12)
ax2.set_xlabel("Asset Operating Time (Cumulative Telemetry Hours)", fontsize=9.5, fontweight='bold', color='#475569')
ax2.set_ylabel("Asset Health Index (AHI %)", fontsize=9.5, fontweight='bold', color='#475569')
ax2.set_ylim(-5, 105)
ax2.set_xlim(-10, 700)
ax2.grid(True, linestyle='--', alpha=0.4, color='#CBD5E1')
ax2.legend(loc='upper right', fontsize=8, frameon=True, facecolor='#F8FAFC', edgecolor='#E2E8F0')

# Card Frame borders
for ax in [ax1, ax2]:
    for spine in ax.spines.values():
        spine.set_color('#E2E8F0')
        spine.set_linewidth(1.2)

plt.tight_layout()
plt.savefig('ahi_rul_degradation_chart.png', dpi=300, bbox_inches='tight')
print("Successfully generated ahi_rul_degradation_chart.png")
