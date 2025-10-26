from RsInstrument import RsInstrument
from datetime import datetime
import math

def check_connection(IP_address):
    """
    Checks whether the oscilloscope at the given IP address is reachable.

    Parameters:
        IP_address (str): IP address of the oscilloscope

    Returns:
        bool: True if the connection is successful, False otherwise
    """
    visa_resource = f'TCPIP0::{IP_address}::INSTR'
    try:
        # Open connection to instrument
        instr = RsInstrument(visa_resource, reset=False, id_query=False)
        idn = instr.query_str("*IDN?")  # Query identity string
        print(f"Connected successfully: {idn}")
        instr.close()
        return True
    except Exception as e:
        print(f"Connection failed to {IP_address}: {e}")
        return False


def save_data(ip_address, particle_no, pressure_no):
    """
    Connects to an R&S RTO oscilloscope and saves the full waveform 
    (including X and Y values) directly to the oscilloscope's internal storage.
    No data is transferred back to the PC.

    Parameters:
        ip_address (str): IP address of the oscilloscope
        particle_no (int): Particle number for naming the file
        pressure_no (int): Pressure number for naming the file
    """
    visa_resource = f"TCPIP0::{ip_address}::INSTR"
    instr = None

    try:
        # === Connect to the oscilloscope ===
        instr = RsInstrument(visa_resource, reset=False, id_query=False)
        instr.visa_timeout = 10000          # Timeout for VISA operations (ms)
        instr.chunk_size = 1048576          # Chunk size for transfers (1 MB)
        print(f"Connected to: {instr.query_str('*IDN?').strip()}")

        # === Configure waveform export settings ===
        instr.write_str("EXPort:WAVeform:FASTexport ON")     # Fast export mode
        instr.write_str("EXPort:WAVeform:SOURce C1W1")       # Channel 1, Waveform 1
        instr.write_str("EXPort:WAVeform:SCOPe WFM")         # Export full scope waveform
        instr.write_str("EXPort:WAVeform:RAW ON")            # Use raw binary format
        instr.write_str("EXPort:WAVeform:INCXvalues ON")     # Include X (time) values
        instr.write_str("EXPort:WAVeform:DLOGging OFF")      # Disable continuous logging

        # === Process pressure number into order and magnitude ===
        pressure_no = float(pressure_no)
        if pressure_no == 0:
            order = 0
            magnitude = 0.00
        else:
            order = int(math.floor(math.log10(abs(pressure_no))))
            magnitude = pressure_no / (10 ** order)

        # Zero-pad the order to 2 digits (negative numbers keep the sign)
        if order >= 0:
            order_str = f"{order:02d}"
        else:
            order_str = f"-{abs(order):02d}"

        # Format magnitude and replace decimal point with underscore
        magnitude_str = f"{magnitude:.2f}".replace('.', '_')

        # === Build target directory and filename ===
        time_str = datetime.now().strftime('%H%M%S')
        date_only = datetime.now().strftime('%Y%m%d')
        scope_dir = rf"C:\Users\Instrument\Desktop\Tim\Year 4\{date_only}"

        base_name = (
            f"{date_only}_Particle{particle_no}"
            f"_Pr_order{order_str}_magnitude{magnitude_str}_time{time_str}"
        )

        # Ensure directory exists on oscilloscope
        #instr.write_str(f"MMEMory:MDIRectory '{scope_dir}'") # include this if it doesn't work

        # Tell the scope where to save the file
        instr.write_str(f"EXPort:WAVeform:NAME '{scope_dir}\\{base_name}.bin'")

        # === Save waveform internally on the oscilloscope ===
        instr.write_str("EXPort:WAVeform:SAVE")
        instr.query_opc()  # Wait for operation complete
        print(f"Waveform saved on oscilloscope at: {scope_dir}\\{base_name}.bin")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        # Always close the connection safely
        if instr:
            instr.close()
            print("Instrument connection closed.")
# check that this saves both .Wfm.bin and .bin files internally to the oscilloscope!!