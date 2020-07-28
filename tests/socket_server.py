# -*- coding: UTF-8 -*-
import socket
import os

server = socket.socket()
server.bind(('localhost', 6968))
server.listen(5)  # 最大监听的连接数量
print("开始监听")
while True:
    conn, addr = server.accept()
    print("客户端{}接入:".format(addr))
    while True:
        print("等待命令")
        data = conn.recv(1024)
        if not data:
            print("客户端{}已断开".format(addr))
            break
        print("执行命令:", data.decode())
        cmd_res = os.popen(data.decode()).read()  # 接受字符串，返回也是字符串
        if len(cmd_res) == 0:
            cmd_res = 'command not found'  # 输入命令行错误时，返回
        conn.send(str(len(cmd_res.encode())).encode('utf-8'))  # 先发数据大小给客户端
        client_ack = conn.recv(1024)  # 解决粘包问题,增加ack
        conn.send(cmd_res.encode('utf-8'))

server.close()
