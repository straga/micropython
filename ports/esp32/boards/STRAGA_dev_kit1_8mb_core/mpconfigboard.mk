# ESPIDF = /upy/esp-idf/
# PORT = /dev/ttyUSB0
FLASH_MODE = dio
FLASH_SIZE = 8MB

SDKCONFIG += boards/sdkconfig.base

SDKCONFIG += boards/STRAGA_dev_kit1_8mb_core/sdkconfig.mod
PART_SRC = boards/STRAGA_dev_kit1_8mb_core/partitions.csv
FROZEN_MANIFEST = boards/STRAGA_dev_kit1_8mb_core/manifest.py

