from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QComboBox,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLabel,
    QLineEdit,
    QSpinBox,
    QDoubleSpinBox,
    QPushButton,
    QCheckBox,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QIntValidator, QDoubleValidator
from serial.tools import list_ports
from Model import DataManager
import serial


class LabeledLineEdit(QWidget):
    def __init__(self, name: str, parent=None):
        super().__init__(parent)
        # 创建 QLabel 和 QTextEdit
        self.label = QLabel(name)
        self.line_edit = QLineEdit()
        self.setObjectName(name)

        # 布局设置
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.line_edit)
        self.setLayout(layout)

    def setLabelText(self, text):
        self.label.setText(text)

    def getText(self):
        return self.line_edit.text()

    def setText(self, text):
        self.line_edit.setPlainText(text)


class LabeledCheckBox(QWidget):
    def __init__(self, name: str, parent=None):
        super().__init__(parent)
        self.label = QLabel(name)
        self.check_box = QCheckBox()
        self.setObjectName(name)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.check_box)
        self.setLayout(layout)

    def setLabelText(self, text):
        self.label.setText(text)

    def setChecked(self, state):
        self.check_box.setChecked(state)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("West8100+ example")

        self.data_manager = DataManager(data_csv="data_points.csv", port_csv="port_info.csv")

        # 创建控件
        self.main_layout = QVBoxLayout()
        for data_point in self.data_manager.data_points.values():
            if data_point.data_type == "bool":
                check_box = LabeledCheckBox(name=data_point.name, parent=self)

                if data_point.read_only:
                    check_box.check_box.setEnabled(False)

                self.main_layout.addWidget(check_box)

            elif data_point.data_type == "int16":
                int_line_edit = LabeledLineEdit(name=data_point.name, parent=self)
                int_line_edit.line_edit.setValidator(QIntValidator())

                if data_point.read_only:
                    int_line_edit.line_edit.setReadOnly(True)

                self.main_layout.addWidget(int_line_edit)

            elif data_point.data_type == "float32":
                float_line_edit = LabeledLineEdit(name=data_point.name, parent=self)
                float_line_edit.line_edit.setValidator(QDoubleValidator(float("-inf"), float("inf"), 2))

                if data_point.read_only:
                    int_line_edit.line_edit.setReadOnly(True)

                self.main_layout.addWidget(float_line_edit)
        self.setLayout(self.main_layout)


app = QApplication([])
window = MainWindow()
window.show()
app.exec()


# 自定义 LED 控件
# class LedIndicator(QLabel):
#     def __init__(self):
#         super().__init__()
#         self.setFixedSize(20, 20)
#         self.state = False
#         self.setState(self.state)

#     def setState(self, state: bool):
#         self.state = state
#         painter = QPainter(self)
#         if self.state:
#             QColor("green")
#         else:
#             color = QColor("darkgreen")
#         painter.setBrush(color)
#         painter.setRenderHint(QPainter.RenderHint.Antialiasing)
#         painter.drawEllipse(0, 0, self.width(), self.height())
