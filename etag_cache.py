
'''
 * Copyright@Lcenter
 * Author:TuYongXuan
 * Date:2019-09-20
 * Description:内存缓存库
'''
import os
import time
import threading

class PaiCache():

    def __init__(self):
        self.file_info_list = {}
        self.running = True
        threading.Thread(target=self.quickVerification, args=()).start()

    def getFileInfo(self, path):
        if path not in self.file_info_list:
            result = self.setFileInfo(path)
            self.file_info_list[path] = [result[0], result[1]]
            return result
        else:
            return self.file_info_list[path]

    def setFileInfo(self, path):
        etag    = hex(int(os.path.getmtime(path)))[2:] + '-' + hex(os.path.getsize(path))[2:]
        last_mf = time.strftime('%a, %d %b %Y %H:%M:%S GMT' , time.localtime(os.path.getmtime(path)))
        return [etag, last_mf]
    
    def quickVerification(self):
        while self.running:
            if self.file_info_list:
                for info in self.file_info_list:
                    if os.path.exists(info):
                        self.file_info_list[info] = self.setFileInfo(info)
                    else:
                        del self.file_info_list[info]
                time.sleep(0.001)

            else:
                #最小间隔 1s
                time.sleep(1)
