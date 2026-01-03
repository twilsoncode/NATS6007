Optoanalysis Tool - README
===========================

Overview - opto_GUI.py
--------
This tool provides a graphical user interface (GUI) for analyzing power spectral density (PSD) data from oscilloscope files (.csv, .bin, .trc). The application supports three modes of operation:

1. Manual Optoanalysis: Manual entry of frequency peaks.
2. Auto Optoanalysis: Automatic peak prediction using a neural network model.
3. Hybrid Optoanalysis: Combines automatic peak prediction with user refinement.

The GUI is built using `customtkinter`, with backend processing handled via the `opto_save` and `NN_peak_pred` modules.

Features
--------
- Import and visualize PSD data from `.csv`, `.bin`, and `.trc` files
- Estimate physical parameters based on frequency peaks and pressure values
- Support for multiple particle types
- Peak prediction using a machine learning model
- Save analyzed results automatically for further use

Installation
------------
Before running the script, you must install the required Python packages. Run the following in your terminal:

pip install customtkinter matplotlib numpy scipy

Overview - opto_save.py
--------
This script is a backend utility module for analyzing PSD (Power Spectral Density) data derived from oscilloscopes. It supports `.csv`, `.bin`, and `.trc` files from different instruments (e.g., Rohde & Schwarz, LeCroy), extracts relevant data, fits peaks, computes particle characteristics, and optionally plots and saves the results.

The tool is designed to work with a GUI or can be called from other Python scripts. It supports three types of workflows:

1. Manual Analysis
2. Automated Peak Detection
3. Hybrid Analysis (auto + user correction)

Key Functionalities
-------------------
- Load `.bin`, `.csv`, and `.trc` files using the appropriate method
- Extract time-domain data and calculate the sample frequency
- Compute and plot PSD data
- Fit frequency peaks and extract physical properties: radius, mass, damping, etc.
- Save analysis results into structured CSV tables

Directory Structure
-------------------
Expected folders (create them if missing):
- `Output/` — CSV tables (e.g., `master_table_manual.csv`, `master_table_auto.csv`, `master_table_hybrid.csv`)

Installation
------------
Required Python packages (install with pip):

pip install numpy pandas matplotlib scipy tk optoanalysis

also need pip install RTxReadBin-1.0-py3-none-any.whl
source this file from the group server, a group member or online

Overview - NN_peak_pred.py
--------

The core function:

    f1, f2, f3 = extract_psd_model(data)

- Takes in a `data` object (from `optoanalysis`)
- Extracts the PSD, preprocesses it
- Uses a trained neural network to predict the three dominant peak frequencies in Hz

--------------------------------------------------
Prerequisites
-------------

Python Packages:

    pip install numpy scipy joblib tensorflow

Files Required:

The following model and scalers must be in the same directory:

- peak_predictor_model_tuned.keras – Trained TensorFlow/Keras model
- x_scaler_tuned.pkl – Scikit-learn scaler for input (PSD)
- y_scaler_tuned.pkl – Scikit-learn scaler for output (frequencies)

--------------------------------------------------
Function Description
--------------------

extract_psd_model(data)

Inputs:
- `data`: an object with a `.get_PSD()` method returning `(freq, psd)` (e.g., from `optoanalysis.load_voltage_data(...)`)

Process:
- PSD is filtered to frequencies below 500 kHz (MAX_FREQ)
- Log-scaled and resampled to 512 points (FIXED_PSD_LENGTH)
- Input vector is scaled with `x_scaler_tuned`
- Model predicts scaled peak frequencies
- Output is inverse-transformed with `y_scaler_tuned`

Returns:
- `f1`, `f2`, `f3`: the three predicted peak frequencies in Hz

--------------------------------------------------
Notes
-----

- This model is intended for peak detection in levitated particle signal analysis.
- Ensure the PSD length and max frequency match the values used during model training.
- Model accuracy may degrade if the input PSD characteristics differ significantly from training data.

--------------------------------------------------