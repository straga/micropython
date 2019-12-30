try:
    from ucollections import OrderedDict
except Exception:
    from collections import OrderedDict


def init_db(umod):

    tb_name = "board_cfg"
    tb_schema = OrderedDict([
        ("name", ""),
        ("board", ""),
        ("uid", ""),
        ("client", ""),
        ("init", 0)
    ])

    umod.mod_add(tb_name, tb_schema)

    tb_name = "board_mod"
    tb_schema = OrderedDict([
        ("name", ""),
        ("active", ""),
        ("status", ""),
    ])

    umod.mod_add(tb_name, tb_schema)
