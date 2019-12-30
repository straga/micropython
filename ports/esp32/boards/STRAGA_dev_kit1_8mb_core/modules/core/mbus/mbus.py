# Copyright (c) 2019 Viktor Vorobjov


try:
    import uasyncio as asyncio
    from uasyncio.queues import Queue
except Exception:
    import asyncio as asyncio
    from asyncio.queues import Queue
    pass

from core.asyn.asyn import launch

import logging
log = logging.getLogger("MBUS")
log.setLevel(logging.INFO)


class MbusManager:


    def __init__(self):
        self.queue = Queue()
        self.msub = {}
        self.mpub = []
        self.sid = 0


    def start(self):
        loop = asyncio.get_event_loop()
        loop.create_task(self.consumer())
        loop.create_task(self.producer())


    def _msg(self, pub_id, sub_prm, pld , retain=False):

        #return {"id": pub_id, "key": sub_prm, "pld": pld, "rt": retain}

        return (pub_id, sub_prm, pld, retain)


    def _all_tpc(self, pub_id, sub_prm, len_tpc):

        if len_tpc == 1:
            all_tpc = "{}".format(pub_id)
        else:
            all_tpc = "{}/{}".format(pub_id, sub_prm)

        return all_tpc



    def sub_check(self, msg):
        log.debug("[SUB] : msg: {}".format(msg))

        msub = self.msub.copy()
        for key, value in msub.items():
            sub_ = value["id"].rsplit("/#", 1)
            func = value["func"]
            env = value["env"]

            tpc = msg["tpc"].rsplit("/", 1)
            pub_id = tpc[0]
            sub_prm = tpc[-1] #action params /last from topic , led/led_1/set: "set" is it.
            pld = msg["pld"] # playload
            brk_id = msg["brk"] # broker


            func_msg = False

            sub_id = sub_[0]

            #log.debug("sub_id: {}, KEY: {}".format(sub_id, key, ))
            #log.debug("sub_id: {}, pub_id: {}".format(sub_id, pub_id, ))

            if sub_id == "ALL":
                func_msg = self._msg(brk_id, self._all_tpc(pub_id, sub_prm, len(tpc)), pld, msg["retain"])
            else:
                if len(sub_) > 1:
                    if pub_id.find(sub_id, 0) > -1:
                        func_msg = True
                elif sub_id == pub_id:
                    func_msg = True

                if func_msg:
                    func_msg = self._msg(pub_id, sub_prm, pld, msg["retain"])

            if func_msg:
                try:
                    method = getattr(self.core.env[env], func)
                    launch(method, func_msg)
                except Exception as e:
                    log.debug("Error: call_back: {} - {}".format(func, e))
                    pass
        msub = None


    def local(self, msg):
        # log.debug("[brk LOCAL] : msg: {}".format(msg))
        return msg


    # consumer
    def sub(self, key, value):

        if key in self.msub:
            self.sid += 1
            key = "{}-{}".format(key, self.sid)

        self.msub[key] = value


    def sub_h(self, uid, topic, env, func):

        self.sub(uid, {"id": topic, "env": env, "func": func})

    async def consumer(self):

        while True:
            message = await self.queue.get()
            if message:
                log.debug("[GET] msg: {}".format(message))

                try:
                    br_func = getattr(self, message["brk"])
                except Exception as e:
                    log.debug("Error: getattr: {}".format(e))
                    br_func = None
                    pass

                if br_func:
                    self.sub_check(br_func(message))

            await asyncio.sleep(0.3)


    # producer
    def pub(self, value):
        self.mpub.append(value)

    def pub_h(self, tpc, pld, brk="local", retain=False, ):
        self.pub({"brk": brk, "tpc": tpc, "pld": pld, "retain": retain})


    async def producer(self):
        while True:
            while len(self.mpub) > 0:
                await self.queue.put(self.mpub.pop(0))
            await asyncio.sleep(0.3)
