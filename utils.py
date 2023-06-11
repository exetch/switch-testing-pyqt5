import serial.tools.list_ports
import json
import math
from time import sleep

SPACE_KEY = b' '
NEXT_POSITION_SIGNAL = b'\x89'
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


def read_data(ser, expected_data):
    while True:
        data = ser.read()
        if data == expected_data:
            break


def send_command(ser, command):
    sleep(0.5)
    ser.write(command)


def check_switch(ser):
    while True:
        data = ser.read()
        if data == NEXT_POSITION_SIGNAL or data == SPACE_KEY:
            break
