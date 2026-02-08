"""
Battery Degradation Analysis Module

This module analyzes and visualizes battery capacity degradation over multiple
discharge cycles using data from the NASA Battery Dataset. It demonstrates how
battery health declines with use by tracking the capacity in each discharge cycle.

The module provides:
1. Data loading: Extracts discharge cycles and capacity measurements from MATLAB files
2. Feature engineering: Calculates State of Health (SoH) as percentage of initial capacity
3. Visualization: Creates plots showing capacity decline and degradation trends
4. Analysis: Displays statistics of battery performance over time

This analysis is useful for:
- Understanding battery aging characteristics
- Identifying degradation rates
- Predicting battery end-of-life
- Validating battery health models

Dependencies:
    - scipy: MATLAB file loading (.mat format)
    - pandas: Data manipulation and analysis
    - matplotlib: Data visualization and plotting
"""

import scipy.io
import pandas as pd
import matplotlib.pyplot as plt

# ============================================================================
# Configuration
# ============================================================================

# Path to battery data file
DATA_FILE = "data/raw/B0005.mat"

# Output file for degradation plot
OUTPUT_PLOT = "basis/output/battery_degradation_B0005.png"

# Figure size for plots (width, height) in inches
FIGURE_SIZE = (10, 5)

# ============================================================================
# Data Loading and Processing
# ============================================================================


def load_battery_data(file_path):
    """
    Load battery cycling data from a MATLAB file and extract discharge capacity.

    This function reads the NASA Battery Dataset in MATLAB format and processes
    all discharge cycles to extract capacity measurements. Each discharge cycle
    has an associated capacity value that indicates how much charge the battery
    can hold at that point in its life.

    Args:
        file_path (str): Path to the MATLAB file containing battery cycling data
                        Expected format: NASA Battery Dataset (e.g., B0005.mat)

    Returns:
        pd.DataFrame: DataFrame with two columns:
            - Cycle: Discharge cycle number (sequential numbering: 1, 2, 3, ...)
            - Capacity: Measured capacity for that discharge cycle (in Ah)

    Note:
        - Only discharge cycles are processed; charge cycles are skipped
        - Capacity values are extracted from the nested MATLAB structure
        - The cycle numbering is relative (sequential) not absolute
    """
    # Load the MATLAB file
    mat = scipy.io.loadmat(file_path)

    # Extract the cycle array from nested MATLAB structure
    # The [0, 0] indexing navigates the nested structure
    data = mat["B0005"][0, 0]["cycle"][0]

    # Initialize lists to store extracted data
    discharge_capacity = []  # Capacity values for each discharge
    cycle_number = []  # Cycle counter

    # ========================================================================
    # Process each cycle in the dataset
    # ========================================================================
    for i in range(len(data)):
        # Get the type of this cycle (discharge or charge)
        cycle_type = data[i]["type"][0]

        # Only process discharge cycles
        # (Charge cycles are less useful for degradation analysis)
        if cycle_type == "discharge":
            # Extract the capacity measurement for this discharge
            # Access pattern: data[i]["data"][0, 0]["Capacity"][0][0]
            capacity = data[i]["data"][0, 0]["Capacity"][0][0]

            # Store the capacity value
            discharge_capacity.append(capacity)

            # Increment the cycle counter
            # Use length of list for sequential numbering
            cycle_number.append(len(discharge_capacity))

    # ========================================================================
    # Create DataFrame from collected data
    # ========================================================================
    df = pd.DataFrame({"Cycle": cycle_number, "Capacity": discharge_capacity})
    return df


# ============================================================================
# Analysis and Visualization
# ============================================================================


def visualize_battery_degradation(df):
    """
    Analyze and visualize battery capacity degradation over discharge cycles.

    This function calculates the State of Health (SoH) for each cycle relative to
    the initial battery capacity, then creates a line plot showing how capacity
    decreases with cycle count. The visualization helps identify degradation rate
    and remaining battery life.

    The State of Health is calculated as:
        SoH(%) = (Current_Capacity / Initial_Capacity) * 100

    A 100% SoH indicates a healthy battery at the beginning of life (BOL).
    As the battery ages, SoH decreases. Batteries are typically considered
    end-of-life (EOL) at 80% SoH.

    Args:
        df (pd.DataFrame): DataFrame with columns:
            - Cycle: Discharge cycle number
            - Capacity: Capacity measurement for that cycle (in Ah)

    Output:
        - Creates a plot with capacity vs cycle number
        - Displays the plot in interactive window
        - Saves the plot as PNG file for documentation
        - Prints first 10 rows of the dataset to console
    """
    # ========================================================================
    # Step 1: Calculate State of Health (SoH)
    # ========================================================================
    # Get the capacity of the first cycle (reference for healthy battery)
    initial_capacity = df["Capacity"].iloc[0]

    # Calculate SoH as percentage relative to initial capacity
    # SoH = (Current Capacity / Initial Capacity) × 100%
    df["SoH"] = (df["Capacity"] / initial_capacity) * 100

    # ========================================================================
    # Step 2: Create visualization
    # ========================================================================
    # Create figure with specified size
    plt.figure(figsize=FIGURE_SIZE)

    # Plot capacity vs cycle number
    # Use circular markers to show individual measurements
    # Use solid line to connect points and show trend
    # Use blue color for clarity
    plt.plot(df["Cycle"], df["Capacity"], marker="o", linestyle="-", color="b")

    # Add descriptive title
    plt.title("Battery Degradation (B0005)")

    # Label x-axis (cycle count)
    plt.xlabel("Number of Discharge Cycles")

    # Label y-axis (capacity in Ampere-hours)
    plt.ylabel("Capacity (Ah)")

    # Enable grid for easier reading of values
    plt.grid(True)

    # ========================================================================
    # Step 3: Display data and save results
    # ========================================================================
    # Print first 10 rows of the dataset
    print(df.head(10))

    # Save the figure to disk as PNG for documentation and sharing
    plt.savefig(OUTPUT_PLOT)

    # Display the figure in the interactive window
    plt.show()


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    """
    Main execution block for battery degradation analysis.

    Workflow:
    1. Load battery cycling data from MATLAB file
    2. Extract discharge capacity measurements
    3. Calculate State of Health metrics
    4. Generate and display degradation plot
    5. Save results to disk

    Input:
        - Battery data file: input/B0005.mat (NASA Battery Dataset)

    Output:
        - Console: First 10 rows of cycle/capacity data
        - File: battery_degradation_B0005.png (degradation plot)
        - Display: Interactive plot window showing capacity vs cycle count
    """
    # Load the battery data from MATLAB file
    battery_data_df = load_battery_data(DATA_FILE)

    # Analyze and visualize the degradation
    visualize_battery_degradation(battery_data_df)
