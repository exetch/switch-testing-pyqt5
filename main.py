from PyQt5.QtWidgets import QAction, QToolBar, QWidget, QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QDialog, QLabel, QLineEdit, QVBoxLayout, QPushButton, QComboBox, QMessageBox
from add_switch_dialog import AddSwitchDialog



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CamSwitch Tester")
        self.setGeometry(100, 100, 800, 800)

        self.button_add_switch = QPushButton("Добавить переключатель", self)
        self.button_add_switch.clicked.connect(self.open_add_switch_dialog)

        layout = QVBoxLayout()
        layout.addWidget(self.button_add_switch)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        self.init_toolbar()  # Инициализация главной панели инструментов

    def init_toolbar(self):
        toolbar = QToolBar(self)  # Создание главной панели инструментов
        self.addToolBar(toolbar)

        file_action = QAction("Файл", self)
        config_action = QAction("Конфигурация", self)
        help_action = QAction("Справка", self)

        toolbar.addAction(file_action)
        toolbar.addAction(config_action)
        toolbar.addAction(help_action)

    def open_add_switch_dialog(self):
        dialog = AddSwitchDialog()
        dialog.exec_()

app = QApplication([])
window = MainWindow()
window.show()
app.exec()
