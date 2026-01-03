# Module imports
import customtkinter
import opto_save
import NN_peak_pred
import re
import os

if __name__ == "__main__":
    # Setting the layout of the GUI
    customtkinter.set_appearance_mode("dark")
    customtkinter.set_default_color_theme("green")
    root = customtkinter.CTk()
    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()
    root.geometry("%dx%d" % (width, height))
    root.resizable(True, True)
    root.tk.call('tk', 'scaling', 1.0)
    root.state("normal")
    root.title("")
    switch_var_bin = customtkinter.StringVar(value="off")
    switch_var_csv = customtkinter.StringVar(value="off")
    file_switch = customtkinter.StringVar(value="off")
    root.grid_columnconfigure(10, weight=1)
    root.grid_rowconfigure(10, weight=1)

    # Setting the program title
    logo_label = customtkinter.CTkLabel(master=root, text="Welcome to the Optoanalysis Tool v3.0", font=customtkinter.CTkFont(size=30, weight="bold"))
    logo_label.grid(row=0, column=0, padx=20, pady=(20, 10), rowspan=2, columnspan=11)

    # Setting up the tabs for future expandability
    tabview = customtkinter.CTkTabview(root, width=width, height=height)
    tabview.grid(row=2, column=0, padx=(20, 0), pady=(20, 0), columnspan=11, rowspan=10)
    tabview.add("Manual Optoanalysis")
    tabview.add("Auto Optoanalysis")
    tabview.add("Hybrid Optoanalysis")
    tabview.tab("Manual Optoanalysis").grid_columnconfigure(0, weight=1)
    tabview.tab("Auto Optoanalysis").grid_columnconfigure(0, weight=1)
    tabview.tab("Hybrid Optoanalysis").grid_columnconfigure(0, weight=1)

    # Creating a scrollable frame
    scroll_frame_manual = customtkinter.CTkScrollableFrame(tabview.tab("Manual Optoanalysis"), height=height-300)
    scroll_frame_manual.grid(row=3, column=0, padx=(2, 0), pady=(20, 0), sticky="nsew")
    scroll_frame_manual.grid_columnconfigure(20, weight=1)
    scroll_frame_manual.grid_rowconfigure(50, weight=1)

    # Creating a scrollable frame
    scroll_frame_auto = customtkinter.CTkScrollableFrame(tabview.tab("Auto Optoanalysis"), height=height-300)
    scroll_frame_auto.grid(row=3, column=0, padx=(2, 0), pady=(20, 0), sticky="nsew")
    scroll_frame_auto.grid_columnconfigure(20, weight=1)
    scroll_frame_auto.grid_rowconfigure(50, weight=1)

    # Creating a scrollable frame
    scroll_frame_hybrid = customtkinter.CTkScrollableFrame(tabview.tab("Hybrid Optoanalysis"), height=height-300)
    scroll_frame_hybrid.grid(row=3, column=0, padx=(2, 0), pady=(20, 0), sticky="nsew")
    scroll_frame_hybrid.grid_columnconfigure(20, weight=1)
    scroll_frame_hybrid.grid_rowconfigure(50, weight=1)

    def extract_pressure(filename: str) -> str:
        """
        Extracts the pressure value in scientific notation from the given filename,
        but only if it matches the required format:
        YYYYMMDD_Particle#_Pr_order±##_magnitude#_##_time######.Wfm.bin
        
        Examples of valid filenames:
        20230815_Particle2_Pr_order02_magnitude3_45_time123456.Wfm.bin
        20230815_Particle2_Pr_order-01_magnitude3_45_time123456.Wfm.bin
        """
        # Regex for full filename validation (allow negative order)
        pattern = r"^\d{8}_Particle\d+_Pr_order-?\d{2}_magnitude\d+_\d+_time\d{6}\.Wfm\.bin$"
        
        if not re.match(pattern, filename):
            raise ValueError("Filename does not match expected format")
        
        # Extract exponent (allow negative sign)
        order_match = re.search(r"Pr_order(-?\d{2})", filename)
        # Extract coefficient parts
        mag_match = re.search(r"magnitude(\d+)_(\d+)", filename)
        
        if not order_match or not mag_match:
            raise ValueError("Could not parse coefficient or exponent")
        
        exponent = int(order_match.group(1))  # handles negative numbers too
        coefficient = f"{mag_match.group(1)}.{mag_match.group(2)}"
        
        return f"{coefficient}e{exponent}"


    # Function to plot the R&S .csv PSD using the particular oscilloscope parameters
    # Note - change these parameters depending on your settings
    def plot_csv_PSD(scroll_frame):
        global file_path
        file_path = opto_save.get_file()
        placeholder_box = customtkinter.CTkEntry(scroll_frame, width = 600, height = 28)
        placeholder_box.grid(row=6, column=0, padx=20, pady=(20, 10), columnspan=1)
        placeholder_box.insert(0, file_path[0])
        placeholder_box.configure(state="disabled")
        time_start = -0.249992
        time_stop = 0.250008
        signal_record_length = 5000000
        data = opto_save.get_csv_data(file_path[0], time_start, time_stop, signal_record_length)
        opto_save.plot_default_PSD(data, scroll_frame, file_path[0])        
        return
    
    # Function to plot the R&S .bin PSD
    def plot_bin_PSD(scroll_frame):
        global file_path
        file_path = opto_save.get_file()

        # show the file path
        placeholder_box = customtkinter.CTkEntry(scroll_frame, width=600, height=28)
        placeholder_box.grid(row=6, column=0, padx=20, pady=(20, 10), columnspan=1)
        placeholder_box.insert(0, file_path[0])
        placeholder_box.configure(state="disabled")

        # load and plot data
        data = opto_save.get_bin_data(file_path[0])
        opto_save.plot_default_PSD(data, scroll_frame, file_path[0])

        # extract and insert pressure
        try:
            filename = os.path.basename(file_path[0])
            pressure = extract_pressure(filename)

            # Decide which pressure_box to use based on scroll_frame
            if scroll_frame is scroll_frame_manual:
                target_box = pressure_box
            elif scroll_frame is scroll_frame_auto:
                target_box = pressure_box2
            elif scroll_frame is scroll_frame_hybrid:
                target_box = pressure_box3
            else:
                target_box = None

            if target_box:
                target_box.delete(0, "end")        # clear any previous text
                target_box.insert(0, pressure)    # insert new pressure value

        except ValueError:
            print("Wrong file format")
            pass
        return

    # Function to plot the R&S .bin PSD
    def plot_trc_PSD(scroll_frame):
        global file_path
        file_path = opto_save.get_file()
        placeholder_box = customtkinter.CTkEntry(scroll_frame, width = 600, height = 28)
        placeholder_box.grid(row=6, column=0, padx=20, pady=(20, 10), columnspan=1)
        placeholder_box.insert(0, file_path[0])
        placeholder_box.configure(state="disabled")
        data = opto_save.get_trc_data(file_path[0])
        opto_save.plot_default_PSD(data, scroll_frame, file_path[0])        
        return
    
    # Function to calculate the parameters using the entered data
    def calculate_parameters():
        particle_type = particle_box.get()
        pressure = pressure_box.get()
        f1_rough = f1_rough_box.get()
        f2_rough = f2_rough_box.get()
        f3_rough = f3_rough_box.get()
        easy_peaks = read_peaks_box.get()
        data = None

        # Checking the file type
        if file_path[0].endswith(".csv"):
            time_start = -0.249992
            time_stop = 0.250008
            signal_record_length = 5000000
            data = opto_save.get_csv_data(file_path[0], time_start, time_stop, signal_record_length)
        elif file_path[0].endswith(".bin"):
            data = opto_save.get_bin_data(file_path[0])
        elif file_path[0].endswith(".trc"):
            data = opto_save.get_trc_data(file_path[0])
        else:
            print("Unsupported file type. Please use .csv, .bin or .trc.")
            return

        # Checking that the entered data is reasonable
        try:
            peak_freq = [float(f1_rough), float(f2_rough), float(f3_rough)]
            pressure = float(pressure)
            pressure_error = 1
            if data is not None:
                opto_save.save_data(data, peak_freq, pressure, pressure_error, file_path, particle_type, easy_peaks)
            else:
                print("Data is None. Unable to save.")
        except Exception as e:
            print(f"Error in processing: {e}")

    # Function to calculate the parameters using the auto_model
    def auto_opto():
        particle_type = particle_box2.get()
        pressure = pressure_box2.get()        
        data = None

        # Checking the file type
        if file_path[0].endswith(".csv"):
            time_start = -0.249992
            time_stop = 0.250008
            signal_record_length = 5000000
            data = opto_save.get_csv_data(file_path[0], time_start, time_stop, signal_record_length)
        elif file_path[0].endswith(".bin"):
            data = opto_save.get_bin_data(file_path[0])
        elif file_path[0].endswith(".trc"):
            data = opto_save.get_trc_data(file_path[0])
        else:
            print("Unsupported file type. Please use .csv, .bin or .trc.")
            return
        
        f1_rough, f2_rough, f3_rough = NN_peak_pred.extract_psd_model(data)

        f1_no_dec = int(f1_rough)
        f2_no_dec = int(f2_rough)
        f3_no_dec = int(f3_rough)

        f1_kHz = f1_no_dec / 1000
        f2_kHz = f2_no_dec / 1000
        f3_kHz = f3_no_dec / 1000

        placeholder_box = customtkinter.CTkEntry(scroll_frame_auto, width = 600, height = 28)
        placeholder_box.grid(row=10, column=0, padx=20, pady=(20, 10), columnspan=1)
        placeholder_box.insert(0, f"f1 predicted: {f1_kHz} kHz")
        placeholder_box.configure(state="disabled")

        placeholder_box = customtkinter.CTkEntry(scroll_frame_auto, width = 600, height = 28)
        placeholder_box.grid(row=11, column=0, padx=20, pady=(20, 10), columnspan=1)
        placeholder_box.insert(0, f"f2 predicted: {f2_kHz} kHz")
        placeholder_box.configure(state="disabled")

        placeholder_box = customtkinter.CTkEntry(scroll_frame_auto, width = 600, height = 28)
        placeholder_box.grid(row=12, column=0, padx=20, pady=(20, 10), columnspan=1)
        placeholder_box.insert(0, f"f3 predicted: {f3_kHz} kHz")
        placeholder_box.configure(state="disabled")

        # Checking that the entered data is reasonable
        try:
            peak_freq = [float(f1_rough), float(f2_rough), float(f3_rough)]
            pressure = float(pressure)
            pressure_error = 1
            if data is not None:
                opto_save.save_data_auto(data, peak_freq, pressure, pressure_error, file_path, particle_type)
            else:
                print("Data is None. Unable to save.")
        except Exception as e:
            print(f"Error in processing: {e}")
    
    def calculate_parameters_hybrid():
        global placeholder_box_f1, placeholder_box_f2, placeholder_box_f3

        data = None

        # Determine data from file
        if file_path[0].endswith(".csv"):
            time_start = -0.249992
            time_stop = 0.250008
            signal_record_length = 5000000
            data = opto_save.get_csv_data(file_path[0], time_start, time_stop, signal_record_length)
        elif file_path[0].endswith(".bin"):
            data = opto_save.get_bin_data(file_path[0])
        elif file_path[0].endswith(".trc"):
            data = opto_save.get_trc_data(file_path[0])
        else:
            print("Unsupported file type. Please use .csv, .bin or .trc.")
            return

        particle_type = particle_box3.get()
        pressure_str = pressure_box3.get()
        f1_str = placeholder_box_f1.get()
        f2_str = placeholder_box_f2.get()
        f3_str = placeholder_box_f3.get()

        print(f"DEBUG: f1={f1_str}, f2={f2_str}, f3={f3_str}, pressure={pressure_str}")

        try:
            # Check if fields are empty
            if not all([f1_str.strip(), f2_str.strip(), f3_str.strip(), pressure_str.strip()]):
                raise ValueError("One or more input fields are empty.")

            # Convert strings to float
            f1 = float(f1_str)
            f2 = float(f2_str)
            f3 = float(f3_str)
            pressure = float(pressure_str)

            peak_freq = [f1*1000, f2*1000, f3*1000]
            pressure_error = 1  # static for now

            if data is not None:
                opto_save.save_data_hybrid(data, peak_freq, pressure, pressure_error, file_path, particle_type)
            else:
                print("Data is None. Unable to save.")
        except Exception as e:
            print(f"Error in processing: {e}")


    # Function to calculate the parameters using the auto_model
    def hybrid_opto():
        global placeholder_box_f1, placeholder_box_f2, placeholder_box_f3

        data = None

        # Determine data from file
        if file_path[0].endswith(".csv"):
            time_start = -0.249992
            time_stop = 0.250008
            signal_record_length = 5000000
            data = opto_save.get_csv_data(file_path[0], time_start, time_stop, signal_record_length)
        elif file_path[0].endswith(".bin"):
            data = opto_save.get_bin_data(file_path[0])
        elif file_path[0].endswith(".trc"):
            data = opto_save.get_trc_data(file_path[0])
        else:
            print("Unsupported file type. Please use .csv, .bin or .trc.")
            return

        # Use model to extract frequencies
        f1_rough, f2_rough, f3_rough = NN_peak_pred.extract_psd_model(data)

        f1_kHz = int(f1_rough) / 1000
        f2_kHz = int(f2_rough) / 1000
        f3_kHz = int(f3_rough) / 1000

        # Insert into existing boxes
        for box, value in zip([placeholder_box_f1, placeholder_box_f2, placeholder_box_f3], [f1_kHz, f2_kHz, f3_kHz]):
            box.configure(state="normal")
            box.delete(0, "end")
            box.insert(0, f"{value}")
            box.configure(state="normal")

    # Setting up the scaling of the GUI
    def change_scaling_event(new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)

    # Button for calling the plot_csv_PSD function
    button = customtkinter.CTkButton(scroll_frame_auto, text = "Plot R&S .csv PSD", command=lambda: plot_csv_PSD(scroll_frame_auto))
    button.grid(row=3, column=0, padx=20, pady=(20, 10))

    # Button for calling the plot_bin_PSD function
    button = customtkinter.CTkButton(scroll_frame_auto, text = "Plot R&S .bin PSD", command=lambda: plot_bin_PSD(scroll_frame_auto))
    button.grid(row=4, column=0, padx=20, pady=(20, 10))

    # Button for calling the plot_trc_PSD function
    button = customtkinter.CTkButton(scroll_frame_auto, text = "Plot LeCroy .trc PSD", command=lambda: plot_trc_PSD(scroll_frame_auto))
    button.grid(row=5, column=0, padx=20, pady=(20, 10))

    # Button for calling the plot_csv_PSD function
    button = customtkinter.CTkButton(scroll_frame_manual, text = "Plot R&S .csv PSD", command=lambda: plot_csv_PSD(scroll_frame_manual))
    button.grid(row=3, column=0, padx=20, pady=(20, 10))

    # Button for calling the plot_bin_PSD function
    button = customtkinter.CTkButton(scroll_frame_manual, text = "Plot R&S .bin PSD", command=lambda: plot_bin_PSD(scroll_frame_manual))
    button.grid(row=4, column=0, padx=20, pady=(20, 10))

    # Button for calling the plot_trc_PSD function
    button = customtkinter.CTkButton(scroll_frame_manual, text = "Plot LeCroy .trc PSD", command=lambda: plot_trc_PSD(scroll_frame_manual))
    button.grid(row=5, column=0, padx=20, pady=(20, 10))

    # Button for calling the plot_csv_PSD function
    button = customtkinter.CTkButton(scroll_frame_hybrid, text = "Plot R&S .csv PSD", command=lambda: plot_csv_PSD(scroll_frame_hybrid))
    button.grid(row=3, column=0, padx=20, pady=(20, 10))

    # Button for calling the plot_bin_PSD function
    button = customtkinter.CTkButton(scroll_frame_hybrid, text = "Plot R&S .bin PSD", command=lambda: plot_bin_PSD(scroll_frame_hybrid))
    button.grid(row=4, column=0, padx=20, pady=(20, 10))

    # Button for calling the plot_trc_PSD function
    button = customtkinter.CTkButton(scroll_frame_hybrid, text = "Plot LeCroy .trc PSD", command=lambda: plot_trc_PSD(scroll_frame_hybrid))
    button.grid(row=5, column=0, padx=20, pady=(20, 10))

    # Creating a blank plot as a placeholder
    opto_save.blank_plot(scroll_frame_manual)

    # Creating a blank plot as a placeholder
    opto_save.blank_plot(scroll_frame_auto)

    # Creating a blank plot as a placeholder
    opto_save.blank_plot(scroll_frame_hybrid)

    # Placeholder box for the file path
    placeholder_box = customtkinter.CTkEntry(scroll_frame_manual, width = 600, height = 28)
    placeholder_box.grid(row=6, column=0, padx=20, pady=(20, 10), columnspan=1)
    placeholder_box.configure(state="disabled")

    # Placeholder box for the file path
    placeholder_box = customtkinter.CTkEntry(scroll_frame_auto, width = 600, height = 28)
    placeholder_box.grid(row=6, column=0, padx=20, pady=(20, 10), columnspan=1)
    placeholder_box.configure(state="disabled")

    # Placeholder box for the file path
    placeholder_box = customtkinter.CTkEntry(scroll_frame_hybrid, width = 600, height = 28)
    placeholder_box.grid(row=6, column=0, padx=20, pady=(20, 10), columnspan=1)
    placeholder_box.configure(state="disabled")

    # Box for the entry of the pressure value
    pressure_box = customtkinter.CTkEntry(scroll_frame_manual, placeholder_text="Enter the pressure (mbar)", width = 600, height = 28)
    pressure_box.grid(row=7, column=0, padx=20, pady=(20, 10), columnspan=1)     

    # Box for the entry of the pressure value
    pressure_box2 = customtkinter.CTkEntry(scroll_frame_auto, placeholder_text="Enter the pressure (mbar)", width = 600, height = 28)
    pressure_box2.grid(row=7, column=0, padx=20, pady=(20, 10), columnspan=1) 

    # Box for the entry of the pressure value
    pressure_box3 = customtkinter.CTkEntry(scroll_frame_hybrid, placeholder_text="Enter the pressure (mbar)", width = 600, height = 28)
    pressure_box3.grid(row=7, column=0, padx=20, pady=(20, 10), columnspan=1) 

    # Label text for Enter the particle type
    particle_box_label = customtkinter.CTkLabel(scroll_frame_manual, text="Enter the particle type:", anchor="w")
    particle_box_label.grid(row=8, column=0, padx=20, pady=(20, 10), columnspan=1)

    # Label text for Enter the particle type
    particle_box_label = customtkinter.CTkLabel(scroll_frame_auto, text="Enter the particle type:", anchor="w")
    particle_box_label.grid(row=8, column=0, padx=20, pady=(20, 10), columnspan=1)

    # Label text for Enter the particle type
    particle_box_label = customtkinter.CTkLabel(scroll_frame_hybrid, text="Enter the particle type:", anchor="w")
    particle_box_label.grid(row=8, column=0, padx=20, pady=(20, 10), columnspan=1)

    # Dropdown box for the selection of particle type tested
    particle_box = customtkinter.CTkComboBox(scroll_frame_manual, values=["SiNP", "1000uM ZnCl2 SiNP", "25A 1000uM ZnCl2 SiNP", "25T 1000uM ZnCl2 SiNP", "20A/5T 1000uM ZnCl2 SiNP", "20T/5A 1000uM ZnCl2 SiNP", "13T/12A 1000uM ZnCl2 SiNP"])
    particle_box.grid(row=9, column=0, columnspan=1)

    # Dropdown box for the selection of particle type tested
    particle_box2 = customtkinter.CTkComboBox(scroll_frame_auto, values=["SiNP", "1000uM ZnCl2 SiNP", "25A 1000uM ZnCl2 SiNP", "25T 1000uM ZnCl2 SiNP", "20A/5T 1000uM ZnCl2 SiNP", "20T/5A 1000uM ZnCl2 SiNP", "13T/12A 1000uM ZnCl2 SiNP"])
    particle_box2.grid(row=9, column=0, columnspan=1)

    # Dropdown box for the selection of particle type tested
    particle_box3 = customtkinter.CTkComboBox(scroll_frame_hybrid, values=["SiNP", "1000uM ZnCl2 SiNP", "25A 1000uM ZnCl2 SiNP", "25T 1000uM ZnCl2 SiNP", "20A/5T 1000uM ZnCl2 SiNP", "20T/5A 1000uM ZnCl2 SiNP", "13T/12A 1000uM ZnCl2 SiNP"])
    particle_box3.grid(row=9, column=0, columnspan=1)

    # A button to run the calculate_parameters function
    button = customtkinter.CTkButton(scroll_frame_hybrid, text = "Get Estimate f1, f2, f3", command=hybrid_opto)
    button.grid(row=10, column=0, padx=20, pady=(20, 10))

    placeholder_box_f1 = customtkinter.CTkEntry(scroll_frame_hybrid, width = 600, height = 28)
    placeholder_box_f1.grid(row=11, column=0, padx=20, pady=(20, 10), columnspan=1)
    placeholder_box_f1.insert(0, "f1 frequency (kHz)")
    placeholder_box_f1.configure(state="disabled")

    placeholder_box_f2 = customtkinter.CTkEntry(scroll_frame_hybrid, width = 600, height = 28)
    placeholder_box_f2.grid(row=12, column=0, padx=20, pady=(20, 10), columnspan=1)
    placeholder_box_f2.insert(0, "f2 frequency (kHz)")
    placeholder_box_f2.configure(state="disabled")

    placeholder_box_f3 = customtkinter.CTkEntry(scroll_frame_hybrid, width = 600, height = 28)
    placeholder_box_f3.grid(row=13, column=0, padx=20, pady=(20, 10), columnspan=1)
    placeholder_box_f3.insert(0, "f3 frequency (kHz)")
    placeholder_box_f3.configure(state="disabled")    

    # A button to run the calculate_parameters function
    button = customtkinter.CTkButton(scroll_frame_hybrid, text = "Calculate Parameters", command=calculate_parameters_hybrid)
    button.grid(row=14, column=0, padx=20, pady=(20, 10))

    placeholder_box = customtkinter.CTkEntry(scroll_frame_auto, width = 600, height = 28)
    placeholder_box.grid(row=10, column=0, padx=20, pady=(20, 10), columnspan=1)
    placeholder_box.insert(0, "f1 frequency (kHz)")
    placeholder_box.configure(state="disabled")

    placeholder_box = customtkinter.CTkEntry(scroll_frame_auto, width = 600, height = 28)
    placeholder_box.grid(row=11, column=0, padx=20, pady=(20, 10), columnspan=1)
    placeholder_box.insert(0, "f2 frequency (kHz)")
    placeholder_box.configure(state="disabled")

    placeholder_box = customtkinter.CTkEntry(scroll_frame_auto, width = 600, height = 28)
    placeholder_box.grid(row=12, column=0, padx=20, pady=(20, 10), columnspan=1)
    placeholder_box.insert(0, "f3 frequency (kHz)")
    placeholder_box.configure(state="disabled")

    # A button to run the calculate_parameters function
    button = customtkinter.CTkButton(scroll_frame_auto, text = "Run Auto Optoanalysis", command=auto_opto)
    button.grid(row=13, column=0, padx=20, pady=(20, 10))

    # Box for the entry of the rough f1 peak frequency
    f1_rough_box = customtkinter.CTkEntry(scroll_frame_manual, placeholder_text="Enter the f1 Rough Peak Frequency (kHz)", width = 600, height = 28)
    f1_rough_box.grid(row=10, column=0, padx=20, pady=(20, 10), columnspan=1)

    # Box for the entry of the rough f2 peak frequency
    f2_rough_box = customtkinter.CTkEntry(scroll_frame_manual, placeholder_text="Enter the f2 Rough Peak Frequency (kHz)", width = 600, height = 28)
    f2_rough_box.grid(row=11, column=0, padx=20, pady=(20, 10), columnspan=1)

    # Box for the entry of the rough f2 peak frequency
    f3_rough_box = customtkinter.CTkEntry(scroll_frame_manual, placeholder_text="Enter the f3 Rough Peak Frequency (kHz)", width = 600, height = 28)
    f3_rough_box.grid(row=12, column=0, padx=20, pady=(20, 10), columnspan=1)

    # Text label saying Are the PSD peaks easy to fit?
    read_peaks_box_label = customtkinter.CTkLabel(scroll_frame_manual, text="Are the PSD peaks easy to fit?", anchor="w")
    read_peaks_box_label.grid(row=13, column=0, padx=20, pady=(20, 10), columnspan=1)

    # Dropdown box for Yes/No if the PSD peaks are easy to fit
    read_peaks_box = customtkinter.CTkComboBox(scroll_frame_manual, values=["Yes", "No"])
    read_peaks_box.grid(row=14, column=0, columnspan=1)
    
    # A button to run the calculate_parameters function
    button = customtkinter.CTkButton(scroll_frame_manual, text = "Calculate Parameters", command=calculate_parameters)
    button.grid(row=15, column=0, padx=20, pady=(20, 10))

    # Setting up the GUI scaling as a dropdown list
    optionmenu_var = customtkinter.StringVar(value="100%")
    root.scaling_label = customtkinter.CTkLabel(master=root, text="UI Scaling:", anchor="w")
    root.scaling_label.grid(row=0, column=0, padx=20, pady=(10, 0))
    root.scaling_optionemenu = customtkinter.CTkOptionMenu(master=root, values=["50%", "60%", "70%", "80%", "90%", "100%", "110%", "120%", "130%", "140%", "150%"],
                                                               command=change_scaling_event, variable=optionmenu_var)
    root.scaling_optionemenu.grid(row=1, column=0, padx=20, pady=(10, 20))

    # Ending the customtkinter root main loop
    root.mainloop()