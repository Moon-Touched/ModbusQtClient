from Model import DataManager

serial_manager = DataManager(csv_file="data_points.csv", port_name="COM3", baudrate=9600, bytesize=8, parity="N", stopbits=1, timeout=1)

names = serial_manager.data_points.keys()
for name in names:
    print(serial_manager.read_data(name))
