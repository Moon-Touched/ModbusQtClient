class DataPoint:
    def __init__(self, name: str, port_name: str, data_type: str, slave_address: int, register_address: int, read_only: bool):
        self.name = name
        self.port_name = port_name
        self.data_type = data_type
        self.slave_address = slave_address
        self.register_address = register_address
        self.read_only = read_only
        self.control = None
        self.value = None
