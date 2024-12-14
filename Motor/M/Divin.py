import sys
import time
import math
from PyQt5 import QtGui, QtWidgets, QtCore
from ui_motor import Ui_MainWindow
from pypot.dynamixel.io import DxlIO

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Pushbuttons connections
        self.ui.pushbutton_connect.clicked.connect(self.connect)
        self.ui.pushbutton_close.clicked.connect(self.close)
        self.ui.dblspinbox_set_pos.valueChanged.connect(self.set_position)

        # Timer for periodic updates
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_position)
        self.angle = 0  # Initial angle for the sinusoidal function

    # Slots definition
    def connect(self):
        try:
            self.dxlio = DxlIO("COM6", baudrate=1000000)
            self.m_id = self.dxlio.scan(ids=range(5))
            if self.m_id:
                print(f"Connected to motor ID: {self.m_id[0]}")
                self.dxlio.set_pid_gain({self.m_id[0]: [11 * 0.125, 10 * 1000 / 2048, 8 * 0.004]})
                self.dxlio.set_moving_speed({self.m_id[0]: 100})
                self.timer.start(100)  # Update every 100ms
            else:
                print("No motor found!")
        except Exception as e:
            print(f"Error connecting to Dynamixel: {e}")

    def close(self):
        if hasattr(self, 'dxlio'):
            self.timer.stop()
            self.dxlio.close()
        self.close()

    def set_position(self, value):
        try:
            self.dxlio.set_goal_position({self.m_id[0]: value})
            time.sleep(0.5)
            current_pos = self.dxlio.get_present_position(self.m_id)
            self.ui.label_current_pos.setText(f'Current Position: {current_pos[0]:.2f}')
        except Exception as e:
            print(f"Error setting position: {e}")

    def update_position(self):
        try:
            # Compute the target position as a sinusoidal function
            target_pos = 45 * math.sin(math.radians(self.angle))
            self.dxlio.set_goal_position({self.m_id[0]: target_pos})
            
            # Update PID gains dynamically (optional)
            p_gain = max(0, 11 * math.cos(math.radians(self.angle)))  # Example: vary proportional gain
            self.dxlio.set_pid_gain({self.m_id[0]: [p_gain, 10 * 1000 / 2048, 8 * 0.004]})
            
            # Increment angle for next update
            self.angle += 5  # Increment angle (step size)
            if self.angle > 360:
                self.angle = 0

            # Update label
            current_pos = self.dxlio.get_present_position(self.m_id)
            self.ui.label_current_pos.setText(f'Current Position: {current_pos[0]:.2f}')
        except Exception as e:
            print(f"Error in update loop: {e}")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())
