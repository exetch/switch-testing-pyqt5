from PyQt5.QtWidgets import QMainWindow, QToolBar, QAction, QMenu, QWidget, QLabel, QLineEdit, QCompleter, QTableWidget, \
    QTableWidgetItem, QVBoxLayout, QPushButton, QApplication, QHBoxLayout, QComboBox, QSplitter, QSizePolicy, QTextEdit, \
    QScrollArea
from PyQt5.QtCore import Qt, QMetaObject, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QColor, QFont
import json
import threading
import sys
from utils import get_open_com_ports, load_saved_vendor_code, save_vendor_code, save_selected_port, load_saved_port, \
    save_tests_counter, load_tests_counter
from configuration import EditSwitchDialog, AddSwitchDialog, DelSwitchDialog
from data_processing import data_processing
from users import add_user, del_user



class MainWindow(QMainWindow):
    updateTableSignal = pyqtSignal(int, list, dict)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("CamSwitch Tester")
        self.setGeometry(100, 100, 1620, 800)
        self.init_toolbar()  # Инициализация главной панели инструментов
        self.init_vendor_selection()  # Инициализация панели выбора переключателя
        self.init_table_widget()  # Инициализация таблицы для отображения информации о переключателе
        self.message_widget = QTextEdit()

        self.init_layout()  # Инициализация макета и добавление виджетов
        self.updateTableSignal.connect(self.update_table_with_results_slot)
        self.tests_counter = load_tests_counter()
        self.update_tests_counter_label()
        load_saved_vendor_code(self.combo_box_vendor_code)
        load_saved_port(self.combo_box_ports)
        self.stop_event = threading.Event()

    def init_toolbar(self):
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        configuration_menu = QMenu("Конфигурация", self)
        user_menu = QMenu("Пользователь", self)

        add_switch_action = QAction("Добавить переключатель", self)
        add_switch_action.triggered.connect(self.open_add_switch_dialog)
        configuration_menu.addAction(add_switch_action)

        edit_switch_action = QAction("Редактировать переключатель", self)
        edit_switch_action.triggered.connect(self.edit_switch)
        configuration_menu.addAction(edit_switch_action)

        delete_switch_action = QAction("Удалить переключатель", self)
        delete_switch_action.triggered.connect(self.open_del_switch_dialog)
        configuration_menu.addAction(delete_switch_action)

        add_user_action = QAction("Добавить пользователя", self)
        add_user_action.triggered.connect(self.add_user)
        user_menu.addAction(add_user_action)

        delete_user_action = QAction("Удалить пользователя", self)
        delete_user_action.triggered.connect(self.del_user)
        user_menu.addAction(delete_user_action)

        configuration_button = QPushButton("Конфигурация")
        configuration_button.setMenu(configuration_menu)

        user_button = QPushButton("Пользователь")
        user_button.setMenu(user_menu)

        configuration_button.clicked.connect(configuration_menu.exec_)
        user_button.clicked.connect(user_menu.exec_)

        toolbar.addWidget(configuration_button)

        toolbar.addWidget(user_button)
        space = QLabel("")
        space.setMinimumWidth(20)
        toolbar.addWidget(space)

        active_user_label = QLabel("Активный пользователь:")
        active_user_label.setMinimumWidth(170)  # Установка минимальной ширины в пикселях
        toolbar.addWidget(active_user_label)

        self.user_combobox = QComboBox()
        self.user_combobox.setFixedHeight(27)
        self.user_combobox.setFixedWidth(115)
        toolbar.addWidget(self.user_combobox)

        self.update_user_combobox()

        self.setCentralWidget(QWidget())

    def init_vendor_selection(self):
        self.vendor_selection = QWidget(self)

        vendor_selection_layout = QHBoxLayout(self.vendor_selection)

        self.label_vendor_code = QLabel("Выберите артикул переключателя:", self.vendor_selection)
        self.combo_box_vendor_code = QComboBox(self.vendor_selection)
        self.combo_box_vendor_code.setEditable(True)
        self.combo_box_vendor_code.setCompleter(self.create_completer_old())
        self.create_completer()
        self.search_button = QPushButton("Найти", self.vendor_selection)
        self.start_button = QPushButton("Старт", self.vendor_selection)
        self.stop_button = QPushButton("Стоп", self.vendor_selection)
        self.clear_button = QPushButton("Очистить консоль вывода", self.vendor_selection)
        self.reset_counter_button = QPushButton("Сброс счетчика", self.vendor_selection)

        self.label_vendor_code.setFixedWidth(210)
        self.combo_box_vendor_code.setFixedWidth(300)
        self.combo_box_vendor_code.view().setFixedHeight(500)
        self.search_button.setFixedWidth(75)
        self.start_button.setFixedWidth(75)
        self.stop_button.setFixedWidth(75)
        self.clear_button.setFixedWidth(175)

        vendor_selection_layout.addWidget(self.label_vendor_code)
        vendor_selection_layout.addWidget(self.combo_box_vendor_code)
        vendor_selection_layout.addWidget(self.search_button)
        vendor_selection_layout.addWidget(self.start_button)
        vendor_selection_layout.addWidget(self.stop_button)
        vendor_selection_layout.addWidget(self.clear_button)

        self.label_select_port = QLabel("Выберите порт:", self.vendor_selection)
        self.combo_box_ports = QComboBox(self.vendor_selection)
        self.combo_box_ports.setFixedHeight(27)

        vendor_selection_layout.addWidget(self.label_select_port)
        vendor_selection_layout.addWidget(self.combo_box_ports)

        vendor_selection_layout.addStretch(1)

        self.combo_box_vendor_code.lineEdit().returnPressed.connect(self.retrieve_switch_data)
        self.search_button.clicked.connect(self.retrieve_switch_data)
        self.search_button.clicked.connect(self.clear_message_widget)
        self.start_button.clicked.connect(self.run_data_processing)
        self.stop_button.clicked.connect(self.stop_data_processing)
        self.clear_button.clicked.connect(self.clear_message_widget)
        self.start_button.clicked.connect(self.init_layout)

        # Получаем список открытых портов и добавляем их в выпадающий список
        open_ports = get_open_com_ports()
        self.combo_box_ports.addItems(open_ports)
        vendor_selection_layout.addWidget(self.reset_counter_button)
        self.reset_counter_button.clicked.connect(self.reset_tests_counter)
        self.label_tests_counter = QLabel("Тестов выполнено: 0", self.vendor_selection)
        self.label_tests_counter.setFixedWidth(170)
        vendor_selection_layout.addWidget(self.label_tests_counter)


    def reset_tests_counter(self):
        self.tests_counter = 0
        self.update_tests_counter_label()

    def update_tests_counter_label(self):
        self.label_tests_counter.setText(f"Тестов выполнено: {self.tests_counter}")
        save_tests_counter(self.tests_counter)

    def init_table_widget(self):
        self.table_widget = QTableWidget(self)
        self.table_widget.setGeometry(0, 100, 1400, 700)
        self.table_widget.setFixedHeight(250)
        self.table_widget.verticalHeader().setVisible(False)
        header_style = "QHeaderView::section { background-color: rgb(135, 206, 250); }"  # Голубой цвет (RGB: 135, 206, 250)
        self.table_widget.setStyleSheet(header_style)

    def create_completer(self):
        with open('switches_data.json', 'r') as file:
            data = json.load(file)
            vendor_codes = [switch['vendor_code'] for switch in data]
            self.combo_box_vendor_code.addItems(vendor_codes)

    def create_completer_old(self):
        with open('switches_data.json', 'r') as file:
            data = json.load(file)
            vendor_codes = [switch['vendor_code'] for switch in data]
            completer = QCompleter(vendor_codes)
            completer.setCaseSensitivity(Qt.CaseInsensitive)
            return completer

    def retrieve_switch_data(self):
        vendor_code = self.combo_box_vendor_code.currentText()
        save_vendor_code(self.combo_box_vendor_code)
        save_selected_port(self.combo_box_ports)
        with open('switches_data.json', 'r') as file:
            data = json.load(file)
            for switch in data:
                if switch['vendor_code'] == vendor_code:
                    positions = switch['positions']
                    self.display_switch_info(positions, switch)
                    return

        self.display_switch_info(0, {})

    def display_switch_info(self, positions, switch_data):
        self.table_widget.clear()
        self.table_widget.setRowCount(positions)
        self.table_widget.setColumnCount(49)

        header_labels = ['Номер положения'] + [str(i) for i in range(1, 49)]
        self.table_widget.setHorizontalHeaderLabels(header_labels)

        for position in range(1, positions + 1):
            position_key = f"position_{position}"
            contacts = switch_data.get(position_key, [])
            self.table_widget.setItem(position - 1, 0, QTableWidgetItem(f"Положение {position}"))
            for contact_pair in contacts:
                if len(contact_pair) == 2:
                    contact1, contact2 = contact_pair
                    item = QTableWidgetItem(str(contact2))
                    item.setTextAlignment(Qt.AlignCenter)  # Установка выравнивания содержимого ячейки
                    self.table_widget.setItem(position - 1, contact1, item)

        self.table_widget.resizeColumnsToContents()
        self.table_widget.resizeRowsToContents()

        for column in range(1, 49):
            self.table_widget.horizontalHeader().setMinimumSectionSize(30)
            self.table_widget.setColumnWidth(column, 30)

    def init_layout(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(self.table_widget)

        main_layout.addWidget(self.vendor_selection)
        main_layout.addWidget(splitter)

        contact_info_widget = QWidget()
        contact_info_layout = QHBoxLayout(contact_info_widget)
        contact_info_layout.setContentsMargins(20, 10, 0, 10)

        color_mapping = {
            "green": ("Соответствует схеме", "#00FF00"),
            "red": ("Не соответствует схеме, не замкнуты", "#FF0000"),
            "yellow": ("Не соответствует схеме, замкнуты", "#FFFF00")
        }

        for color, (label_text, color_code) in color_mapping.items():
            color_rect = QLabel()
            color_rect.setFixedSize(30, 30)
            color_rect.setStyleSheet(f"background-color: {color_code};")

            color_label = QLabel(label_text)

            contact_info_layout.addWidget(color_rect)
            contact_info_layout.addWidget(color_label)

        main_layout.addWidget(contact_info_widget)
        message_scroll_area = QScrollArea()
        message_scroll_area.setWidgetResizable(True)
        message_scroll_area.setWidget(self.message_widget)

        main_layout.addWidget(message_scroll_area)

        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(10)

        self.table_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def open_add_switch_dialog(self):
        dialog = AddSwitchDialog(self)
        dialog.exec_()

    def update_vendor_selection(self):
        completer = self.create_completer()
        self.line_edit_vendor_code.setCompleter(completer)

    def edit_switch(self):
        edit_dialog = EditSwitchDialog(self)
        edit_dialog.exec_()

    def open_del_switch_dialog(self):
        dialog = DelSwitchDialog(self)
        dialog.exec_()

    def run_data_processing(self):
        port = self.combo_box_ports.currentText()
        vendor_code = self.combo_box_vendor_code.currentText()


        processing_thread = threading.Thread(
            target=data_processing, args=(port, vendor_code, self.stop_event, self)
        )
        processing_thread.start()



    def update_user_combobox(self):
        with open("users.txt", "r", encoding="utf-8") as file:
            users = [line.strip() for line in file]
        self.user_combobox.clear()
        self.user_combobox.addItems(users)

    def stop_data_processing(self):
        self.stop_event.set()
        self.retrieve_switch_data()


    def add_user(self):
        add_user(self)
        self.update_user_combobox()

    def del_user(self):
        del_user(self)
        self.update_user_combobox()

    def add_message_to_widget(self, message):
        self.message_widget.append(message)

    def clear_message_widget(self):
        QMetaObject.invokeMethod(self.message_widget, "clear")

    @pyqtSlot(int, list, dict)
    def update_table_with_results_slot(self, position, switch_data, measured_data):
        for contact_pair in switch_data:
            contact1, contact2 = contact_pair
            item = self.table_widget.item(position - 1, contact1)
            if item is not None:
                if (
                        contact1 in measured_data
                        and contact2 in measured_data[contact1]
                        and measured_data[contact1][contact2] == 1
                ):
                    item.setBackground(QColor("green"))
                elif (
                        contact1 in measured_data
                        and contact2 in measured_data[contact1]
                        and measured_data[contact1][contact2] == 0
                ):
                    item.setBackground(QColor("red"))
        for contact1 in measured_data:
            for contact2 in measured_data[contact1]:
                contact_pair = [contact1, contact2]
                if (
                        contact_pair not in switch_data
                        and measured_data[contact1][contact2] == 1
                ):
                    item = self.table_widget.item(position - 1, contact1)
                    if item is None:
                        item = QTableWidgetItem()
                        self.table_widget.setItem(position - 1, contact1,
                                                  item)
                    item.setBackground(QColor("yellow"))
                    item.setTextAlignment(Qt.AlignCenter)
                    item.setText(f"{contact2}")

    def closeEvent(self, event):
        self.stop_event.set()
        self.processing_thread.join()

        if self.ser.is_open:
            self.ser.close()

        super().closeEvent(event)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()