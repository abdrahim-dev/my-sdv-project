"""
Battery Digital Twin REST API Server.

This module provides HTTP endpoints to query the battery health monitoring system's
persistent SQLite database. It exposes endpoints for retrieving the latest battery
state of health (SoH) and historical data for analytics and visualization.

API Endpoints:
  - GET /: Health check endpoint.
  - GET /status/latest: Returns the most recent battery health record.
  - GET /history: Returns all historical health records for time-series analysis.

Dependencies:
  - FastAPI: Web framework for building the REST API.
  - Uvicorn: ASGI server to run the FastAPI application.
  - sqlite3: Standard library for SQLite database access.
  - pandas: Data manipulation and SQL query results handling.
"""

from fastapi import FastAPI
import uvicorn
import sqlite3
import pandas as pd

app = FastAPI(title="Battery Digital Twin API")


def get_db_connection():
    """
    Establish and return a connection to the battery health SQLite database.

    Returns:
        sqlite3.Connection: A database connection with row_factory configured
                          to return rows as dictionaries with column names.
    """
    conn = sqlite3.connect("data/databank/battery_data.db")
    conn.row_factory = sqlite3.Row  # Enable column name access in results
    return conn


@app.get("/")
def read_root():
    """
    Health check endpoint.

    Returns:
        dict: Status information indicating the API is online.
    """
    return {"status": "Online", "message": "Battery Digital Twin API is running"}


@app.get("/status/latest")
def get_latest_status():
    """
    Retrieve the most recent battery health record.

    Queries the health_history table and returns the latest state of health (SoH),
    capacity, average resistance, and timestamp.

    Returns:
        dict: The latest health record, or an error message if no data is available.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM health_history ORDER BY timestamp DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()

    if row:
        return dict(row)
    return {"error": "No data available"}


@app.get("/history")
def get_history():
    """
    Retrieve all historical battery health records.

    Fetches the complete health history from the database and returns it as a list
    of dictionaries. Intended for time-series visualization and analytics.

    Returns:
        list[dict]: A list of health records containing cycle_id, soh, avg_resistance,
                   and timestamp for each recorded measurement.
    """
    conn = get_db_connection()
    df = pd.read_sql_query(
        "SELECT cycle_id, soh, avg_resistance, timestamp FROM health_history", conn
    )
    conn.close()
    return df.to_dict(orient="records")


@app.get("/forecast")
def get_rul_forecast():
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT cycle_id, soh FROM health_history", conn)
    conn.close()

    if len(df) < 5:  # need at least some data points to calculate a trend
        return {"error": "not enough data for forecast"}

    # linear regression: how much SoH degrades per cycle?
    # compare first and last SoH to get an average degradation rate per cycle, then extrapolate to 80% SoH
    first_soh = df["soh"].iloc[0]
    last_soh = df["soh"].iloc[-1]
    total_cycles = df["cycle_id"].iloc[-1] - df["cycle_id"].iloc[0]

    if total_cycles == 0:
        return {"error": "Berechnung noch nicht möglich"}

    deg_rate = (first_soh - last_soh) / total_cycles

    if deg_rate <= 0:  # battery is "improving" according to data (measurement noise)
        return {
            "prediction": "Stable",
            "remaining_cycles": "Infinite",
            "estimated_end_cycle": "N/A",
        }

    # how many cycles until we reach 80% SoH?
    remaining_soh = last_soh - 80
    rul_cycles = max(0, int(remaining_soh / deg_rate))

    return {
        "deg_rate_per_cycle": round(deg_rate, 4),
        "remaining_cycles": rul_cycles,
        "estimated_end_cycle": int(df["cycle_id"].iloc[-1] + rul_cycles),
    }


if __name__ == "__main__":
    # Start the server on port 8000 with auto-reload enabled for development.
    # In production, use: uvicorn api_server:app --host 0.0.0.0 --port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
