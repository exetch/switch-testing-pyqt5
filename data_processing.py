import logging
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

logging.basicConfig(filename='data_processing.log', level=logging.ERROR, encoding='utf-8')
def data_processing(port, vendor_code, instance):
    # switch_data = get_switch_data(vendor_code)
    # sleep(1)
    #
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
    # measured_data_2= {1: {2: 1, 3: 1, 4: 0}, 2: {3: 0, 4: 1}, 3: {4: 1}}
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
    # instance.tests_counter += 1
    # instance.update_tests_counter_label()
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
    reset_signal_received = False

    baudrate = 256000
    ser = serial.Serial(port, baudrate)
    try:
        while True:
            read_data(ser, RESET_SIGNAL)

            print('Сигнал сброс получен!')
            instance.add_message_to_widget('Сигнал сброс получен!')
            instance.tests_counter += 1
            instance.update_tests_counter_label()
            instance.retrieve_switch_data()
            while True:
                if reset_signal_received:
                    reset_signal_received = False
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
                    sleep(0.5)
                    if process_position(ser, switch_data, contacts_count, position, instance):
                        correct_positions.append(position)
                    if position == switch_data['positions']:
                        break

                    check_result = check_switch(ser)
                    if check_result == RESET_SIGNAL:
                        reset_signal_received = True
                        break
                if reset_signal_received:
                    instance.tests_counter += 1
                    instance.update_tests_counter_label()
                    instance.retrieve_switch_data()
                    instance.add_message_to_widget('Сигнал сброс получен!')
                    continue
                if len(correct_positions) == switch_data['positions']:
                    print("Переключатель полностью годен.")
                    instance.add_message_to_widget("Переключатель полностью годен.")
                    send_command(ser, CORRECT_ALL_COMMAND)
                else:
                    print("Переключатель негоден. Некорректные положения:")
                    instance.add_message_to_widget("Переключатель негоден. Некорректные положения:")
                    for position in range(1, switch_data['positions'] + 1):
                        if position not in correct_positions:
                            print(f"Положение {position}")
                            instance.add_message_to_widget(f"Положение {position}")

                break
    except Exception as e:
        logging.exception('An error occurred during data processing:')
