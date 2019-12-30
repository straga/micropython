
import logging

#board
log = logging.getLogger("BOARD")
log.setLevel(logging.INFO)

from board.cfg_db import _name_board
import sys

from .umod.table import uTable

try:
    import uasyncio as asyncio
except Exception:
    import asyncio as asyncio

class uCore:
    __slots__ = ('__dict__', 'env', 'board', 'mbus', 'umod')

    def __init__(self, mbus, umod, board):
        self.mbus = mbus
        self.umod = umod
        self.board = board
        self.env = {}

    def table_get(self, model):
        return uTable(tb_name=model, env=model, core=self)


class Activate:

    __slots__ = ('board_id', 'board', 'mbus', 'umod', 'core', '_modules')

    def __init__(self, mbus, umod, board_id):



        self.mbus = mbus
        self.umod = umod
        self.board_id = board_id
        self.board = self.init_board()

        self.core = uCore(mbus, umod, self.board)
        self.mbus.core = self.core

        self._modules = []

        log.info("BID: {}".format(board_id))


    def init_board(self):

        s_mod = self.umod.mod_sel("board_cfg")

        if not len(s_mod):
            from core.umod.board import init_db
            init_db(self.umod)
            del sys.modules["core.umod.board"]

        from board.cfg_db import push_board
        push_board(self.umod)
        board = _name_board

        log.info("BOARD: {}".format(board))

        return board


    async def init_modules(self):

        self._modules = await self.umod.call_db("_scan", "board_mod")

        for mod in self._modules:
            name_mod = mod["name"]
            await self.umod.call_db("_upd", "board_mod", {"name": name_mod}, status="")

            if mod["active"]:
                try:
                    init_db = __import__("{}_mod".format(name_mod)).init_db
                    init_db(self.umod)
                    log.info("MOD DB ACTIVATE: {}".format(name_mod))
                    del sys.modules["{}_mod".format(name_mod)]

                except Exception as e:
                    log.info("MOD: {}, init db err: {}".format(mod, e))


    async def init_data(self):
        from board.cfg_db import push_data

        try:
            push_data(self.umod)
            del sys.modules["board.cfg_db"]
            await self.umod.call_db("_upd", "board_cfg", {"board": _name_board}, init=1, uid=self.board_id.decode())
            log.info("MOD DATA UPDATE: {}".format(_name_board))
        except Exception as e:
            log.info("Data update err: {}".format(e))



    async def init_action(self):

        for mod in self._modules:
            if mod["active"]:
                name_mod = mod["name"]

                try:
                    __import__("{}_mod".format(name_mod)).init_act(self.core)
                    del sys.modules["{}_mod".format(name_mod)]

                    await self.umod.call_db("_upd", "board_mod", {"name": name_mod}, status="loaded")
                    log.info("MOD ACT ACTIVATE: {}".format(name_mod))
                except Exception as e:
                    log.info("MOD: {}, activate err: {}".format(mod, e))

        self._modules = None


