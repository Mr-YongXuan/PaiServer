'''
 * Copyright@Lcenter
 * Author:TuYongXuan
 * Date:2019-09-20
 * Description:PyServer网络核心库
'''

import ssl
import time
import gevent
import threading
import PaiFileCache
import PaiRequest
import PaiCommon as cfg
from gevent import socket, monkey
from multiprocessing import Process

monkey.patch_all()

info_cache = PaiFileCache.PaiCache()

#连接管理器类
class ConnectionManager():

    def __init__(self):
        self.connection_pool = []
        tc = threading.Thread(target=self.time_connection, args=())
        tc.start()
    
    def add_connection(self, cli_sock):
        self.connection_pool.append([cli_sock, 0])
    
    def del_connection(self, cli_sock):
        for connect in self.connection_pool:
            if connect[0] == cli_sock:
                connect[0].close()
                self.connection_pool.remove(connect)
                return True
        return False
    
    def time_connection(self):
        while True:
            if self.connection_pool:
                for connect in self.connection_pool:
                    if connect[1] >= cfg.TimeOut:
                        self.del_connection(connect[0])
                    else:
                        connect[1] += 1
                        time.sleep(1)
            else:
                #防止因无连接导致CPU占用率过高
                time.sleep(1)

#运行核心类
class RunCore():

    def __init__(self, counter, config):
        
        self.sock = socket.socket()
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.sock.bind((cfg.HttpServer[config]['BindAddress'], cfg.HttpServer[config]['DefaultPort']))

#待确认
#        if "Https" in cfg.HttpServer[config]:
#            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
#            context.load_cert_chain(cfg.HttpServer[config]["Https"]["cert_pem"],
#            cfg.HttpServer[config]["Https"]["cert_key"])
#            self.sock = context.wrap_socket(self.sock, server_side = True)

        self.sock.listen(24511)
        
        for process_id in range(counter):
            Process(target=self.handle_process, args=(self.sock, process_id, config)).start()
        print("Server started at http://%s:%s Running core:%s" %(cfg.HttpServer[config]['BindAddress'], cfg.HttpServer[config]['DefaultPort'], counter))

    def handle_process(self, main_sock, pid, config):
        manager = ConnectionManager()
        while True:
            cli_sock, cli_addr = main_sock.accept()
            manager.add_connection(cli_sock)
            #print("Process %s:New connection: %s:%s" %(pid, cli_addr[0], cli_addr[1]))
            gevent.spawn(self.handle_coroutines, cli_sock, pid, manager, config)

#用户请求处理协程,每个用户都会有一个协程为其服务
    def handle_coroutines(self, cli_sock, pid, cm, config):
        while True:
            #当连接管理进程断开连接后,recv将会异常抛出
            try:
                result = cli_sock.recv(1024).decode('utf-8')
            except:
                break
            if not result:
                cli_sock.close()
                break
            feedback, data = PaiRequest.handle_request(result, info_cache, config)
            if feedback['EndFile']:
                try:
                    with open(feedback['path'], 'rb') as f:
                        cli_sock.sendall(data + f.read(cfg.SplitFileSize))
                        while True:
                            data = f.read(cfg.SplitFileSize)
                            cli_sock.sendall(data)
                            if len(data) < cfg.SplitFileSize:
                                break
                except:
                    cli_sock.close()
            else:
                cli_sock.sendall(data)
            #无需保持连接
            if not feedback['keep']:
                cm.del_connection(cli_sock)
                break

