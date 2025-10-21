import csv
import os
import pyExSi as es
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import math
from scipy import signal
import scipy.signal.windows
from scipy.signal import butter, lfilter
import os
import platform
import esptool
import subprocess
import matplotlib
matplotlib.use('Qt5Agg')  # Use the Qt5 backend for Matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QFrame
import serial
import time
import sys

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None):
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setParent(parent)

class Siguls:
    def __new__(cls):
        return super().__new__(cls)

    def __init__(self):
        self.signalType = 0
        self.sineFrequency = 0
        self.cutoffFrequency = 0
        self.startFrequency = 0
        self.endFrequency = 0
        self.taperOnSine = False
        self.taperOnSweep = False
        self.taperOnBLRandom = False
        self.taperRatioSine= 0
        self.taperRatioSweep= 0
        self.taperRatioBLRandom= 0
        self.samplingRate = 0
        self.sampleSize = 0
        self.duration = 0
        self.data = 0
        self.outputVoltage = 0
        self.serialPort = None

    def generateCSV(file_name, data):
        with open(file_name, mode='w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(data)
        print(f"CSV file '{file_name}' created")

    def bandlimit(data, cutoff, fs, order=4):
        nyquist = 0.5 * fs  # Nyquist frequency
        normal_cutoff = cutoff / nyquist
        b, a = butter(order, normal_cutoff, btype='low', analog=False)
        return lfilter(b, a, data)

    def normalize(data):
        return data / np.max(np.abs(data))

    def window(data, taper_ratio):
        # Generate a Tukey window using the correct function
        window = scipy.signal.windows.tukey(len(data), alpha=taper_ratio)

        # Apply the window to the data
        tapered_data = data * window

        return tapered_data, window

    def generateData(self):
        print("generating data")

        amplitude = 1

        if (self.signalType == 0):
            # sweep
            self.sampleSize = self.duration * self.samplingRate
            w = 2*np.pi*self.sineFrequency
            t = np.linspace(0, self.duration, self.sampleSize)
            self.data = np.sin(w*t)
            self.data = Siguls.normalize(self.data)

            if (self.taperOnSine):
                self.data, window = Siguls.window(self.data, self.taperRatioSine)

        if (self.signalType == 1):
            # sweep
            self.sampleSize = self.duration * self.samplingRate
            t = np.linspace(0, self.duration, self.sampleSize)
            self.data = es.sine_sweep(time=t, freq_start=self.startFrequency, freq_stop=self.endFrequency)
            self.data = Siguls.normalize(self.data)

            if (self.taperOnSweep):
                self.data, window = Siguls.window(self.data, self.taperRatioSweep)

        if (self.signalType == 2):
            # Random Generator
            seed = 1234
            rg = np.random.default_rng(seed)

            # Pseudo random
            self.sampleSize = self.samplingRate*self.duration
            self.data = es.pseudo_random(N=self.sampleSize, rg=rg)

            self.data = Siguls.bandlimit(self.data, self.cutoffFrequency, self.samplingRate)
            self.data = Siguls.normalize(self.data)

            if (self.taperOnBLRandom):
                self.data, window = Siguls.window(self.data, self.taperRatioBLRandom)

        print("data generated")

    def updatePlot(self, canvas: MplCanvas):
        print("updating plot")
        canvas.ax.clear()

        # Plot the data
        t = np.linspace(0, self.duration, self.sampleSize)
        canvas.ax.plot(t, self.data)
        canvas.ax.set_xlabel('Time / s')
        canvas.ax.set_ylabel('Amplitude')
        canvas.draw()

    def uploadData(self):
        print("translating data")

        # Translate data into 18bit format
        # For +1V / -1V
        if (self.outputVoltage == 1):
            dac_min_value = 0x39999
            dac_max_value = 0x46555

        # For +10V / -10V
        if (self.outputVoltage == 0):
            dac_min_value = 0x00000
            dac_max_value = 0x7FFFF

        data_to_write = [
            int((d + 1.0) / 2.0 * (dac_max_value - dac_min_value) + dac_min_value) # ASSUMES AMPLITUDE OF DATA = 1
            for d in self.data
        ]

        params = np.zeros(5)
        params[0] = self.samplingRate

        print("generating CSV files")

        # Determine the directory of the current script
        SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

        # Path to the SIGULS_data directory
        SIGULS_DATA_DIR = os.path.join(SCRIPT_DIR, "SIGULS_data")

        # Ensure the directory exists (create it if not)
        os.makedirs(SIGULS_DATA_DIR, exist_ok=True)

        # Path for the CSV files inside SIGULS_data
        CSV_FILE_1 = os.path.join(SIGULS_DATA_DIR, "data.csv")
        CSV_FILE_2 = os.path.join(SIGULS_DATA_DIR, "parameters.csv")

        Siguls.generateCSV(CSV_FILE_1, data_to_write)
        Siguls.generateCSV(CSV_FILE_2, params)

        print("uploading data")

        # Get the current script directory
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # Detect OS and select correct binary
        if platform.system() == "Windows":
            mklittlefs_bin = os.path.join(current_dir, "mklittlefs.exe")
        else:  # Linux/macOS
            mklittlefs_bin = os.path.join(current_dir, "mklittlefs")

        # Define the command as a list of arguments
        command = [
            mklittlefs_bin,
            "-c", os.path.join(current_dir, "SIGULS_data"),
            "-b", "4096",
            "-p", "256",
            "-s", "0x5E0000",
            os.path.join(current_dir, "data.bin")
        ]

        try:
            result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("Command output:", result.stdout.decode())
        except subprocess.CalledProcessError as e:
            print("Error during command execution:", e.stderr.decode())

        flash_command = [
            sys.executable, "-m", "esptool",
            "--chip", "esp32s3",
            "--port", self.serialPort,
            "--baud", "115200",
            "write-flash", "0x110000", os.path.join(current_dir, "data.bin")
        ]

        try:
            subprocess.run(flash_command, check=True)
        except Exception:
            print("[Error] device not found")

    def startOutput(self):
        print("starting output")
        try:
            with serial.Serial(self.serialPort, 115200, timeout=1, dsrdtr=False, rtscts=False) as ser:
                ser.dtr = False
                ser.rts = False
                time.sleep(0.5)
                ser.write(b'SIGULS.Start\n')     # write a string
                time.sleep(1)
                ser.close()             # close port
        except Exception as e:
            print(f"[Error] device not found")

    def stopOutput(self):
        print("stopping output")
        try:
            with serial.Serial(self.serialPort, 115200, timeout=1) as ser:
                ser.write(b'SIGULS.Stop\n')     # write a string
                time.sleep(1)
                line = ser.readline()   # read a '\n' terminated line
                ser.close()             # close port
                line = line.replace(b'\n', b' ').replace(b'\r', b' ')
                line=str(line,'utf-8')
                print(line)
        except Exception as e:
            print(f"[Error] device not found")

    def pingDevice(self):
        print("pinging device")
        try:
            with serial.Serial(self.serialPort, 115200, timeout=1) as ser:
                ser.write(b'SIGULS.Ping\n')     # write a string
                time.sleep(1)
                line = ser.readline()   # read a '\n' terminated line
                ser.close()             # close port
                line = line.replace(b'\n', b' ').replace(b'\r', b' ')
                line=str(line,'utf-8')
                print(line)
                print("device pinged")
        except Exception as e:
            print(f"[Error] device not found")

    # Set functions
    def setDuration(self, text):
        try:
            self.duration = int(text)
        except Exception as e:
            print(f"[Error] invalid input")

    def setSignalType(self, index):

        try:
            self.signalType = index
        except Exception as e:
            print(f"[Error] invalid input")

    def setSamplingRate(self, text):
        try:
            self.samplingRate = int(text)
        except Exception as e:
            print(f"[Error] invalid input")

    def setStartFrequency(self, text):
        try:
            self.startFrequency = int(text)
        except Exception as e:
            print(f"[Error] invalid input")

    def setEndFrequency(self, text):
        try:
            self.endFrequency = int(text)
        except Exception as e:
            print(f"[Error] invalid input")

    def setSineFrequency(self, text):
        try:
            self.sineFrequency = int(text)
        except Exception as e:
            print(f"[Error] invalid input")

    def setCutoffFrequency(self, text):
        try:
            self.cutoffFrequency = int(text)
        except Exception as e:
            print(f"[Error] invalid input")

    def toggleTaperSine(self, text):
        self.taperOnSine = not self.taperOnSine

    def toggleTaperSweep(self, text):
        self.taperOnSweep = not self.taperOnSweep

    def toggleTaperBLRandom(self, text):
        self.taperOnBLRandom = not self.taperOnBLRandom

    def setTaperRatioSine(self, text):
        try:
            self.taperRatioSine = int(text)/100
        except Exception as e:
            print(f"[Error] invalid input")

    def setTaperRatioSweep(self, text):
        try:
            self.taperRatioSweep = int(text)/100
        except Exception as e:
            print(f"[Error] invalid input")

    def setTaperRatioBLRandom(self, text):
        try:
            self.taperRatioBLRandom = int(text)/100
        except Exception as e:
            print(f"[Error] invalid input")

    def setOutputVoltage(self, index):
        try:
            self.outputVoltage = index
        except Exception as e:
            print(f"[Error] invalid input")

    def setSerialPort(self):
        print(f"setting serial port")

    def setSerialPort(self, port_name: str):
        try:
            self.serialPort = port_name
            print(f"serial port set to: {self.serialPort}")
        except Exception as e:
            print(f"[Error] could not set serial port")

