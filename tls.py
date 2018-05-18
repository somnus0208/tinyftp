import argparse
import socket
import struct
RES_CMD_OK = 1
RES_DIR = 2
RES_FILE_SIZE = 8
RES_FILE_BEG = 9
RES_FILE_END = 10
RES_FILE_BUF = 3
RES_ERROR = 4
RES_UPL_FILE_OK = 11

REQ_DIR = 5
REQ_FILE = 6
REQ_UPL_FILE = 7
REQ_CLS = 12

class TLV:
    def __init__(self,tag,val=None):
        self.tag = tag
        self.val = val
        self.length = 0
        if isinstance(self.val,str):
            self.length = len(bytes(self.val,'utf-8'))
        elif isinstance(self.val,bytes):
            self.length = len(val)
    def __bytes__(self):
        if isinstance(self.val,str):
            return struct.pack('ii',self.tag,self.length) + bytes(self.val,'utf-8')
        elif isinstance(self.val,bytes):
            return struct.pack('ii',self.tag,self.length) + self.val
        return struct.pack('ii',self.tag,self.length)

class ArgumentParserError(Exception): pass


class ThrowingArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise ArgumentParserError(message)
    def exit(self, status=0, message=None):
        pass

class tlvsocket:
    def __init__(self, family=socket.AF_INET, type=socket.SOCK_STREAM, proto=0, fileno=None):
        self._socket = socket.socket(family,type,proto,fileno)
    def accept(self):
        s,addr = self._socket.accept()
        tlvs = tlvsocket()
        tlvs._socket = s
        return tlvs,addr  
    def sendtlv(self,tlv):
        if isinstance(tlv,TLV):
            self._socket.sendall(bytes(tlv))
        else:
            raise TypeError

    def recvtlv(self):
        tag,length = struct.unpack('ii',self._socket.recv(8))
        if tag==RES_FILE_BUF:
            val = self._socket.recv(length)
        else:
            val = str(self._socket.recv(length),'utf-8')
        return TLV(tag,val)

    def bind(self,*addr):
        self._socket.bind(*addr)
    def listen(self,backlog):
        self._socket.listen(backlog)
    def connect(self,address):
        self._socket.connect(address)
    def close(self):
        self._socket.close()
