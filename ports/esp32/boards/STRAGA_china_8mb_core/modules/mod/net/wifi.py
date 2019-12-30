
import network

try:
    import uasyncio as asyncio
except Exception:
    import asyncio as asyncio


import logging
log = logging.getLogger("WIFI")
# log.setLevel(logging.INFO)

from core.umod.table import uTable


class WIFIRun:

    def __init__(self, env, core):
        self.core = core
        self.mbus = core.mbus
        self.umod = core.umod
        self.env = env
        self._run = False
        self.sta = STA(tb_name="cfg_wifi_sta", env="wifi.sta", core=core)
        self.scan_ap = self.sta.scan_ap
        self.ap = None


    async def start_ap(self):
        if not self.ap:
            self.ap = AP(tb_name="cfg_wifi_ap", env="wifi.ap", core=self.core)
        await self.ap.start()


    async def _keepalive(self):

        while self._run:
            sleep = await self.sta.sta_keepalive()

            if self.sta.loss > 10:
                log.debug("Loss: {}".format(self.sta.loss))
                self.sta.loss = 0
                await asyncio.wait_for(self.sta.connect(), 20)

            if not self.sta.ip:
                await self.start_ap()
            elif self.ap:
                log.info("AP deactivate")
                self.ap.stop()
                self.ap = None

            await asyncio.sleep(sleep)


    def start(self):

        if not self._run:
            self._run = True

            loop = asyncio.get_event_loop()
            loop.create_task(self._keepalive())

            log.info("WIFI Coro Start")

    def stop(self):
        self._run = False
        log.info("WIFI Coro Stop")



class AP(uTable):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.mbus = self.core.mbus
        self.umod = self.core.umod

        self.net = network.WLAN(network.AP_IF)
        self.ip = None


    async def start(self):

        if not self.ip:

            config = await self.sel_one(active=1)

            if config:
                self.net.active(True)
                log.debug("config: {}".format(config.password))
                if len(config.password) < 8:
                    log.error("AP password to short < 8: {}")
                    return
                try:
                    self.net.config(essid=config.essid,
                                    password=config.password,
                                    authmode=config.authmode,
                                    channel=config.channel)
                except Exception as e:
                    log.error("AP CONFIG: {}".format(e))
                    return

                self.ip = self.net.ifconfig()[0]
                self.mbus.pub_h("WIFI/ap/ip/set", self.ip)


    def stop(self):

        if self.ip:
            self.net.active(False)
            self.ip = None
            self.mbus.pub_h("WIFI/ap/ip/clear", self.ip)



class STA(uTable):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._run = False
        self.mbus = self.core.mbus
        self.umod = self.core.umod

        self.net = network.WLAN(network.STA_IF)
        self.net.active(True)
        self.loss = 0
        self.ip = None


    async def connect(self):

        self.net.disconnect()
        configs = await self.sel_where(active=1)
        log.debug("configs: {}".format(configs))

        if self.ip is not None:
            self.ip = None
            self.mbus.pub_h("WIFI/sta/ip/clear", self.ip)

        if configs:

            try:
                res = self.net.scan()
            except Exception as e:
                log.error("scan: {}".format(e))
                return

            ap_names = []
            for ap in res:
                ap_names.append(ap[0].decode())

            log.debug("ap_names: {}".format(ap_names))

            for ap_conf in configs:
                if ap_conf["ssid"] in ap_names:
                    self.net.connect(ap_conf["ssid"], ap_conf["passwd"])
                    await asyncio.sleep(15)



    async def sta_keepalive(self):

        if self.net.isconnected():
            self.loss = 0
            sleep = 10
            ip = self.net.ifconfig()[0]

            if ip != self.ip:
                self.ip = ip
                self.mbus.pub_h("WIFI/sta/ip/set", self.ip)
        else:
            self.loss += 1
            sleep = 1

        return sleep



    def scan_ap(self):

        data = []
        try:
            for ap in self.net.scan():
                #import ustruct
                #val = {"ssid": ap[0].decode(), "bssid": ustruct.unpack("<L", ap[1])[0], "channel": ap[2], "RSSI": ap[3], "authmode": ap[4],
                #       "hidden": ap[5]}

                val = {"ssid": ap[0].decode(), "bssid": "", "channel": ap[2], "RSSI": ap[3], "authmode": ap[4], "hidden": ap[5]}
                data.append(val)

        except Exception as e:
            log.error("WiFi SCAN AP: {}".format(e))
            pass

        return {
            "head": ("ssid", "bssid", "channel", "RSSI", "authmode", "hidden"),
            "data": data,
            "options": "simple"
        }
