import serial
from time import sleep
from utils import get_contact_count, get_switch_data, check_position, read_data, send_command, check_switch

RESET_SIGNAL = b'\x80'
READY_SIGNAL = b'\x87'
START_MEASUREMENT_COMMAND = b'\x82'
CORRECTNESS_COMMAND = b'\x83'
INCORRECTNESS_COMMAND = b'\x84'
CORRECT_ALL_COMMAND = b'\x85'
CONTACTS_COUNT = b'\x88'


def run_data_processing(port, vendor_code, instance):
    while True:
        baudrate = 9600
        ser = serial.Serial(port, baudrate)
        read_data(ser, READY_SIGNAL)
        print("Сигнал сброса принят!")
        # Получение данных о переключателе
        switch_data = get_switch_data(vendor_code)
        # Выставление количества контактов
        contacts_count = get_contact_count(vendor_code)

        if contacts_count is not None:
            print("Выставление количества контактов...")
            send_command(ser, CONTACTS_COUNT)
            ser.write(bytes([contacts_count]))
            print("Команда выставления количества контактов отправлена.")
        else:
            print("Не удалось получить данные о количестве контактов.")

        # Ожидание сигнала "готов к измерению" (10000111)
        read_data(ser, READY_SIGNAL)
        print("Сигнал 'готов к измерению' принят!")

        # Подготовка команды "10000010" для начала измерений
        send_command(ser, START_MEASUREMENT_COMMAND)

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
                # print(measured_data)

            # Проверка данных согласно настройкам переключателя
            incorrect_closed, incorrect_opened = check_position(switch_data[f'position_{position}'], measured_data)
            instance.update_table_with_results(position, switch_data[f'position_{position}'],
                                               measured_data)  # Вызов метода на экземпляре

            if len(incorrect_closed) == 0 and len(incorrect_opened) == 0:
                print(f"В положении {position} все хорошо. Положение собрано корректно")
                correct_positions.append(position)
                # Отправить команду о правильности положения "10000011"
                send_command(ser, CORRECTNESS_COMMAND)

            else:
                print(f"Положение {position} собрано некорректно. Некорректные контакты:")
                for closed_contact in incorrect_closed:
                    print(f"Замкнуты контакты {closed_contact[0]} и {closed_contact[1]}")
                for opened_contact in incorrect_opened:
                    print(f"Разомкнуты контакты {opened_contact[0]} и {opened_contact[1]}")
                # Отправить команду о неправильности положения "10000100"
                send_command(ser, INCORRECTNESS_COMMAND)

            # Переключение на следующее положение или завершение программы
            check_switch(ser)

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
