import asyncio
from fastapi import FastAPI,APIRouter,WebSocket
from fastapi.websockets import WebSocketState
import uvicorn
import loger
import proto


class Server:
    clients:dict[str,WebSocket] = {}
    def __init__(self,moreLog:bool = False) -> None:
        self.moreLog = moreLog
        self.app = FastAPI()
        self.api = APIRouter()
        self.api.add_api_websocket_route("/{path}",self.__listen)
        self.app.include_router(self.api)
        self.log = loger.Log()
    
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
                        if(opcode == proto.Proto_Const.OP_AUTH_REPLY):
                            # 收到认证返包，开启定时心跳
                            pass
                        elif(opcode == proto.Proto_Const.OP_HEART_REPLY):
                            # 收到心跳返包
                            pass
                        elif(opcode == proto.Proto_Const.OP_MSG_RECV):
                            # 接收到消息
                            pass
                        elif(opcode == proto.Proto_Const.OP_MSG_SEND_REPLY):
                            # 接收到发送消息的回复包
                            pass
                        elif(opcode == proto.Proto_Const.OP_MSG_STATUS):
                            # 接收到消息状态更新包
                            pass
                    

                    self.writeLog(loger.LogLevel.Info,info)
                except RuntimeError:
                    self.writeLog(loger.LogLevel.Warning,"客户端发生错误")
                except proto.Proto_Error:
                    self.writeLog(loger.LogLevel.Warning,"客户端发送数据错误")
                except :
                    pass
    
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



