#!/usr/bin/env python3
print "Content-type: text/html\r\n\r\n", 

import cgi, subprocess

log = {}

log['git_log'] = subprocess.check_output(['git', 'log', '-1'])
log['git_status'] = subprocess.check_output(['git', 'status'])
log['python_version'] = subprocess.check_output(['python', '--version'],
  stderr=subprocess.STDOUT)

print '''
<!DOCTYPE html>
<html>
  <head>
    <title>Feedvalidator status check</title>
  </head>
  <body>
    <h1>Git</h1>
    <h2>log</h2>
    <pre>%(git_log)s</pre>
    <h2>status</h2>
    <pre>%(git_status)s</pre>

    <h1>Python</h1>
    <pre>%(python_version)s</pre>
  </body>
<html>
'''[1:-1] % {k: cgi.escape(v.strip()) for k,v in log.items()}
