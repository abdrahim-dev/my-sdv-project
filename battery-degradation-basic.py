import scipy.io
import pandas as pd
import matplotlib.pyplot as plt

# ----------------------------------------------------
# Upload battery data from MATLAB file
# ----------------------------------------------------


def load_battery_data(file_path):
    """
    Uploads the battery data from a MATLAB file and extracts the discharge capacity.

    Args:
        file_path (str): Path to the MATLAB file.

    Returns:
        pd.DataFrame: DataFrame with cycle number and capacity.
    """
    mat = scipy.io.loadmat(file_path)
    data = mat["B0005"][0, 0]["cycle"][0]

    discharge_capacity = []
    cycle_number = []

    for i in range(len(data)):
        cycle_type = data[i]["type"][0]

        if cycle_type == "discharge":
            capacity = data[i]["data"][0, 0]["Capacity"][0][0]
            discharge_capacity.append(capacity)
            cycle_number.append(len(discharge_capacity))

    df = pd.DataFrame({"Cycle": cycle_number, "Capacity": discharge_capacity})
    return df


# ----------------------------------------------------
# Visualization of Battery Degradation
# ----------------------------------------------------


def visualize_battery_degradation(df):
    """
    Visualizes the battery degradation based on the DataFrame.

    Args:
        df (pd.DataFrame): DataFrame with cycle number and capacity.
    """
    initial_capacity = df["Capacity"].iloc[0]
    df["SoH"] = (df["Capacity"] / initial_capacity) * 100

    plt.figure(figsize=(10, 5))
    plt.plot(df["Cycle"], df["Capacity"], marker="o", linestyle="-", color="b")
    plt.title("Battery Degradation (B0005)")
    plt.xlabel("Number of Discharge Cycles")
    plt.ylabel("Capacity (Ah)")
    plt.grid(True)
    print(df.head(10))  # shows the first 10 rows of the table
    plt.savefig("battery_degradation_B0005.png")
    plt.show()


# ----------------------------------------------------
# Main function
# ----------------------------------------------------

if __name__ == "__main__":
    battery_data_df = load_battery_data("input/B0005.mat")
    visualize_battery_degradation(battery_data_df)
