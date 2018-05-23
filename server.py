import socket
import os
import struct
import threading
import tls

def thread_handler(client,addr):
    while True:
        tlv = client.recv_tlv()
        if tlv.tag == tls.REQ_CLS:
            client.close()
            print('client {0} is closed'.format(addr[0]))
            break
        elif tlv.tag == tls.REQ_W_DIR:
            print('client {0} reqesting working directory'.format(addr[0]))
            client.send_tlv(tls.TLV(tls.RES_CMD_OK,str(client.working_dir)))
        elif tlv.tag == tls.REQ_DIR:
            files = os.listdir(client.working_dir)
            print('client {0} accessing {1}'.format(addr[0],client.working_dir))
            client.send_tlv(tls.TLV(tls.RES_DIR,str(files)))
        elif tlv.tag == tls.REQ_W_DIR_CHANGE:
            nw_dir = client.working_dir
            if os.path.isabs(tlv.val):
                nw_dir = tlv.val
            else:
                nw_dir = os.path.join(client.working_dir, tlv.val)
            try:
                os.listdir(nw_dir)
                client.working_dir = nw_dir
                client.send_tlv(tls.TLV(tls.RES_CMD_OK))
                print('client {0} change working dir to {1}'.format(addr[0],client.working_dir))
            except FileNotFoundError:
                client.send_tlv(tls.TLV(tls.RES_ERROR,'request directory error'))      
                print('client {0} request {1} bad'.format(addr[0],tlv.val))
                continue
            except OSError:
                client.send_tlv(tls.TLV(tls.RES_ERROR,'file or directory format error'))      
                print('client {0} request {1} bad'.format(addr[0],tlv.val))
                continue
        elif tlv.tag == tls.REQ_FILE:
            file_abs_name = os.path.join(client.working_dir,tlv.val)
            file_name = tlv.val
            try:
                file_size = str(os.stat(file_abs_name).st_size)
                client.send_tlv(tls.TLV(tls.RES_FILE_BEG,file_name))
                client.send_tlv(tls.TLV(tls.RES_FILE_SIZE,file_size))   
                file_object = open(file_abs_name, 'rb')
                print ('client {0} accessing {1}'.format(addr[0],file_abs_name))
                buff = file_object.read(1024)
                while (buff):
                    client.send_tlv(tls.TLV(tls.RES_FILE_BUF,buff))
                    buff = file_object.read(1024)
                client.send_tlv(tls.TLV(tls.RES_FILE_END))
                print('client {0} sending {1} completed'.format(addr[0],file_abs_name))
            except FileNotFoundError:
                client.send_tlv(tls.TLV(tls.RES_ERROR,'request file error'))      
                print('client {0} request {1} bad'.format(addr[0],file_abs_name))
                continue

        elif tlv.tag == tls.REQ_UPL_FILE:
            client.sendtlv(tls.TLV(tls.RES_UPL_FILE_OK))
            tlv = client.recvtlv()
            if tlv.tag==tls.RES_FILE_BEG:
                file_abs_name = tlv.val
                file_name = os.path.basename(file_abs_name)
                file_object = open(file_name,'wb')
                print ('client {0} uploading {1}'.format(addr[0],file_name))
                tlv = client.recvtlv()
                if tlv.tag == tls.RES_FILE_SIZE:
                    file_size = eval(tlv.val)
                tlv = client.recvtlv()
                while tlv.tag!=tls.RES_FILE_END:
                    file_object.write(tlv.val)
                    tlv = client.recvtlv()
            print('client {0} uploading {1} completed'.format(addr[0],file_name))
            file_object.close()


if __name__=='__main__':
    
    localip = socket.gethostbyname(socket.gethostname())
    server = tls.tlvsocket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((localip,9000))
    server.listen(5)
    print('listening at {}'.format(localip))
    while True:
        client,addr = server.accept()
        client.working_dir = os.getcwd()
        print('accept from {}'.format(addr))
        t = threading.Thread(target=thread_handler, args=(client,addr))
        t.start()

