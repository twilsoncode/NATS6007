import numpy as np
import joblib
import tensorflow as tf
from scipy.signal import resample

FIXED_PSD_LENGTH = 512  # Make sure this matches training
MAX_FREQ = 500e3        # Upper frequency limit for PSD

def extract_psd_model(data):
    model = tf.keras.models.load_model("peak_predictor_model_tuned.keras")
    x_scaler = joblib.load("x_scaler_tuned.pkl")
    y_scaler = joblib.load("y_scaler_tuned.pkl")
    max_freq=MAX_FREQ
    
    freq, psd = data.get_PSD()

    # Filter and log scale
    mask = freq < max_freq
    psd = psd[mask]
    psd = np.log10(psd + 1e-12)

    # Resample to fixed length
    psd_vector = resample(psd, FIXED_PSD_LENGTH)
    psd_vector_scaled = x_scaler.transform(psd_vector.reshape(1, -1))
    pred_scaled = model.predict(psd_vector_scaled)
    pred_freqs = y_scaler.inverse_transform(pred_scaled)
    f1, f2, f3 = pred_freqs[0]
    return f1, f2, f3