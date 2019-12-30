
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
except Exception:
    pass


if safe_mode:

    print("Pin Control: LED {}, BTN: {}".format(led_pin, btn_pin))

    safe_pin = Pin(btn_pin, Pin.IN, Pin.PULL_DOWN)
    led_pin = Pin(led_pin, Pin.OUT)
    led_pin.value(led_on)
    print("Wait 5sec - Safe Mode")
    sleep(5)
    print("Safe Mode Activate: {}".format(safe_pin.value() == reset_val))

    if safe_pin.value() == reset_val:
        led_pin.value(1 - led_on)
        Partition.set_boot(Partition('factory'))
        reset()

    sleep(1)
    led_pin.value(1 - led_on)

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
