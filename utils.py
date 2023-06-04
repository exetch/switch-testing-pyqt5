import serial.tools.list_ports
import serial

def get_open_com_ports():
    ports = serial.tools.list_ports.comports()
    open_com_ports = []
    for port in ports:
        try:
            serial_port = serial.Serial(port.device)
            serial_port.close()
            open_com_ports.append(port.device)
        except (OSError, serial.SerialException):
            pass
    return open_com_ports