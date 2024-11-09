if data_type == "bool":
    value = struct.unpack(">?", response[3:4])[0]
    return value
elif data_type == "int16":
    value = struct.unpack(">h", response[3:5])[0]
    return value
elif data_type == "float32":
    value = struct.unpack(">f", response[3:7])[0]
    return value