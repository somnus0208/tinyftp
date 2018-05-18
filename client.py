import socket
import os
import argparse
import struct
import tls
import sys
    

if __name__=='__main__':
    mainparser = argparse.ArgumentParser()
    mainparser.add_argument('serverip')
    addr = (mainparser.parse_args().serverip,9000)
    client = tls.tlvsocket()
    client.connect(addr)
    print('server {} connected'.format(addr[0]))
    parser = tls.ThrowingArgumentParser(prog='',add_help=False)
    parser.add_argument('action',choices=['list','get','put'])
    parser.add_argument('param',metavar='fileordirectory')
    while True:
        try:
            subcmd = input('Tinyftp>>>')
            if (subcmd=='close'):
                client.sendtlv(tls.TLV(tls.REQ_CLS))
                sys.exit()
            args = parser.parse_args(subcmd.split())
            tlv = None
            if args.action=='list':
                tlv = tls.TLV(tls.REQ_DIR,args.param)
            elif args.action=='get':
                tlv = tls.TLV(tls.REQ_FILE,args.param)
            elif args.action=='put':
                tlv = tls.TLV(tls.REQ_UPL_FILE)
                try:
                    os.stat(args.param)
                except FileNotFoundError:
                    print('{0} not Found'.format(args.param))
                    continue
            client.sendtlv(tlv)
        except tls.ArgumentParserError:
            parser.print_usage()
            continue

        tlv = client.recvtlv()
        if tlv.tag == tls.RES_ERROR:
            print('Error:{}'.format(tlv.val))
        elif tlv.tag == tls.RES_DIR:
            print(tlv.val)
        elif tlv.tag == tls.RES_FILE_BEG:
            file_abs_name = tlv.val
            file_name = os.path.basename(file_abs_name)
            file_object = open(file_name,'wb')
            tlv = client.recvtlv()
            if tlv.tag == tls.RES_FILE_SIZE:
                file_size = eval(tlv.val)
            tlv = client.recvtlv()
            while tlv.tag!=tls.RES_FILE_END:
                file_object.write(tlv.val)
                tlv = client.recvtlv()
            print('receiving {} completed'.format(file_name))
            file_object.close()
        elif tlv.tag == tls.RES_UPL_FILE_OK:
            file_abs_name = args.param
            file_name = os.path.basename(file_abs_name)
            file_size = str(os.stat(file_abs_name).st_size)
            client.sendtlv(tls.TLV(tls.RES_FILE_BEG,file_name))        
            client.sendtlv(tls.TLV(tls.RES_FILE_SIZE,file_size))   
            file_object = open(file_abs_name, 'rb')
            buff = file_object.read(1024)
            while (buff):
                client.sendtlv(tls.TLV(tls.RES_FILE_BUF,buff))
                buff = file_object.read(1024)
            client.sendtlv(tls.TLV(tls.RES_FILE_END))
            print('sending {} completed'.format(file_name))
        
