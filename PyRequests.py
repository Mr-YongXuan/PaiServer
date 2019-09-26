'''
 * Copyright@Lcenter
 * Author:TuYongXuan
 * Date:2019-09-20
 * Description:HTTP请求解析库
'''

import os
import time
import mimetypes
import PyCommon as cfg

def handle_request(header):
    feedback = {}
    file_range = []
    response = cfg.HttpVersion
    header = header.split('\n')
    #for i in header:
    #  print(i)
    common = header[0].split(' ')
    print("method:%s resource:%s version:%s" %(common[0], common[1], common[2]))

    #请注意此需要处理GET请求
    if '?' in common[1]:
      common[1] = common[1].split('?')[0]
    
    for i in header:
      if "Range:" in i:
        file_range.append(int(i.split('bytes=')[1].split('-')[0]))
        file_range.append(int(i.split('bytes=')[1].split('-')[1][:-1]))
        break

    result = handle_file(common[1], common[0], file_range)
    response += " %s %s\n" %(result['code'], cfg.CodeList[result['code']])
    response += "Server: %s %s\n" %(cfg.ServerName, cfg.ServerVer)
    response += "Date: %s\n" % time.strftime('%a, %d %b %Y %H:%M:%S GMT' ,time.gmtime())

    feedback['keep'] = False
    for i in header:
      if "Connection:" in i and 'keep-alive'in i.split(':')[1]:
        feedback['keep'] = True
        response += "Connection: keep-alive\n"
    
    response += "Content-Type: %s\n" % result['type']
    if result['options']:
      for option in result['options']:
        response += option
    response += "Content-Length: %s\n\n" % result['size']

    response = response.encode('utf-8')
    response += result['data']
    return feedback, response

def handle_file(path, method, file_range):
    file_info = {}
    file_info['options'] = []
    path = 'html' + path
    if os.path.isdir(path):
        path = os.path.join(path, 'index.html')
    if not os.path.exists(path):
        file_info['code'] = 404
        file_info['size'] = len(cfg.NotFound)
        file_info['type'] = 'text/html' + "; charset=%s" %cfg.CharSet
        file_info['data'] = cfg.NotFound.encode('utf-8')
    else:
      if os.access(path, os.R_OK):
        file_info['code'] = 200
        
        if file_range:
          file_info['size'] =  file_range[1] - file_range[0] + 1
        else:
          file_info['size'] = os.path.getsize(path)
        file_info['real_size'] = os.path.getsize(path)

        mime = mimetypes.guess_type(path)[0]
        if  mime != "text/html":
          file_info['options'].append("Accept-Ranges: bytes\n")
          if 'text' in mime:
            file_info['type'] = mimetypes.guess_type(path)[0] + "; charset=%s" %cfg.CharSet
          else:
            file_info['type'] = mimetypes.guess_type(path)[0]
        else:
          file_info['type'] = mimetypes.guess_type(path)[0] + "; charset=%s" %cfg.CharSet

        if method == 'HEAD':
          file_info['data'] = b''
        else:
          with open(path, 'rb') as f:
            if file_range:
              file_info['code'] = 206
              f.seek(file_range[0])
              file_info['data'] = f.read(file_range[1] + 1)
              file_info['options'].append("Content-Range: bytes %s-%s/%s\n" %(file_range[0], file_range[1], file_info['real_size']))
            else:
              file_info['data'] = f.read()
      else:
        file_info['code'] = 403
        file_info['size'] = len(cfg.Forbidden)
        file_info['type'] = 'text/html' + "; charset=%s" %cfg.CharSet
        file_info['data'] = cfg.Forbidden.encode('utf-8')

    return file_info
