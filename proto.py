import struct
from hashlib import sha256
import io

class Proto_Const:
    OP_AUTH = 0 # 认证
    OP_AUTH_REPLY = 1 # 认证回复
    OP_HEART = 2 # 心跳
    OP_HEART_REPLY = 3 # 心跳回复
    OP_MSG_RECV = 4 # 消息下发
    OP_MSG_SEND = 5 # 消息上传
    OP_MSG_SEND_REPLY = 6 # 消息上传回复
    OP_MSG_STATUS = 7 # 消息状态下发

    VERSION = 1 # 协议版本

    HEAD_CONST = "FurIM"

class Proto_Error(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
    
        
class Proto:
    def pack(self,op_code:int,version:int,_data:bytes):
        # header 16 bytes
        data = struct.pack(">16s",Proto_Const.HEAD_CONST.encode())
        # OP Code
        data += struct.pack(">H",op_code)
        # version
        data += struct.pack(">H",version)
        # sign Flag
        data += struct.pack(">H",1)
        # 先拼接后面的数据，在进行校验计算，校验时默认校验数值为0
        # data Flag
        lastData = struct.pack(">H",2)
        lastData += struct.pack(f">{len(_data)}s",_data)
        # 进行校验计算
        _tempData = data + struct.pack(">32x") + lastData
        s = sha256()
        s.update(_tempData)
        data += struct.pack(">32s",s.digest())
        data += struct.pack(f">{len(lastData)}s",lastData)
        return data

    def unpack(self,data:bytes):
        if(len(data) < 56):
            raise Proto_Error("Cannot unpack in-data because its not a proto data")
        with io.BytesIO(data) as f:
            header = bytes(struct.unpack(">16s",f.read(16))[0]).decode()
            if(header != Proto_Const.HEAD_CONST):
                return None
            opcode = struct.unpack(">H",f.read(2))[0]
            version = struct.unpack(">H",f.read(2))[0]
            sign_flag = struct.unpack(">H",f.read(2))[0]
            sign_data = struct.unpack(">32s",f.read(32))[0]
            if(self.__resign(data,sign_data) is False):
                raise Proto_Error("Signature verification failed")
            data_flag = struct.unpack(">H",f.read(2))[0]
            lastData = f.read()
            data_data = struct.unpack(">%ds"%(len(lastData)),lastData)[0]
        return opcode,version,data_data

    def __resign(self,_o:bytes,_s:bytes):
        _temp = _o[:22] + struct.pack(">32x") + _o[54:]
        s = sha256()
        s.update(_temp)
        return s.digest() == _s
        

