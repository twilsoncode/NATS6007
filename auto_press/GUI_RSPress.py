import customtkinter
from ADCPi import ADCPi
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import RS_save_data  # Your custom module for saving data

# =============================================================================
# --- Constants ---
# =============================================================================

# --- Update Intervals ---
TEXT_UPDATE_INTERVAL_MS = 20   # How often to update text labels and check for triggers (in ms)
PLOT_UPDATE_INTERVAL_MS = 300  # How often to update the graph (in ms)
PLOT_DATA_POINTS = 60          # Number of data points to show on the graph (a 300ms * 60 = 18-second window)

# --- Detection ---
DETECTION_TOLERANCE = 0.05     # 5% tolerance for pressure matching (e.g., 1.05 and 0.95)

# --- Sensor Calibration ---
# TODO: Verify these values are correct for your setup
VOLTAGE_CALIBRATION_FACTOR = 1.977  # Factor for voltage divider (was 1.98)
# Pressure (mbar) = 10^((Voltage - OFFSET) / SLOPE) - From sensor datasheet
PRESSURE_CALC_OFFSET = 7.75
PRESSURE_CALC_SLOPE = 0.75

# --- ADC Configuration ---
ADC_ADDRESS_1 = 0x68
ADC_ADDRESS_2 = 0x69
ADC_BITRATE = 12
ADC_CHANNEL = 1  # ADC channel to read from

# --- GUI Colors ---
BORDER_COLOR_OFF = "#444444"
BORDER_COLOR_ON = "#ff0000"  # Red border when detection is active


# =============================================================================
# --- Global State Variables ---
# =============================================================================

# --- Live Data ---
current_voltage = 0.0
current_pressure = 0.0

# --- Target Pressures ---
pressure_list = []              # List of target pressures to trigger on
triggered_pressures = set()     # Set of pressures already triggered to avoid re-triggering
matched_labels = {}             # Dict to manage GUI widgets for matched pressures {pressure: (label, button)}

# --- Application State ---
detection_active = False        # Flag to enable/disable pressure detection
particle_number = 1             # Counter for particle samples

# --- Plotting Data ---
x_data_timestamps = []
y_data_voltage = []
y_data_pressure = []

# --- Tkinter Update Job IDs ---
# Initialized to None so on_closing() doesn't fail if app closes before loops start
text_update_job_id = None
plot_update_job_id = None


# =============================================================================
# --- Hardware Initialization ---
# =============================================================================
try:
    # Initialize the ADC Pi
    adc = ADCPi(ADC_ADDRESS_1, ADC_ADDRESS_2, ADC_BITRATE)
except Exception as e:
    print(f"CRITICAL: Error initializing ADCPi: {e}")
    print("--- RUNNING IN SIMULATION MODE ---")
    
    # Create a dummy adc object for simulation if ADCPi fails to init
    # This allows the GUI to run for testing without hardware.
    class DummyADCPi:
        def read_voltage(self, channel):
            # Simulate a voltage oscillating around a pressure of 5e-3 mbar
            base_v = (PRESSURE_CALC_OFFSET + PRESSURE_CALC_SLOPE * np.log10(5e-3))
            sim_v = base_v + (np.sin(datetime.now().timestamp()) * 0.05)
            return sim_v / VOLTAGE_CALIBRATION_FACTOR
    
    adc = DummyADCPi()


# =============================================================================
# --- Core Logic Functions ---
# =============================================================================

def show_matched_pressure(pressure_value):
    """Creates a new GUI entry in the 'matched_frame' to show a triggered pressure."""
    entry_frame = customtkinter.CTkFrame(master=matched_frame)
    entry_frame.pack(fill="x", pady=2, padx=10)

    label_text = f"Saved at {pressure_value:.2e} mbar (Particle {particle_number})"
    label = customtkinter.CTkLabel(master=entry_frame, text=label_text)
    label.pack(side="left", padx=(0, 10))

    def remove_matched():
        """Removes this specific entry from the GUI and the tracking lists."""
        entry_frame.destroy()
        if pressure_value in matched_labels:
            del matched_labels[pressure_value]
        # Note: We don't remove from triggered_pressures here,
        # so it doesn't immediately re-trigger.
        # triggered_pressures is cleared when detection is toggled off.

    button = customtkinter.CTkButton(master=entry_frame, text="Remove", width=80, command=remove_matched)
    button.pack(side="right")

    # Store widgets for later management
    matched_labels[pressure_value] = (label, button)


def trigger_test_action(pressure_value, particle_num):
    """
    Placeholder function called when a pressure match is detected.
    This is where you save data using RS_save_data.
    """
    date_str = datetime.now().strftime("%Y%m%d")
    print(f"Test print at {pressure_value:.2e} mbar for Particle {particle_num} on {date_str}")
    
    # Get the IP address from the entry box
    ip_address = ip_entry.get()
    if not ip_address:
        print("Error: No IP address set. Cannot save data.")
        connection_status_label.configure(text="Error: Enter IP before saving.")
        return

    # Call the external save function
    try:
        RS_save_data.save_data(ip_address, particle_num, pressure_value)
        print(f"Data saved for Particle {particle_num} at {pressure_value:.2e} mbar.")
    except Exception as e:
        print(f"Error calling RS_save_data.save_data: {e}")
        connection_status_label.configure(text=f"Error saving data: {e}")


def change_scaling_event(new_scaling: str):
    """Rescales all UI elements based on the dropdown menu selection."""
    scaling_float = int(new_scaling.replace("%", "")) / 100
    customtkinter.set_widget_scaling(scaling_float)
    
    # Rescale matplotlib figure and fonts
    fig.set_size_inches(10 * scaling_float, 5 * scaling_float)
    for ax in [ax_voltage, ax_pressure]:
        ax.title.set_fontsize(12 * scaling_float)
        ax.xaxis.label.set_fontsize(10 * scaling_float)
        ax.yaxis.label.set_fontsize(10 * scaling_float)
        ax.tick_params(axis='both', labelsize=8 * scaling_float)
    canvas.draw_idle()  # Request a redraw


def connect_to_ip():
    """Tests the connection to the oscilloscope IP address."""
    ip_address = ip_entry.get()
    if not ip_address:
        connection_status_label.configure(text="Please enter an IP address.")
        return
        
    if RS_save_data.check_connection(ip_address):
        connection_status_label.configure(text=f"Connected to oscilloscope @ {ip_address}", text_color="green")
    else:
        connection_status_label.configure(text="Could not connect to oscilloscope", text_color="red")


def update_pressure_display():
    """Updates the text box showing the list of target pressures."""
    if pressure_list:
        # Format list with 1-based indexing and scientific notation
        text = "\n".join([f"{i+1}. {p:.2e} mbar" for i, p in enumerate(pressure_list)])
    else:
        text = "No target pressures added."
    pressure_list_label.configure(text=text)


def add_pressure():
    """Adds a new target pressure from the entry boxes to the pressure_list."""
    try:
        p = float(pressure_entry.get())
        m = int(magnitude_entry.get())
        full_pressure = p * (10**m)
        
        pressure_list.append(full_pressure)
        pressure_list.sort()  # Keep the list sorted
        update_pressure_display()
        
        # Clear entry boxes
        pressure_entry.delete(0, 'end')
        magnitude_entry.delete(0, 'end')
    except ValueError:
        pressure_list_label.configure(text="Invalid input. Please enter valid numbers.")


def remove_last_pressure():
    """Removes the most recently added pressure from the list."""
    if pressure_list:
        pressure_list.pop()  # Removes the last item
        update_pressure_display()


def update_particle_label():
    """Updates the 'Particle X' label text."""
    if particle_label:  # Ensure the widget has been created
        particle_label.configure(text=f"Particle {particle_number}")


def decrease_particle():
    """Decrements the particle number, with a minimum of 1."""
    global particle_number
    if particle_number > 1:
        particle_number -= 1
        update_particle_label()


def increase_particle():
    """Increments the particle number."""
    global particle_number
    particle_number += 1
    update_particle_label()


def toggle_detection():
    """Toggles the pressure detection state (ON/OFF)."""
    global detection_active, particle_number

    if detection_active:
        # --- Turning OFF ---
        detection_active = False
        detection_toggle_button.configure(text="Detection: ON")
        graph_border_frame.configure(fg_color=BORDER_COLOR_OFF)
        
        # Clear all "Saved at..." labels from the GUI
        for label, button in matched_labels.values():
            label.master.destroy()  # Destroys the parent frame
        matched_labels.clear()
        
        # Clear the set of triggered pressures to allow re-triggering next time
        triggered_pressures.clear()
        
        # Increment particle number for the *next* run
        particle_number += 1
        update_particle_label()
        
    else:
        # --- Turning ON ---
        detection_active = True
        detection_toggle_button.configure(text="Detection: OFF")
        graph_border_frame.configure(fg_color=BORDER_COLOR_ON)


def update_data_and_detect():
    """
    High-frequency loop (every 20ms).
    1. Reads hardware (ADC).
    2. Calculates voltage and pressure.
    3. Updates text labels.
    4. Performs pressure match detection.
    """
    global current_voltage, current_pressure, text_update_job_id
    
    # 1. & 2. Read hardware and calculate values
    try:
        voltage_raw = adc.read_voltage(ADC_CHANNEL)
        current_voltage = VOLTAGE_CALIBRATION_FACTOR * voltage_raw
        current_pressure = np.power(10, (current_voltage - PRESSURE_CALC_OFFSET) / PRESSURE_CALC_SLOPE)
    except Exception as e:
        print(f"Error reading ADC: {e}")
        current_voltage = 0.0
        current_pressure = 0.0

    # 3. Update text labels
    pressure_sci = np.format_float_scientific(current_pressure, precision=2)
    voltage_label.configure(text=f"Voltage: {current_voltage:.2f} V")
    pressure_label.configure(text=f"Pressure: {pressure_sci} mbar")

    # 4. Perform pressure match detection
    if detection_active:
        for saved_p in pressure_list:
            # Check if current pressure is within the tolerance window
            lower_bound = saved_p * (1.0 - DETECTION_TOLERANCE)
            upper_bound = saved_p * (1.0 + DETECTION_TOLERANCE)
            
            if lower_bound <= current_pressure <= upper_bound:
                # We have a match!
                if saved_p not in triggered_pressures:
                    # Only trigger if it hasn't been triggered before in this session
                    triggered_pressures.add(saved_p)
                    show_matched_pressure(saved_p)
                    trigger_test_action(saved_p, particle_number)
    
    # Schedule the next run of this function
    text_update_job_id = root.after(TEXT_UPDATE_INTERVAL_MS, update_data_and_detect)


def update_plot():
    """
    Low-frequency loop (every 300ms).
    1. Takes the latest data from the other loop.
    2. Appends it to the plot data lists.
    3. Truncates lists to 'PLOT_DATA_POINTS'.
    4. Redraws the matplotlib graphs.
    """
    global plot_update_job_id
    
    # 1. Get latest data and timestamp
    timestamp = datetime.now().strftime('%M:%S.%f')[:-4] # Format: "MM:SS.ms"
    
    # Use data from the high-frequency loop instead of re-reading hardware
    voltage = float(f"{current_voltage:.3g}")
    pressure = float(f"{current_pressure:.3g}")

    # 2. Append to data lists
    x_data_timestamps.append(timestamp)
    y_data_voltage.append(voltage)
    y_data_pressure.append(pressure)

    # 3. Truncate lists to keep a rolling window
    if len(x_data_timestamps) > PLOT_DATA_POINTS:
        x_data_timestamps.pop(0)
        y_data_voltage.pop(0)
        y_data_pressure.pop(0)

    # 4. Redraw Voltage Plot
    ax_voltage.clear()
    ax_voltage.plot(y_data_voltage, marker='o', linestyle='-')
    ax_voltage.set_title("Live Voltage")
    ax_voltage.set_xlabel("Time")
    ax_voltage.set_ylabel("Voltage (V)")
    # Set X-axis labels to timestamps, but only show every 3rd one
    ax_voltage.set_xticks(range(0, len(x_data_timestamps), 3))
    ax_voltage.set_xticklabels([x_data_timestamps[i] for i in range(0, len(x_data_timestamps), 3)], rotation=45, ha='right')
    ax_voltage.grid(True)
    ax_voltage.set_xlim(-1, PLOT_DATA_POINTS + 1) # Set fixed X-axis width

    # 5. Redraw Pressure Plot
    ax_pressure.clear()
    ax_pressure.plot(y_data_pressure, marker='o', linestyle='-', color='red')
    ax_pressure.set_title("Live Pressure")
    ax_pressure.set_xlabel("Time")
    ax_pressure.set_ylabel("Pressure (mbar)")
    ax_pressure.set_yscale('log') # Use a logarithmic scale for pressure
    # Set X-axis labels to timestamps
    ax_pressure.set_xticks(range(0, len(x_data_timestamps), 3))
    ax_pressure.set_xticklabels([x_data_timestamps[i] for i in range(0, len(x_data_timestamps), 3)], rotation=45, ha='right')
    ax_pressure.grid(True)
    ax_pressure.set_xlim(-1, PLOT_DATA_POINTS + 1)

    # Update the canvas
    canvas.draw()
    
    # Schedule the next run of this function
    plot_update_job_id = root.after(PLOT_UPDATE_INTERVAL_MS, update_plot)


def on_closing():
    """
    Called when the window's 'X' button is pressed.
    Cancels all pending 'root.after' jobs to ensure a clean exit.
    """
    print("Closing application...")
    global text_update_job_id, plot_update_job_id
    
    if text_update_job_id is not None:
        root.after_cancel(text_update_job_id)
    if plot_update_job_id is not None:
        root.after_cancel(plot_update_job_id)
        
    root.quit()     # Stops the mainloop
    root.destroy()  # Destroys the tkinter window


# =============================================================================
# --- GUI Setup ---
# =============================================================================

# --- 1. Root Window & Theme ---
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("green")
root = customtkinter.CTk()
root.geometry("1920x1080")
root.title("Live Voltage and Pressure Graph with Trigger")

# --- 2. Main Scrollable Frame ---
scrollable_frame = customtkinter.CTkScrollableFrame(master=root, width=1900, height=1000)
scrollable_frame.pack(fill="both", expand=True)

# --- 3. UI Scaling Dropdown ---
scaling_label = customtkinter.CTkLabel(master=scrollable_frame, text="UI Scaling:", anchor="w")
scaling_label.pack(pady=(10, 0))

scaling_optionmenu = customtkinter.CTkOptionMenu(
    master=scrollable_frame,
    values=["50%", "60%", "70%", "80%", "90%", "100%", "110%", "120%", "130%", "140%", "150%"],
    command=change_scaling_event,
    variable=customtkinter.StringVar(value="100%")
)
scaling_optionmenu.pack(pady=(0, 10))

# --- 4. Oscilloscope Connection Frame ---
ip_frame = customtkinter.CTkFrame(master=scrollable_frame)
ip_frame.pack(pady=(0, 20))

ip_entry = customtkinter.CTkEntry(master=ip_frame, placeholder_text="Enter Oscilloscope IP address", width=200)
ip_entry.grid(row=0, column=0, padx=(10, 5), pady=10)

connect_button = customtkinter.CTkButton(master=ip_frame, text="Connect", command=connect_to_ip)
connect_button.grid(row=0, column=1, padx=(5, 10))

connection_status_label = customtkinter.CTkLabel(master=ip_frame, text="Not connected")
connection_status_label.grid(row=0, column=2, padx=(10, 0))

# --- 5. Target Pressure Input Frame ---
pressure_frame = customtkinter.CTkFrame(master=scrollable_frame)
pressure_frame.pack(pady=(0, 10))

pressure_entry = customtkinter.CTkEntry(master=pressure_frame, placeholder_text="Pressure (e.g., 1.5)", width=120)
pressure_entry.grid(row=0, column=0, padx=(10, 5), pady=10)

magnitude_entry = customtkinter.CTkEntry(master=pressure_frame, placeholder_text="Order (e.g., -3)", width=120)
magnitude_entry.grid(row=0, column=1, padx=(5, 5), pady=10)

add_button = customtkinter.CTkButton(master=pressure_frame, text="Add", command=add_pressure, width=80)
add_button.grid(row=0, column=2, padx=(5, 5))

remove_button = customtkinter.CTkButton(master=pressure_frame, text="Remove Last", command=remove_last_pressure, width=100)
remove_button.grid(row=0, column=3, padx=(5, 10))

# --- 6. Target Pressure Display Frame ---
display_frame = customtkinter.CTkFrame(master=scrollable_frame)
display_frame.pack(pady=(0, 10), fill="x", padx=10)

pressure_list_label = customtkinter.CTkLabel(master=display_frame, text="No pressures added.", justify="left")
pressure_list_label.pack(padx=10, pady=5, anchor="w")

# --- 7. Particle Number Frame ---
particle_frame = customtkinter.CTkFrame(master=scrollable_frame)
particle_frame.pack(pady=(10, 5))

decrease_button = customtkinter.CTkButton(master=particle_frame, text="-", width=40, command=decrease_particle)
decrease_button.grid(row=0, column=0, padx=(10, 0))

# This label is configured by update_particle_label()
particle_label = customtkinter.CTkLabel(master=particle_frame, text=f"Particle {particle_number}", width=100)
particle_label.grid(row=0, column=1, padx=10)

increase_button = customtkinter.CTkButton(master=particle_frame, text="+", width=40, command=increase_particle)
increase_button.grid(row=0, column=2, padx=(0, 10))

# --- 8. Detection Toggle Button ---
detection_toggle_button = customtkinter.CTkButton(master=scrollable_frame, text="Detection: ON", command=toggle_detection)
detection_toggle_button.pack(pady=(5, 15))

# --- 9. Live Data Labels ---
voltage_label = customtkinter.CTkLabel(scrollable_frame, text="Voltage: ...", font=customtkinter.CTkFont(size=20))
voltage_label.pack(pady=5)

pressure_label = customtkinter.CTkLabel(scrollable_frame, text="Pressure: ...", font=customtkinter.CTkFont(size=20))
pressure_label.pack(pady=10)

# --- 10. Matplotlib Graph Setup ---
# Create the figure and subplots
fig, (ax_voltage, ax_pressure) = plt.subplots(1, 2, figsize=(10, 5))
fig.subplots_adjust(left=0.1, right=0.95, wspace=0.4)
# Set log scale for pressure axis immediately
ax_pressure.set_yscale('log')

# Create a border frame that will change color
graph_border_frame = customtkinter.CTkFrame(master=scrollable_frame, corner_radius=12, fg_color=BORDER_COLOR_OFF)
graph_border_frame.pack(fill="both", expand=True, padx=10, pady=10)

# Create an inner frame to hold the graph
graph_frame = customtkinter.CTkFrame(master=graph_border_frame, corner_radius=8, fg_color=root._fg_color)
graph_frame.pack(fill="both", expand=True, padx=5, pady=5)

# Embed the matplotlib figure into the tkinter frame
canvas = FigureCanvasTkAgg(fig, master=graph_frame)
canvas.get_tk_widget().pack(fill="both", expand=True)

# --- 11. Matched Pressures Display Frame ---
matched_frame = customtkinter.CTkFrame(master=scrollable_frame)
matched_frame.pack(pady=(10, 0), fill="x", padx=10)


# =============================================================================
# --- Start Application ---
# =============================================================================

# Set the protocol for window closing
root.protocol("WM_DELETE_WINDOW", on_closing)

# Start the update loops
update_data_and_detect()
update_plot()

# Start the Tkinter main event loop
root.mainloop()