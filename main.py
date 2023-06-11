from PyQt5.QtWidgets import QMainWindow, QToolBar, QAction, QMenu, QWidget, QLabel, QLineEdit, QCompleter, QTableWidget, \
    QTableWidgetItem, QVBoxLayout, QPushButton, QApplication, QHBoxLayout, QComboBox, QSplitter, QSizePolicy
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
import json
from utils import get_open_com_ports
from configuration import EditSwitchDialog, AddSwitchDialog, DelSwitchDialog
from data_processing import run_data_processing
from users import add_user, del_user
from terminal import TerminalWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CamSwitch Tester")
        self.setGeometry(100, 100, 1620, 800)
        self.init_toolbar()  # Инициализация главной панели инструментов
        self.init_vendor_selection()  # Инициализация панели выбора переключателя
        self.init_table_widget()  # Инициализация таблицы для отображения информации о переключателе
        self.init_layout()  # Инициализация макета и добавление виджетов

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

        toolbar.addWidget(QLabel("Активный пользователь:"))
        self.user_combobox = QComboBox()
        self.user_combobox.setFixedHeight(27)
        toolbar.addWidget(self.user_combobox)

        self.update_user_combobox()

    def init_vendor_selection(self):
        self.vendor_selection = QWidget(self)

        vendor_selection_layout = QHBoxLayout(self.vendor_selection)

        self.label_vendor_code = QLabel("Введите артикул переключателя:", self.vendor_selection)
        self.line_edit_vendor_code = QLineEdit(self.vendor_selection)
        self.line_edit_vendor_code.setCompleter(self.create_completer())
        self.search_button = QPushButton("Найти", self.vendor_selection)
        self.start_button = QPushButton("Старт", self.vendor_selection)

        self.label_vendor_code.setFixedWidth(210)
        self.line_edit_vendor_code.setFixedWidth(300)
        self.search_button.setFixedWidth(75)
        self.start_button.setFixedWidth(75)

        vendor_selection_layout.addWidget(self.label_vendor_code)
        vendor_selection_layout.addWidget(self.line_edit_vendor_code)
        vendor_selection_layout.addWidget(self.search_button)
        vendor_selection_layout.addWidget(self.start_button)

        self.label_select_port = QLabel("Выберите порт:", self.vendor_selection)
        self.combo_box_ports = QComboBox(self.vendor_selection)
        self.combo_box_ports.setFixedHeight(27)

        vendor_selection_layout.addWidget(self.label_select_port)
        vendor_selection_layout.addWidget(self.combo_box_ports)

        vendor_selection_layout.addStretch(1)

        self.line_edit_vendor_code.returnPressed.connect(self.retrieve_switch_data)
        self.search_button.clicked.connect(self.retrieve_switch_data)
        self.start_button.clicked.connect(self.run_data_processing)

        # Получаем список открытых портов и добавляем их в выпадающий список
        open_ports = get_open_com_ports()
        self.combo_box_ports.addItems(open_ports)

    def init_table_widget(self):
        self.table_widget = QTableWidget(self)
        self.table_widget.setGeometry(0, 100, 1400, 700)
        self.table_widget.setFixedHeight(250)
        self.table_widget.verticalHeader().setVisible(False)

    def create_completer(self):
        with open('switches_data.json', 'r') as file:
            data = json.load(file)
            vendor_codes = [switch['vendor_code'] for switch in data]
            completer = QCompleter(vendor_codes)
            completer.setCaseSensitivity(Qt.CaseInsensitive)
            return completer

    def retrieve_switch_data(self):
        vendor_code = self.line_edit_vendor_code.text()
        with open('switches_data.json', 'r') as file:
            data = json.load(file)
            for switch in data:
                if switch['vendor_code'] == vendor_code:
                    positions = switch['positions']
                    self.display_switch_info(positions, switch)
                    return
        # If vendor code not found
        self.display_switch_info(0, {})

    def display_switch_info(self, positions, switch_data):
        self.table_widget.clear()
        self.table_widget.setRowCount(positions)
        self.table_widget.setColumnCount(49)

        self.table_widget.setHorizontalHeaderLabels(['Номер положения'] + [str(i) for i in range(1, 49)])

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

        splitter = QSplitter(Qt.Vertical)  # Создаем вертикальный разделитель
        splitter.addWidget(self.table_widget)  # Добавляем table_widget в разделитель

        layout = QVBoxLayout(central_widget)
        layout.addWidget(self.vendor_selection)  # Добавляем vendor_selection в макет
        layout.addWidget(splitter)  # Добавляем разделитель в макет

        # Добавляем информацию о контактах
        contact_info_widget = QWidget()
        contact_info_layout = QHBoxLayout(contact_info_widget)
        contact_info_layout.setContentsMargins(20, 10, 0, 10)

        green_rect = QLabel()
        green_rect.setFixedSize(30, 30)
        green_rect.setStyleSheet("background-color: green;")
        green_label = QLabel("Соответствует схеме")

        red_rect = QLabel()
        red_rect.setFixedSize(30, 30)
        red_rect.setStyleSheet("background-color: red;")
        red_label = QLabel("Не соответствует схеме, не замкнуты")

        yellow_rect = QLabel()
        yellow_rect.setFixedSize(30, 30)
        yellow_rect.setStyleSheet("background-color: yellow;")
        yellow_label = QLabel("Не соответствует схеме, замкнуты")

        contact_info_layout.addWidget(green_rect)
        contact_info_layout.addWidget(green_label)
        contact_info_layout.addWidget(red_rect)
        contact_info_layout.addWidget(red_label)
        contact_info_layout.addWidget(yellow_rect)
        contact_info_layout.addWidget(yellow_label)

        layout.addWidget(contact_info_widget)  # Добавляем информацию о контактах в макет

        terminal_widget = QWidget()
        terminal_layout = QVBoxLayout(terminal_widget)
        terminal_layout.setContentsMargins(0, 0, 0, 0)

        terminal_title = QLabel("Протокол теста")
        terminal_title.setStyleSheet("font-weight: bold;")

        terminal_text_edit = TerminalWindow()
        terminal_text_edit.setFixedHeight(400)

        terminal_layout.addWidget(terminal_title)
        terminal_layout.addWidget(terminal_text_edit)

        layout.addWidget(terminal_widget)
        # Добавляем кнопку для очистки окна терминала
        clear_button = QPushButton("Очистить")
        clear_button.clicked.connect(terminal_text_edit.clear_terminal)
        layout.addWidget(clear_button)

        # Устанавливаем политики размера для центрального виджета
        layout.setContentsMargins(5, 5, 5, 5)  # Устанавливаем отступы макета в 0
        layout.setSpacing(0)
        layout.addStretch(1)  # Растягиваем свободное пространство внизу

        # Устанавливаем политики размера для table_widget
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
        vendor_code = self.line_edit_vendor_code.text()

        run_data_processing(port, vendor_code, self)


    def update_user_combobox(self):
        with open("users.txt", "r", encoding="utf-8") as file:
            users = [line.strip() for line in file]
        self.user_combobox.clear()
        self.user_combobox.addItems(users)

    def add_user(self):
        add_user(self)
        self.update_user_combobox()

    def del_user(self):
        del_user(self)
        self.update_user_combobox()

    def update_table_with_results(self, position, switch_data, measured_data):
        position_key = f"position_{position}"
        contacts = switch_data.get(position_key, [])
        for contact_pair in contacts:
            if len(contact_pair) == 2:
                contact1, contact2 = contact_pair
                item = self.table_widget.item(position - 1, contact1)
                if item is not None:
                    if (
                            (contact1, contact2) in measured_data
                            and measured_data[contact1][contact2] == 0
                    ):
                        item.setBackground(QColor("red"))
                    elif (
                            (contact1, contact2) in measured_data
                            and measured_data[contact1][contact2] == 1
                    ):
                        item.setBackground(QColor("green"))
                    else:
                        item.setBackground(QColor("yellow"))


app = QApplication([])
window = MainWindow()
window.show()
app.exec()
