from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QDialog, QLabel, QLineEdit, QVBoxLayout, QPushButton, QComboBox, QMessageBox, QCompleter
from PyQt5.QtCore import Qt
import json

class AddSwitchDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
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

        self.table = QTableWidget(48, 2)
        self.table.setHorizontalHeaderLabels(["Контакт 1", "Контакт 2"])
        self.table.verticalHeader().setVisible(False)

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

        self.current_position = 1
        self.switch_data = {
            "vendor_code": "",
            "positions": 0,
            "position_1": []
        }

        self.setWindowTitle(f"Добавить переключатель - Положение {self.current_position}")

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
                data = json.load(file)
        except FileNotFoundError:
            data = []
        data.append(self.switch_data)
        with open(filename, "w", encoding='utf-8') as file:
            json.dump(data, file, indent=4,
                      separators=(", ", ": "))
        self.parent().update_vendor_selection()
        QMessageBox.information(self, "Информация", "Переключатель сохранен")

        self.close()

class EditSwitchDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Редактировать переключатель")
        self.setGeometry(200, 200, 600, 500)

        self.label_vendor_code = QLabel("Введите артикул переключателя:", self)
        self.line_edit_vendor_code = QLineEdit(self)
        self.line_edit_vendor_code.setCompleter(self.create_completer())

        self.button_search = QPushButton("Поиск", self)
        self.button_search.clicked.connect(self.search_switch)

        self.label_positions = QLabel("Выберите количество положений:", self)
        self.combo_box_positions = QComboBox(self)
        self.combo_box_positions.addItems(["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"])

        self.button_next_position = QPushButton("Сохранить положение и перейти к следующему", self)
        self.button_save_switch = QPushButton("Сохранить переключатель", self)
        self.button_previous_position = QPushButton("Вернуться к предыдущему положению", self)

        self.table = QTableWidget(48, 2)
        self.table.setHorizontalHeaderLabels(["Контакт 1", "Контакт 2"])
        self.table.verticalHeader().setVisible(False)

        layout = QVBoxLayout()
        layout.addWidget(self.label_vendor_code)
        layout.addWidget(self.line_edit_vendor_code)
        layout.addWidget(self.button_search)
        layout.addWidget(self.label_positions)
        layout.addWidget(self.combo_box_positions)
        layout.addWidget(self.table)
        layout.addWidget(self.button_next_position)
        layout.addWidget(self.button_previous_position)
        layout.addWidget(self.button_save_switch)

        self.setLayout(layout)

        self.current_position = 1
        self.switch_data ={}

        self.button_next_position.clicked.connect(self.save_and_next_position)
        self.button_save_switch.clicked.connect(self.save_switch)
        self.button_previous_position.clicked.connect(self.go_to_previous_position)

    def create_completer(self):
        with open('switches_data.json', 'r') as file:
            data = json.load(file)
            vendor_codes = [switch['vendor_code'] for switch in data]
            completer = QCompleter(vendor_codes)
            completer.setCaseSensitivity(Qt.CaseInsensitive)
            return completer

    def search_switch(self):
        vendor_code = self.line_edit_vendor_code.text()

        with open('switches_data.json', 'r') as file:
            data = json.load(file)
            matching_switches = [switch for switch in data if switch['vendor_code'] == vendor_code]
            if matching_switches:
                self.switch_data = matching_switches[0]
                self.line_edit_vendor_code.setEnabled(False)
                self.line_edit_vendor_code.setText(vendor_code)
                self.combo_box_positions.setCurrentText(
                    str(self.switch_data['positions']))
                self.populate_table()
                self.setWindowTitle(f"Редактировать переключатель - {vendor_code} (Положение 1)")
            else:
                QMessageBox.critical(self, "Ошибка", "Переключатель не найден")

    def populate_table(self):
        positions = self.switch_data['positions']

        self.table.clearContents()

        if positions > 1:
            position_key = f"position_{self.current_position}"
            contacts = self.switch_data[position_key]

            if contacts:
                for row, contact in enumerate(contacts):
                    contact_1 = QTableWidgetItem(str(contact[0]))
                    contact_2 = QTableWidgetItem(str(contact[1]))
                    self.table.setItem(row, 0, contact_1)
                    self.table.setItem(row, 1, contact_2)
            else:
                self.table.clearContents()

    def save_and_next_position(self):
        contacts = []
        for row in range(2):
            contact1_item = self.table.item(row, 0)
            contact2_item = self.table.item(row, 1)
            if contact1_item is not None and contact2_item is not None:
                contact1 = int(contact1_item.text())
                contact2 = int(contact2_item.text())
                contacts.append([contact1, contact2])

        self.switch_data[f"position_{self.current_position}"] = contacts

        positions = int(self.combo_box_positions.currentText())
        if self.current_position == positions:
            QMessageBox.information(self, "Информация", f"Вы выбрали {positions} положений")
        else:
            self.current_position += 1
            self.setWindowTitle(
                f"Редактировать переключатель - {self.switch_data['vendor_code']} (Положение {self.current_position})")
            self.table.clearContents()

            if f"position_{self.current_position}" in self.switch_data:
                contacts = self.switch_data[f"position_{self.current_position}"]
                for row, (contact1, contact2) in enumerate(contacts):
                    self.table.setItem(row, 0, QTableWidgetItem(str(contact1)))
                    self.table.setItem(row, 1, QTableWidgetItem(str(contact2)))

    def go_to_previous_position(self):
        if self.current_position > 1:
            self.current_position -= 1
            self.setWindowTitle(
                f"Редактировать переключатель - {self.switch_data['vendor_code']} (Положение {self.current_position})")
            self.table.clearContents()

            if f"position_{self.current_position}" in self.switch_data:
                contacts = self.switch_data[f"position_{self.current_position}"]
                for row, (contact1, contact2) in enumerate(contacts):
                    self.table.setItem(row, 0, QTableWidgetItem(str(contact1)))
                    self.table.setItem(row, 1, QTableWidgetItem(str(contact2)))

    def save_switch(self):
        positions = int(self.combo_box_positions.currentText())

        for position in range(positions + 1, self.switch_data['positions'] + 1):
            if f"position_{position}" in self.switch_data:
                del self.switch_data[f"position_{position}"]

        contacts = []
        for row in range(24):
            contact1_item = self.table.item(row, 0)
            contact2_item = self.table.item(row, 1)
            if contact1_item is not None and contact2_item is not None:
                contact1 = int(contact1_item.text())
                contact2 = int(contact2_item.text())
                contacts.append([contact1, contact2])

        self.switch_data['positions'] = positions
        self.switch_data[f"position_{self.current_position}"] = contacts

        with open('switches_data.json', 'r', encoding='utf-8') as file:
            data = json.load(file)

        for i, switch in enumerate(data):
            if switch['vendor_code'] == self.switch_data['vendor_code']:
                data[i] = self.switch_data
                break

        with open('switches_data.json', 'w') as file:
            json.dump(data, file, indent=4, separators=(", ", ": "))

        QMessageBox.information(self, "Информация", "Переключатель сохранен")

        self.current_position = 1
        self.switch_data = None
        self.line_edit_vendor_code.setEnabled(True)
        self.line_edit_vendor_code.clear()
        self.combo_box_positions.setCurrentIndex(0)
        self.table.clearContents()
        self.setWindowTitle("Редактировать переключатель")

class DelSwitchDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Удаление переключателя")
        self.label_vendor_code = QLabel("Введите артикул для удаления переключателя:", self)
        self.line_edit_vendor_code = QLineEdit(self)
        self.line_edit_vendor_code.setCompleter(self.create_completer())

        self.button_delete = QPushButton("Удалить", self)
        self.button_delete.clicked.connect(self.delete_switch)

        layout = QVBoxLayout()
        layout.addWidget(self.label_vendor_code)
        layout.addWidget(self.line_edit_vendor_code)
        layout.addWidget(self.button_delete)
        self.setLayout(layout)

    def create_completer(self):
        with open('switches_data.json', 'r') as file:
            data = json.load(file)
            vendor_codes = [switch['vendor_code'] for switch in data]
            completer = QCompleter(vendor_codes)
            completer.setCaseSensitivity(Qt.CaseInsensitive)
            return completer

    def show_confirm_dialog(self, vendor_code):
        reply = QMessageBox.question(self, "Подтверждение удаления",
                                     f"Вы действительно хотите удалить переключатель '{vendor_code}'?",
                                     QMessageBox.Yes | QMessageBox.No)
        return reply == QMessageBox.Yes

    def delete_switch(self):
        vendor_code = self.line_edit_vendor_code.text()
        with open('switches_data.json', 'r') as file:
            data = json.load(file)
        found = False
        for i, switch in enumerate(data):
            if switch['vendor_code'] == vendor_code:
                found = True
                break
        if found:
            if self.show_confirm_dialog(vendor_code):
                del data[i]

                with open('switches_data.json', 'w') as file:
                    json.dump(data, file, indent=4)
                self.parent().update_vendor_selection()
                QMessageBox.information(self, "Удаление переключателя", f"Переключатель '{vendor_code}' успешно удален.")
                self.line_edit_vendor_code.clear()
        else:
            QMessageBox.warning(self, "Удаление переключателя", "Переключатель не найден.")

class ContactWidgetItem(QTableWidgetItem):
    def __init__(self, contacts):
        super().__init__()
        self.contacts = contacts
        self.setFlags(self.flags() & ~Qt.ItemIsEditable)

    def setData(self, role, value):
        if role == Qt.UserRole:
            self.contacts = value

    def data(self, role):
        if role == Qt.DisplayRole:
            return ", ".join(str(contact) for contact in self.contacts)

        return super().data(role)

