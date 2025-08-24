# Squegg Python API

This project provides a simple Python interface for connecting to the [Squegg smart squeeze ball](https://www.mysquegg.com/pages/get-started-with-squegg?srsltid=AfmBOopGW9zFaGqLT9o5n219v1uaixzSeJj-RVT1PXzd5tNKZ8NxLp-2).  
Squegg is a Bluetooth-enabled grip strength trainer designed for everyday fitness, rehab, and wellness. It is a well-built device with a clean mobile app.

I am not affiliated with Squegg. I originally wrote this API for a medical research lab that wanted to stream grip strength data directly into their analysis pipeline. Since the company did not provide a desktop integration, I built this open-source solution in Python.

---

## Features
* Connects to a Squegg device over Bluetooth Low Energy (BLE)  
* Streams real-time grip strength data  
* Parses battery level and squeeze status  
* Simple command line runner  

---

## Installation

Clone this repository and install the required package:

```bash
pip install -r requirements.txt
```

Run the main script to connect to your Squegg and begin streaming data:

```bash 
python main.py
```
Press Ctrl+C to disconnect.

## Executable
If you want to build the program as an executable file then run the following after installing PyInstaller:
```bash
pyinstaller --noconfirm --clean --onefile --name SqueggReader main.py
```

## Disclaimer
The Squegg is an excellent device and I am not affiliated with them, and only developed this solution for research purposes. Please checkout their website and their app for the device's native capabilities.