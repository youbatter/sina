#coding:utf-8
'''
app配置模块
'''
import json
import os
CURRET_PATH = os.path.dirname(__file__)
CONFIG_FILE = CURRET_PATH + "/CONFIG.ini"
CONFIG = {}

def LoadConfig():
    global CONFIG
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            CONFIG = json.loads(f.read(),encoding="utf-8")
    CONFIG.update({"state":0})

def ChangeConfig(**kwargs):
    CONFIG.update(kwargs)
    with open(CONFIG_FILE, "w") as f:
        f.write(json.dumps(CONFIG))

def GetConfig(key,default=None):
    return  CONFIG.get(key,default)

if __name__ == "__main__":
    print (CONFIG)
    ChangeConfig(test=5,hello="hello")
    print (CONFIG)
