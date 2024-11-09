from PySide6.QtCore import QObject, Signal, Slot


class ViewModel(QObject):
    registerUpdated = Signal(str, str)  # 发送寄存器值更新的信号

    def __init__(self, model):
        super().__init__()
        self.model = model

    def get_registers(self):
        # 获取寄存器列表
        return self.model.registers.keys()

    def read_register(self, register_name):
        try:
            value = self.model.read_register(register_name)
            self.registerUpdated.emit(register_name, str(value))  # 发出更新信号
        except ValueError as e:
            print(f"Error reading register {register_name}: {e}")

    @Slot(str, str)
    def write_register(self, register_name, value):
        try:
            register = self.model.registers[register_name]
            # 将字符串转换为实际数据类型
            if register.data_type == "bool":
                value = bool(int(value))
            elif register.data_type == "int16":
                value = int(value)

            self.model.write_register(register_name, value)
            self.registerUpdated.emit(register_name, str(value))  # 发出更新信号
        except ValueError as e:
            print(f"Error writing register {register_name}: {e}")
