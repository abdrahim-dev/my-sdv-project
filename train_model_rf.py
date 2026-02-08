"""
Random Forest Model Training for Battery Capacity Prediction

This module trains a machine learning model to predict battery capacity (State of Health)
based on discharge cycle telemetry data. It implements a complete ML pipeline:

1. Data Loading: Reads battery cycling data from NASA Battery Dataset (MATLAB format)
2. Feature Engineering: Extracts key health indicators from raw telemetry
3. Model Training: Trains a Random Forest regressor on historical cycles
4. Model Evaluation: Validates performance on unseen test data
5. Model Persistence: Saves the trained model for deployment in digital twin backend

The trained model can predict remaining capacity in Ah given three key features:
- Average internal resistance (Ω) - increases with battery degradation
- Discharge duration (s) - decreases as capacity fades
- Average voltage (V) - characterizes discharge profile

This model is designed to be used in real-time by the cloud_listener.py backend
for online battery health monitoring.

Dependencies:
    - scipy: MATLAB file loading
    - pandas: Data manipulation and analysis
    - numpy: Numerical computations
    - scikit-learn: Machine learning algorithms and evaluation metrics
    - joblib: Model serialization for deployment
"""

import scipy.io
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import joblib

# ============================================================================
# Configuration
# ============================================================================

# Path to the NASA Battery Dataset (MATLAB format)
# Contains discharge/charge cycles for battery B0005
DATA_FILE = "data/raw/B0005.mat"

# Path to save the trained model
MODEL_OUTPUT_PATH = "data/processed/battery_model_rf.pkl"

# Random Forest Hyperparameters
N_ESTIMATORS = 100  # Number of trees in the forest
RANDOM_STATE = 42  # Seed for reproducibility

# Train/Test Split Configuration
TEST_SIZE = 0.2  # Use 20% of data for testing
TRAIN_SIZE = 0.8  # Use 80% of data for training

# ============================================================================
# Feature Engineering Function
# ============================================================================


def prepare_ml_data(file_path):
    """
    Load battery data and engineer features for ML model training.

    This function reads raw battery cycling data from a MATLAB file and extracts
    meaningful features that correlate with battery degradation. The NASA Battery
    Dataset contains voltage, current, temperature, and capacity measurements for
    each discharge cycle.

    Feature Engineering Strategy:
    - Average Internal Resistance: Computed as V/I per measurement, then averaged
      Interpretation: Lower resistance indicates healthier battery
    - Discharge Duration: Total time from start to end of discharge
      Interpretation: Longer duration indicates better capacity
    - Average Voltage: Mean voltage throughout discharge
      Interpretation: Characterizes the discharge profile and health state

    Args:
        file_path (str): Path to MATLAB file containing battery cycle data
                        Expected format: NASA Battery Dataset (B0005.mat)

    Returns:
        pd.DataFrame: DataFrame with columns:
            - avg_resistance: Average resistance V/I over discharge (Ohms)
            - duration: Total discharge time (seconds)
            - avg_voltage: Mean voltage during discharge (Volts)
            - target_capacity: Capacity at end of cycle (Ah) - the target variable

    Note:
        Only discharge cycles are processed (charge cycles are excluded).
        This is because discharge cycles provide better degradation indicators.
    """
    # Load MATLAB file and extract cycle data
    mat = scipy.io.loadmat(file_path)
    cycles = mat["B0005"][0, 0]["cycle"][0]

    # Initialize list to collect engineered features
    dataset = []

    # Process each cycle in the dataset
    for entry in cycles:
        # Only analyze discharge cycles (skip charge cycles)
        if entry["type"][0] == "discharge":
            # Extract measurement arrays from nested MATLAB structure
            d = entry["data"][0, 0]
            v = d["Voltage_measured"][0]  # Voltage (V)
            i = d["Current_measured"][0]  # Current (A)
            t = d["Time"][0]  # Time (s)
            capacity = d["Capacity"][0][0]  # Final capacity (Ah) - our target

            # ================================================================
            # Feature 1: Average Internal Resistance
            # ================================================================
            # Calculate instantaneous resistance at each measurement point
            # as V/I (Ohm's law approximation of battery internal resistance)
            res = v / np.abs(i)

            # Take mean to get single representative resistance value
            # Higher resistance indicates increased degradation
            avg_res = np.mean(res)

            # ================================================================
            # Feature 2: Discharge Duration
            # ================================================================
            # Calculate total time for complete discharge cycle
            # Longer discharge time indicates battery can hold charge longer
            duration = t[-1] - t[0]

            # ================================================================
            # Feature 3: Average Voltage
            # ================================================================
            # Calculate mean voltage throughout discharge
            # Helps characterize discharge profile and health state
            avg_v = np.mean(v)

            # ================================================================
            # Store engineered features with target variable
            # ================================================================
            dataset.append(
                {
                    "avg_resistance": avg_res,
                    "duration": duration,
                    "avg_voltage": avg_v,
                    "target_capacity": capacity,  # Machine learning target/label
                }
            )

    # Convert list of dictionaries to pandas DataFrame
    return pd.DataFrame(dataset)


# ============================================================================
# Main Training Pipeline
# ============================================================================

if __name__ == "__main__":
    """
    Execute the complete machine learning pipeline for battery capacity prediction.

    The pipeline consists of 6 stages:
    1. Data Loading and Feature Engineering
    2. Train/Test Split
    3. Model Training
    4. Model Evaluation
    5. Model Persistence
    6. Results Reporting
    """

    # ========================================================================
    # Stage 1: Data Loading and Feature Engineering
    # ========================================================================
    print("=" * 70)
    print("Stage 1: Loading and preparing training data...")
    print("=" * 70)

    df = prepare_ml_data(DATA_FILE)
    print(f"Dataset size: {len(df)} discharge cycles\n")
    print("Prepared data (Features):")
    print(df.head())
    print(f"\nStatistics:\n{df.describe()}\n")

    # ========================================================================
    # Stage 2: Feature and Target Separation
    # ========================================================================
    print("=" * 70)
    print("Stage 2: Separating features (X) and target (y)...")
    print("=" * 70)

    # Extract input features (independent variables)
    # These are the measurements that will be used to make predictions
    X = df[["avg_resistance", "duration", "avg_voltage"]]

    # Extract target variable (dependent variable to predict)
    # This is the battery capacity we want to predict
    y = df["target_capacity"]

    print(f"Feature matrix shape: {X.shape}")
    print(f"Target vector shape: {y.shape}")
    print(f"Target range: {y.min():.4f} - {y.max():.4f} Ah\n")

    # ========================================================================
    # Stage 3: Train/Test Split
    # ========================================================================
    print("=" * 70)
    print("Stage 3: Splitting data into training and test sets...")
    print("=" * 70)

    # Split data: 80% for training, 20% for testing
    # random_state=42 ensures reproducible splits
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE
    )

    print(f"Training set size: {len(X_train)} samples ({TRAIN_SIZE * 100:.0f}%)")
    print(f"Test set size: {len(X_test)} samples ({TEST_SIZE * 100:.0f}%)\n")

    # ========================================================================
    # Stage 4: Model Training
    # ========================================================================
    print("=" * 70)
    print("Stage 4: Training Random Forest model...")
    print("=" * 70)

    # Initialize and train the Random Forest model
    # Random Forest is chosen because:
    # - Excellent for tabular/structured data
    # - Handles non-linear relationships well
    # - Provides feature importance scores
    # - Robust to outliers
    # - No feature scaling required
    model = RandomForestRegressor(
        n_estimators=N_ESTIMATORS,
        random_state=RANDOM_STATE,
        n_jobs=-1,  # Use all available CPU cores
        verbose=0,
    )

    print(f"Model configuration: {N_ESTIMATORS} decision trees")
    model.fit(X_train, y_train)
    print("Model training completed.\n")

    # ========================================================================
    # Stage 5: Model Evaluation
    # ========================================================================
    print("=" * 70)
    print("Stage 5: Evaluating model on test set...")
    print("=" * 70)

    # Make predictions on the test set
    predictions = model.predict(X_test)

    # Calculate Mean Absolute Error (MAE)
    # Represents average magnitude of prediction errors in Ah
    error = mean_absolute_error(y_test, predictions)

    print(f"Test Set Performance:")
    print(f"  Mean Absolute Error (MAE): {error:.4f} Ah")
    print(f"  Prediction range: {predictions.min():.4f} - {predictions.max():.4f} Ah")
    print(f"  Actual range: {y_test.min():.4f} - {y_test.max():.4f} Ah\n")

    # ========================================================================
    # Feature Importance Analysis
    # ========================================================================
    print("Feature Importance Scores:")
    feature_names = ["avg_resistance", "duration", "avg_voltage"]
    for feature, importance in zip(feature_names, model.feature_importances_):
        print(f"  {feature:20s}: {importance:.4f} ({importance * 100:.1f}%)\n")

    # ========================================================================
    # Stage 6: Model Persistence
    # ========================================================================
    print("=" * 70)
    print("Stage 6: Saving trained model...")
    print("=" * 70)

    # Serialize the model to disk using joblib
    # This model will be loaded by cloud_listener.py for real-time inference
    joblib.dump(model, MODEL_OUTPUT_PATH)
    print(f"Model saved to: {MODEL_OUTPUT_PATH}")
    print("Model is ready for deployment in the Digital Twin Backend!\n")

    print("=" * 70)
    print("Training pipeline completed successfully!")
    print("=" * 70)
