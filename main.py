from PyQt5.QtWidgets import QApplication
from my_classes import  TestSwitchesApp


if __name__ == "__main__":
    app = QApplication([])
    test_app = TestSwitchesApp()
    test_app.show()
    app.exec_()

