
# import esp
from utime import sleep
from machine import Pin, reset

from esp32 import Partition

import sys
import uos
import gc

bootpart = Partition(Partition.BOOT)
runningpart = Partition(Partition.RUNNING)

print("INFO - Partitions")
print("Boot: {}".format(bootpart))
print("Run: {}".format(runningpart))

# SAFE MODE
safe_mode = False

try:
    import boot_pin
    safe_mode = boot_pin.safe_mode
    print(safe_mode)
except Exception:
    pass


if safe_mode:

    print("Pin Control: LED {}, BTN: {}".format(boot_pin.led_pin, boot_pin.btn_pin))

    safe_pin = Pin(boot_pin.btn_pin, Pin.IN, Pin.PULL_DOWN)
    led_pin = Pin(boot_pin.led_pin, Pin.OUT)
    led_pin.value(boot_pin.led_on)
    print("Wait 5sec - Safe Mode")
    sleep(5)
    print("Safe Mode Activate: {}".format(safe_pin.value() == boot_pin.reset_val))

    if safe_pin.value() == boot_pin.reset_val:
        led_pin.value(1 - boot_pin.led_on)
        Partition.set_boot(Partition('factory'))
        reset()

    sleep(1)
    led_pin.value(1 - boot_pin.led_on)

else:
    print("Not Board Detect for - Safe Mode")


# PARTITIONS

part_info = runningpart.info()
part_name = part_info[4]

try:
    uos.mkdir(part_name)
except OSError as e:
    print("Path already exist")
    pass

pyversion = 'None'
try:
    with open("/{}/VERSION".format(part_name), "r") as f:
        pyversion = f.read()
except:
    pass
print("Version hash: {}".format(pyversion.strip()))

sys.path.append("/{}".format(part_name))
sys.path.append("/{}/{}".format(part_name, "lib"))
sys.path.append("/{}/{}".format(part_name, "app"))
uos.chdir("/{}".format(part_name))

print("Working Sys Path: {}".format(sys.path))

gc.collect()
