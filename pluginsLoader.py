import typing
from typing import (
    Tuple,Union,List,Dict,
    Callable,Optional,Any
)
import time
import importlib as lib
from types import ModuleType

import asyncio
import os
import sqlite3
import pickle
from base64 import b64encode, b64decode
import loger
import traceback
import inspect


def dealPath(*path):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "./plugins",*path))

class PluginsType:
    pluginsName:str = "testPlugins"
    pluginsDec:str = "testPlugins"
    pluginsLoaderTime:float = 0.0
    pluginsModuleType:ModuleType = None
    
    def __eq__(self, __value: object) -> bool:
        _this = vars(self)
        _obj = vars(__value)
        _this.pop("pluginsLoaderTime") if "pluginsLoaderTime" in _this else None
        _this.pop("pluginsModuleType") if "pluginsModuleType" in _this else None
        _this.pop("pluginsDec") if "pluginsDec" in _this else None
        _obj.pop("pluginsLoaderTime") if "pluginsLoaderTime" in _obj else None
        _obj.pop("pluginsModuleType") if "pluginsModuleType" in _obj else None
        _obj.pop("pluginsDec") if "pluginsDec" in _obj else None
        return _this == _obj
    
    def __str__(self) -> str:
        return str(vars(self))

class LoaderDeal:
    __LoaderPlugins:Dict[str, PluginsType] = {}
    def __init__(self,caller) -> None:
        self.caller = caller
        # 打开数据库并创建交互游标
        if(os.path.exists(dealPath("./cache/plugins.db"))):
            os.remove(dealPath("./cache/plugins.db"))
        if(not os.path.exists(dealPath("./cache"))):
            os.mkdir(dealPath("./cache"))
        self.__plugins = sqlite3.connect(dealPath("./cache/plugins.db"))
        self.__cursor = self.__plugins.cursor()
        # 初始化本地库表
        self.__cursor.execute(
            '''CREATE TABLE "plugins" (
                "ID" INTEGER NOT NULL,
                "name" TEXT NOT NULL,
                "op_0" ENUM(0,1) NOT NULL,
                "op_1" ENUM(0,1) NOT NULL,
                "op_2" ENUM(0,1) NOT NULL,
                "op_3" ENUM(0,1) NOT NULL,
                "op_4" ENUM(0,1) NOT NULL,
                "op_5" ENUM(0,1) NOT NULL,
                "op_6" ENUM(0,1) NOT NULL,
                "op_7" ENUM(0,1) NOT NULL,
                PRIMARY KEY ("ID")
            )
            ;'''
            )
        self.__plugins.commit()
    # 类内——加载
    def __load(self,pluginName:str,reload:bool = False) -> PluginsType:
        if(os.path.exists(dealPath(f"./{pluginName}.py")) is False):
            return None
        _ret_cursor = self.__cursor.execute("SELECT ID,name FROM plugins WHERE name = ?;",(pluginName,))
        if(len(_ret_cursor.fetchall()) == 0):
            # 说明从未载入过这个模块
            self.__cursor.execute("INSERT INTO plugins VALUES (?,?,?,?,?,?,?,?,?,?);",
                                  (None,pluginName,0,0,0,0,0,0,0,0))
            self.__plugins.commit()
            _ret_cursor = self.__cursor.execute("SELECT ID,name FROM plugins WHERE name = ?;",(pluginName,))
            for _data in _ret_cursor:
                ID = _data[0]
                _plugin = PluginsType()
                _plugin.pluginsName = pluginName
                _plugin.pluginsLoaderTime = time.time()
                _plugin.pluginsModuleType = lib.import_module(f".{pluginName}","plugins")
                _plugin.pluginsDec = _plugin.pluginsModuleType._dec
                self.__LoaderPlugins.update({f"ID_{ID}":_plugin})
                asyncio.get_event_loop().run_until_complete(_plugin.pluginsModuleType.init(self.caller))
                return _plugin
        else:
            _ret_cursor = self.__cursor.execute("SELECT ID,name FROM plugins WHERE name = ?;",(pluginName,))
            for _data in _ret_cursor:
                ID = _data[0]
                if(f"ID_{ID}" not in self.__LoaderPlugins):
                    _plugin = PluginsType()
                    _plugin.pluginsName = pluginName
                    _plugin.pluginsLoaderTime = time.time()
                    _plugin.pluginsModuleType = lib.import_module(f".{pluginName}","plugins")
                    _plugin.pluginsDec = _plugin.pluginsModuleType._dec
                    self.__LoaderPlugins.update({f"ID_{ID}":_plugin})
                    asyncio.get_event_loop().run_until_complete(_plugin.pluginsModuleType.init(self.caller))
                    return _plugin
                else:
                    if(reload):
                        _plugin = self.__LoaderPlugins[f"ID_{ID}"]
                        _plugin.pluginsModuleType = lib.reload(_plugin.pluginsModuleType)
                        _plugin.pluginsDec = _plugin.pluginsModuleType._dec
                        _plugin.pluginsLoaderTime = time.time()
                        self.__LoaderPlugins.update({f"ID_{ID}":_plugin})
                        asyncio.get_event_loop().run_until_complete(_plugin.pluginsModuleType.init(self.caller))
                        return _plugin
                    else:
                        return self.__LoaderPlugins[f"ID_{ID}"]
    # 类内——设置通知状态
    def __setOPStatus(self,pluginName:str,opcode:int,status:bool):
        _status = 1 if status else 0
        _ret_cursor = self.__cursor.execute("select ID,? from plugins where name = ?;",
            (f"op_{opcode}",pluginName))
        _ret = _ret_cursor.fetchall()
        if(len(_ret) == 0):
            return False
        if(_ret[0][1] == _status):
            return False
        self.__cursor.execute(f"update plugins set op_{opcode} = {_status} where ID = {_ret[0][0]};")
        self.__plugins.commit()
    # 注册插件
    def registPlugin(self,pluginName:str,opcode:Optional[Union[int,List[int]]] = None):
        # 默认接收全部通知
        self.__load(pluginName)
        if(opcode is None):
            for i in range(0,8):
                _retStatus = self.__setOPStatus(pluginName,i,True)
                if(_retStatus == False):
                    self.writeLog(loger.LogLevel.Warning,
                                  f"when regist opcode event ID {i} to plugin {pluginName} failed")
        elif(type(opcode) == int):
            _retStatus = self.__setOPStatus(pluginName,opcode,True)
            if(_retStatus == False):
                self.writeLog(loger.LogLevel.Warning,
                              f"when regist opcode event ID {opcode} to plugin {pluginName} failed")
        elif(type(opcode) == List):
            for op in opcode:
                _retStatus = self.__setOPStatus(pluginName,op,True)
                if(_retStatus == False):
                    self.writeLog(loger.LogLevel.Warning,
                              f"when regist opcode event ID {op} to plugin {pluginName} failed")
    # 重载插件
    def reloadPlugin(self,pluginName:str):
        self.__load(pluginName,True)
    # 卸载插件
    def unRegistPlugin(self,pluginName:str):
        _ret_cursor = self.__cursor.execute(f'SELECT ID,name FROM plugins WHERE name = "{pluginName}";')
        if(len(_ret_cursor.fetchall()) == 0):
            # 尚未加载
            return False
        for _data in _ret_cursor:
            ID = _data[0]
            self.__LoaderPlugins.pop(f"ID_{ID}") if f"ID_{ID}" in self.__LoaderPlugins else None
            self.__cursor.execute(f'DELETE FROM plugins WHERE ID = "{ID}";')
            self.__plugins.commit()
        return True
    # 对父级方法进行封装
    def writeLog(self,level,content:str):
        self.caller.writeLog(level,content)
    # 处理函数
    async def deal(self,opcode:int,version:int,data:bytes,path:str):
        _ret_cursor = self.__cursor.execute(f'SELECT ID,name FROM plugins WHERE op_{opcode} = 1;')
        for _data in _ret_cursor.fetchall():
            ID = _data[0]
            _thisPlugin = self.__LoaderPlugins[f"ID_{ID}"]
            try:
                await _thisPlugin.pluginsModuleType.dealFunc(opcode,version,data,path)
            except:
                self.writeLog(loger.LogLevel.Error,
                              f"can not deal opcode event ID {opcode} to plugin {_thisPlugin.pluginsName}, error traceback:\n{traceback.format_exc()}")
            await asyncio.sleep(0)
        
class Loader:
    __breakPlugin = ["sdk","testPlugin"]
    def __init__(self) -> None:
        __callerFrame = inspect.currentframe().f_back.f_locals
        if("self" in __callerFrame):
            self.caller = __callerFrame["self"]
        self.callerGlobal = inspect.currentframe().f_back.f_globals
        self.log = self.caller.log
        self.LoaderDeal = LoaderDeal(self)
        self.__load()
    def __load(self):
        for root, dirs, files in os.walk("./plugins"):
            for file in files:
                if(file.endswith(".py")):
                    fileName,_back_py = os.path.splitext(file)
                    if(fileName in self.__breakPlugin):
                        continue
                    self.load(fileName,None)
    # 对父级方法进行封装
    def writeLog(self,level,content:str):
        self.caller.writeLog(level,content)

    def load(self,pluginsName:str,opcode:Optional[Union[int,List[int]]] = None):
        self.LoaderDeal.registPlugin(pluginsName,opcode)
    
    def reload(self,pluginsName:str):
        self.LoaderDeal.reloadPlugin(pluginsName)

    async def deal(self,opcode:int,version:int,data:bytes,path:str):
        await self.LoaderDeal.deal(opcode,version,data,path)