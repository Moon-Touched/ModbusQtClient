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
from Model import DataPoint
from ViewModel import RWTask
from typing import Any
import csv


class LabeledLineEdit(QWidget):
    def __init__(self, name: str, parent=None):
        super().__init__(parent)
        # 创建 QLabel 和 QTextEdit
        self.label = QLabel(name)
        self.line_edit = QLineEdit()
        self.line_edit.setObjectName(name)

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
        self.line_edit.setText(text)


class LabeledCheckBox(QWidget):
    def __init__(self, name: str, parent=None):
        super().__init__(parent)
        self.label = QLabel(name)
        self.check_box = QCheckBox()
        self.check_box.setObjectName(name)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.check_box)
        self.setLayout(layout)

    def setLabelText(self, text):
        self.label.setText(text)

    def getChecked(self):
        return self.check_box.isChecked()

    def setChecked(self, state):
        self.check_box.setChecked(state)


class MainWindow(QWidget):
    def __init__(self, data_csv: str, port_csv: str):
        super().__init__()
        self.setWindowTitle("West8100+ example")

        self.data_points_dict: dict[str, DataPoint] = self.load_data_points_info(data_csv)

        self.rw_task = RWTask(self.data_points_dict, port_csv)
        self.rw_task.data_received_signal.connect(self.update_data)

        # 创建控件
        self.main_layout = QVBoxLayout()
        for data_point in self.data_points_dict.values():
            # 新建控件后读取一次数据
            if data_point.data_type == "bool":
                bool_check_box = LabeledCheckBox(name=data_point.name, parent=self)
                value = self.rw_task.read_data(data_point)
                data_point.value = value
                bool_check_box.check_box.setChecked(value)
                if data_point.read_only:
                    bool_check_box.check_box.setEnabled(False)
                else:
                    bool_check_box.check_box.stateChanged.connect(self.add_write_task)

                self.main_layout.addWidget(bool_check_box)
                data_point.control = bool_check_box

            elif data_point.data_type == "int16":
                int_line_edit = LabeledLineEdit(name=data_point.name, parent=self)
                value = self.rw_task.read_data(data_point)
                data_point.value = value
                int_line_edit.line_edit.setText(str(value))

                if data_point.read_only:
                    int_line_edit.line_edit.setReadOnly(True)
                else:
                    int_line_edit.line_edit.setValidator(QIntValidator())
                    int_line_edit.line_edit.editingFinished.connect(self.add_write_task)

                self.main_layout.addWidget(int_line_edit)
                data_point.control = int_line_edit

            elif data_point.data_type == "float32":
                float_line_edit = LabeledLineEdit(name=data_point.name, parent=self)
                value = self.rw_task.read_data(data_point)
                data_point.value = value
                float_line_edit.line_edit.setText(str(value))

                if data_point.read_only:
                    int_line_edit.line_edit.setReadOnly(True)
                else:
                    float_line_edit.line_edit.setValidator(QDoubleValidator(float("-inf"), float("inf"), 2))
                    float_line_edit.line_edit.editingFinished.connect(self.add_write_task)

                self.main_layout.addWidget(float_line_edit)
                data_point.control = float_line_edit

        self.setLayout(self.main_layout)

        self.rw_task.start()

    def update_data(self, data_point: DataPoint, data: Any):
        if data_point.data_type == "bool":
            data_point.control.setChecked(data)
        else:
            data_point.control.setText(str(data))

        data_point.value = data

    def add_write_task(self):
        sender = self.sender()
        data_point = self.data_points_dict[sender.objectName()]
        if data_point.data_type == "bool":
            value = data_point.control.getChecked()
        elif data_point.data_type == "int16":
            value = int(data_point.control.getText())
        elif data_point.data_type == "float32":
            value = float(data_point.control.getText())
        self.rw_task.task_quque.appendleft(("write", data_point, value))

    def load_data_points_info(self, csv_file: str) -> dict[str, DataPoint]:
        point_dict = {}
        with open(csv_file, mode="r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["是否只读"] == "Y":
                    read_only = True
                else:
                    read_only = False
                data_point = DataPoint(
                    row["变量名"], row["串口名"], row["数据类型"], int(row["从机地址"]), int(row["寄存器起始地址"]), read_only
                )
                point_dict[row["变量名"]] = data_point
        return point_dict


app = QApplication([])
window = MainWindow(data_csv="data_points.csv", port_csv="port_info.csv")
window.show()
app.exec()
