from .ftp import FTPServer

import logging
log = logging.getLogger("FTP")
log.setLevel(logging.INFO)

from core.umod.table import uTable


class FTPRunner(uTable):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.ftp = FTPServer()
        self.core.mbus.sub_h("FTP", "ftp/#", self.env, "ftp_act")


    async def ftp_act(self, _id, _key, _pld, _rt):
        log.debug("[ACT]: id: {}, key: {}, pld: {}, rt: {}".format(_id, _key, _pld, _rt))

        if _id == "ftp/ctr":

            if _key == "start":
                await self.ftp_param(_pld)
                self.ftp.start()

    async def ftp_param(self, addr):

        log.debug("addr: {}".format(addr))

        ftp_obj = await self.sel_one(name="default")

        log.debug("cfg: {},".format(ftp_obj))

        if ftp_obj:

            self.ftp.port = ftp_obj.port
            self.ftp.dport = ftp_obj.dport

        self.ftp.addr = addr

