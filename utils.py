import serial.tools.list_ports
from PyQt5.QtWidgets import QStyledItemDelegate
from PyQt5.QtGui import QPainter, QColor
def get_open_com_ports():
    ports = serial.tools.list_ports.comports()
    open_com_ports = []
    for port in ports:
        if port.hwid:
            open_com_ports.append(port.device)
    return open_com_ports

class HeaderDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        painter.save()
        painter.fillRect(option.rect, QColor(200, 200, 200))  # Заливка фона серым цветом
        painter.drawText(option.rect, index.data())
        painter.restore()