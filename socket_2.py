"""
socket 简易ftp工具，只支持下载暂不支持上传，已实现MD5校验
"""

#server_start

#!/usr/bin/env python
# -*- coding:utf-8 -*-

import socket,os,hashlib
server = socket.socket()
server.bind(('localhost',9999))

server.listen()

while True:
    conn,addr = server.accept()
    print("new conn",addr)
    while True:
        print("等待新指令...")
        data = conn.recv(8192)
        if not data:
            print("客户端已断开")
            break
        cmd,filename = data.decode().split()
        print(filename)
        if os.path.isfile(filename):
            f = open(filename,'rb')
            m = hashlib.md5()
            file_size = os.stat(filename).st_size
            conn.send(str(file_size).encode("utf-8")) # send file size
            conn.recv(1024) #wait for ack
            for line in f:
                m.update(line)
                conn.send(line)
            print("file md5",m.hexdigest())
            f.close()
            conn.send(m.hexdigest().encode("utf-8")) # send md5
        print("send done...")
server.close()

#server_end

================================分割线======================

#client_start

#!/usr/bin/env python
# -*- coding:utf-8 -*-
import socket,hashlib
client = socket.socket()

client.connect(('localhost',9999))

while True:
    cmd = input(">>: ").strip()
    if not cmd: continue
    if cmd.startswith("get"):
        client.send(cmd.encode())
        server_response = client.recv(1024)
        print("server response:",server_response.decode())
        client.send(b"ready to recv file.")
        file_total_size = int(server_response.decode())
        received_size = 0
        filename = cmd.split()[1]
        f = open(filename+".new",'wb')
        m = hashlib.md5()
        while received_size < file_total_size :
            if file_total_size - received_size > 1024: #  要收不止一次
                size = 1024
            else: # 最后一次，剩多少收多少
                size = file_total_size - received_size
            data = client.recv(size)
            received_size += len(data)
            m.update(data)
            f.write(data)
            #print(file_total_size,received_size)
        else:
            new_file_md5 = m.hexdigest()
            print("file recv done...",received_size,file_total_size)
            f.close()
        server_file_md5 = client.recv(1024)
        print("server file md5:",server_file_md5.decode())
        print("client file md5:",new_file_md5)
client.close()

#client_end
