import sys
import os
import math
import Gempyre
from datetime import datetime
from datetime import date
from datetime import timedelta
from Gempyre import resource

name = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(sys.argv[0]), "python_test_1.html")

map, names = resource.from_file(name)
print(names[name], name)

ui = Gempyre.Ui(map, names[name], "Test app") if sys.platform != 'win32' or sys.version_info < (
    3, 8) else Gempyre.Ui(map, names[name], "")

ver, major, minor = Gempyre.version()
Gempyre.Element(ui, 'ver').set_html("Gempyre Version: " + str(ver) + '.' + str(major) + '.' + str(minor));

eyes = Gempyre.CanvasElement(ui, 'eyes')
eyes_rect = None


def on_start():
    global eyes_rect
    eyes_rect = eyes.rect()
    print(ui.root().html())
    ui.start_periodic(timedelta(seconds=1), lambda: Gempyre.Element(ui,'time').set_html(
                       datetime.now().strftime("%d/%m/%Y %H:%M:%S")))


ui.on_open(on_start)

elementCount = 0

addbutton = Gempyre.Element(ui, 'do')


def add_element(event):
    global elementCount
    new = Gempyre.Element(ui, "name_" + str(elementCount), "img", ui.root())
    elementCount += 1
    new.set_attribute("SRC", "https://www.animatedimages.org/data/media/202/animated-dog-image-0931.gif")

    
addbutton.subscribe('click', add_element)

removebutton = Gempyre.Element(ui, 'take')


def removeElement(event):
    global elementCount
    if elementCount <= 0:
        return
    elementCount -= 1
    Gempyre.Element(ui, "name_" + str(elementCount)).remove()


removebutton.subscribe('click', removeElement)

ui.on_exit(lambda: print("on Exit"))

tick1 = Gempyre.Element(ui, 'tick1')
tick2 = Gempyre.Element(ui, 'tick2')


def toggle(e0, e1):
    if e0.values()['checked'] == 'true':
        e1.set_attribute('checked', 'false')
    else:
        e1.set_attribute('checked', 'true')


tick1.subscribe('click', lambda _: toggle(tick1, tick2))
tick2.subscribe('click', lambda _: toggle(tick2, tick1))
tick1.set_attribute('checked', 'true')

def move_eyes(x, y):
    fc = Gempyre.FrameComposer()
    fc.clear_rect(Gempyre.Rect(0, 0, 80, 80))
    
    def draw_eye(fc, px, py, x, y):
        fc.begin_path()
        fc.arc(px, py, 20, 0, 2 * math.pi)
        fc.stroke_style('black')
        fc.stroke()
    
        angle = math.atan2(x, y)
        dx = math.fabs(x - px)
        dy = math.fabs(y - py)
        xx = math.sin(angle) * min(dx, 10)
        yy = math.cos(angle) * min(dy, 10)
        fc.begin_path()
        fc.arc(px + xx, py + yy, 10, 0, 2 * math.pi)
        fc.fill_style('black')
        fc.fill()
    
    draw_eye(fc, 20, 40, x, y)
    draw_eye(fc, 60, 40, x, y)
    eyes.draw_frame(fc)
    
ui.root().subscribe('mousemove', lambda e: move_eyes(float(e.properties['clientX']) - eyes_rect.x,
                                                     float(e.properties['clientY']) - eyes_rect.y),
                     ["clientX", "clientY"], timedelta(milliseconds=100))

kitt_canvas = Gempyre.CanvasElement(ui, "kitt")
g = Gempyre.Bitmap(200, 20)
position = 1
direction = 1


def draw_kitt():
    global position
    global direction
    position += direction
    if position >= 198:
        direction = -1
    if position <= 0:
        direction = 1;
    g.draw_rect(Gempyre.Rect(0, 0, 200, 20), Gempyre.Black)
    for i in range(0, 20):
        g.set_pixel(position - 1, i, Gempyre.Red)
    for i in range(0, 20):
        g.set_pixel(position, i, Gempyre.Bitmap.pix(0xFF, 0xFF, 0))
    for i in range(0, 20):
        g.set_pixel(position + 1, i, Gempyre.Red)

# set redraw
kitt_canvas.draw_completed(lambda: kitt_canvas.draw_bitmap(g))
# set graphics motion update, i.e. fps and anitmation are now decoupled (which is important)
ui.start_periodic(timedelta(milliseconds=10), draw_kitt)
# draw 1st time, draw_completed does redraw
kitt_canvas.draw_bitmap(g)

ui.run()


