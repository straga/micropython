from machine import reset
from esp32 import Partition

print("RUN MAIN FROM FACTORY")



def reboot(part="ota_0"):

    ota_0 = Partition(part)
    Partition.set_boot(ota_0)

    reset()



def main():

    print("INFO: reboot(), it will be reboot to ota_0")


if __name__ == '__main__':

    print("MAIN")
    main()

