from typing import (
    Any,List,Dict,
    Callable
)
import asyncio
from proto import Proto_Const

class OPCODE:
    OP_AUTH = Proto_Const.OP_AUTH # 认证
    OP_AUTH_REPLY = Proto_Const.OP_AUTH_REPLY # 认证回复
    OP_HEART = Proto_Const.OP_HEART # 心跳
    OP_HEART_REPLY = Proto_Const.OP_HEART_REPLY # 心跳回复
    OP_MSG_RECV = Proto_Const.OP_MSG_RECV # 消息下发
    OP_MSG_SEND = Proto_Const.OP_MSG_SEND # 消息上传
    OP_MSG_SEND_REPLY = Proto_Const.OP_MSG_SEND_REPLY # 消息上传回复
    OP_MSG_STATUS = Proto_Const.OP_MSG_STATUS # 消息状态下发
    

class EvnetDeal:
    __dealDict:Dict[str,List[Callable]] = {}
    # 处理函数
    async def dealFunc(self, opcode:int, version:int, data:bytes, path:str):
        if(f"OP_{opcode}" not in self.__dealDict):
            return None
        for func in self.__dealDict[f"OP_{opcode}"]:
            await func(version, data, path)
            await asyncio.sleep(0)
    
    # 装饰器注册器
    def registFunc(self,*opcode:int):
        def wrapper(func):
            for op in opcode:
                self.addRegistFunc(op,func)
            return func
        return wrapper
    
    # 函数注册器
    def addRegistFunc(self,opcode:int,func:Callable):
        if(f"OP_{opcode}" not in self.__dealDict):
            self.__dealDict[f"OP_{opcode}"] = [func]
            return
        self.__dealDict[f"OP_{opcode}"].append(func)