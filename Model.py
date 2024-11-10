import serial
import csv
import struct
import time


class DataPoint:
    def __init__(self, name: str, port_name: str, data_type: str, slave_address: int, register_address: int, read_only: bool):
        self.name = name
        self.port_name = port_name
        self.data_type = data_type
        self.slave_address = slave_address
        self.register_address = register_address
        self.read_only = read_only
        self.value = None


class DataManager:
    def __init__(self, data_csv: str, port_csv: str):
        self.data_points_dict: dict[str, DataPoint] = self.load_data_points_info(data_csv)
        # self.port_list: dict[str, serial.Serial] = self.load_port_info(port_csv)

    def load_data_points_info(self, csv_file: str) -> dict[str, DataPoint]:
        point_dict = {}
        with open(csv_file, mode="r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                data_point = DataPoint(
                    row["变量名"], row["串口名"], row["数据类型"], int(row["从机地址"]), int(row["寄存器起始地址"]), bool(row["是否只读"])
                )
                point_dict[row["变量名"]] = data_point
        return point_dict

    def load_port_info(self, csv_file: str) -> dict[str, serial.Serial]:
        port_dict = {}
        with open(csv_file, mode="r") as file:
            reader = csv.DictReader(file)

            for row in reader:
                port = serial.Serial(
                    port=row["串口名"],
                    baudrate=int(row["波特率"]),
                    bytesize=int(row["数据位"]),
                    parity=row["校验位"],
                    stopbits=int(row["停止位"]),
                )
                port_dict[row["串口名"]] = port
        return port_dict

    def read_data(self, data_name: str):
        data_point = self.data_points_dict[data_name]
        request = bytearray()
        # 从机地址
        request.append(data_point.slave_address)
        # 功能码
        if data_point.data_type == "bool":
            request.append(0x01)
        elif data_point.data_type == "int16":
            request.append(0x03)
        elif data_point.data_type == "float32":
            request.append(0x03)

        # 起始寄存器地址
        request.extend(struct.pack(">H", data_point.register_address))

        # 读取寄存器数量
        if data_point.data_type == "bool":
            request.extend(struct.pack(">H", 0x0001))
        elif data_point.data_type == "int16":
            request.extend(struct.pack(">H", 0x0001))
        elif data_point.data_type == "float32":
            request.extend(struct.pack(">H", 0x0002))

        # 计算并添加 CRC 校验
        crc = self.calculate_crc(request)
        request.extend(struct.pack("<H", crc))  # CRC 小端序??

        # 打印发送的字节流
        # print(f"发送读取请求: {request.hex()}")

        # 发送请求
        self.port_list[data_point.port_name].write(request)
        # 接收并解析响应
        value = self.receive_response(data_point.data_type)
        return value

    def write_data(self, data_name: str, value):
        data_point = self.data_points_dict[data_name]
        request = bytearray()

        # 从机地址
        request.append(data_point.slave_address)

        # 功能码
        if data_point.data_type == "bool":
            request.append(0x05)
        elif data_point.data_type == "int16":
            request.append(0x06)
        elif data_point.data_type == "float32":
            # float32使用功能码10，需指定寄存器数量和字节数
            request.append(0x10)
            request.append(0x0002)
            request.append(0x04)

        # 起始寄存器地址
        request.extend(struct.pack(">H", data_point.register_address))

        # 写入值
        if data_point.data_type == "bool":
            if value.type() != bool:
                """
                暂时使用print输出错误信息，与界面链接后可使用信号发送错误信息
                """
                print(f"Data type error. Expected: bool, Received: {value.type()}")
                return
            request.extend(struct.pack(">?", value))

        elif data_point.data_type == "int16":
            if value.type() != int:
                """
                暂时使用print输出错误信息，与界面链接后可使用信号发送错误信息
                """
                print(f"Data type error. Expected: int, Received: {value.type()}")
                return
            request.extend(struct.pack(">h", value))

        elif data_point.data_type == "float32":
            if value.type() != float:
                """
                暂时使用print输出错误信息，与界面链接后可使用信号发送错误信息
                """
                print(f"Data type error. Expected: float, Received: {value.type()}")
            request.extend(struct.pack(">f", value))

        # 计算并添加 CRC 校验
        crc = self.calculate_crc(request)
        request.extend(struct.pack("<H", crc))  # CRC 小端序??

        # 发送请求
        self.port_list[data_point.port_name].write(request)

    def receive_response(self, data_point: DataPoint, wait_seconds: float = 0.2):
        # 等待响应
        time.sleep(wait_seconds)

        # in_waiting 属性表示接收缓冲区中的字节数
        if self.port_list[data_point.port_name].in_waiting:
            # 读取响应数据
            response = self.port_list[data_point.port_name].read(self.port_list[data_point.port_name].in_waiting)
            # print(f"收到响应: {response.hex()}")

            # 校验CRC
            crc_received = struct.unpack("<H", response[-2:])[0]
            crc_calculated = self.calculate_crc(response[:-2])

            if crc_received != crc_calculated:
                """
                暂时使用print输出错误信息，与界面链接后可使用信号发送错误信息
                """
                print(f"CRC check failed. Received: {crc_received}, Calculated: {crc_calculated}")
                return

            if data_point.data_type == "bool":
                value = struct.unpack(">?", response[3:4])[0]
                return value
            elif data_point.data_type == "int16":
                value = struct.unpack(">h", response[3:5])[0]
                return value
            elif data_point.data_type == "float32":
                value = struct.unpack(">f", response[3:7])[0]
                return value

        else:
            """
            暂时使用print输出错误信息，与界面链接后可使用信号发送错误信息
            """
            print("No response received.")
            return

    def calculate_crc(self, request_string):
        crc = 0xFFFF
        for pos in request_string:
            crc ^= pos
            for _ in range(8):
                if (crc & 0x0001) != 0:
                    crc >>= 1
                    crc ^= 0xA001
                else:
                    crc >>= 1
        return crc
