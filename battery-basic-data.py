import scipy.io
import matplotlib.pyplot as plt

first_discharge = None


def load_battery_data(file_path):
    mat = scipy.io.loadmat(file_path)
    data = mat["B0005"][0, 0]["cycle"][0]
    global first_discharge

    for entry in data:
        if entry["type"][0] == "discharge":
            first_discharge = entry["data"]
            break
    return first_discharge
    # Extraktion der Zeitreihen-Signale
    # Diese sind wieder verschachtelt [0,0]


# ----------------------------------------------------
# Visualization of Battery Data
# ----------------------------------------------------


def visualize_battery_data(df):
    plt.figure(figsize=(12, 6))
    plt.subplot(2, 1, 1)
    plt.plot(time_stamps, voltage_measured, color="red")
    plt.ylabel("Spannung (V)")
    plt.title("Details eines Entladezyklus (Telemetrie-Simulation)")

    plt.subplot(2, 1, 2)
    plt.plot(time_stamps, temperature_measured, color="orange")
    plt.ylabel("Temperatur (°C)")
    plt.xlabel("Zeit (s)")
    plt.savefig("battery_data_B0005.png")
    plt.show()


# ----------------------------------------------------
# Main function
# ----------------------------------------------------

if __name__ == "__main__":
    battery_data_df = load_battery_data("input/B0005.mat")
    voltage_measured = first_discharge[0, 0]["Voltage_measured"][0]
    current_measured = first_discharge[0, 0]["Current_measured"][0]
    temperature_measured = first_discharge[0, 0]["Temperature_measured"][0]
    time_stamps = first_discharge[0, 0]["Time"][0]
    visualize_battery_data(battery_data_df)
