import socket
import os
import argparse
import struct
import tls
import sys

class ArgumentParserError(Exception): pass


class ThrowingArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise ArgumentParserError(message)
    def exit(self, status=0, message=None):
        pass

def command_cd(client, args):
    tlv = tls.TLV(tls.REQ_W_DIR_CHANGE, args.param)
    print(args.param)
    client.send_tlv(tlv)
    tlv = client.recv_tlv()
    if tlv.tag == tls.RES_ERROR:
        print('error: {}'.format(tlv.val))

def command_lcd(client, args):
    nw_dir = client.working_dir
    if os.path.isabs(args.param):
        nw_dir = args.param
    else:
        nw_dir = os.path.join(nw_dir,args.param)
    try:
        os.listdir(nw_dir)
        client.working_dir = nw_dir
    except FileNotFoundError:
        print('error: no such file or directory:{0}'.format(args.param))
def command_pwd(client, args):
    tlv = tls.TLV(tls.REQ_W_DIR)
    client.send_tlv(tlv)
    tlv = client.recv_tlv()
    if tlv.tag == tls.RES_ERROR:
        print('error: {}'.format(tlv.val))
    elif tlv.tag == tls.RES_CMD_OK:
        print('remote:{0}'.format(tlv.val))

def command_lpwd(client, args):
    print(client.working_dir)

def command_lst(client, args):
    tlv = tls.TLV(tls.REQ_DIR)
    client.send_tlv(tlv)
    tlv = client.recv_tlv()
    if tlv.tag == tls.RES_ERROR:
        print('error:{}'.format(tlv.val))
    elif tlv.tag == tls.RES_DIR:
        print(tlv.val)

def command_put(args):
    print("upload")

def command_get(client, args):
    tlv = tls.TLV(tls.REQ_FILE,args.param)
    client.send_tlv(tlv)
    tlv = client.recv_tlv()
    if tlv.tag == tls.RES_ERROR:
        print('Error:{}'.format(tlv.val))
    elif tlv.tag == tls.RES_FILE_BEG:
        w_dir = client.working_dir
        file_name = tlv.val
        file_abs_name = os.path.join(w_dir,file_name)
        file_object = open(file_abs_name, 'wb')
        tlv = client.recv_tlv()
        if tlv.tag == tls.RES_FILE_SIZE:
            eval(tlv.val)
        tlv = client.recv_tlv()
        while tlv.tag!=tls.RES_FILE_END:
            file_object.write(tlv.val)
            tlv = client.recv_tlv()
        file_object.close()

def command_cls(client, args):
    client.send_tlv(tls.TLV(tls.REQ_CLS))
    sys.exit()

if __name__=='__main__':
    mainparser = argparse.ArgumentParser()
    mainparser.add_argument('serverip')
    addr = (mainparser.parse_args().serverip,9000)
    client = tls.tlvsocket()
    client.working_dir = os.getcwd()
    client.connect(addr)
    print('server {} connected'.format(addr[0]))
    parser = ThrowingArgumentParser(description='tiny ftp client')
    subparsers = parser.add_subparsers()

    parser_pwd = subparsers.add_parser('close', help='close this connection')
    parser_pwd.set_defaults(handler=command_cls)

    parser_pwd = subparsers.add_parser('pwd', help='print name of working directory')
    parser_pwd.set_defaults(handler=command_pwd)

    parser_lpwd = subparsers.add_parser('lpwd', help='print name of local working directory')
    parser_lpwd.set_defaults(handler=command_lpwd)

    parser_cd = subparsers.add_parser('cd', help='change remote working directory')
    parser_cd.add_argument('param',metavar='directory')
    parser_cd.set_defaults(handler=command_cd)

    parser_lcd = subparsers.add_parser('lcd', help='changes local working directory')
    parser_lcd.add_argument('param',metavar='directory')
    parser_lcd.set_defaults(handler=command_lcd)

    parser_lst = subparsers.add_parser('list', help='returns information of working directory')
    parser_lst.set_defaults(handler=command_lst)

    parser_put = subparsers.add_parser('put', help='uploads file')
    parser_put.add_argument('param',metavar='file')
    parser_put.set_defaults(handler=command_put)

    parser_get = subparsers.add_parser('get', help='downloads file')
    parser_get.add_argument('param',metavar='file')
    parser_get.set_defaults(handler=command_get)

    while True:
        sub_cmd = input('Tinyftp>>>')
        try:
            args = parser.parse_args(sub_cmd.split())
            if hasattr(args, 'handler'):
                args.handler(client, args)
        except ArgumentParserError:
            parser.print_help()
            continue
