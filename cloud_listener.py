"""
Digital Twin Backend for Battery Health Monitoring

This module implements a real-time MQTT listener that receives battery telemetry
data from electric vehicle simulators and uses a pre-trained Random Forest model
to predict battery capacity and State of Health (SoH).

The system:
1. Subscribes to MQTT topic for incoming battery telemetry
2. Aggregates telemetry data for each discharge cycle
3. Extracts features (average resistance, duration, voltage) when cycle changes
4. Makes capacity predictions using the trained ML model
5. Calculates and reports State of Health metrics

Dependencies:
    - paho-mqtt: MQTT client library
    - pandas: Data frame manipulation
    - joblib: Model loading/serialization
    - numpy: Numerical computations
"""

import paho.mqtt.client as mqtt
import json
import pandas as pd
import joblib
import numpy as np

# ============================================================================
# Configuration
# ============================================================================

# Path to the pre-trained Random Forest model
MODEL_PATH = "data/processed/battery_model_rf.pkl"

# MQTT Connection Settings
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "automotive/battery/telemetry"

# Reference capacity for State of Health calculation (in Ah)
# Assumption: A new battery has 1.85 Ah capacity
REFERENCE_CAPACITY = 1.85

# ============================================================================
# Model Loading
# ============================================================================

# Load the pre-trained Random Forest model
model = joblib.load(MODEL_PATH)

# ============================================================================
# Global Variables
# ============================================================================

# Buffer to store telemetry data for the current discharge cycle
current_cycle_data = []

# ID of the last processed cycle (used to detect cycle changes)
last_cycle_id = None

# ============================================================================
# Alert System
# ============================================================================


def send_alert(soh):
    """
    Send an alert if the State of Health (SoH) falls below a critical threshold.

    This function can be extended to integrate with external notification systems
    such as email, SMS, or dashboard alerts.

    Args:
        soh (float): Calculated State of Health percentage
    """
    CRITICAL_SOH_THRESHOLD = 80.0  # Alert if SoH drops below 80%
    if soh <= CRITICAL_SOH_THRESHOLD:
        print(
            f"⚠️ ALERT: Battery SoH critically low at {soh:.2f}%! Immediate attention required."
        )
    elif soh < CRITICAL_SOH_THRESHOLD + 10.0:
        print(
            f"⚠️ WARNING: Battery SoH is low at {soh:.2f}%. Consider scheduling maintenance."
        )


# ============================================================================
# Message Handling
# ============================================================================


def on_message(client, userdata, msg):
    """
    MQTT message callback handler for processing incoming telemetry data.

    This function is called whenever a new message arrives on the subscribed MQTT topic.
    It aggregates telemetry points for each cycle and triggers model inference when
    a cycle change is detected.

    Args:
        client: MQTT client instance
        userdata: User data (not used in this implementation)
        msg: MQTT message object containing the telemetry payload

    Process:
        1. Parse the incoming JSON payload
        2. Check if cycle ID has changed (indicating end of current cycle)
        3. If cycle changed: extract features and make predictions
        4. Append current message to cycle buffer
        5. Display live progress indicator
    """
    global last_cycle_id, current_cycle_data

    # Parse incoming JSON payload
    payload = json.loads(msg.payload.decode())
    cycle_id = payload["cycle_id"]

    # Detect cycle transition and trigger prediction
    if last_cycle_id is not None and cycle_id != last_cycle_id:
        if len(current_cycle_data) > 0:
            # Convert collected data into a pandas DataFrame for easier manipulation
            df_temp = pd.DataFrame(current_cycle_data)

            # ================================================================
            # Feature Engineering
            # ================================================================
            # Extract the same features used during model training

            # Average internal resistance (Ohms)
            # Lower resistance indicates healthier battery
            avg_res = df_temp["internal_resistance"].mean()

            # Average voltage (Volts)
            # Used to characterize the battery's discharge profile
            avg_v = df_temp["voltage"].mean()

            # Discharge duration (seconds)
            # Calculated as time from first to last measurement
            duration = df_temp["timestamp_s"].iloc[-1] - df_temp["timestamp_s"].iloc[0]

            # ================================================================
            # Model Inference
            # ================================================================
            # Reshape features into 2D array required by scikit-learn
            # Format: [[avg_resistance, duration, avg_voltage]]
            input_features = np.array([[avg_res, duration, avg_v]])

            # Get capacity prediction from the trained model (in Ah)
            prediction = model.predict(input_features)[0]

            # ================================================================
            # Health Assessment
            # ================================================================
            # Calculate State of Health as percentage of reference capacity
            soh_ai = (prediction / REFERENCE_CAPACITY) * 100

            # Display diagnosis results
            print(f"\n--- 🔋 DIAGNOSIS COMPLETED FOR CYCLE {last_cycle_id} ---")
            print(f"Estimated capacity: {prediction:.4f} Ah")
            print(f"State of Health (SoH): {soh_ai:.2f} %")
            print(f"Basic features: R = {avg_res:.4f} Ω, Duration = {duration:.0f} s")
            print(f"----------------------------------------------------\n")

            # Send alert if SoH is critically low
            send_alert(soh_ai)

        # Reset buffer for next cycle
        current_cycle_data = []

    # Add current measurement to cycle buffer
    current_cycle_data.append(payload)
    last_cycle_id = cycle_id

    # Display live progress (overwrites same line with carriage return)
    print(f"Processing telemetry for cycle {cycle_id}", end="\r")


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    # Initialize MQTT client
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "Digital_Twin_Backend")

    # Register callback function for incoming messages
    client.on_message = on_message

    # Establish connection to MQTT broker
    client.connect(MQTT_BROKER, MQTT_PORT)

    # Subscribe to battery telemetry topic
    client.subscribe(MQTT_TOPIC)

    # Start listening for messages
    print("Digital Twin Backend is LIVE. Waiting for vehicle data...")
    client.loop_forever()
