from PyQt5.QtWidgets import QMainWindow, QToolBar, QAction, QMenu, QWidget, QLabel, QLineEdit, QCompleter, QTableWidget, \
    QTableWidgetItem, QVBoxLayout, QPushButton, QApplication, QHBoxLayout, QComboBox
from PyQt5.QtCore import Qt
import json
from utils import get_open_com_ports
from configuration import EditSwitchDialog, AddSwitchDialog, DelSwitchDialog


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

        add_switch_action = QAction("Добавить переключатель", self)
        add_switch_action.triggered.connect(self.open_add_switch_dialog)
        configuration_menu.addAction(add_switch_action)

        edit_switch_action = QAction("Редактировать переключатель", self)
        edit_switch_action.triggered.connect(self.edit_switch)
        configuration_menu.addAction(edit_switch_action)

        delete_switch_action = QAction("Удалить переключатель", self)
        delete_switch_action.triggered.connect(self.open_del_switch_dialog)
        configuration_menu.addAction(delete_switch_action)

        toolbar.addAction(configuration_menu.menuAction())

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

        vendor_selection_layout.addWidget(self.label_select_port)
        vendor_selection_layout.addWidget(self.combo_box_ports)

        vendor_selection_layout.addStretch(1)

        self.line_edit_vendor_code.returnPressed.connect(self.retrieve_switch_data)
        self.search_button.clicked.connect(self.retrieve_switch_data)

        # Получаем список открытых портов и добавляем их в выпадающий список
        open_ports = get_open_com_ports()
        self.combo_box_ports.addItems(open_ports)

    def init_table_widget(self):
        self.table_widget = QTableWidget(self)
        self.table_widget.setGeometry(0, 100, 1400, 700)




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

        # # Добавление нижней границы к строке с заголовком
        # self.table_widget.horizontalHeader().setStyleSheet("QHeaderView::section { border-bottom: 1px solid black; }")

    def init_layout(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.addWidget(self.vendor_selection)  # Добавляем панель выбора переключателя
        layout.addWidget(self.table_widget)  # Добавляем таблицу

        layout.setContentsMargins(0, 0, 0, 0)  # Устанавливаем отступы макета в 0
        layout.setSpacing(0)


    def open_add_switch_dialog(self):
        dialog = AddSwitchDialog()
        dialog.exec_()

    def edit_switch(self):
        edit_dialog = EditSwitchDialog()
        edit_dialog.exec_()

    def open_del_switch_dialog(self):
        dialog = DelSwitchDialog(self)
        dialog.exec_()

app = QApplication([])
window = MainWindow()
window.show()
app.exec()
