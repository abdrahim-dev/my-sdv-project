"""
Battery Telemetry Simulator

This module simulates real-time battery telemetry data from electric vehicle
discharge cycles and streams it to an MQTT broker. It reads battery cycling data
from MATLAB files (NASA Battery Dataset format) and publishes telemetry measurements
including voltage, current, temperature, and calculated internal resistance.

The simulator:
1. Loads battery discharge cycle data from a .mat file
2. Establishes a connection to an MQTT broker
3. Streams telemetry data point-by-point to simulate real-time vehicle operation
4. Publishes at configurable rate (default: 10 Hz)

This data can be consumed by digital twin backends for real-time battery health
monitoring and prognostics.

Dependencies:
    - scipy: MATLAB file loading (.mat format)
    - paho-mqtt: MQTT client for publishing
"""

import scipy.io
import time
import json
import paho.mqtt.client as mqtt

# ============================================================================
# Configuration
# ============================================================================

# MQTT Broker Settings
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "automotive/battery/telemetry"

# Data Source
# Path to battery cycling data in MATLAB format (NASA Battery Dataset)
FILE_NAME = "data/raw/B0005.mat"

# Simulation Parameters
SIMULATION_RATE_HZ = 10  # Publish rate in Hz
SIMULATION_DELAY_S = 1.0 / SIMULATION_RATE_HZ  # Delay between messages in seconds

# ============================================================================
# Data Loading
# ============================================================================


def load_battery_data(file_path):
    """
    Load battery cycling data from a MATLAB file.

    Reads the NASA Battery Dataset format (.mat file) and extracts the cycle
    information for the specified battery (B0005).

    Args:
        file_path (str): Path to the .mat file containing battery data

    Returns:
        numpy.ndarray: Array of cycle objects, each containing discharge/charge data

    Raises:
        FileNotFoundError: If the specified file does not exist
    """
    mat = scipy.io.loadmat(file_path)
    return mat["B0005"][0, 0]["cycle"][0]


# ============================================================================
# Main Simulator
# ============================================================================


def run_simulator():
    """
    Run the battery telemetry simulator.

    This function orchestrates the entire simulation workflow:
    1. Loads battery data from file
    2. Connects to MQTT broker
    3. Iterates through discharge cycles
    4. Extracts telemetry measurements (voltage, current, temperature)
    5. Calculates internal resistance
    6. Publishes data to MQTT topic at specified rate
    7. Handles graceful shutdown on interruption

    The simulator publishes only discharge cycles and skips charge cycles,
    as discharge cycles provide the most relevant degradation indicators.

    Raises:
        FileNotFoundError: If the data file is not found
        Exception: If MQTT broker connection fails
    """
    # ========================================================================
    # Step 1: Load battery data
    # ========================================================================
    try:
        data = load_battery_data(FILE_NAME)
    except FileNotFoundError:
        print(f"File {FILE_NAME} not found!")
        return

    # ========================================================================
    # Step 2: Initialize MQTT client
    # ========================================================================
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "Vehicle_Simulator_B0005")

    try:
        client.connect(MQTT_BROKER, MQTT_PORT)
        print(f"Connected to broker {MQTT_BROKER}")
    except Exception as e:
        print(f"Connection to broker failed: {e}")
        return

    # Start the client background thread to handle message publishing
    client.loop_start()

    # ========================================================================
    # Step 3: Stream discharge cycles
    # ========================================================================
    try:
        for cycle_idx, entry in enumerate(data):
            # Only process discharge cycles
            # (charge cycles are less useful for degradation analysis)
            if entry["type"][0] == "discharge":
                # Extract telemetry arrays from the cycle data
                # Note: Data is nested in MATLAB format [0, 0] structure
                d = entry["data"][0, 0]
                v_array = d["Voltage_measured"][0]  # Voltage in volts
                i_array = d["Current_measured"][0]  # Current in amperes
                t_array = d["Temperature_measured"][0]  # Temperature in Celsius
                time_array = d["Time"][0]  # Time elapsed in seconds

                print(f"\n--- Start cycle {cycle_idx} ---")

                # Stream each telemetry point in this cycle
                for i in range(len(v_array)):
                    # ============================================================
                    # Extract and process measurements
                    # ============================================================
                    voltage = float(v_array[i])

                    # Use absolute current value for resistance calculation
                    # (discharge current is negative in the dataset)
                    current = abs(float(i_array[i]))

                    # ============================================================
                    # Calculate internal resistance
                    # ============================================================
                    # Internal resistance is approximated as V/I
                    # Safety check: only calculate when current is significant
                    # (> 10 mA) to avoid division artifacts at low currents
                    if current > 0.01:
                        resistance = voltage / current
                    else:
                        resistance = 0.0

                    # ============================================================
                    # Create telemetry payload
                    # ============================================================
                    # JSON message containing all telemetry for this measurement
                    payload = {
                        "cycle_id": int(cycle_idx),  # Which discharge cycle
                        "step": int(i),  # Measurement index within cycle
                        "voltage": voltage,  # Instantaneous voltage (V)
                        "current": current,  # Instantaneous current (A)
                        "internal_resistance": float(resistance),  # Calculated R (Ω)
                        "temp": float(t_array[i]),  # Temperature (°C)
                        "timestamp_s": float(time_array[i]),  # Elapsed time (s)
                    }

                    # ============================================================
                    # Publish to MQTT
                    # ============================================================
                    json_data = json.dumps(payload)
                    client.publish(MQTT_TOPIC, json_data)

                    # Progress indicator (reduced frequency to avoid terminal spam)
                    if i % 10 == 0:
                        print(f"Sending point {i} for cycle {cycle_idx}...")

                    # Simulate real-time streaming at specified rate (10 Hz default)
                    time.sleep(SIMULATION_DELAY_S)

    except KeyboardInterrupt:
        print("\nSimulator stopped.")
    finally:
        # Graceful shutdown: stop background thread and disconnect
        client.loop_stop()
        client.disconnect()


# ============================================================================
# Entry Point
# ============================================================================

if __name__ == "__main__":
    """
    Main entry point for the battery telemetry simulator.

    This script reads battery cycling data from a MATLAB file (NASA Battery Dataset)
    and streams it to an MQTT broker in real-time. Each discharge cycle is processed
    sequentially, and measurement points are published at 10 Hz to simulate actual
    vehicle telemetry.

    Usage:
        python battery_streamer.py

    Prerequisites:
        - MQTT broker running on localhost:1883
        - Battery data file: data/raw/B0005.mat
        - Dependencies: scipy, paho-mqtt

    To stop the simulator:
        Press Ctrl+C to trigger graceful shutdown

    Output:
        - Streams JSON messages to MQTT topic: automotive/battery/telemetry
        - Console output showing progress (cycle number and measurement count)
        - Each message contains: cycle_id, step, voltage, current, internal_resistance,
          temperature, and timestamp
    """
    run_simulator()

