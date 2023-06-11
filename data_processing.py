import math
import json
import serial
from time import sleep


def get_contact_count(vendor_code):
    with open('switches_data.json') as file:
        data = json.load(file)

    switch = next((switch for switch in data if switch['vendor_code'] == vendor_code), None)
    if switch:
        max_contacts = max(
            (max((max(position_data, default=0) for position_data in switch.get(f'position_{i}', [])), default=0)) for i
            in range(1, switch.get('positions', 0) + 1))
        return min(math.ceil(max_contacts / 4) * 4, 48)

    return None


def get_switch_data(vendor_code):
    with open('switches_data.json') as f:
        switches_data = json.load(f)

    for switch in switches_data:
        if switch['vendor_code'] == vendor_code:
            return switch

    return None


# Функция для проверки корректности положений переключателя
def check_position(switch_data, measured_data):
    incorrect_closed = []
    incorrect_opened = []

    for closed_contacts in switch_data:
        contact1, contact2 = closed_contacts

        if (
                contact1 in measured_data
                and contact2 in measured_data[contact1]
                and measured_data[contact1][contact2] == 0
        ):
            incorrect_opened.append(closed_contacts)

    for contact1 in measured_data:
        for contact2 in measured_data[contact1]:
            if (
                    (contact1, contact2) not in switch_data
                    and measured_data[contact1][contact2] == 0
            ):
                # Контакты разомкнуты, но не должны быть разомкнуты
                incorrect_closed.append((contact1, contact2))

    return incorrect_closed, incorrect_opened


def run_data_processing(port, vendor_code, instance):
    print('Привет!')
    print(port)
    print(vendor_code)
    baudrate = 9600
    ser = serial.Serial(port, baudrate)
    reset_signal = b'\x80'  # Байтовая последовательность "10000000"
    while True:
        # Чтение данных из порта
        data = ser.read()

        if data == reset_signal:
            print("Сигнал сброса принят!")
            break
    # Получение данных о переключателе
    switch_data = get_switch_data(vendor_code)
    # Выставление количества контактов
    contacts_count = get_contact_count(vendor_code)

    if contacts_count is not None:
        print("Выставление количества контактов...")
        # command = bytes([0x88, contacts_count])
        ser.write(b'\x88')
        sleep(0.5)
        ser.write(bytes([contacts_count]))
        print("Команда выставления количества контактов отправлена.")
    else:
        print("Не удалось получить данные о количестве контактов.")

    # Ожидание сигнала "готов к измерению" (10000111)
    ready_signal = b'\x87'  # Байтовая последовательность "10000111"

    while True:
        # Чтение данных из порта
        data = ser.read()

        if data == ready_signal:
            print("Сигнал 'готов к измерению' принят!")
            break

    # Подготовка команды "10000010" для начала измерений
    sleep(0.5)
    start_measurement_command = b'\x82'
    ser.write(start_measurement_command)

    correct_positions = []  # Список для хранения номеров корректных положений
    for position in range(1, switch_data['positions'] + 1):
        measured_data = {}  # Словарь для хранения измеренных данных

        for i in range(1, contacts_count):
            # Принятие первого байта с номером первого контакта "01ХХХХХХ"
            first_contact_byte = ser.read()
            print(first_contact_byte)

            first_contact_number = first_contact_byte[0] & 0x3F  # Младшие 6 битов

            contact_status = {}  # Словарь для хранения состояний контактов

            while True:
                # Принятие последующих байтов с состоянием контактов и номером следующего контакта
                contact_byte = ser.read()
                print(contact_byte)

                if contact_byte == b'\x86':
                    # Принят сигнал окончания передачи "10000110"
                    break

                contact_number = contact_byte[0] & 0x3F  # Младшие 6 битов
                contact_state = (contact_byte[0] & 0xC0) >> 6  # Старшие 2 бита

                contact_status[contact_number] = contact_state

            measured_data[first_contact_number] = contact_status
            print(measured_data)

        # Проверка данных согласно настройкам переключателя
        incorrect_closed, incorrect_opened = check_position(switch_data[f'position_{position}'], measured_data)
        instance.update_table_with_results(position, switch_data[f'position_{position}'], measured_data)  # Вызов метода на экземпляре

        if len(incorrect_closed) == 0 and len(incorrect_opened) == 0:
            print(f"В положении {position} все хорошо. Положение собрано корректно")
            correct_positions.append(position)
            # Отправить команду о правильности положения "10000011"
            correctness_command = b'\x83'
            sleep(0.5)
            ser.write(correctness_command)
        else:
            print(f"Положение {position} собрано некорректно. Некорректные контакты:")
            for closed_contact in incorrect_closed:
                print(f"Замкнуты контакты {closed_contact[0]} и {closed_contact[1]}")
            for opened_contact in incorrect_opened:
                print(f"Разомкнуты контакты {opened_contact[0]} и {opened_contact[1]}")
            # Отправить команду о неправильности положения "10000100"
            incorrectness_command = b'\x84'
            sleep(0.5)
            ser.write(incorrectness_command)

        # Переключение на следующее положение или завершение программы
        next_position_signal = b'\x89'  # Байтовая последовательность "10001001"
        space_key = b' '

        while True:
            data = ser.read()

            if data == next_position_signal or data == space_key:
                break

    if len(correct_positions) == switch_data['positions']:
        print("Переключатель полностью годен.")
        # Отправить команду о правильности всех положений "10000101"
        correct_all_command = b'\x85'
        sleep(0.5)
        ser.write(correct_all_command)
    else:
        print("Переключатель негоден. Некорректные положения:")
        for position in range(1, switch_data['positions'] + 1):
            if position not in correct_positions:
                print(f"Положение {position}")
