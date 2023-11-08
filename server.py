import asyncio
from fastapi import FastAPI,APIRouter,WebSocket
from fastapi.websockets import WebSocketState
import uvicorn
import loger

class Server:
    clients:dict[str,WebSocket] = {}
    def __init__(self,moreLog:bool = False) -> None:
        self.moreLog = moreLog
        self.app = FastAPI()
        self.api = APIRouter()
        self.api.add_api_websocket_route("/{path}",self.__listen)
        self.app.include_router(self.api)
        self.log = loger.Log()
    
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
                break
            else:
                try:
                    data = await ws.receive_text()
                    self.writeLog(loger.LogLevel.Info,data)
                except:
                    self.writeLog(loger.LogLevel.Info,"客户端断开连接")
    
    # 运行服务器
    async def runServer(self):
        self.writeLog(loger.LogLevel.Info,"正在创建websocket服务器")
        _config = uvicorn.Config(self.app, host="localhost", port=8000,log_config=None)
        server = uvicorn.Server(_config)
        await server.serve()

    # 主动推送消息
    async def sendMessage(self,path:str,data:str):
        if(path in self.clients):
            _ws = self.clients[path]
            if(_ws.client_state != WebSocketState.CONNECTED):
                return
            await _ws.send_text(data)

    # writeLog功能封装
    def writeLog(self,level:loger.LogLevel,content:str):
        self.log.writeLog(level,content)
        print(self.log.createLogContentOutToConsole(level,content)) if self.moreLog else None

s = Server(moreLog=True)
asyncio.run(s.runServer())