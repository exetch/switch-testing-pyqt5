import serial
from time import sleep
from utils import get_switch_data, get_contact_count, check_position

RESET_SIGNAL = b'\x80'
READY_SIGNAL = b'\x87'
START_MEASUREMENT_COMMAND = b'\x82'
CORRECTNESS_COMMAND = b'\x83'
INCORRECTNESS_COMMAND = b'\x84'
NEXT_POSITION_SIGNAL = b'\x89'
SPACE_KEY = b' '
CORRECT_ALL_COMMAND = b'\x85'


def read_data(ser, expected_data):
    while True:
        data = ser.read()
        if data == expected_data:
            break


def send_command(ser, command):
    sleep(0.5)
    ser.write(command)


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
    instance.update_table_with_results(position, switch_data[f'position_{position}'], measured_data)

    if len(incorrect_closed) == 0 and len(incorrect_opened) == 0:
        print(f"В положении {position} все хорошо. Положение собрано корректно")
        send_command(ser, CORRECTNESS_COMMAND)
        return position
    else:
        print(f"Положение {position} собрано некорректно. Некорректные контакты:")
        for closed_contact in incorrect_closed:
            print(f"Замкнуты контакты {closed_contact[0]} и {closed_contact[1]}")
        for opened_contact in incorrect_opened:
            print(f"Разомкнуты контакты {opened_contact[0]} и {opened_contact[1]}")
        send_command(ser, INCORRECTNESS_COMMAND)
        return None




def check_switch(ser):
    while True:
        data = ser.read()
        if data == NEXT_POSITION_SIGNAL or data == SPACE_KEY:
            break


def run_data_processing(port, vendor_code, instance):
    baudrate = 9600
    ser = serial.Serial(port, baudrate)

    read_data(ser, RESET_SIGNAL)

    switch_data = get_switch_data(vendor_code)
    contacts_count = get_contact_count(vendor_code)

    if contacts_count is not None:
        print("Выставление количества контактов...")
        send_command(ser, b'\x88')
        sleep(0.5)
        send_command(ser, bytes([contacts_count]))
        print("Команда выставления количества контактов отправлена.")
    else:
        print("Не удалось получить данные о количестве контактов.")

    read_data(ser, READY_SIGNAL)

    send_command(ser, START_MEASUREMENT_COMMAND)

    correct_positions = []

    for position in range(1, switch_data['positions'] + 1):
        correct_position = process_position(ser, switch_data, contacts_count, position, instance)
        if correct_position is not None:
            correct_positions.append(correct_position)
        check_switch(ser)

    if len(correct_positions) == switch_data['positions']:
        print("Переключатель полностью годен.")
        send_command(ser, CORRECT_ALL_COMMAND)
    else:
        print("Переключатель негоден. Некорректные положения:")
        for position in range(1, switch_data['positions'] + 1):
            if position not in correct_positions:
                print(f"Положение {position}")
