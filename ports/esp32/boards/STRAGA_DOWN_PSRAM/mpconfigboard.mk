#ESPIDF = ~/upy/esp-idf/
#PORT = /dev/ttyS6
FLASH_MODE = dio
FLASH_SIZE = 16MB


SDKCONFIG += boards/sdkconfig.base
SDKCONFIG += boards/sdkconfig.spiram

SDKCONFIG += boards/STRAGA_DOWN_PSRAM/sdkconfig.mod
PART_SRC = boards/STRAGA_DOWN_PSRAM/partitions.csv
FROZEN_MANIFEST = boards/STRAGA_DOWN_PSRAM/manifest.py
