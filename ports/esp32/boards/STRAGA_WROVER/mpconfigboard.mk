#ESPIDF = /upy/esp-idf/
#PORT = /dev/ttyUSB0
#FLASH_MODE = dio
#FLASH_SIZE = 16MB


SDKCONFIG += boards/sdkconfig.base
SDKCONFIG += boards/sdkconfig.spiram

SDKCONFIG += boards/STRAGA_WROVER/sdkconfig.mod
PART_SRC = boards/STRAGA_WROVER/partitions.csv
FROZEN_MANIFEST = boards/STRAGA_WROVER/manifest.py