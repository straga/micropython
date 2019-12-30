# Copyright (c) 2019 Viktor Vorobjov

from core.db import filedb as uorm

try:
    import uasyncio as asyncio
    from ucollections import OrderedDict
    import ujson

except ImportError:
    from collections import OrderedDict
    import json as ujson
    import asyncio

from core.asyn.asyn import Lock
lock = Lock()

import logging
log = logging.getLogger("MOD")
log.setLevel(logging.INFO)


class ModManager:
    __slots__ = ('__dict__', 'db', '_tbl', '_sch')

    def __init__(self, db="u_db"):

        self.db = uorm.DB(db)
        self.model = uorm.Model
        self.model.__db__ = self.db

        self._tbl = "modules"
        self._sch = OrderedDict([
            ("name", ""),
            ("sch", ""),
            ("active", ""),
            ("up", ""),
        ])



    def mod_get(self, m_name):
        self.tbl_add()
        if self._tbl == m_name:
            return self._sch

        s_mod = self.mod_sel(m_name)
        if len(s_mod):
            sch = OrderedDict(s_mod[0]["sch"])
            self.tbl_add(s_mod[0]["name"], sch)
            return sch
        return False


    def tbl_add(self, tb_name=None, tb_sch=None):
        if not tb_name:
            tb_name = self._tbl
            tb_sch = self._sch
        self.model.__table__ = tb_name
        self.model.__schema__ = tb_sch
        self.model.create_table()
        log.debug("TBL SELECT: {},  {}".format(tb_name, tb_sch))

    def mod_sel(self, m_name):
        self.tbl_add()
        return list(self.model.select(name=m_name))

    def mod_add(self, tb_name, tb_sch, **fields):

        self.tbl_add(tb_name, tb_sch)
        self.tbl_add()
        log.debug("MOD ADD: {} {}".format(tb_name, tb_sch))
        if not len(self.mod_sel(tb_name)):
            log.debug("CREATE MODEL: {}".format( tb_name ))

            self.model.create(name=tb_name, sch=list(tb_sch.items()), **fields)






    def _call_cmd(self, method, table, *args, **kwargs):

        result = []
        if hasattr(self, method):

            try:
                func = getattr(self, method)
                res = func(table, *args, **kwargs)

                if res:

                    if not isinstance(res, (list, tuple, dict)):
                        res = list(res)

                    if len(res):
                        result = res

            except Exception as e:
                log.debug("Err : {}, {}, {}, {}, {}".format(e, method, table, args, kwargs))
                pass

        return result

    def data_load(self, table, **kwargs):
        self._call_cmd("_add", table, **kwargs)



    async def call_db(self, method, table, *args, **kwargs):

        await lock.acquire()
        result = self._call_cmd(method, table, *args, **kwargs)
        lock.release()

        return result




    def _add(self, mod_name, **fields):

        if self.mod_get(mod_name):
            return self.model.create(**fields)

        return False


    def _scan(self, mod_name, **kwargs):
        if self.mod_get(mod_name):
            return self.model.scan()

    def _scan_name(self, mod_name, **kwargs):
        if self.mod_get(mod_name):
            return self.model.scan_name()

    def _scan_head(self, mod_name, **kwargs):
        sch = self.mod_get(mod_name)
        if sch:
            return {
                "head": list(sch),
                "data": list(self.model.scan())
            }

    def _sel(self, mod_name, **fields):
        if self.mod_get(mod_name):
            return list(self.model.select(**fields))


    def _upd(self, mod_name, where, **fields):
        if self.mod_get(mod_name):
            return self.model.update(where, **fields)


    def _by_id(self, mod_name, pkey):
        if self.mod_get(mod_name):
            return self.model.get_id(pkey)


    def _sel_one(self, mod_name, **fields):

        rcds = self._sel(mod_name, **fields)

        if rcds and len(rcds):
            return rcds[0]
        else:
            return False











