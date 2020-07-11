# -*- coding: UTF-8 -*-
import socket

client=socket.socket() #
client.connect(('localhost',6968))

while True:
    cmd=input('>>>:').strip()
    if len(cmd)==0: continue #如果输入空格，不发送，重新循环
    client.send(cmd.encode('utf-8'))
    cmd_res_size=client.recv(1024) #接收命令结果的长度
    client.send('cmd_res_size ack'.encode('utf-8')) #解决粘包问题
    received_size=0
    received_data=b''
    while received_size < int(cmd_res_size.decode()):
        data=client.recv(1024)
        received_size += len(data)
        received_data += data
    else:
        #sprint(received_size)
        print(received_data.decode())

client.close()