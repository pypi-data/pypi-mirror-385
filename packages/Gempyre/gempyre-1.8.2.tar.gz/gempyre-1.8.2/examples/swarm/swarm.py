import Gempyre
from Gempyre import resource
import random
import math
from datetime import timedelta  # for time periods
import os
import sys


def normalize(r):
    while r < 0:
        r += 2 * math.pi
    while r >= 2 * math.pi:
        r -= 2 * math.pi
    return r


def _towards(r0, r, step):
    delta = r0 - r
    if delta < 0:
        if delta < math.pi:
            return r0 + step
        elif delta > math.pi:
            return r0 - step
        else:
            return r0 + step * random.randint(-1, 1)
    elif delta > 0:
        if delta > math.pi:
            return r0 + step
        elif delta < math.pi:
            return r0 - step
        else:
            return r0 + step * random.randint(-1, 1)


def towards(r0, r, step):
    return normalize(_towards(r0, r, step))


class Bee:
    width = 10
    height = 10
    min_distance = 300
    sight_len = 5

    def __init__(self, swarm):
        self.x = 0
        self.y = 0
        self.direction = random.random() * math.pi * 2
        self.heading = self.direction
        self.swarm = swarm
        self.speed = 1
        self.chasing = False
        self.see_x = 0
        self.see_y = 0

    def move(self):
        bee, dist = self.swarm.closest(self)
        if not bee:
            return
        if dist < self.min_distance:
            xx = self.x - bee.x
            yy = self.y - bee.y
            self.direction = math.atan2(yy, xx)
            self.chasing = False
        else:
            xx = self.x - self.swarm.fake_bee.x
            yy = self.y - self.swarm.fake_bee.y
            self.direction = math.atan2(yy, xx) + math.pi
            self.chasing = True
        self.heading = towards(self.heading, self.direction, 0.03)
        next_x = math.cos(self.heading) * self.speed
        next_y = math.sin(self.heading) * self.speed
        self.x += next_x
        self.y += next_y

        self.see_x = self.x + next_x * self.sight_len
        self.see_y = self.y + next_y * self.sight_len

    def draw(self, drawer):
        d = self.heading
        drawer.save()
        if self.chasing:
            drawer.fill_style('black')
        else:
            drawer.fill_style('blue')
        drawer.translate(self.x, self.y)
        drawer.rotate(d)
        drawer.translate(-self.x, -self.y)
        drawer.begin_path()
        drawer.move_to(self.x - self.width / 2, self.y - self.height / 2)
        drawer.line_to(self.x + self.width / 2, self.y)
        drawer.line_to(self.x - self.width / 2, self.y + self.height / 2)
        drawer.line_to(self.x - self.width / 4, self.y)
        drawer.fill()
        drawer.restore()


class Swarm:
    def __init__(self, bee_count):
        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0
        self.bees = []
        self.fake_bee = Bee(self)
        for i in range(0, bee_count):
            self.bees.append(Bee(self))

    def closest(self, bee):
        closest_one = None
        closest_one_dist = self.width * self.height
        for b in self.bees:
            if b != bee:
                dx = bee.see_x - b.see_x
                dy = bee.see_y - b.see_y
                dist = dx * dx + dy * dy
                if dist < closest_one_dist:
                    closest_one_dist = dist
                    closest_one = b
        return closest_one, closest_one_dist

    def mid_point(self):
        return (self.x + self.width / 2,
                self.y + self.height / 2)

    def set_pos(self, x, y):
        self.fake_bee.x = x
        self.fake_bee.y = y

    def move(self):
        for b in self.bees:
            b.move()

    def draw(self, drawer):
        for b in self.bees:
            b.draw(drawer)
        drawer.fill_rect(Gempyre.Rect(self.fake_bee.x - 5, self.fake_bee.y - 5, 10, 10))


def main():
    print(Gempyre.version())
    #Gempyre.set_debug()
    current_dir = os.path.dirname(sys.argv[0])
    file_map, names = resource.from_file(current_dir + "/swarm.html")
    ui = Gempyre.Ui(file_map, '/swarm.html', "Swarm", 800 + 15, 600 + 20)
    canvas = Gempyre.CanvasElement(ui, "canvas")
    swarm = Swarm(200)
    canvas_rect = Gempyre.Rect()

    def resize_handler(_):
        nonlocal canvas_rect
        canvas_rect = canvas.rect()
        swarm.x = 0
        swarm.y = 0
        swarm.width = canvas_rect.width
        swarm.height = canvas_rect.height

    ui.root().subscribe("resize", resize_handler)

    def draw():
        frame = Gempyre.FrameComposer()
        frame.clear_rect(Gempyre.Rect(swarm.x, swarm.y, swarm.width, swarm.height))
        swarm.draw(frame)
        frame.fill_rect(Gempyre.Rect(swarm.fake_bee.x - 5, swarm.fake_bee.y - 5, 10, 10))
        canvas.draw_frame(frame)

    def on_start():
        resize_handler(None)
        for b in swarm.bees:
            b.x = random.randint(b.width + swarm.x, swarm.width)
            b.y = random.randint(b.height + swarm.y, swarm.height)
        draw()

    ui.on_open(on_start)

    ui.start_periodic(timedelta(milliseconds=40), lambda: swarm.move())

    canvas.draw_completed(draw)

    def make_move(event):
        mouse_x = float(event.properties['clientX']) - canvas_rect.x
        mouse_y = float(event.properties['clientY']) - canvas_rect.y
        swarm.set_pos(mouse_x, mouse_y)

    canvas.subscribe('mousemove', make_move,
                     ["clientX", "clientY"], timedelta(milliseconds=100))

    ui.run()


if __name__ == "__main__":
    main()
