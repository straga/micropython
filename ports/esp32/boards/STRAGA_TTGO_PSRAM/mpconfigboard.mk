#ESPIDF = ~/upy/esp-idf/
#PORT = /dev/ttyS6
FLASH_MODE = dio
FLASH_SIZE = 16MB


SDKCONFIG += boards/sdkconfig.base
SDKCONFIG += boards/sdkconfig.spiram

SDKCONFIG += boards/STRAGA_TTGO_PSRAM/sdkconfig.mod
PART_SRC = boards/STRAGA_TTGO_PSRAM/partitions.csv
