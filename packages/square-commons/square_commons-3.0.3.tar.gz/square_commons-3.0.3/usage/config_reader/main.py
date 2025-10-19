from square_commons import ConfigReader

config = ConfigReader("config.ini").read_configuration()
print(config)
# {'SECTION1': {'KEY1': 'VALUE1'}}
