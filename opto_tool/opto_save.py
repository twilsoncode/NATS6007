# Module imports
import tkinter as tk
from tkinter.filedialog import askopenfilenames
from RS_RTxReadBin import RTxReadBin
import optoanalysis as oa
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
from matplotlib.figure import Figure
from matplotlib.ticker import MultipleLocator

# Opening a TK window to get the file path
def get_file():    
    root = tk.Tk()
    root.withdraw()
    file_list = askopenfilenames()    
    root.destroy()
    return file_list

# Function to get the R&S .bin data
def get_bin_data(file):
    y, time_data, save_info = RTxReadBin(file)
    voltages = y[:, 0, 0]
    time_start = save_info["XStart"]
    time_stop = save_info["XStop"]
    signal_record_length = save_info["SignalRecordLength"]
    time_step = (time_stop - time_start) / signal_record_length
    sample_frequency = 1 / time_step
    data = oa.load_voltage_data(voltages, SampleFreq = sample_frequency, timeStart = time_start)
    return data

# Function to get the R&S .bin data
def get_trc_data(file):
    data = oa.load_data(file)
    return data

# Function to get the R&S .csv data
def get_csv_data(file, time_start, time_stop, signal_record_length):
    data_frame = pd.read_csv(file)
    time_step = (time_stop - time_start) / signal_record_length
    sample_frequency = 1 / time_step
    data = oa.load_voltage_data(data_frame[data_frame.columns[1]], SampleFreq = sample_frequency, timeStart = time_start)
    return data

# Function to plot the PSD in the GUI
def plot_default_PSD(data):
    freq, psd = data.get_PSD()
    data.plot_PSD([0, 500])
    plt.figure(figsize=[8, 5])
    plt.plot(freq/1e3, psd)
    plt.xlim(0, 500)
    plt.yscale("log")
    plt.xlabel("Frequency (kHz)")
    plt.ylabel("$S_{xx}$ ($V^2/Hz$)")
    plt.grid(True)
    return

# Function to save the data to master_table.csv
def save_data(data, peak_freq, pressure, pressure_error, file, particle_type, easy_peaks):
    master_csv_path = "Output/master_table_manual.csv" #change master table save path!!
    master_csv = pd.read_csv(master_csv_path)
    master_csv.head()
    A = [] # The 'A' parameter as stated in Jamie Vovrosh's thesis (page 44)
    Gamma = [] # Damping
    R = [] # Radius
    M = [] # Mass
    ConvFactorZ = [] # Conversion Factor - volts to meters
    fit_freq = [] # Peak frequencies    
    for freq in peak_freq:
        W_temp, A_temp, G_temp, fig, ax = data.get_fit_auto(freq * 1000,plot_initial=False)
        R_temp, M_temp, ConvFactorZ_temp = data.extract_parameters(pressure, pressure_error*0.01) 
        fit_freq.append(W_temp/(2*np.pi))
        A.append(A_temp)
        Gamma.append(G_temp)
        R.append(R_temp)
        M.append(M_temp)
        ConvFactorZ.append(ConvFactorZ_temp)
    
    # Creating a dictionary with the new row of particle data
    new_data = {
        "File Path": file[0],
        "Particle Type": particle_type,
        "Pressure (mbar)": pressure,
        "Are the PSD peaks easy to fit?": easy_peaks,
        "f1 Rough Peak Frequency (kHz)": peak_freq[0],
        "f2 Rough Peak Frequency (kHz)": peak_freq[1],
        "f3 Rough Peak Frequency (kHz)": peak_freq[2],
        "f1 Peak Frequency (Hz)": fit_freq[0],
        "f2 Peak Frequency (Hz)": fit_freq[1],
        "f3 Peak Frequency (Hz)": fit_freq[2],
        "f1 Radius (m)": R[0],
        "f2 Radius (m)": R[1],
        "f3 Radius (m)": R[2],
        "Assumed Density (kg m^-3)": 1800,
        "f1 Mass (kg)": M[0],
        "f2 Mass (kg)": M[1],
        "f3 Mass (kg)": M[2],
        "f1 Damping (Hz)": Gamma[0],
        "f2 Damping (Hz)": Gamma[1],
        "f3 Damping (Hz)": Gamma[2],
        "f1 A Parameter (V^2 Hz^3)": A[0],
        "f2 A Parameter (V^2 Hz^3)": A[1],
        "f3 A Parameter (V^2 Hz^3)": A[2],
        "f1 Conversion Factor (V m^-1)": ConvFactorZ[0],
        "f2 Conversion Factor (V m^-1)": ConvFactorZ[1],
        "f3 Conversion Factor (V m^-1)": ConvFactorZ[2],
    }

    new_data_df = pd.DataFrame([new_data])

    # Ensuring that duplicate data are not created for each particle file
    if new_data["File Path"] not in master_csv["File Path"].values:
        master_csv = pd.concat([master_csv, new_data_df], ignore_index=True)
        master_csv.to_csv("Output/master_table_manual.csv", index=False)
    else:
        print("This is a duplicate piece of data")
    return

# Function to save the data to master_table.csv
def save_data_auto(data, peak_freq, pressure, pressure_error, file, particle_type):
    master_csv_path = "Output/master_table_auto.csv" #change master table save path!!
    master_csv = pd.read_csv(master_csv_path)
    master_csv.head()
    easy_peaks = "Yes"
    A = [] # The 'A' parameter as stated in Jamie Vovrosh's thesis (page 44)
    Gamma = [] # Damping
    R = [] # Radius
    M = [] # Mass
    ConvFactorZ = [] # Conversion Factor - volts to meters
    fit_freq = [] # Peak frequencies    
    for freq in peak_freq:
        W_temp, A_temp, G_temp, fig, ax = data.get_fit_auto(freq,plot_initial=False)
        R_temp, M_temp, ConvFactorZ_temp = data.extract_parameters(pressure, pressure_error*0.01) 
        fit_freq.append(W_temp/(2*np.pi))
        A.append(A_temp)
        Gamma.append(G_temp)
        R.append(R_temp)
        M.append(M_temp)
        ConvFactorZ.append(ConvFactorZ_temp)
    
    # Creating a dictionary with the new row of particle data
    new_data = {
        "File Path": file[0],
        "Particle Type": particle_type,
        "Pressure (mbar)": pressure,
        "Are the PSD peaks easy to fit?": easy_peaks,
        "f1 Rough Peak Frequency (kHz)": peak_freq[0],
        "f2 Rough Peak Frequency (kHz)": peak_freq[1],
        "f3 Rough Peak Frequency (kHz)": peak_freq[2],
        "f1 Peak Frequency (Hz)": fit_freq[0],
        "f2 Peak Frequency (Hz)": fit_freq[1],
        "f3 Peak Frequency (Hz)": fit_freq[2],
        "f1 Radius (m)": R[0],
        "f2 Radius (m)": R[1],
        "f3 Radius (m)": R[2],
        "Assumed Density (kg m^-3)": 1800,
        "f1 Mass (kg)": M[0],
        "f2 Mass (kg)": M[1],
        "f3 Mass (kg)": M[2],
        "f1 Damping (Hz)": Gamma[0],
        "f2 Damping (Hz)": Gamma[1],
        "f3 Damping (Hz)": Gamma[2],
        "f1 A Parameter (V^2 Hz^3)": A[0],
        "f2 A Parameter (V^2 Hz^3)": A[1],
        "f3 A Parameter (V^2 Hz^3)": A[2],
        "f1 Conversion Factor (V m^-1)": ConvFactorZ[0],
        "f2 Conversion Factor (V m^-1)": ConvFactorZ[1],
        "f3 Conversion Factor (V m^-1)": ConvFactorZ[2],
    }

    new_data_df = pd.DataFrame([new_data])

    # Ensuring that duplicate data are not created for each particle file
    if new_data["File Path"] not in master_csv["File Path"].values:
        master_csv = pd.concat([master_csv, new_data_df], ignore_index=True)
        master_csv.to_csv("Output/master_table_auto.csv", index=False)
    else:
        print("This is a duplicate piece of data")
    return

# Function to save the data to master_table.csv
def save_data_hybrid(data, peak_freq, pressure, pressure_error, file, particle_type):
    master_csv_path = "Output/master_table_hybrid.csv" #change master table save path!!
    master_csv = pd.read_csv(master_csv_path)
    master_csv.head()
    easy_peaks = "Yes"
    A = [] # The 'A' parameter as stated in Jamie Vovrosh's thesis (page 44)
    Gamma = [] # Damping
    R = [] # Radius
    M = [] # Mass
    ConvFactorZ = [] # Conversion Factor - volts to meters
    fit_freq = [] # Peak frequencies    
    for freq in peak_freq:
        W_temp, A_temp, G_temp, fig, ax = data.get_fit_auto(freq,plot_initial=False)
        R_temp, M_temp, ConvFactorZ_temp = data.extract_parameters(pressure, pressure_error*0.01) 
        fit_freq.append(W_temp/(2*np.pi))
        A.append(A_temp)
        Gamma.append(G_temp)
        R.append(R_temp)
        M.append(M_temp)
        ConvFactorZ.append(ConvFactorZ_temp)
    
    # Creating a dictionary with the new row of particle data
    new_data = {
        "File Path": file[0],
        "Particle Type": particle_type,
        "Pressure (mbar)": pressure,
        "Are the PSD peaks easy to fit?": easy_peaks,
        "f1 Rough Peak Frequency (kHz)": peak_freq[0],
        "f2 Rough Peak Frequency (kHz)": peak_freq[1],
        "f3 Rough Peak Frequency (kHz)": peak_freq[2],
        "f1 Peak Frequency (Hz)": fit_freq[0],
        "f2 Peak Frequency (Hz)": fit_freq[1],
        "f3 Peak Frequency (Hz)": fit_freq[2],
        "f1 Radius (m)": R[0],
        "f2 Radius (m)": R[1],
        "f3 Radius (m)": R[2],
        "Assumed Density (kg m^-3)": 1800,
        "f1 Mass (kg)": M[0],
        "f2 Mass (kg)": M[1],
        "f3 Mass (kg)": M[2],
        "f1 Damping (Hz)": Gamma[0],
        "f2 Damping (Hz)": Gamma[1],
        "f3 Damping (Hz)": Gamma[2],
        "f1 A Parameter (V^2 Hz^3)": A[0],
        "f2 A Parameter (V^2 Hz^3)": A[1],
        "f3 A Parameter (V^2 Hz^3)": A[2],
        "f1 Conversion Factor (V m^-1)": ConvFactorZ[0],
        "f2 Conversion Factor (V m^-1)": ConvFactorZ[1],
        "f3 Conversion Factor (V m^-1)": ConvFactorZ[2],
    }

    new_data_df = pd.DataFrame([new_data])

    # Ensuring that duplicate data are not created for each particle file
    if new_data["File Path"] not in master_csv["File Path"].values:
        master_csv = pd.concat([master_csv, new_data_df], ignore_index=True)
        master_csv.to_csv("Output/master_table_hybrid.csv", index=False)
    else:
        print("This is a duplicate piece of data")
    return

# Parameters used for the .csv data - use different parameters for your own oscilloscope settings
time_start = -0.249992
time_stop = 0.250008
signal_record_length = 5000000
pres_error = 1
master_csv_path = "Output/master_table_manual.csv"
master_csv = pd.read_csv(master_csv_path)
master_csv.head()

# Creating a blank canvas for the PSD plot
def blank_plot(root):
    fig = Figure(figsize = (10,8), dpi = 100)
    plot1 = fig.add_subplot(111)
    plot1.plot()
    plot1.set_title("PSD of the signal")
    plot1.set_xlabel("Frequency (kHz)")
    plot1.set_ylabel("$S_{xx}$ ($V^2/Hz$)")
    plot1.set_yscale("log")
    plot1.set_xbound(0, 500)
    plot1.xaxis.set_major_locator(MultipleLocator(20))
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()    
    canvas.get_tk_widget().grid(row=3, column=6, padx=20, pady=(20, 10), rowspan=11, columnspan=20, sticky="nsew")
    toolbar = NavigationToolbar2Tk(canvas, root, pack_toolbar = False)
    for widget in toolbar.winfo_children():
        if isinstance(widget, tk.Label):
            widget.config(font=("Helvetica", 30))
    toolbar.grid(row=14, column=6, padx=20, pady=(20, 10), rowspan=1, columnspan=20, sticky="nsew")
    toolbar.update()

# Plotting the PSD on a tkinter canvas
def plot_default_PSD(data, root, file):
    freq, psd = data.get_PSD()
    fig = Figure(figsize = (10,8), dpi = 100)
    plot1 = fig.add_subplot(111)
    plot1.plot(freq/1e3, psd)
    plot1.set_title("PSD of the signal")
    plot1.set_xlabel("Frequency (kHz)")
    plot1.set_ylabel("$S_{xx}$ ($V^2/Hz$)")
    plot1.set_yscale("log")
    plot1.set_xbound(0, 500)
    plot1.xaxis.set_major_locator(MultipleLocator(20))
    fig.savefig(file + ".png", format="png", dpi=500)
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()    
    canvas.get_tk_widget().grid(row=3, column=6, padx=20, pady=(20, 10), rowspan=11, columnspan=20, sticky="nsew")
    toolbar = NavigationToolbar2Tk(canvas, root, pack_toolbar = False)
    for widget in toolbar.winfo_children():
        if isinstance(widget, tk.Label):
            widget.config(font=("Helvetica", 30))
    toolbar.grid(row=14, column=6, padx=20, pady=(20, 10), rowspan=1, columnspan=20, sticky="nsew")
    toolbar.update()    