import scipy.io
import time
import json
import paho.mqtt.client as mqtt

# Konfiguration
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "automotive/battery/telemetry"
FILE_NAME = "input/B0005.mat"


def load_battery_data(file_path):
    mat = scipy.io.loadmat(file_path)
    return mat["B0005"][0, 0]["cycle"][0]


def run_simulator():
    # 1. Daten laden
    try:
        data = load_battery_data(FILE_NAME)
    except FileNotFoundError:
        print(f"Datei {FILE_NAME} nicht gefunden!")
        return

    # 2. MQTT Client aufsetzen
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "Vehicle_Simulator_B0005")

    try:
        client.connect(MQTT_BROKER, MQTT_PORT)
        print(f"Verbunden mit Broker {MQTT_BROKER}")
    except Exception as e:
        print(f"Verbindung zum Broker fehlgeschlagen: {e}")
        return

    client.loop_start()

    # 3. Streaming-Logik
    try:
        for cycle_idx, entry in enumerate(data):
            if entry["type"][0] == "discharge":
                # Daten-Extraktion
                d = entry["data"][0, 0]
                v_array = d["Voltage_measured"][0]
                i_array = d["Current_measured"][0]
                t_array = d["Temperature_measured"][0]
                time_array = d["Time"][0]

                print(f"\n--- Starte Zyklus {cycle_idx} ---")

                for i in range(len(v_array)):
                    # Paket schnüren
                    payload = {
                        "cycle_id": int(cycle_idx),
                        "step": int(i),
                        "voltage": float(v_array[i]),
                        "current": float(i_array[i]),
                        "temp": float(t_array[i]),
                        "timestamp_s": float(time_array[i]),
                    }

                    # Senden
                    json_data = json.dumps(payload)
                    client.publish(MQTT_TOPIC, json_data)

                    # Kleiner Print zur Kontrolle
                    if i % 10 == 0:  # Nur jeder 10. Punkt, um Terminal nicht zu fluten
                        print(f"Sende Punkt {i} für Zyklus {cycle_idx}...")

                    time.sleep(0.1)  # 10 Hz Simulation
    except KeyboardInterrupt:
        print("\nSimulator gestoppt.")
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    run_simulator()
