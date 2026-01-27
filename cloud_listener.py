import paho.mqtt.client as mqtt
import json

# Konfiguration (muss mit dem Simulator übereinstimmen)
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "automotive/battery/telemetry"


# Diese Funktion wird aufgerufen, wenn eine Nachricht ankommt
def on_message(client, userdata, message):
    try:
        # JSON-String zurück in Python-Dictionary verwandeln
        payload = json.loads(message.payload.decode("utf-8"))

        # Hier passiert die Magie: Wir empfangen die Daten eines "fernen" Autos
        v = payload["voltage"]
        t = payload["temp"]
        c_id = payload["cycle_id"]

        print(f"EMPFANGEN - Zyklus: {c_id} | Spannung: {v:.4f}V | Temp: {t:.2f}°C")

    except Exception as e:
        print(f"Fehler beim Verarbeiten: {e}")


# Setup des Listeners
def run_listener():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "Cloud_Backend_Listener")
    client.on_message = on_message

    client.connect(MQTT_BROKER, MQTT_PORT)
    client.subscribe(MQTT_TOPIC)

    print(f"Warte auf Daten auf Topic: {MQTT_TOPIC}...")

    # loop_forever hält das Skript am Laufen und wartet auf Nachrichten
    client.loop_forever()


if __name__ == "__main__":
    run_listener()
