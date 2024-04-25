import machine

def get_temperature():
    sensor_temp = machine.ADC(4)
    conversion_factor = 3.3 / (65535)
    raw_temperature = sensor_temp.read_u16() * conversion_factor

    # Convert raw temperature to Celsius
    temperature_c = 27 - (raw_temperature - 0.706) / 0.001721
    return temperature_c