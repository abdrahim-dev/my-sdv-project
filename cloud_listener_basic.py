"""
MQTT Cloud Listener for Battery Telemetry

This module implements a simple MQTT subscriber that receives real-time battery
telemetry data from a simulated electric vehicle. It subscribes to an MQTT topic
and processes incoming telemetry messages, displaying key battery metrics.

This listener is designed to work with battery_streamer.py which publishes
telemetry data. Together, they demonstrate:
1. Real-time data streaming from simulated vehicles
2. MQTT pub/sub communication pattern
3. JSON message parsing and processing
4. Live telemetry monitoring in a cloud backend

Features:
- Subscribes to MQTT topic for battery telemetry
- Parses JSON messages containing voltage, current, temperature, resistance
- Displays received measurements in real-time
- Error handling for malformed messages
- Continuous listening loop for live monitoring

Use Cases:
- Real-time battery health monitoring
- Cloud-based vehicle telemetry reception
- Data collection for analytics and diagnostics
- Live vehicle fleet monitoring

Dependencies:
    - paho-mqtt: MQTT client library for pub/sub messaging
"""

import paho.mqtt.client as mqtt
import json

# ============================================================================
# Configuration
# ============================================================================

# MQTT Broker connection settings
# Must match the settings in battery_streamer.py
MQTT_BROKER = "localhost"  # Broker address
MQTT_PORT = 1883  # Standard MQTT port
MQTT_TOPIC = "automotive/battery/telemetry"  # Topic to subscribe to

# ============================================================================
# Message Handling
# ============================================================================


def on_message(client, userdata, message):
    """
    MQTT message callback handler for processing incoming telemetry.

    This function is automatically called by the MQTT client whenever a new
    message arrives on the subscribed topic. It parses the JSON payload and
    displays the battery telemetry data.

    Message Format (JSON):
    {
        "cycle_id": int,              # Discharge cycle number
        "step": int,                  # Measurement index within cycle
        "voltage": float,             # Battery voltage (Volts)
        "current": float,             # Discharge current (Amperes)
        "internal_resistance": float, # Calculated resistance (Ohms)
        "temp": float,                # Battery temperature (Celsius)
        "timestamp_s": float          # Elapsed time (seconds)
    }

    Args:
        client: MQTT client instance
        userdata: User data passed to the client (unused here)
        message: MQTT message object containing:
            - message.payload: Raw message bytes (JSON encoded)
            - message.topic: The topic on which message arrived

    Behavior:
        - Decodes the JSON payload from bytes to string
        - Extracts key telemetry fields
        - Formats and displays the data to console
        - Catches and reports any parsing errors
    """
    try:
        # ====================================================================
        # Parse incoming message
        # ====================================================================
        # Decode the message payload from bytes to UTF-8 string
        # then parse the JSON to get a Python dictionary
        payload = json.loads(message.payload.decode("utf-8"))

        # ====================================================================
        # Extract telemetry fields
        # ====================================================================
        # Extract individual measurements from the payload dictionary
        v = payload["voltage"]  # Voltage in Volts
        t = payload["temp"]  # Temperature in Celsius
        i = payload["current"]  # Current in Amperes
        r = payload["internal_resistance"]  # Internal resistance in Ohms
        c_id = payload["cycle_id"]  # Cycle identifier
        s = payload["step"]  # Measurement step/index

        # ====================================================================
        # Display received telemetry
        # ====================================================================
        # Print formatted telemetry data to console
        # This shows real-time battery metrics as they arrive
        print(
            f"RECEIVED - Cycle: {c_id} | Step: {s} | Voltage: {v:.4f}V | Temp: {t:.2f}°C | Current: {i:.4f}A | Internal Resistance: {r:.4f}Ω"
        )

    except Exception as e:
        # Handle any errors in message parsing or processing
        print(f"Error processing: {e}")


# ============================================================================
# MQTT Listener Setup and Execution
# ============================================================================


def run_listener():
    """
    Initialize and run the MQTT listener for battery telemetry.

    This function sets up the MQTT client with:
    1. Client initialization with unique client ID
    2. Callback registration for message handling
    3. Connection to the MQTT broker
    4. Subscription to the telemetry topic
    5. Continuous listening loop

    The listener will run indefinitely, receiving and processing telemetry
    messages from simulated vehicles in real-time.

    Workflow:
        1. Create MQTT client with unique identifier
        2. Register on_message callback function
        3. Connect to MQTT broker (localhost:1883)
        4. Subscribe to automotive/battery/telemetry topic
        5. Enter blocking loop to receive messages
        6. Process each incoming message through callback

    Press Ctrl+C to interrupt and stop the listener.
    """
    # ========================================================================
    # Step 1: Create MQTT client instance
    # ========================================================================
    # Initialize the MQTT client with:
    # - CallbackAPIVersion: Protocol version specification
    # - Client ID: Unique identifier for this listener ("Cloud_Backend_Listener")
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "Cloud_Backend_Listener")

    # ========================================================================
    # Step 2: Register message callback
    # ========================================================================
    # Set the callback function to be called when messages arrive
    # The on_message function will be automatically called for each message
    client.on_message = on_message

    # ========================================================================
    # Step 3: Connect to MQTT broker
    # ========================================================================
    # Connect to the MQTT broker at the specified host and port
    client.connect(MQTT_BROKER, MQTT_PORT)

    # ========================================================================
    # Step 4: Subscribe to telemetry topic
    # ========================================================================
    # Subscribe to the topic where vehicle telemetry is published
    client.subscribe(MQTT_TOPIC)

    # Display startup message
    print(f"Waiting for data on topic: {MQTT_TOPIC}...")

    # ========================================================================
    # Step 5: Start message receiving loop
    # ========================================================================
    # loop_forever() enters a blocking loop that:
    # - Maintains the connection to the broker
    # - Listens for incoming messages
    # - Calls on_message callback for each received message
    # - Continues running until interrupted (Ctrl+C)
    client.loop_forever()


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    """
    Main execution block for the MQTT telemetry listener.

    This script acts as a cloud backend that receives real-time battery telemetry
    from simulated vehicles publishing via MQTT. It demonstrates:
    - MQTT pub/sub communication pattern
    - Real-time data streaming
    - Cloud-based vehicle monitoring

    Prerequisites:
        - MQTT broker running on localhost:1883
        - battery_streamer.py running to publish telemetry data
        - paho-mqtt library installed

    Usage:
        python cloud_listener_basic.py

    Output:
        - Prints received telemetry messages to console in real-time
        - Shows cycle ID, step number, voltage, temperature, current, and resistance
        - Error messages for any malformed or unparseable messages

    To stop:
        Press Ctrl+C to interrupt the listening loop
    """
    run_listener()
