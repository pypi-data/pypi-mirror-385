import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPlainTextEdit
from PyQt5 import QtCore, QtGui
from siguls_gui.siguls_gui_helper import Ui_MainWindow
from siguls_gui.siguls_class import Siguls, MplCanvas
import matplotlib as plt
plt.use('Qt5Agg')  # Use the Qt5 backend for Matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QFrame

# Define a stream, custom class, that reports data written to it, with a Qt signal
class EmittingStream(QtCore.QObject):

    textWritten = QtCore.pyqtSignal(str)

    def write(self, text):
        self.textWritten.emit(str(text))

    def flush(self):
        pass  # Required for compatibility with code that expects sys.stdout to support flush()

class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.siguls = Siguls()

        # Create a layout for the frame (if it doesn't already have one)
        layout = QVBoxLayout(self.ui.frame_plot)

        # Create a Matplotlib canvas and add it to the frame
        self.canvas = MplCanvas(self)
        layout.addWidget(self.canvas)   

        self.output_stream = EmittingStream(textWritten=self.output_terminal_written)
        sys.stdout = self.output_stream

        # Connect inputs to attributes
        # Line edits
        self.ui.lineEdit_duration.textChanged.connect(lambda text: self.siguls.setDuration(text))
        self.ui.lineEdit_samplingRate.textChanged.connect(lambda text: self.siguls.setSamplingRate(text))
        self.ui.lineEdit_taperBLRandom.textChanged.connect(lambda text: self.siguls.setTaperRatioBLRandom(text))
        self.ui.lineEdit_taperSine.textChanged.connect(lambda text: self.siguls.setTaperRatioSine(text))
        self.ui.lineEdit_taperSweep.textChanged.connect(lambda text: self.siguls.setTaperRatioSweep(text))
        self.ui.lineEdit_cutoffFrequencyBLRandom.textChanged.connect(lambda text: self.siguls.setCutoffFrequency(text))
        self.ui.lineEdit_sineFrequency.textChanged.connect(lambda text: self.siguls.setSineFrequency(text))
        self.ui.lineEdit_sweepStartFrequency.textChanged.connect(lambda text: self.siguls.setStartFrequency(text))
        self.ui.lineEdit_sweepEndFrequency.textChanged.connect(lambda text: self.siguls.setEndFrequency(text))

        # Combo boxes
        self.ui.comboBox_outputVoltage.currentIndexChanged.connect(lambda index: self.siguls.setOutputVoltage(index))
        self.ui.comboBox_signalType.currentIndexChanged.connect(lambda index: self.siguls.setSignalType(index))
        self.ui.comboBox_signalType.currentIndexChanged.connect(lambda index: self.ui.stackedWidget.setCurrentIndex(index))
        self.ui.comboBox_serialPort.currentIndexChanged.connect(lambda index: self.siguls.setSerialPort(self.ui.comboBox_serialPort.currentText()))

        # Check boxes
        self.ui.checkBox_taperSine.stateChanged.connect(lambda state: self.ui.lineEdit_taperSine.setEnabled(state))
        self.ui.checkBox_taperSine.stateChanged.connect(self.siguls.toggleTaperSine)

        self.ui.checkBox_taperSweep.stateChanged.connect(lambda state: self.ui.lineEdit_taperSweep.setEnabled(state))
        self.ui.checkBox_taperSweep.stateChanged.connect(self.siguls.toggleTaperSweep)

        self.ui.checkBox_taperBLRandom.stateChanged.connect(lambda state: self.ui.lineEdit_taperBLRandom.setEnabled(state))
        self.ui.checkBox_taperBLRandom.stateChanged.connect(self.siguls.toggleTaperBLRandom)

        # Connect push buttons to methods
        self.ui.pushButton_startOutput.clicked.connect(self.siguls.startOutput)
        self.ui.pushButton_uploadData.clicked.connect(self.siguls.uploadData)
        self.ui.pushButton_updatePlot.clicked.connect(lambda: self.siguls.updatePlot(self.canvas))
        self.ui.pushButton_stopOutput.clicked.connect(self.siguls.stopOutput)
        self.ui.pushButton_generateData.clicked.connect(self.siguls.generateData)
        self.ui.pushButton_pingDevice.clicked.connect(self.siguls.pingDevice)
        self.ui.pushButton_searchPorts.clicked.connect(self.searchPorts)

    #custom method to write anything printed out to console/terminal to my QTextEdit widget via append function.
    def output_terminal_written(self, text):
        cursor = self.ui.plainTextEdit_terminal.textCursor()
        cursor.movePosition(cursor.End)
        self.ui.plainTextEdit_terminal.setTextCursor(cursor)
        self.ui.plainTextEdit_terminal.insertPlainText(text)

    def searchPorts(self):
        print(f"searching for serial ports")
        import serial.tools.list_ports
        self.ui.comboBox_serialPort.clear()
        ports = serial.tools.list_ports.comports()
        for p in ports:
            self.ui.comboBox_serialPort.addItem(p.device)
        if not ports:
            self.ui.comboBox_serialPort.addItem("No ports found")

# ------------- Main -------------
def main():
    if sys.platform.startswith('win'):
        import ctypes
        myappid = 'OASIS-GUI'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    plt.style.use('dark_background')
    app = QApplication(sys.argv)
    
    # set app icon    
    app_icon = QtGui.QIcon()
    app_icon.addFile(':/Icons/ui_resources/16x16.png', QtCore.QSize(16,16))
    app_icon.addFile(':/Icons/ui_resources/24x24.png', QtCore.QSize(24,24))
    app_icon.addFile(':/Icons/ui_resources/32x32.png', QtCore.QSize(32,32))
    app_icon.addFile(':/Icons/ui_resources/48x48.png', QtCore.QSize(48,48))
    app_icon.addFile(':/Icons/ui_resources/64x64.png', QtCore.QSize(64,64))
    app_icon.addFile(':/icons/ui_resources/128x128.png', QtCore.QSize(128,128))
    app_icon.addFile(':/Icons/ui_resources/256x256.png', QtCore.QSize(256,256))
    app.setWindowIcon(app_icon)

    window = MyApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()