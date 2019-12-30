from .telnet import TelnetServer

import logging
log = logging.getLogger("Telnet")
log.setLevel(logging.INFO)

from core.umod.table import uTable


class TelnetRunner(uTable):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.telnet = TelnetServer()
        self.core.mbus.sub_h("Telnet", "telnet/#", self.env, "telnet_act")


    async def telnet_act(self, _id, _key, _pld, _rt):
        log.debug("[ACT]: id: {}, key: {}, pld: {}, rt: {}".format(_id, _key, _pld, _rt))

        if _id == "telnet/ctr":

            if _key == "start":
                await self.telnet_param(_pld)
                self.telnet.start()

            if _key == "stop":
                self.telnet.stop()

    async def telnet_param(self, addr):

        log.debug("addr: {}".format(addr))

        telnet_obj = await self.sel_one(name="default")

        log.debug("telnet: {},".format(telnet_obj))

        if telnet_obj:
            self.telnet.port = telnet_obj.port
            self.telnet.pswd = telnet_obj.pswd

