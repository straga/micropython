# Copyright (c) 2019 Viktor Vorobjov

try:
    import uos
    import utime
    import ujson
    from ucollections import OrderedDict

except Exception:

    import os as uos
    import time as utime
    from collections import OrderedDict
    import json as ujson
    pass

import logging
log = logging.getLogger("FDB")
log.setLevel(logging.INFO)

class DB:

    def __init__(self, name):
        self.name = name

    def connect(self):
        pass

    def close(self):
        pass


class Model:

    @classmethod
    def path_to_file(cls, pkey):
        return "{}/{}/{}".format(cls.__db__.name, cls.__table__, pkey)

    @classmethod
    def path_to_dir(cls):
        return "{}/{}".format(cls.__db__.name, cls.__table__)


    @classmethod
    def list_dir(cls, path):
        try:
            return uos.listdir(path)
        except OSError as e:
            log.debug("LSDIR: {}".format(e))
            return []


    @classmethod
    def isfile(cls, file):
        try:
            if uos.stat(file)[6]: #size more 0
                return True
            else:
                return False
        except OSError as e:
            log.debug("LSFILE: {}".format(e))
            return False


    @classmethod
    def create_table(cls):
        cls.__fields__ = list(cls.__schema__.keys())

        for d in (cls.__db__.name, cls.path_to_dir()):
            if not cls.list_dir(d):
                try:
                    uos.mkdir(d)
                except OSError as e:
                    log.debug("MKDIR: {}, {}".format(e, d))
                    pass


    @classmethod
    def create(cls, **fields):
        pkey_field = cls.__fields__[0]
        for k, v in cls.__schema__.items():
            if k not in fields:
                default = v
                if callable(default):
                    default = default()
                fields[k] = default

        pkey = fields[pkey_field]
        exs = cls.isfile(cls.path_to_file(pkey))

        log.debug("Exist:{}, file: {}".format(exs , cls.path_to_file(pkey)))
        log.debug("create: fields:{}".format(ujson.dumps(fields)))

        if not exs:
            with open(cls.path_to_file(pkey), "w") as f:
                f.write(ujson.dumps(fields))
            log.debug("create: pkey:{}".format(pkey))
            return pkey
        else:
            log.debug("exist: pkey:{}".format(pkey))
            return False


    @classmethod
    def get_id(cls, pkey):
        with open(cls.path_to_file(pkey)) as f:
            return ujson.loads(f.read())



    @classmethod
    def update(cls, where, **fields):
        pkey_field = cls.__fields__[0]

        if len(where) == 1 and pkey_field in where:

            with open(cls.path_to_file(where[pkey_field])) as f:
                data = ujson.loads(f.read())

            data.update(fields)

            with open(cls.path_to_file(where[pkey_field]), "w") as f:
                f.write(ujson.dumps(data))

            return True



    @classmethod
    def scan(cls):
        for file_name in cls.list_dir(cls.path_to_dir()):

            # log.debug("fname: {}".format(cls.fname(fname)))

            with open(cls.path_to_file(file_name)) as f:
                tb = f.read()
                if tb:
                    row = ujson.loads(tb)
                    yield row

    @classmethod
    def scan_name(cls):
        for file_name in cls.list_dir(cls.path_to_dir()):
            yield file_name
            # log.debug("fname: {}".format(cls.fname(fname)))

            # with open(cls.fname(fname)) as f:
            #     tb = f.read()
            #     if tb:
            #         row = ujson.loads(tb)
            #         yield row

    @classmethod
    def delete(cls, where):
        pkey_field = cls.__fields__[0]

        if len(where) == 1 and pkey_field in where:
            uos.remove(cls.path_to_file(where[pkey_field]))
            return True


    @classmethod
    def select(cls, **fields):

        for v in cls.list_dir(cls.path_to_dir()):

            with open(cls.path_to_file(v)) as f:
                tb = f.read()
                if tb:
                    row = ujson.loads(tb)

                    for k in cls.__fields__:
                        if k in fields and k in row:
                            if row[k] == fields[k]:
                                yield row


# if hasattr(utime, "localtime"):
#     def now():
#         return "%d-%02d-%02d%02d:%02d:%02d" % utime.localtime()[:6]
# else:
#     def now():
#         return str(int(utime.time()))

def now():
    return str(int(utime.time()))
