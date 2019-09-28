HttpVersion = "HTTP/1.1"

Processes   = 8

HostName    = "localhost"

BindAddress = "127.0.0.1"

DefaultPort =  80

IndexPage   = ["index.html", "index.htm"]

RootPath    = "html"

ServerName  = "PaiServer"

ServerVer   = "0.0.1 Alpha" 

#默认MIME类型为text的数据编码格式
CharSet     = "UTF-8"

TimeOut     = 60

#最大不分段单文件传输大小,默认50M,单位为字节
MaxFileSize = 52428800

#单文件分段传输块大小,如无特殊需求,请不要改动SplitFileSize的属性值
#它可能会引起大文件传输时的不稳定性
SplitFileSize = 4096

#如无特殊需求,请不要改动CodeList的属性值,它可能会引起PaiServer不正常的工作现象
CodeList = {
    200 : "OK",
    206 : "PARTIAL CONTENT",
    400 : "BAD REQUEST",
    403 : "FORBIDDEN",
    404 : "NOT FOUND"
}

BadRequest = '''
<html>
  <head>
    <title>400 Bad Request</title>
  </head>
  <body>
    <center>
      <br /><br />
      <h1>400 Bad Request</h1>
      <hr>
      <h3>%s %s</h3>
    </center>
  </body>
</html>
''' % (ServerName, ServerVer)

Forbidden = '''
<html>
  <head>
    <title>403 Forbidden</title>
  </head>
  <body>
    <center>
      <br /><br />
      <h1>403 Forbidden</h1>
      <hr>
      <h3>%s %s</h3>
    </center>
  </body>
</html>
'''  % (ServerName, ServerVer)

NotFound = '''
<html>
  <head>
    <title>404 NotFound</title>
  </head>
  <body>
    <center>
      <br /><br />
      <h1>404 NotFound</h1>
      <hr>
      <h3>%s %s</h3>
    </center>
  </body>
</html>
'''  % (ServerName, ServerVer)

