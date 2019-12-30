from mod.telnet.runner import TelnetRunner

try:
    from ucollections import OrderedDict
except Exception:
    from collections import OrderedDict


def init_db(umod):

    tb_name = "cfg_telnet"
    tb_schema = OrderedDict([
        ("name", ""),
        ("ip", ""),
        ("port", ""),
        ("pwd", ""),
    ])

    umod.mod_add(tb_name, tb_schema, active="1", up="ap")


def init_act(core):
    core.env["telnet"] = TelnetRunner(tb_name="cfg_telnet", env="telnet", core=core)








