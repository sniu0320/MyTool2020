# -*- coding: UTF-8 -*-
import socket

client=socket.socket() #
client.connect(('localhost',6969))

while True:
    msg=input('>>>:').strip()
    if len(msg)==0: continue #如果输入空格，不发送
    client.send(msg.encode('utf-8'))
    data=client.recv(1024)
    print(data.decode('utf-8'))

client.close()