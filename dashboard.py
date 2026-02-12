"""
Battery Digital Twin Live Dashboard.

This module provides a real-time Streamlit dashboard for monitoring battery health metrics
from the Digital Twin backend. It displays State of Health (SoH), internal resistance trends,
and historical data through interactive charts.

The dashboard connects to the FastAPI backend (api_server.py) and auto-refreshes every
10 seconds to display the latest battery monitoring data.

Dependencies:
  - streamlit: Web framework for interactive dashboard creation.
  - requests: HTTP client for fetching data from the FastAPI backend.
  - pandas: Data manipulation and DataFrame operations.
  - time: Built-in module for implementing refresh intervals.

Environment:
  - API_URL: Expected to be running at http://127.0.0.1:8000
"""

import streamlit as st
import requests
import pandas as pd
import time

# Configure Streamlit page settings
st.set_page_config(page_title="Battery Digital Twin", layout="wide")

st.title("🔋 Battery Health Live Dashboard")
st.markdown("---")

# API endpoint configuration (FastAPI backend server)
API_URL = "http://127.0.0.1:8000"


def fetch_data(endpoint):
    """
    Fetch JSON data from the FastAPI backend.

    Args:
        endpoint (str): The API endpoint path (e.g., 'status/latest', 'history').

    Returns:
        dict or list: Parsed JSON response data if successful, None otherwise.
    """
    try:
        response = requests.get(f"{API_URL}/{endpoint}")
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        return None
    return None


# ============ SIDEBAR & STATUS ============
latest_data = fetch_data("status/latest")


if latest_data and "error" not in latest_data:
    soh = latest_data["soh"]

    st.sidebar.header("System Status")
    st.sidebar.success("✓ API Connected")
    st.sidebar.write(f"Last Update: {latest_data['timestamp']}")

    # ============ KEY METRICS (Top Row) ============
    col1, col2, col3 = st.columns(3)

    with col1:
        # State of Health metric with delta showing deviation from reference capacity
        delta_val = f"{soh - 100:.2f}%"
        st.metric(
            label="State of Health (SoH)",
            value=f"{soh:.2f} %",
            delta=delta_val,
            delta_color="normal",
        )

    with col2:
        # Average internal resistance metric (ohms)
        st.metric(
            label="Internal Resistance (Average)",
            value=f"{latest_data['avg_resistance']:.2f} Ω",
        )

    with col3:
        # Battery status indicator with explicit, non-overlapping thresholds:
        # - Healthy: SoH > 90% (green) — Battery performing well, no action needed
        # - Warning: 80% < SoH <= 90% (amber) — Monitor performance, schedule maintenance soon
        # - Maintenance Required: SoH <= 80% (red) — Immediate battery inspection and potential replacement needed
        if soh >= 90:
            status_text = "✓ Healthy"
            color = "#16a34a"  # green
        elif soh > 80:
            status_text = "⚠ Warning - Check Soon"
            color = "#f59e0b"  # amber
        else:
            status_text = "🚨 Maintenance Required"
            color = "#dc2626"  # red

        # Render status indicator with HTML/CSS for color support and custom styling.
        # This allows visual distinction between status states for quick dashboard interpretation.
        status_html = f"""
        <div style="text-align:left;">
        <div style="font-size:14px;color:#FFFFFF;margin-bottom:6px;">Battery State Indicator</div>
        <div style="font-size:20px;color:{color};font-weight:600;">{status_text}</div>
        </div>
        """
        st.markdown(status_html, unsafe_allow_html=True)

    forecast = fetch_data("forecast")
    if forecast and "remaining_cycles" in forecast:
        st.markdown("--- Predictive Maintenance Prognose ---")

        # Eine schöne Info-Box
        c1, c2 = st.columns(2)
        with c1:
            st.info(
                f"**Verbleibende Zyklen bis 80% SoH:** ca. {forecast['remaining_cycles']} Zyklen"
            )
        with c2:
            st.info(
                f"**Voraussichtliches Ende bei Zyklus:** {forecast['estimated_end_cycle']}"
            )

        # Kleiner Fortschrittsbalken zum "Lebensende"
        # Wenn wir bei 100% starten und bei 80% Schluss ist, sind 20% der Bereich.
        progress = max(
            0, min(100, (latest_data["soh"] - 80) / 0.2)
        )  # Normalisiert auf 0-100%
        st.write("Lebensdauer-Budget:")
        st.progress(progress / 100)

    # ============ CHARTS (Bottom Row) ============
    # Fetch historical battery data and display interactive time-series charts for trend analysis.
    history_data = fetch_data("history")
    if history_data:
        df = pd.DataFrame(history_data)

        c1, c2 = st.columns(2)

        with c1:
            st.subheader("Capacity Loss (SoH Trend)")
            st.line_chart(df.set_index("cycle_id")["soh"])
            st.write(
                "Shows how the State of Health (SoH) has evolved over discharge cycles. A downward trend indicates degradation."
            )

        with c2:
            st.subheader("Internal Resistance Rise")
            st.area_chart(df.set_index("cycle_id")["avg_resistance"])
            st.write(
                "Shows the average internal resistance over cycles. An increasing trend can indicate worsening battery health."
            )

    # Display critical warning if State of Health drops below 80%.
    # This serves as an alert to maintenance teams that immediate action is required.
    if soh <= 80:
        st.error(
            f"🚨 CRITICAL ALERT: State of Health has dropped to {soh:.2f}%. Battery inspection required."
        )

else:
    # Display error if API is unreachable. Ensures the user is aware of connectivity issues.
    st.error(
        "❌ Unable to connect to API. Please ensure 'api_server.py' is running on port 8000."
    )

# Auto-refresh dashboard every 5 seconds for live updates.
# This keeps the displayed metrics current without requiring manual page refresh.
time.sleep(5)
st.rerun()
