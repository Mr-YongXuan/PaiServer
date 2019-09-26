HttpVersion = "HTTP/1.1"

ServerName  = "PaiServer"

ServerVer   = "1.0.0 Alpha" 

CharSet     = "UTF-8"

TimeOut     = 60

CodeList = {
    200 : "OK",
    403 : "Forbidden",
    404 : "NotFound"
}

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
      <h3>PaiServer</h3>
    </center>
  </body>
</html>
'''

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
      <h3>PaiServer</h3>
    </center>
  </body>
</html>
'''

