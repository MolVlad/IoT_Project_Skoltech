import sys
from PyQt5.QtGui import QFont
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *


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
        self.label = QLabel('Burnout', self) # label initialization
        self.label.setFont(QFont('Times', 30))
        self.label.setStyleSheet('color: yellow') 
        self.label.resize(150, 30)
        self.label.move(30, 10) # change label location
        timerTime = QtCore.QTimer(self) # close label after 10s
        timerTime.timeout.connect(self.close_window)
        timerTime.start(10000)

    def close_window(self):
        QtWidgets.qApp.quit()

def show_pop_up():
    app = QApplication(sys.argv)
    mywindow = MainWindow()
    mywindow.show()
    app.exec_()


if __name__ == '__main__':
    show_pop_up()