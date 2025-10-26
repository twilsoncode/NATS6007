---
# NATS6007 - Levitated Optomechanical Classification of DNA Sequences: Integration of Machine Learning and Automated Pressure Control

This repository contains code used in my placement report work for the NATS6007 module. This research was carried out at the [University of Southampton](https://www.southampton.ac.uk/) under the supervision of [Prof Hendrik Ulbricht](https://www.southampton.ac.uk/people/5x5wz8/professor-hendrik-ulbricht).

---
### Software and package versions with documentation links
- [Python 3.13.5](https://www.python.org/downloads/release/python-3135/)
- [Customtkinter 5.2.2](https://pypi.org/project/customtkinter/)
- [Matplotlib 3.10.5](https://matplotlib.org/stable/index.html)
- [Numpy 2.3.2](https://numpy.org/devdocs/release/2.3.2-notes.html)
- [RSInstrument 1.120.0](https://rsinstrument.readthedocs.io/en/latest/RsInstrument.html)


---
### Installation instructions for the packages used that are not included in the standard python library using `pip`
- `pip install customtkinter==5.2.2`
- `pip install matplotlib==3.10.5`
- `pip install numpy==2.3.2`
- `pip install RSInstrument==1.120.0`

To check that these packages are installed, use the `pip list` command to see all installed packages and their versions available to be viewed with `pip`.

---
### Automated Pressure Control System
The code in the folder `auto_press` is for the automated pressure control for saving `.Wfm.bin` files from the R&S RTO2014 Oscilloscope over a local wired ethernet connection. A [Raspberry Pi 5 8 GB model](https://www.raspberrypi.com/products/raspberry-pi-5/) was used with an [ADC Pi](https://www.abelectronics.co.uk/p/69/adc-pi) connected to an [Agilent Technologies FRG-720 Gauge](https://www.agilent.com/en/product/vacuum-technologies/vacuum-measurement/active-gauges/frg-720-730-full-range-pirani-bayard-alpert-gauge). A potential divider halves the input 0 - 10 V signal such that it can be read within the 0 - 5 V range of the ADC board. An equation converts the input voltage to pressure, where the input voltage is scaled up 2x in code. When the desired pressure value is reached +/- a specified percentage range, the Raspberry Pi sends a signal to the IP address on the oscilloscope to save the raw data locally.

---
