import serial.tools.list_ports

def get_open_com_ports():
    ports = serial.tools.list_ports.comports()
    open_com_ports = []
    for port in ports:
        if port.hwid:
            open_com_ports.append(port.device)
    return open_com_ports
