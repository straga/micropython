try:
    import uasyncio as asyncio
except Exception:
    import asyncio as asyncio


class WIFIActions:

    def __init__(self, env, core):
        self.mbus = core.mbus
        self.umod = core.umod
        self.mbus.sub_h(uid="WIFI-ACT", topic="WIFI/#", env=env, func="mod_ctrl")

    def mod_state(self, mods, up, pld, cmd):
        for mod in mods:
            if mod["active"] == "1" and mod["up"] in up:
                mod_name = mod["name"].split("cfg_", 1)
                if mod_name:
                    self.mbus.pub_h(tpc="{}/ctr/{}".format(mod_name[-1], cmd), pld=pld)


    async def mod_ctrl(self, _id, _key, _pld, _rt):

        mods = await self.umod.call_db(method="_scan", table="modules")

        if mods:

            if _id == "WIFI/sta/ip" and _key == "set":
                self.mod_state(mods, ["sta", "ap"], _pld, "start")

            if _id == "WIFI/ap/ip" and _key == "set":
                self.mod_state(mods, ["ap"], _pld, "start")

            if _id == "WIFI/sta/ip" and _key == "clear":
                self.mod_state(mods, ["sta"], _pld, "stop")