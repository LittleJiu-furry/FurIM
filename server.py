import asyncio
from fastapi import FastAPI,APIRouter,WebSocket
from fastapi.websockets import WebSocketState
import uvicorn
import loger
import proto
from pluginsLoader import Loader
import traceback

class Server:
    clients:dict[str,WebSocket] = {}
    def __init__(self,moreLog:bool = False) -> None:
        self.moreLog = moreLog
        self.app = FastAPI()
        self.api = APIRouter()
        self.api.add_api_websocket_route("/{path}",self.__listen)
        self.app.include_router(self.api)
        self.log = loger.Log()
        self.loader = Loader()
    
    # 连接维护函数
    async def __listen(self,ws:WebSocket,path:str):
        if(path in self.clients):
            return None
        await ws.accept()
        self.writeLog(loger.LogLevel.Info,f"客户 {path} 连接")
        self.clients.update({path:ws})
        while True:
            _status = ws.client_state
            if(_status == WebSocketState.CONNECTING):
                continue
            elif(_status == WebSocketState.DISCONNECTED):
                self.clients.pop(path)
                self.writeLog(loger.LogLevel.Info,f"客户 {path} 断开连接")
                break
            else:
                try:
                    data = await ws.receive_bytes()
                    info = proto.Proto().unpack(data)
                    if(info):
                        opcode,version,data = info
                        # 将opcode，data，以及path传递到LoaderDeal里面，以便于loader下发事件到各个函数

                        # 这里是Server内部用于处理接收数据处理的部分
                        if(opcode == proto.Proto_Const.OP_AUTH):
                            # 客户端请求认证
                            pass
                        
                    
                        await self.loader.deal(opcode,version,data,path)
                    
                except RuntimeError:
                    self.writeLog(loger.LogLevel.Warning,"客户端发生错误")
                except proto.Proto_Error:
                    self.writeLog(loger.LogLevel.Warning,"客户端发送数据错误")
                except :
                    pass
            await asyncio.sleep(0)
    
    # 运行服务器
    async def runServer(self):
        self.writeLog(loger.LogLevel.Info,"正在创建websocket服务器")
        _config = uvicorn.Config(self.app, host="localhost", port=8000,log_config=None)
        server = uvicorn.Server(_config)
        await server.serve()

    # 主动推送消息
    async def sendMessage(self,path:str,data:bytes):
        if(path in self.clients):
            _ws = self.clients[path]
            if(_ws.client_state != WebSocketState.CONNECTED):
                return
            await _ws.send_bytes(proto.Proto().pack(proto.Proto_Const.OP_MSG_SEND,proto.Proto_Const.VERSION,data))

    # 主动断开连接
    async def closeClient(self,path:str):
        if(path in self.clients):
            _ws = self.clients[path]
            if(_ws.client_state != WebSocketState.CONNECTED):
                return
            await _ws.close()
            self.clients.pop(path)

    # writeLog功能封装
    def writeLog(self,level:loger.LogLevel,content:str):
        self.log.writeLog(level,content)
        print(self.log.createLogContentOutToConsole(level,content)) if self.moreLog else None



