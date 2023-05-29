from PyQt5.QtWidgets import QMainWindow, QLabel, QPushButton, QDialog, QVBoxLayout, QLineEdit
import json

class AddSwitchDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Добавить переключатель")
        self.setGeometry(200, 200, 300, 200)

        self.label = QLabel("Введите артикул выключателя:", self)
        self.line_edit = QLineEdit(self)
        self.button = QPushButton("Сохранить", self)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.line_edit)
        layout.addWidget(self.button)

        self.setLayout(layout)

        self.button.clicked.connect(self.save_switch)



    def save_switch(self):
        vendor_code = self.line_edit.text()
        print(f"Артикул выключателя: {vendor_code}")
        self.accept()

class TestSwitchesApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Тестирование переключателей")
        self.setGeometry(100, 100, 500, 500)

        self.add_switch_button = QPushButton("Добавить переключатель", self)
        self.add_switch_button.setGeometry(150, 150, 200, 50)
        self.switches_data = []  # Создаем пустой список для хранения данных о переключателях
        self.add_switch_button.clicked.connect(self.add_switch)

    def add_switch(self):
        dialog = AddSwitchDialog()
        if dialog.exec_() == QDialog.Accepted:
            vendor_code = dialog.line_edit.text()
            switch_data = {"vendor_code": vendor_code}
            self.save_switch_data(switch_data)  # Сохраняем данные в файл
            print("Новый переключатель добавлен")

    def save_switch_data(self, switch_data):
        filename = "switches_data.json"
        try:
            with open(filename, "r") as file:
                data = json.load(file)  # Загружаем существующие данные из файла
        except FileNotFoundError:
            data = []  # Если файл не найден, начинаем с пустого списка
        data.append(switch_data)  # Добавляем новый переключатель к данным
        with open(filename, "w") as file:
            json.dump(data, file, indent=4)  # Записываем все данные в файл

