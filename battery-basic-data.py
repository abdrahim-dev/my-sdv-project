"""
Battery Data Visualization Module

This module provides utilities for loading and visualizing battery discharge cycle data
from the NASA Battery Dataset (MATLAB format). It extracts telemetry measurements
(voltage, current, temperature) from discharge cycles and creates visualizations
to understand battery behavior during operation.

The module demonstrates:
1. Loading MATLAB files containing battery cycling data
2. Extracting the first discharge cycle for analysis
3. Visualizing key telemetry signals (voltage, temperature) over time
4. Saving plots for documentation and analysis

This is useful for:
- Understanding battery discharge characteristics
- Visual inspection of data quality
- Trend analysis of voltage and temperature profiles
- Documentation of battery performance

Dependencies:
    - scipy: MATLAB file format (.mat) loading
    - matplotlib: Data visualization and plotting
"""

import scipy.io
import matplotlib.pyplot as plt

# ============================================================================
# Global Variables
# ============================================================================

# Path to battery data file
DATA_FILE = "data/raw/B0005.mat"

# Store the first discharge cycle data for use across functions
# This is populated by load_battery_data() function
first_discharge = None


# ============================================================================
# Data Loading Functions
# ============================================================================


def load_battery_data(file_path):
    """
    Load battery cycling data from a MATLAB file and extract the first discharge cycle.

    This function reads the NASA Battery Dataset in MATLAB format and locates the
    first discharge cycle. It uses a global variable to store the result for use
    in subsequent visualization functions.

    The data structure is nested in MATLAB format:
    - mat["B0005"][0, 0]["cycle"][0] contains all cycles
    - Each cycle has a "type" field: "discharge" or "charge"
    - Discharge cycles contain the actual telemetry measurements

    Args:
        file_path (str): Path to the MATLAB file (e.g., "input/B0005.mat")
                        Expected format: NASA Battery Dataset

    Returns:
        numpy.ndarray: Nested MATLAB structure containing the first discharge cycle data
                      Access pattern: data[0, 0]["Voltage_measured"][0], etc.

    Note:
        - Only the first discharge cycle is extracted (function returns after finding it)
        - Charge cycles are skipped
        - The data is also stored in the global variable `first_discharge`
    """
    # Load MATLAB file
    mat = scipy.io.loadmat(file_path)

    # Extract cycle array from nested MATLAB structure
    # The [0, 0] indexing navigates the nested structure
    data = mat["B0005"][0, 0]["cycle"][0]

    # Declare we will use the global variable
    global first_discharge

    # Iterate through all cycles to find the first discharge
    for entry in data:
        # Check if this cycle is a discharge (vs. charge)
        if entry["type"][0] == "discharge":
            # Found the first discharge cycle, store it globally
            first_discharge = entry["data"]
            break

    return first_discharge


# ============================================================================
# Visualization Functions
# ============================================================================


def visualize_battery_data(df):
    """
    Create and display a multi-panel visualization of battery telemetry data.

    This function generates a 2-panel figure showing two key telemetry signals
    from a battery discharge cycle:
    - Top panel: Voltage over time (red line)
    - Bottom panel: Temperature over time (orange line)

    The plots use global variables (time_stamps, voltage_measured, temperature_measured)
    that should be extracted from the first_discharge data before calling this function.

    The figure is saved as a PNG file for documentation and analysis purposes.

    Args:
        df: Dataframe parameter (not currently used in implementation)
           Included for function signature compatibility

    Output:
        - Creates a figure with size 12x6 inches
        - Saves the figure as "battery_data_B0005.png"
        - Displays the figure in the interactive window

    Note:
        This function accesses global variables:
        - time_stamps: Time array (seconds)
        - voltage_measured: Voltage array (Volts)
        - temperature_measured: Temperature array (Celsius)

        These variables must be populated before calling this function.
    """
    # Create figure and set size
    plt.figure(figsize=(12, 6))

    # ========================================================================
    # Panel 1: Voltage vs Time
    # ========================================================================
    plt.subplot(2, 1, 1)

    # Plot voltage as a function of time
    # Use red color for voltage to distinguish from temperature
    plt.plot(time_stamps, voltage_measured, color="red")

    # Label the y-axis
    plt.ylabel("Voltage (V)")

    # Add informative title describing the data
    plt.title("Details of a discharge cycle (Telemetry simulation)")

    # ========================================================================
    # Panel 2: Temperature vs Time
    # ========================================================================
    plt.subplot(2, 1, 2)

    # Plot temperature as a function of time
    # Use orange color to distinguish from voltage
    plt.plot(time_stamps, temperature_measured, color="orange")

    # Label the y-axis
    plt.ylabel("Temperature (°C)")

    # Label the x-axis (shared across both panels)
    plt.xlabel("Time (s)")

    # ========================================================================
    # Save and Display
    # ========================================================================

    # Save the figure to disk as PNG for documentation
    plt.savefig("basis/output/battery_data_B0005.png")

    # Display the figure in the window
    plt.show()


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    """
    Main execution block for battery data visualization.

    Workflow:
    1. Load the first discharge cycle from battery data file
    2. Extract telemetry arrays from the discharge cycle
    3. Create and display visualizations
    4. Save plots to disk

    Data file: Uses B0005.mat from the NASA Battery Dataset
    Output: battery_data_B0005.png with voltage and temperature plots
    """

    # ========================================================================
    # Step 1: Load battery data
    # ========================================================================
    # Load the MATLAB file and extract the first discharge cycle
    battery_data_df = load_battery_data(DATA_FILE)

    # ========================================================================
    # Step 2: Extract telemetry measurements
    # ========================================================================
    # Extract voltage measurements (Volts)
    # Access pattern: first_discharge[0, 0]["measurement_name"][0]
    voltage_measured = first_discharge[0, 0]["Voltage_measured"][0]

    # Extract current measurements (Amperes)
    current_measured = first_discharge[0, 0]["Current_measured"][0]

    # Extract temperature measurements (Celsius)
    temperature_measured = first_discharge[0, 0]["Temperature_measured"][0]

    # Extract time array (Seconds elapsed since start of discharge)
    time_stamps = first_discharge[0, 0]["Time"][0]

    # ========================================================================
    # Step 3: Create visualizations
    # ========================================================================
    # Generate plots and save to disk
    visualize_battery_data(battery_data_df)
