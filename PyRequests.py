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

def handle_request(header, info_cache):
    feedback = {}
    file_range = []
    response = cfg.HttpVersion
    header = header.split('\n')
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

    result = handle_file(common[1], common[0], file_range, info_cache)
    response += " %s %s\n" %(result['code'], cfg.CodeList[result['code']])
    response += "Server: %s %s\n" %(cfg.ServerName, cfg.ServerVer)
    response += "Date: %s\n" % time.strftime('%a, %d %b %Y %H:%M:%S GMT' ,time.gmtime())

    feedback['keep'] = False
    feedback['EndFile'] = False
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
    if result['data'] == b'Pai*EndFilePoint*Pai':
      feedback['EndFile'] = True
      feedback['path'] = result['path']
    else:
      response += result['data']
    return feedback, response

def handle_file(path, method, file_range, info_cache):
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

        if file_range:
              file_info['code'] = 206
              file_info['options'].append("Content-Range: bytes %s-%s/%s\n" %(file_range[0], file_range[1], file_info['real_size']))

        mime = mimetypes.guess_type(path)[0]
        if  mime != "text/html":
          etag = info_cache.getFileInfo(path)
          file_info['options'].append("Accept-Ranges: bytes\n")
          file_info['options'].append('Last-Modified: %s\n' % etag[1])
          file_info['options'].append('ETag: "%s"\n' % etag[0])

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
              f.seek(file_range[0])
              file_info['data'] = f.read(file_range[1] + 1)
            else:
              if file_info['size'] >= cfg.MaxFileSize:
                file_info['data'] = b'Pai*EndFilePoint*Pai'
                file_info['path'] = path
              else:
                file_info['data'] = f.read()
      else:
        file_info['code'] = 403
        file_info['size'] = len(cfg.Forbidden)
        file_info['type'] = 'text/html' + "; charset=%s" %cfg.CharSet
        file_info['data'] = cfg.Forbidden.encode('utf-8')

    return file_info
