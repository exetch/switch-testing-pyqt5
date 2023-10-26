import serial.tools.list_ports
import json
import math
from time import sleep
import pickle
import keyboard

SPACE_KEY = b' '
NEXT_POSITION_SIGNAL = b'\x89'
CORRECTNESS_COMMAND = b'\x83'
INCORRECTNESS_COMMAND = b'\x84'
RESET_SIGNAL = b'\x80'
FILENAME = 'switches_data.json'


def get_open_com_ports():
    ports = serial.tools.list_ports.comports()
    open_com_ports = []
    for port in ports:
        if port.hwid:
            open_com_ports.append(port.device)
    return open_com_ports


def load_switch_data(filename):
    with open(filename) as file:
        data = json.load(file)
        return data


def get_contact_count(vendor_code):
    data = load_switch_data(FILENAME)

    switch = next((switch for switch in data if switch['vendor_code'] == vendor_code), None)
    if switch:
        max_contacts = max(
            (max((max(position_data, default=0) for position_data in switch.get(f'position_{i}', [])), default=0)) for i
            in range(1, switch.get('positions', 0) + 1))
        return min(math.ceil(max_contacts / 4) * 4, 48)

    return None


def get_switch_data(vendor_code):
    switches_data = load_switch_data(FILENAME)
    for switch in switches_data:
        if switch['vendor_code'] == vendor_code:
            return switch

    return None


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
            contact_pair = [contact1, contact2]
            if (
                    contact_pair not in switch_data
                    and measured_data[contact1][contact2] == 1
            ):
                # Контакты замкнуты, но должны быть разомкнуты
                incorrect_closed.append((contact1, contact2))

    return incorrect_closed, incorrect_opened


def read_data(ser, expected_data, stop_event):
    while True:
        if stop_event.is_set() or keyboard.is_pressed(' '):
            sleep(0.05)
            break

        # if ser.in_waiting > 0:
        #     data = ser.read()
        #     if data == expected_data:
        #         break




def read_data_return(ser, expected_data, stop_event):
    while True:
        if stop_event.is_set() or keyboard.is_pressed(' '):
            sleep(0.05)
            break

        if ser.in_waiting > 0:
            data = ser.read()
            if data == expected_data:
                break
            elif data == RESET_SIGNAL:
                print('Сигнал сброс получен!')
                return RESET_SIGNAL

    return expected_data
def send_command(ser, command):
    sleep(0.05)
    ser.write(command)


def check_switch(ser, stop_event):
    while True:
        if stop_event.is_set() or keyboard.is_pressed(' '):
            sleep(0.05)
            break

        if ser.in_waiting > 0:
            data = ser.read()
            if data == NEXT_POSITION_SIGNAL:
                break
            elif data == RESET_SIGNAL:
                print('Сигнал сброс получен!')
                return RESET_SIGNAL
            return data
def process_position(ser, switch_data, contacts_count, position, instance):
    measured_data = {}
    for i in range(1, contacts_count):
        first_contact_byte = ser.read()
        first_contact_number = first_contact_byte[0] & 0x3F

        contact_status = {}
        while True:
            contact_byte = ser.read()
            if contact_byte == b'\x86':
                break

            contact_number = contact_byte[0] & 0x3F

            contact_state = (contact_byte[0] & 0xC0) >> 6
            contact_status[contact_number] = contact_state

        measured_data[first_contact_number] = contact_status

    incorrect_closed, incorrect_opened = check_position(switch_data[f'position_{position}'], measured_data)
    instance.updateTableSignal.emit(position, switch_data[f'position_{position}'], measured_data)


    if len(incorrect_closed) == 0 and len(incorrect_opened) == 0:
        print(f"В положении {position} все хорошо. Положение собрано корректно")
        instance.add_message_to_widget(f"В положении {position} все хорошо. Положение собрано корректно")
        send_command(ser, CORRECTNESS_COMMAND)
        return position
    else:
        print(f"Положение {position} собрано некорректно. Некорректные контакты:")
        instance.add_message_to_widget(f"\nПоложение {position} собрано некорректно. Некорректные контакты:")
        for closed_contact in incorrect_closed:
            print(f"Замкнуты контакты {closed_contact[0]} и {closed_contact[1]}")
            instance.add_message_to_widget(f"Положение {position} собрано некорректно. Некорректные контакты:")
        for opened_contact in incorrect_opened:
            print(f"Разомкнуты контакты {opened_contact[0]} и {opened_contact[1]}")
            instance.add_message_to_widget(f"Разомкнуты контакты {opened_contact[0]} и {opened_contact[1]}")
        send_command(ser, INCORRECTNESS_COMMAND)
        return []



def load_saved_vendor_code(combo_box_vendor_code):
    try:
        with open('saved_vendor_code.pickle', 'rb') as file:
            saved_code = pickle.load(file)
        if saved_code:
            combo_box_vendor_code.setCurrentText(saved_code)
    except (FileNotFoundError, EOFError):
        pass



def save_vendor_code(combo_box_vendor_code):
    vendor_code = combo_box_vendor_code.currentText()
    with open("saved_vendor_code.pickle", 'wb') as file:
        pickle.dump(vendor_code, file)

def save_selected_port(combo_box_ports):
    selected_port = combo_box_ports.currentText()
    with open('saved_port.pickle', 'wb') as file:
        pickle.dump(selected_port, file)

def load_saved_port(combo_box_ports):
    try:
        with open('saved_port.pickle', 'rb') as file:
            saved_port = pickle.load(file)
        if saved_port:
            index = combo_box_ports.findText(saved_port)
            if index != -1:
                combo_box_ports.setCurrentIndex(index)
    except (FileNotFoundError, EOFError):
        pass

def save_tests_counter(tests_counter):
    with open("tests_counter.pkl", "wb") as file:
        pickle.dump(tests_counter, file)

def load_tests_counter():
    try:
        with open("tests_counter.pkl", "rb") as file:
            if file.peek(1):
                return pickle.load(file)
            else:
                return {}
    except (FileNotFoundError, EOFError):
        return {}

def update_user_tests_counter(username, tests_count):
    tests_counter = load_tests_counter()
    tests_counter[username] = tests_count
    save_tests_counter(tests_counter)

