from PySide6.QtCore import QObject, QTimer, Signal
from Model import DataManager

class ViewModel(QObject):
    data_updated = Signal(str, object)  # 用于通知界面更新数据
    error_occurred = Signal(str)  # 用于通知界面发生错误

    def __init__(self, data_csv: str, port_csv: str, parent=None):
        super().__init__(parent)
        
        self.data_manager = DataManager(data_csv, port_csv)
        self.changed_values = {}  # 用于跟踪控件的值变化
        
        # 定时器设置，用于定期读取数据
        self.timer = QTimer()
        self.timer.timeout.connect(self.read_all_data_points)
        self.timer.start(1000)  # 每秒读取一次

    def read_all_data_points(self):
        # 读取所有数据点
        for data_name, data_point in self.data_manager.data_points.items():
            # 如果当前数据点没有变化，发送读取请求
            if data_name not in self.changed_values:
                try:
                    value = self.data_manager.read_data(data_name)
                    # 发出信号通知界面更新
                    self.data_updated.emit(data_name, value)
                except Exception as e:
                    self.error_occurred.emit(f"读取数据 {data_name} 失败: {e}")

    def update_value(self, data_name: str, value):
        # 更新控件值时调用该方法
        data_point = self.data_manager.data_points.get(data_name)
        if data_point and not data_point.read_only:
            # 将新值记录在 changed_values 中
            self.changed_values[data_name] = value

            try:
                # 写入新值
                self.data_manager.write_data(data_name, value)
                # 写入成功后，删除 changed_values 中的记录
                del self.changed_values[data_name]
            except Exception as e:
                self.error_occurred.emit(f"写入数据 {data_name} 失败: {e}")
