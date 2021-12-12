import sys
from PyQt5.QtGui import QFont
import numpy as np
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *


def get_burnout_status(): # func to return inference 
    #global inference
    #return inference
    return np.random.randint(1, 3)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            QtCore.Qt.WindowStaysOnTopHint |
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.X11BypassWindowManagerHint
        )
        self.setGeometry(
            QtWidgets.QStyle.alignedRect(
                QtCore.Qt.RightToLeft, QtCore.Qt.AlignBottom,
                QtCore.QSize(200, 50),
                QtWidgets.qApp.desktop().availableGeometry()
        ))
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, on = True) # make window transparent
        self.label = QLabel('0', self) # label initialization
        self.label.setFont(QFont('Times', 30))
        self.label.setStyleSheet('color: yellow') 
        self.label.move(100, 10) # change label location
        timerTime = QtCore.QTimer(self) # to update label every 1s
        timerTime.timeout.connect(self.update_label)
        timerTime.start(1000)

    def update_label(self): # is called when label updates
        self.label.setText(f'{get_burnout_status()}')

    def mousePressEvent(self, event): # clode label on mouse click (for debug)
        QtWidgets.qApp.quit()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mywindow = MainWindow()
    mywindow.show()
    app.exec_()