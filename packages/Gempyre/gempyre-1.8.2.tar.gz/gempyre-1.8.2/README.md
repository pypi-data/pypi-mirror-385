# Gempyre-Python 

The easy and productive UI library for Python.

If you know HTML, Gempyre is for you!

## Gempyre

Gempyre is a C++ GUI library, see https://github.com/mmertama/Gempyre.git.

## install from PyPi

There are many flavors in installing - but you need at least Python3.8
on Linux, Windows or MacOS. 

e.g.

```bash
pip3 install Gempyre --user  
```
or using Poetry

```bash
poetry add Gempyre
```
gi
Installs Gempyre to the current user site-packages.

See also  (https://docs.python.org/3/library/venv.html)
or (https://python-poetry.org/), or (https://pipenv.pypa.io/en/latest/)

## Build from sources

You can clone the repository and do install, or get releases from repository.

Gempyre-Python uses scikit build (some OS would need use python3 instead of python, you may need `pip install scikit-build` first):
`python -m build && pip install .`

## Notes:
### Raspberry OS

Todo: Needs optional RASPEBERRY flag to be passed to CMake. 
  
### Missing libraries  

You may need python3-dev and python3-pip be installed. This may depend on your evironment,
In linux e.g. apt-get install python3-dev, in MacOS look brew.

Dialogs requires pywebview installed that wont be hard dependency on 1.8.2 onwards. 
Upon need, please install manually.

### Build with scikit-build

```bash
python3 -m venv venv
source venv/bin/activate
pip3 install scikit-build
pip3 install .
python3 examples/balls/balls.py
```

### Windows:

```
# Windows has a limit of path lengths to 260 chars - 8-+ 
#   
#   "260 characters is enough for everybody"
#                 - W.G III

```

Windows default filepath length is an issue. 
See [Here](https://www.howtogeek.com/266621/how-to-make-windows-10-accept-file-paths-over-260-characters/)
and [Here](https://learn.microsoft.com/en-us/windows/win32/fileio/maximum-file-path-limitation?tabs=powershell)
(reboot after change)

If that does not help (or not an option) you may try say in powershell.

```
mkdir C:\f
$env:TMPDIR = "C:\f"
$env:TEMP = "C:\f"

```

...before pip install. 


### Run

After install, you just run the script!

  ```bash
  $ python3 test/telex_test.py
  ```

## API

See examples how to use e.g. [telex_test](https://github.com/mmertama/Gempyre-Python/blob/master/test/telex_test.py)

The programming interface is very same as in [Gempyre](https://github.com/mmertama/Gempyre.git)
- except I changed function and method name naming from CamelCase to more pythonic snake_case (Im not sure if that was a right choice).

Please look  [Gempyre](https://github.com/mmertama/Gempyre.git) for documentation.

There are some differences with functions, mainly due C++ overloading - I have left out some parameter combinations that are not important. See [exceptions.txt](https://github.com/mmertama/Gempyre-Python/blob/master/exceptions.txt). 

Please note that Gempyre Core and Gempyre Graphics are part of Python API, but not GempyreUtils, it has C++ utilites and thus not applicable for Python programmers as everything and more is already there!

## Python spesific issues:

As Gempyre is having its own event loop, using with asyncio needs Gempyre to be executed in its own thread.

Example

```python

# non-async
def draw(canvas):
  fc = Gempyre.FrameComposer()
  fc.fill_style("magenta")
  fc.fill_rect(Gempyre.Rect(1, 1, 30, 30)) 
  canvas.draw_frame(fc)

# async
async def on_open(canvas)
  await asyncio.sleep(3) # example wait
  draw(canvas)

async def main():
  map, names = resource.from_bytes({"ui.html": bytes(html, 'utf-8')})
  ui = Gempyre.Ui(map, names["ui.html"])
  loop = asyncio.get_running_loop()  # Get the current event loop
  # Schedule on_open to be called in the event loop thread
  ui.on_open(lambda: loop.call_soon_threadsafe(asyncio.create_task, on_open(Gempyre.CanvasElement(ui, 'canvas'))))
  # Run ui.run() in a separate thread
  await asyncio.to_thread(ui.run)

if __name__ == "__main__":
  asyncio.run(main())

```
  
## Examples

See [examples and demos](https://github.com/mmertama/Gempyre-Python/tree/master/examples)

See [small test apps](https://github.com/mmertama/Gempyre-Python/tree/master/test)

### Minimum single file app

```py

#!/usr/bin/python3
import Gempyre
import os
import sys
from Gempyre import resource

html = '''
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate" />
  <meta http-equiv="Pragma" content="no-cache" />
  <meta http-equiv="Expires" content="0" />
</head>
<body>
  <script src="/gempyre.js"></script>
  Hello!
</body>
</html>  
'''


if __name__ == "__main__":
    map, names = resource.from_bytes({"ui.html": bytes(html, 'utf-8')})
    ui = Gempyre.Ui(map, names["ui.html"])
    ui.run()
    

```


### Minimum application with an external UI file

  ```py
  import Gempyre
  import os
  import sys
  from Gempyre import resource

  name = os.path.join(os.path.dirname(sys.argv[0]), "hello.html")
  map, names = resource.from_file(name)
  ui = Gempyre.Ui(map, names[name])
  ui.run()
  ```

#### HTML

Assumed to be found in the same folder as the script

  ```html
  <!DOCTYPE html>
  <html>
    <head>
      <meta charset="utf-8">
    </head>
    <body>
      <script src="/gempyre.js"></script>
      Hello!
    </body>
  </html>
  ```

### Application with interaction
#### Python
```py

def main():
    name = os.path.join(os.path.dirname(sys.argv[0]), "example2.html")
    map, names = resource.from_file(name)
    ui = Gempyre.Ui(map, names[name])
    output = Gempyre.Element(ui, "output")
    open_button = Gempyre.Element(ui, "open")
    open_button.subscribe("click", lambda _: output.set_html("Hello"))
    ui.run()

if __name__ == "__main__":
    main()
```
#### HTML
  ```html
  <!DOCTYPE html>
  <html>
    <head>
      <meta charset="utf-8">
      <title>test</title>
    </head>
    <body>
      <script src="/gempyre.js"></script>
      <button id="open">Open</button>
      <pre id="output"></pre>
    </body>
  </html>
  ```
