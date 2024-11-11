基于 PySide6, Pyserial 和 Modbus 协议的上位机软件。

* 主要功能：

  * 自动读取数据点和串口参数的 csv 文件。
  * 根据读取的数据点自动生成控件并绑定信号，实现数据读写。
  * 以 west8100+ 为例的模板。

* todo

  * [ ] 目前是所有数据点排成一列，研究有没有更智能的方法。
  * [ ] 出现错误时弹出提示。

# 架构

* `DataPoint` 类，存储每个数据点的信息：

  * `name`: 名称。
  * `port_name`: 所在串口的名称。
  * `data_type`: 数据类型（ `bool`、`int16`、`float32`）。用字符串表示。
  * `slave_address`: 从机地址。
  * `register_address`: 起始寄存器地址。
  * `read_only`: 是否为只读。
  * `control`: 界面控件的引用。
  * `value`: 当前数据值。

* `RWTask` 类继承 `QThread`，管理数据的读写操作：

  * **任务队列**：使用 `deque` 维护读写任务队列，每个任务是 `tuple(r/w, data_point, value)` 组成。
  * **定时读取**：当任务队列为空时，自动添加读取任务。
  * **读写操作**：通过 `read_data` 和 `write_data` 方法实现对设备的 Modbus 读写操作。读取数据后，将结果通过 `data_received_signal` 信号发送给界面进行更新。（写入后自动执行一次同一数据点的读取，确认是否成功写入）
  * **CRC 校验**：在 Modbus 数据包中添加 CRC 校验，确保数据传输的完整性。

* 界面：

  * `MainWindow` ：

    * **加载数据点**：从 CSV 文件中读取数据点配置，并创建相应的控件。
    * **控件更新**：更改控件值后，将写入任务插入队列最前面，并在数据读取完成后更新控件显示。
  * `LabeledLineEdit`：包含一个 `QLabel` 和 `QLineEdit`，用于显示和输入 `int16` 和 `float32` 类型的数据。
  * `LabeledCheckBox`：包含一个 `QLabel` 和 `QCheckBox`，用于显示和控制 `bool` 类型的数据。
