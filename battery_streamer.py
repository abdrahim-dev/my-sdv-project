import scipy.io
import time
import json


def load_battery_data(file_path):
    """Lädt die MATLAB-Datei und extrahiert die Zyklen."""
    mat = scipy.io.loadmat(file_path)
    # Wir graben uns durch die Ebenen, wie besprochen
    return mat["B0005"][0, 0]["cycle"][0]


def stream_telemetry(data, delay=0.1):
    """Simuliert den Datenstrom eines Entladezyklus."""
    print(f"{'=' * 20} STARTING TELEMETRY STREAM {'=' * 20}")

    for cycle_idx, entry in enumerate(data):
        # Wir streamen nur die Entlade-Zyklen (Discharge)
        if entry["type"][0] == "discharge":
            print(f"\n>>> Streaming Cycle #{cycle_idx} (Type: Discharge)")

            # Zugriff auf die Zeitreihen-Arrays
            # Wir nutzen .flatten(), um die NumPy-Struktur zu vereinfachen
            v_array = entry["data"][0, 0]["Voltage_measured"][0]
            i_array = entry["data"][0, 0]["Current_measured"][0]
            t_array = entry["data"][0, 0]["Temperature_measured"][0]
            time_array = entry["data"][0, 0]["Time"][0]

            # Wir gehen jeden Messpunkt im Array durch
            for i in range(len(v_array)):
                # 1. DATEN VERPACKEN (Dictionary)
                # Wir konvertieren zu float, da JSON keine NumPy-Typen mag
                payload = {
                    "cycle_id": cycle_idx,
                    "step": i,
                    "voltage": float(v_array[i]),
                    "current": float(i_array[i]),
                    "temp": float(t_array[i]),
                    "timestamp": float(time_array[i]),
                }

                # 2. DATEN SERIALISIEREN (In String umwandeln)
                json_payload = json.dumps(payload)

                # 3. DATEN SENDEN (Aktuell nur Print, später MQTT)
                print(f"SENDING: {json_payload}")

                # 4. TAKTRATE SIMULIEREN
                time.sleep(delay)


if __name__ == "__main__":
    # Pfad zu deiner heruntergeladenen Datei
    FILE_NAME = "input/B0005.mat"

    try:
        battery_data = load_battery_data(FILE_NAME)
        stream_telemetry(battery_data, delay=0.1)
    except FileNotFoundError:
        print(f"Fehler: Die Datei {FILE_NAME} wurde nicht gefunden!")
    except Exception as e:
        print(f"Ein Fehler ist aufgetreten: {e}")
