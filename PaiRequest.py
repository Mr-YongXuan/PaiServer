'''
 * Copyright@Lcenter
 * Author:TuYongXuan
 * Date:2019-09-20
 * Description:HTTP请求解析库
'''

import os
import time
import mimetypes

import PaiCommon as cfg

def handle_request(header, info_cache):
    feedback = {}
    file_range = []
    dict_header = {}
    feedback['keep'] = False
    feedback['EndFile'] = False
    response = cfg.HttpVersion

    #切割头部信息
    try:
      header = header.split('\n')
      common = header.pop(0).split(' ')
    
      #将用户请求头转换为字典 增加后期处理头部效率
      for key_value in header:
        result = key_value.split(':')
        if len(result) == 2:
          dict_header[result[0]] = result[1][:-1]

      print("method:%s resource:%s version:%s" %(common[0], common[1], common[2]))

      #请注意此需要处理GET请求
      if '?' in common[1]:
        common[1] = common[1].split('?')[0]
    except:
      #错误头部信息处理 400
      response += " %s %s\n" %(400, cfg.CodeList[400])
      response += "Server: %s %s\n" %(cfg.ServerName, cfg.ServerVer)
      response += "Date: %s\n" % time.strftime('%a, %d %b %Y %H:%M:%S GMT' ,time.gmtime())
      response += "Content-Type: text/html; charset=%s\n" % cfg.CharSet
      response += "Content-Length: %s\n\n" % len(cfg.BadRequest)
      response += cfg.BadRequest
      return feedback, response.encode('utf-8')

    #检查是否需要分段传输
    if "Range" in dict_header:
      file_range.append(int(dict_header['Range'].split('bytes=')[1].split('-')[0]))
      file_range.append(int(dict_header['Range'].split('bytes=')[1].split('-')[1]))
    
    #调用文件读取 封装基本响应头部
    result = handle_file(common[1], common[0], file_range, info_cache)
    response += " %s %s\n" %(result['code'], cfg.CodeList[result['code']])
    response += "Server: %s %s\n" %(cfg.ServerName, cfg.ServerVer)
    response += "Date: %s\n" % time.strftime('%a, %d %b %Y %H:%M:%S GMT' ,time.gmtime())

    #检查是否需要保持连接
    if "Connection" in dict_header and 'keep-alive' in dict_header['Connection']:
      feedback['keep'] = True
      response += "Connection: keep-alive\n"
    
    #封装文件类型 添加附加选项 封装数据长度
    response += "Content-Type: %s\n" % result['type']
    for option in result['options']:
      response += option
    response += "Content-Length: %s\n\n" % result['size']

    #将头部信息转换为bytes类型并加入文件内容,如果文件过大则告知PaiCore分段传输
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
    path = os.path.join(cfg.RootPath, path[1:])
    if os.path.isdir(path):
        for index in cfg.IndexPage:
          t_path = os.path.join(path, index)
          if os.path.exists(t_path):
            path = t_path
            break
    if not os.path.exists(path) or os.path.isdir(path):
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
