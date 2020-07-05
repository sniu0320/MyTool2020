# -*- coding: UTF-8 -*-
import socket
import os

server=socket.socket() #
server.bind(('localhost',6969))
server.listen(5) #最大监听的连接数量
print("开始监听")

while True:
    con, addr = server.accept()
    print(con, addr)
    print('{} clinet in...'.format(addr))
    while True:
        data=con.recv(1024)
        print("recv:",data.decode('utf-8'))
        if not data:
            print("{} client has lost...".format(addr))
            break
        # con.send(data.upper())
        res=os.popen(data.decode('utf-8')).read()
        # print(type(res))
        con.sendall(res.encode('utf-8'))

server.close()