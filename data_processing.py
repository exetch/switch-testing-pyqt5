import serial
from utils import get_contact_count, get_switch_data, read_data, send_command, check_switch, process_position, \
    read_data_return
from time import sleep

RESET_SIGNAL = b'\x80'
READY_SIGNAL = b'\x87'
START_MEASUREMENT_COMMAND = b'\x82'
CORRECTNESS_COMMAND = b'\x83'
INCORRECTNESS_COMMAND = b'\x84'
CORRECT_ALL_COMMAND = b'\x85'
CONTACTS_COUNT = b'\x88'
NEXT_POSITION_SIGNAL = b'\x89'
SPACE_KEY = b' '


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


def run_data_processing(port, vendor_code, instance):
    # switch_data = get_switch_data(vendor_code)
    # sleep(1)
    # print('данные получены!')
    # correct_positions = []
    # measured_data = {1: {2: 0, 3: 0, 4: 0}, 2: {3: 0, 4: 1}, 3: {4: 0}}
    # sleep(1)
    # incorrect_closed, incorrect_opened = check_position(switch_data[f'position_{1}'], measured_data)
    # instance.updateTableSignal.emit(1, switch_data[f'position_{1}'], measured_data)
    # if incorrect_closed or incorrect_opened:
    #
    #     print('Положение 1 негодно')
    #     for closed_contact in incorrect_closed:
    #         print(f"Замкнуты контакты {closed_contact[0]} и {closed_contact[1]}")
    #     for opened_contact in incorrect_opened:
    #         print(f"Разомкнуты контакты {opened_contact[0]} и {opened_contact[1]}")
    #
    # else:
    #     print("Положение 1 годно")
    #     correct_positions.append(1)
    #
    #
    # measured_data_2= {1: {2: 1, 3: 1, 4: 0}, 2: {3: 0, 4: 1}, 3: {4: 0}}
    # sleep(1)
    # incorrect_closed_2, incorrect_opened_2 = check_position(switch_data[f'position_{2}'], measured_data_2)
    # instance.updateTableSignal.emit(2, switch_data[f'position_{2}'], measured_data_2)
    # if incorrect_closed_2 or incorrect_opened_2:
    #
    #     print('Положение 2 негодго')
    #     for closed_contact in incorrect_closed_2:
    #         print(f"Замкнуты контакты {closed_contact[0]} и {closed_contact[1]}")
    #     for opened_contact in incorrect_opened_2:
    #         print(f"Разомкнуты контакты {opened_contact[0]} и {opened_contact[1]}")
    # else:
    #     print("Положение 2 годно")
    #     correct_positions.append(2)
    #
    #
    #
    #
    # if len(correct_positions) == switch_data['positions']:
    #     print("Переключатель полностью годен.")
    # else:
    #     print("Переключатель негоден. Некорректные положения:")
    #     for position in range(1, switch_data['positions'] + 1):
    #         if position not in correct_positions:
    #             print(f"Положение {position}")
    while True:
        baudrate = 9600
        ser = serial.Serial(port, baudrate)

        read_data(ser, RESET_SIGNAL)
        print('Сигнал сброс получен!')
        while True:
            switch_data = get_switch_data(vendor_code)
            contacts_count = get_contact_count(vendor_code)

            if contacts_count is not None:
                print("Выставление количества контактов...")
                send_command(ser, b'\x88')
                sleep(0.5)

                contacts_count_command = bytes([contacts_count])
                ser.write(contacts_count_command)
                print("Команда выставления количества контактов отправлена.")
            else:
                print("Не удалось получить данные о количестве контактов.")

            if read_data_return(ser, READY_SIGNAL) == RESET_SIGNAL:
                continue

            correct_positions = []

            for position in range(1, switch_data['positions'] + 1):
                send_command(ser, START_MEASUREMENT_COMMAND)
                if process_position(ser, switch_data, contacts_count, position, instance):
                    correct_positions.append(position)
                if position == switch_data['positions']:
                    break

                check_switch(ser)

            if len(correct_positions) == switch_data['positions']:
                print("Переключатель полностью годен.")
                send_command(ser, CORRECT_ALL_COMMAND)
            else:
                print("Переключатель негоден. Некорректные положения:")
                for position in range(1, switch_data['positions'] + 1):
                    if position not in correct_positions:
                        print(f"Положение {position}")
