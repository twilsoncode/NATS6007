---
# NATS6007 - Using machine learning to examine detection limits of oligonucleotide classification in levitated optomechanics with automated data collection and imaging

This repository contains code used in my placement report work for the NATS6007 module. This research was carried out at the [University of Southampton](https://www.southampton.ac.uk/) under the supervision of [Prof Hendrik Ulbricht](https://www.southampton.ac.uk/people/5x5wz8/professor-hendrik-ulbricht) and [Dr Owen Rackham](https://www.southampton.ac.uk/people/5y9xv6/doctor-owen-rackham).

---
### Software and package versions with documentation links
- [Python 3.13.5](https://www.python.org/downloads/release/python-3135/)
- [Customtkinter 5.2.2](https://pypi.org/project/customtkinter/)
- [Joblib 1.5.1](https://pypi.org/project/joblib/)
- [Matplotlib 3.10.5](https://matplotlib.org/stable/index.html)
- [Numpy 2.3.2](https://numpy.org/devdocs/release/2.3.2-notes.html)
- [Optoanalysis 4.3.2](https://pypi.org/project/optoanalysis/)
- [RSInstrument 1.120.0](https://rsinstrument.readthedocs.io/en/latest/RsInstrument.html)
- [RTxReadBin 1.0](https://www.rohde-schwarz.com/uk/applications/working-with-acquired-waveform-data-in-python-application-card_56279-1165008.html)
- [Seaborn 0.13.2](https://seaborn.pydata.org/installing.html)
- [Scikit-learn 1.7.1](https://scikit-learn.org/stable/whats_new/v1.7.html)
- [Scipy 1.16.1](https://pypi.org/project/scipy/)
- [Tensorflow 2.20.0rc0](https://pypi.org/project/tensorflow/)
- [Tkinter 0.1.0](https://pypi.org/project/tk/)
- [Umap-learn 0.5.9.post2](https://pypi.org/project/umap-learn/)


---
### Installation instructions for the packages used that are not included in the standard python library using `pip`
- `pip install customtkinter==5.2.2`
- `pip install joblib==1.5.1`
- `pip install matplotlib==3.10.5`
- `pip install numpy==2.3.2`
- `pip install optoanalysis==4.3.2`
- `pip install RSInstrument==1.120.0`
- `pip install RTxReadBin-1.0-py3-none-any`
- `pip install seaborn==0.13.2`
- `pip install scikit-learn==1.7.1`
- `pip install scipy==1.16.3`
- `pip install tensorflow==2.20.0`
- `pip install tk==0.1.0`
- `pip install umap-learn==0.5.9.post2`

To check that these packages are installed, use the `pip list` command to see all installed packages and their versions available to be viewed with `pip`. The `RTxReadBin-1.0-py3-none-any.whl` file has been provided in this repository for installation of `RTxReadBin`.

---
### Automated Pressure Control System
The code in the folder `auto_press` is for the automated pressure control for saving `.Wfm.bin` files from the R&S RTO2014 Oscilloscope over a local wired ethernet connection. A [Raspberry Pi 5 8 GB model](https://www.raspberrypi.com/products/raspberry-pi-5/) was used with an [ADC Pi](https://www.abelectronics.co.uk/p/69/adc-pi) connected to an [Agilent Technologies FRG-720 Gauge](https://www.agilent.com/en/product/vacuum-technologies/vacuum-measurement/active-gauges/frg-720-730-full-range-pirani-bayard-alpert-gauge). A potential divider halves the input 0 - 10 V signal such that it can be read within the 0 - 5 V range of the ADC board. An equation converts the input voltage to pressure, where the input voltage is scaled up 2x in code. When the desired pressure value is reached +/- a specified percentage range, the Raspberry Pi sends a signal to the IP address on the oscilloscope to save the raw data locally.

---
### Project Figures
The code in the folder `figures` details how the figures have been generated from the output data as presented in the paper.

---
### Optoanalysis Tool
The code in the folder `opto_tool` is the GUI used to analysis the `.bin` files from the R&S Oscilloscope. There is a `README.txt` file in the folder with specific instructions on how it works.

---
