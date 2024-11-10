from PySide6.QtCore import QObject, QTimer, Signal
from Model import DataManager
from collections import deque


class ViewModel(QObject):
    data_updated = Signal(str, object)
    error_occurred = Signal(str)

    def __init__(self, data_csv: str, port_csv: str, parent=None):
        super().__init__(parent)

        # 加载数据和端口信息
        self.data_manager = DataManager(data_csv, port_csv)
        self.task_queue = deque()  # 使用 deque 维护任务队列
        self.changed_values = {}  # 用于跟踪控件的值变化

        # 定时器设置，用于定期处理任务队列
        self.timer = QTimer()
        self.timer.timeout.connect(self.process_task_queue)
        self.timer.start(100)  # 每100毫秒处理一次任务

    def process_task_queue(self):
        if not self.task_queue:
            # 如果队列为空，添加所有读取任务
            for data_name in self.data_manager.data_points_dict:
                self.task_queue.append(("read", data_name))
        else:
            # 从队列中取出任务
            task_type, data_name = self.task_queue.popleft()
            data_point = self.data_manager.data_points_dict[data_name]

            if task_type == "read":
                # 读取任务
                try:
                    value = self.data_manager.read_data(data_name)
                    self.data_updated.emit(data_name, value)
                except Exception as e:
                    self.error_occurred.emit(f"读取数据 {data_name} 失败: {e}")
            elif task_type == "write":
                # 写入任务
                if data_name in self.changed_values:
                    value = self.changed_values.pop(data_name)
                    try:
                        self.data_manager.write_data(data_name, value)
                        # 写入完成后，立即添加一个读取任务以更新显示
                        self.task_queue.appendleft(("read", data_name))
                    except Exception as e:
                        self.error_occurred.emit(f"写入数据 {data_name} 失败: {e}")

    def update_value(self, data_name: str, value):
        # 更新控件值时调用此方法
        data_point = self.data_manager.data_points_dict.get(data_name)
        if data_point and not data_point.read_only:
            # 将新值添加到 changed_values 中
            self.changed_values[data_name] = value
            # 将写入任务和随后的读取任务插入队列前
            self.task_queue.appendleft(("write", data_name))
