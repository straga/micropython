
class uTable:

    def __init__(self, tb_name, env, core):
        self.tb_name = tb_name
        self.env = env
        self.core = core
        self.obj = None

        self.pub_h = core.mbus.pub_h


    def sub_h(self, uid, topic_name, func_name):
        self.core.mbus.sub_h(uid, topic_name, self.env, func_name)


    def return_obj(self, data):
        result = False
        if len(data):
            result = TbModel(data, _table=self)

        return result

    #call with lock acquire
    async def call(self, method, *args, **kwargs):
        return await self.core.umod.call_db(method, self.tb_name, *args, **kwargs)

    #methods
    async def scan(self):
        return await self.call("_scan")


    async def scan_name(self):
        return await self.call("_scan_name")


    async def update(self, *args, **kwargs):
        return await self.call("_upd", *args, **kwargs)


    async def sel_one(self, *args, **kwargs):
        # return await self.call("_sel_one", *args, **kwargs)
        data = await self.call("_sel_one", *args, **kwargs)
        return self.return_obj(data)


    async def sel_where(self, *args, **kwargs):
        return await self.call("_sel", *args, **kwargs)




class TbModel:

    def __init__(self, *args, **kwargs):

        for dictionary in args:
            for key in dictionary:
                setattr(self, key, dictionary[key])
        for key in kwargs:
            setattr(self, key, kwargs[key])

        self.mbus = self._table.core.mbus
        self.core = self._table.core


    async def write(self, **kwargs):

        return await self._table.update({"name": self.name}, **kwargs)


