from Model import DataManager

data_manager = DataManager("data_points.csv")
for data_name in data_manager.data_points:
    print(data_name)