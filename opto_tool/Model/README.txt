NN_model.ipynb - README
===========================================

Overview
--------
This script trains a neural network model to predict the three dominant peak frequencies from a PSD (Power Spectral Density) derived from experimental voltage time-series data. It leverages TensorFlow/Keras, Scikit-learn, and Keras Tuner to perform model selection, training, evaluation, and saving.

The final trained model and scalers are saved as:
- `peak_predictor_model_tuned.keras`
- `x_scaler_tuned.pkl`
- `y_scaler_tuned.pkl`

Inputs
------
- `manual_peaks.csv`: Contains file paths and manually labeled peak frequencies.
- `.bin` or `.trc` files: Raw voltage data from oscilloscopes (R&S or LeCroy).

Output
------
- Trained model file
- Training/validation plots
- Scaler files for preprocessing
- Terminal output with MAE and R² scores

Steps Performed
---------------
1. **Extract PSD Features**:
   - Loads voltage data, computes PSD, applies log scale
   - Filters frequencies below 500 kHz
   - Resamples PSD to a fixed length of 512

2. **Load and Filter Labels**:
   - Reads labeled frequencies from `manual_peaks.csv`
   - Keeps only rows marked "Easy fit"

3. **Preprocessing**:
   - Splits into training and test sets
   - Scales features (X) and labels (y)

4. **Hyperparameter Tuning**:
   - Defines a Keras HyperModel with tunable units, dropout, layers, and learning rate
   - Uses Hyperband tuner to find best architecture

5. **Model Training**:
   - Trains the best model using early stopping and learning rate reduction
   - Further trains the selected model (optional)

6. **Evaluation**:
   - Predicts on test data
   - Reports unscaled MAE and R² score

7. **Model Saving**:
   - Saves trained model and scalers

8. **Plotting**:
   - Visualizes training vs. validation MAE over epochs

Requirements
------------
Python packages:
- numpy
- pandas
- scipy
- scikit-learn
- matplotlib
- tensorflow
- keras-tuner
- joblib

Install with:

    pip install numpy pandas scipy scikit-learn matplotlib tensorflow keras-tuner joblib optoanalysis
    also need pip install RTxReadBin-1.0-py3-none-any.whl
    source this file from the group server, a group member or online

File Structure
--------------
Place the following in the working directory:
- This training script
- `manual_peaks.csv`