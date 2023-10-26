import serial
from utils import get_contact_count, get_switch_data, read_data, send_command, check_switch, process_position, \
    read_data_return
from time import sleep
from utils import update_user_tests_counter

RESET_SIGNAL = b'\x80'
READY_SIGNAL = b'\x87'
START_MEASUREMENT_COMMAND = b'\x82'
CORRECTNESS_COMMAND = b'\x83'
INCORRECTNESS_COMMAND = b'\x84'
CORRECT_ALL_COMMAND = b'\x85'
CONTACTS_COUNT = b'\x88'
NEXT_POSITION_SIGNAL = b'\x89'
SPACE_KEY = b' '


def data_processing(port, vendor_code, stop_event, instance, username):
    reset_signal_received = False

    baudrate = 256000
    ser = serial.Serial(port, baudrate)
    while True:
        instance.add_message_to_widget('Старт теста! Нажмите пробел')
        read_data(ser, RESET_SIGNAL, stop_event)
        if stop_event.is_set():
            stop_event.clear()
            break
        instance.tests_counter[username] = instance.tests_counter.get(username, 0) + 1
        update_user_tests_counter(username, instance.tests_counter[username])
        instance.clear_message_widget()
        instance.update_tests_counter_label()
        instance.retrieve_switch_data()
        while True:
            if stop_event.is_set():
                stop_event.clear()
                break
            if reset_signal_received:
                reset_signal_received = False
            switch_data = get_switch_data(vendor_code)
            contacts_count = get_contact_count(vendor_code)

            if contacts_count is not None:
                print("Выставление количества контактов...")
                instance.add_message_to_widget("Выставление количества контактов...")
                send_command(ser, b'\x88')
                sleep(0.5)

                contacts_count_command = bytes([contacts_count])
                ser.write(contacts_count_command)
                print("Команда выставления количества контактов отправлена.")
            else:
                print("Не удалось получить данные о количестве контактов.")
            if read_data_return(ser, READY_SIGNAL, stop_event) == RESET_SIGNAL:
                if stop_event.is_set():
                    stop_event.clear()
                    break
                continue

            correct_positions = []
            incorrect_positions = []

            for position in range(1, switch_data['positions'] + 1):
                send_command(ser, START_MEASUREMENT_COMMAND)
                if process_position(ser, switch_data, contacts_count, position, instance):
                    correct_positions.append(position)
                else:
                    incorrect_positions.append(position)
                if position == switch_data['positions']:
                    break

                check_result = check_switch(ser, stop_event)
                if stop_event.is_set():
                    break
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
                instance.add_message_to_widget("\nПереключатель полностью годен.")
                send_command(ser, CORRECT_ALL_COMMAND)
            else:
                print("Переключатель негоден. Некорректные положения:")
                instance.add_message_to_widget("\nПереключатель негоден. Некорректные положения:")
                for position in range(1, switch_data['positions'] + 1):
                    if position in incorrect_positions:
                        print(f"Положение {position}")
                        instance.add_message_to_widget(f"Положение {position}")

            break
    ser.close()
    instance.add_message_to_widget('Порт закрыт, тестирование завершено')
