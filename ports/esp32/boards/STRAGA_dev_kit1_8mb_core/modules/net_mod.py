
from mod.net.actions import WIFIActions

try:
    from ucollections import OrderedDict
except Exception:
    from collections import OrderedDict

from mod.net.wifi import WIFIRun

def init_db(umod):


    tb_name= "cfg_wifi_sta"
    tb_schema = OrderedDict([
        ("name", ""),
        ("ssid", ""),
        ("passwd", ""),
        ("active", 0),
    ])

    umod.mod_add(tb_name, tb_schema)

    tb_name= "cfg_wifi_ap"
    tb_schema = OrderedDict([
        ("name", ""),
        ("essid", ""),
        ("channel", ""),
        ("password", ""),
        ("authmode", ""),
        ("active", 1),
        ("delay", 360),
    ])

    umod.mod_add(tb_name, tb_schema)

def init_act(core):

    #wifi act for mbus
    core.env["wifi.act"] = WIFIActions(env="wifi.act", core=core)

    #wifi module
    core.env["wifi"] = WIFIRun(env="wifi", core=core)
    core.env["wifi"].start()

