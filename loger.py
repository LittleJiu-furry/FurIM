import os
import time

def dealPath(*path):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), *path))

class LogLevel:
    Info = 0
    Warning = 1
    Error = 2
    Fatal = 3

class Log:
    level:list[str] = ["Info","Warning","Error","Fatal"]
    color:list[int] = [32,33,31,31]
    def __init__(self) -> None:
        if(os.path.exists(dealPath("./logs/")) is False):
            os.mkdir(dealPath("./logs/"))
    
    def writeLog(self, logLevel:int, logContent:str):
        _file = dealPath("./logs/",f"log-{time.strftime('%Y%m%d',time.localtime(time.time()))}.log")
        with open(_file,"a+",encoding="utf-8") as f:
            f.write(self.createLogContentOutToFile(logLevel,logContent)+"\n")
    
    def createLogContent(self, loglevel:int, logContent:str):
        _content = logContent.replace("\n","\\n")
        _ret1 = f"[{time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))}] [{self.level[loglevel]}] {_content}"
        _ret2 = f"[\033[34m{time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))}\033[0m] [\033[{self.color[loglevel]};1m{self.level[loglevel]}\033[0m] {_content}"
        return _ret1,_ret2
    
    def createLogContentOutToFile(self, loglevel:int, logContent:str):
        return self.createLogContent(loglevel,logContent)[0]

    def createLogContentOutToConsole(self, loglevel:int, logContent:str):
        return self.createLogContent(loglevel,logContent)[1]
