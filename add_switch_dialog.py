from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QDialog, QLabel, QLineEdit, QVBoxLayout, QPushButton, QComboBox, QMessageBox
import json

class AddSwitchDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Добавить переключатель")
        self.setGeometry(200, 200, 500, 500)

        self.label_vendor_code = QLabel("Введите артикул выключателя:", self)
        self.line_edit_vendor_code = QLineEdit(self)

        self.label_positions = QLabel("Выберите количество положений:", self)
        self.combo_box_positions = QComboBox(self)
        self.combo_box_positions.addItems(["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"])

        self.button_next_position = QPushButton("Сохранить позицию и перейти к заполнению следующей позиции", self)
        self.button_save_switch = QPushButton("Сохранить переключатель", self)
        self.button_previous_position = QPushButton("Вернуться к предыдущему положению", self)

        self.table = QTableWidget(24, 2)  # Создаем таблицу с 24 строками и 2 столбцами
        self.table.setHorizontalHeaderLabels(["Контакт 1", "Контакт 2"])  # Задаем названия столбцов
        self.table.verticalHeader().setVisible(False)  # Убираем нумерацию строк

        layout = QVBoxLayout()
        layout.addWidget(self.label_vendor_code)
        layout.addWidget(self.line_edit_vendor_code)
        layout.addWidget(self.label_positions)
        layout.addWidget(self.combo_box_positions)
        layout.addWidget(self.table)
        layout.addWidget(self.button_next_position)
        layout.addWidget(self.button_previous_position)
        layout.addWidget(self.button_save_switch)

        self.setLayout(layout)

        self.current_position = 1  # Первое положение
        self.switch_data = {
            "vendor_code": "",
            "positions": 0,
            "position_1": []
        }

        self.setWindowTitle(f"Добавить переключатель - Положение {self.current_position}")  # Устанавливаем заголовок сразу

        self.button_next_position.clicked.connect(self.save_and_next_position)
        self.button_save_switch.clicked.connect(self.save_switch)
        self.button_previous_position.clicked.connect(self.go_to_previous_position)

    def save_and_next_position(self):
        contacts = []
        for row in range(24):
            contact1_item = self.table.item(row, 0)
            contact2_item = self.table.item(row, 1)
            if contact1_item is not None and contact2_item is not None:
                contact1 = int(contact1_item.text())
                contact2 = int(contact2_item.text())
                contacts.append([contact1, contact2])

        self.switch_data[f"position_{self.current_position}"] = contacts

        positions = int(self.combo_box_positions.currentText())
        if self.current_position == positions:
            QMessageBox.information(self, "Информация", f"Вы выбрали {positions} положения")
        else:
            self.current_position += 1
            self.setWindowTitle(f"Добавить переключатель - Положение {self.current_position}")
            self.table.clearContents()

            if f"position_{self.current_position}" in self.switch_data:
                contacts = self.switch_data[f"position_{self.current_position}"]
                for row, (contact1, contact2) in enumerate(contacts):
                    self.table.setItem(row, 0, QTableWidgetItem(str(contact1)))
                    self.table.setItem(row, 1, QTableWidgetItem(str(contact2)))

    def go_to_previous_position(self):
        if self.current_position > 1:
            self.current_position -= 1
            self.setWindowTitle(f"Добавить переключатель - Положение {self.current_position}")
            self.table.clearContents()

            if f"position_{self.current_position}" in self.switch_data:
                contacts = self.switch_data[f"position_{self.current_position}"]
                for row, (contact1, contact2) in enumerate(contacts):
                    self.table.setItem(row, 0, QTableWidgetItem(str(contact1)))
                    self.table.setItem(row, 1, QTableWidgetItem(str(contact2)))

    def save_switch(self):
        self.switch_data["vendor_code"] = self.line_edit_vendor_code.text()
        self.switch_data["positions"] = int(self.combo_box_positions.currentText())

        filename = "switches_data.json"
        try:
            with open(filename, "r") as file:
                data = json.load(file)  # Загружаем существующие данные из файла
        except FileNotFoundError:
            data = []  # Если файл не найден, начинаем с пустого списка
        data.append(self.switch_data)  # Добавляем новый переключатель к данным
        with open(filename, "w") as file:
            json.dump(data, file, indent=4,
                      separators=(", ", ": "))  # Записываем все данные в файл с желаемым форматированием

        QMessageBox.information(self, "Информация", "Переключатель сохранен")

        self.close()


