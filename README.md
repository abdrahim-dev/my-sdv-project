🔋 Automotive Battery Digital Twin
Predictive Maintenance & SoH Monitoring System

-- AI-Based Stat of Health (SoH) Prediction System for HV Batteries --

This project implements a functional Digital Twin for lithium-ion batteries. It leverages NASA laboratory data to demonstrate telemetry streaming, real-time analysis using machine learning, and an automated alert system.

🏗 System Architecture
The system follows a modern IoT layered architecture to ensure a clean separation between data source, transport, and logic.

1. Hardware Layer (Edge Simulator)

    Component: battery_streamer.py

    Data Source: NASA Li-ion Battery Aging Dataset (B0005.mat).

    Purpose: Simulation of a vehicle Electronic Control Unit (ECU).

    Features: Extracts voltage, current, and temperature; computes the internal resistance (Rᵢ) as a virtual sensor value.

2. Communication Layer (MQTT)

    Protocol: MQTT (Message Queuing Telemetry Transport).

    Broker: Mosquitto (localhost).

    Topic: automotive/battery/telemetry.

    Benefit: Enables loose coupling between the vehicle and the cloud backend.

3. Intelligence Layer (Digital Twin & AI)

    Component: cloud_listener.py

    AI Model: Random Forest Regressor (battery_model.pkl).

    Logic:
        •	Aggregates time-series data into cycle-based features.
        •	Computes the State of Health (SoH) based on learned knowledge.

    Alert System: Triggers warnings when the SoH drops below 80%.

🛠 Technical Workflow (UML Sequence)
    The following flow describes the interaction of the components during a discharge cycle:
        •	Data Ingestion: The simulator sends telemetry data at 10 Hz intervals.
        •	State Aggregation: The backend collects data points until the cycle_id changes.
        •	Inference: The aggregated features (average resistance, duration, average voltage) are passed to the model.
        •	Action: The system evaluates the result and outputs a maintenance recommendation.

📊 Model Performance

    Algorithm: Random Forest Regressor

    MAE (Mean Absolute Error): 0.0077 Ah

    Accuracy: > 99% on the NASA test data.

    Primary Indicators: Internal resistance (Rᵢ) and discharge duration.

🚀 Installation & Startup
	•	Start broker: mosquitto -v
	•	Train model: python train_model_rf.py
	•	Start backend: python cloud_listener.py
	•	Start simulation: python battery_streamer.py
    •	Start API Server: python api_server.py
    •	API-Endpoint: "http://127.0.0.1:8000"
    •	Start Streamlit Dashboard: streamlit run dashboard.py  
