print("RUN MAIN FROM OTA_0")

import uasyncio as asyncio
import ubinascii
import machine, _thread
import uos
import gc


# WDT
async def run_wdt():
    wdt = machine.WDT(timeout=60000)
    print("WDT RUN")
    while True:
        wdt.feed()
        gc.collect()
        # print("WDT RESET")
        await asyncio.sleep(10)

# Lloader
async def loader(g_mbus, g_umod, board_id):
    print("LOADER: ->")

    from core.loader import Activate
    global g_core

    board_activate = Activate(g_mbus, g_umod, board_id)

    print("BOARD ACTIVATE")
    await board_activate.init_modules()
    print("INIT MOD")
    await board_activate.init_data()
    print("INIT DATA")
    await board_activate.init_action()
    print("INIT ACTION")
    g_core = board_activate.core


def main():

    loop = asyncio.get_event_loop()

    #WDT

    loop.create_task(run_wdt())

    _ = _thread.stack_size(8 * 1024)
    _thread.start_new_thread(loop.run_forever, ())


    fs_stat = uos.statvfs('/')
    fs_size = fs_stat[0] * fs_stat[2]
    fs_free = fs_stat[0] * fs_stat[3]
    print("File System Size {:,} - Free Space {:,}".format(fs_size, fs_free))


    board_id = ubinascii.hexlify(machine.unique_id())
    print("BOARD ID: {}".format(board_id))

    # MBUS
    from core.mbus.mbus import MbusManager

    g_mbus = MbusManager()
    g_mbus.start()
    print("MBUS START")

    # MOD
    from core.umod.umod import ModManager
    g_umod = ModManager()
    #g_umod = ModManager("./{}/u_db".format(runnin_gpart_name))
    print("MOD START")

    from utime import sleep
    print("Wait 5s")
    sleep(5)

    loop.create_task(loader(g_mbus, g_umod, board_id))

    # from core.loader import Activate
    # global g_core
    # g_core = Activate(g_mbus, g_umod, board_id).core


    #if error - run manualy:
    # import network
    # sta = network.WLAN(network.STA_IF)
    # sta.active(True)
    # sta.connect("ssid", "psswd")
    #
    # import ftp.ftp as ftp
    # ftp.ftpserver()


if __name__ == '__main__':

    print("MAIN")
    main()





