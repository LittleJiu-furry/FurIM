"""
    插件模板
"""
# =======固定数据区
from . import sdk
# 请勿删除以下内容
_dec = ""
_ver = ""

# 请勿删除或修改以下方法

# 初始化函数
async def init(s):
    global server
    server = s
    await pluginsInit()

# 通知处理函数
async def dealFunc(opcode:int, version:int, data:bytes, path:str):
    print("dealFunc",opcode,version,path,data)

# 父层函数封装
def writeLog(logLevel:int,content:str):
    server.writeLog(logLevel,content)

# =======type hit 定义区
# 此部分内容不建议删除
class LogLevel:
    Info = 0
    Warning = 1
    Error = 2
    Fatal = 3

# =======功能函数区
# 请将所有的功能函数以及变量定义写在这里

# 初始化通知函数
async def pluginsInit():
    writeLog(LogLevel.Info,f"plugin testPlugin was been init")