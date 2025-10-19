import sys
import os
import subprocess
import platform
import shlex
import psutil

import Gempyre
from Gempyre import resource

html = '''<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>test</title>
</head>
<body>
  <script src="/gempyre.js"></script>
  <table id="info">
  <tr id="header">
  </tr>
  </table>
  <input id="command_line" type="text"></input>
  <button id="run">Run</button>
  <pre id="output"></pre>
</body>
</html>
'''

map, names = resource.from_bytes({"main.html": bytes(html, 'utf-8')})

Gempyre.set_debug()

ui = Gempyre.Ui(map, names["main.html"])

header = Gempyre.Element(ui, "header");
Gempyre.Element(ui, "th", header).set_html("Name")
Gempyre.Element(ui, "th", header).set_html("Info")

name = list()

name.append(["Architecture", platform.architecture()[0]])
name.append(["Machine", platform.machine()])
name.append(["Node", platform.node()])
name.append(["System", platform.system()])

info = Gempyre.Element(ui, "info")
for n in name:
    h = Gempyre.Element(ui, "tr", info)
    Gempyre.Element(ui, "td", h).set_html(n[0])
    Gempyre.Element(ui, "td", h).set_html(n[1])
    
input = Gempyre.Element(ui, "command_line")
output = Gempyre.Element(ui, "output")

process = psutil.Process(os.getpid())
parent = process.parent()
decoding = 'CP850' if parent and parent.name() == 'cmd.exe' else 'utf-8'


def do_run(ev):
    global input
    global output
    value = input.values()
    if not value or len(value['value']) == 0:
        return
    command_line = shlex.split(value['value'])
    
    try:
        out = subprocess.run(command_line, stdout=subprocess.PIPE, shell=True).stdout.decode(decoding)
    except FileNotFoundError as e:
         output.set_html(str(e))
    else:
        output.set_html(out)   
               

Gempyre.Element(ui, "run").subscribe('click', do_run)    
    
ui.run()


