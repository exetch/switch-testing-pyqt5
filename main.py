from PyQt5.QtWidgets import QMenu, QAction, QToolBar, QWidget, QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QDialog, QLabel, QLineEdit, QVBoxLayout, QPushButton, QComboBox, QMessageBox
from add_switch_dialog import AddSwitchDialog, EditSwitchDialog



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CamSwitch Tester")
        self.setGeometry(100, 100, 800, 800)
        self.init_toolbar()  # Инициализация главной панели инструментов

    def init_toolbar(self):
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        configuration_menu = QMenu("Конфигурация", self)

        add_switch_action = QAction("Добавить переключатель", self)
        add_switch_action.triggered.connect(self.open_add_switch_dialog)
        configuration_menu.addAction(add_switch_action)

        edit_switch_action = QAction("Редактировать переключатель", self)
        edit_switch_action.triggered.connect(self.edit_switch)
        configuration_menu.addAction(edit_switch_action)

        toolbar.addAction(configuration_menu.menuAction())


    def open_add_switch_dialog(self):
        dialog = AddSwitchDialog()
        dialog.exec_()

    def edit_switch(self):
        pass
        edit_dialog = EditSwitchDialog()
        edit_dialog.exec_()

app = QApplication([])
window = MainWindow()
window.show()
app.exec()
