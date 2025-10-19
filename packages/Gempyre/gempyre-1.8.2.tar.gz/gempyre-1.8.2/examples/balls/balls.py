import sys
import os
import math
import random
from datetime import timedelta
import Gempyre
from Gempyre import resource

TICK_SPEED = 30
MONSTER_SPEED = 0.15
BULLET_SPEED = 1.0
GUN_SPEED = 5.0
NUMBERS_WIDTH = 13
NUMBERS_HEIGHT = 25
BULLET_WIDTH = 20
BULLET_HEIGHT = 20
GUN_HEIGHT = 50
GUN_WIDTH = 100
BARREL_WIDTH = 10
BARREL_HEIGHT = 40
MONSTER_WIDTH = 40
MONSTER_HEIGHT = 40
TURRET_STEP = 0.01
MAX_AMMO = 100
GAME_SPEED = 50


class Number:
    def __init__(self, images):
        self.images = images

    def draw(self, g, x, y, width, height, value):
        g.draw_image_clip(self.images, Gempyre.Rect(
            NUMBERS_WIDTH * value, 0, NUMBERS_WIDTH, NUMBERS_HEIGHT), Gempyre.Rect(x, y, width, height))


class Monster:
    def __init__(self, x, y, width, height, endurance, numbers):
        self.step_y = MONSTER_SPEED
        self.step_x = 0
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.numbers = numbers
        self.endurance = endurance

    def step(self):
        self.y += self.step_y

    def test_inside(self, x, y, width, height):
        return self.y + self.height > y + height

    def draw(self, g, image):
        g.draw_image_rect(image, Gempyre.Rect(self.x, self.y, self.width, self.height))
        f1 = int(self.endurance / 10)
        f2 = self.endurance - (f1 * 10)
        self.numbers.draw(g, self.x + 6, self.y + 6, 10, 10, f1)
        self.numbers.draw(g, self.x + 24, self.y + 6, 10, 10, f2)


class Bullet:
    def __init__(self, direction, x, y):
        self.speed = BULLET_SPEED
        self.x = x
        self.y = y
        self.step_x = math.sin(direction) * self.speed
        self.step_y = math.cos(direction) * self.speed
        self.hit_in = None
        self.LEFT = 1
        self.TOP = 2
        self.RIGHT = 4
        self.BOTTOM = 8

    def step(self):
        self.x += self.step_x
        self.y += self.step_y

    def test_inside(self, x, y, width, height):
        if self.x < x:
            self.step_x *= -1.0
            self.x = x
        elif self.x + BULLET_WIDTH > x + width:
            self.step_x *= -1.0
            self.x = width - BULLET_WIDTH
        elif self.y < y:
            self.step_y *= -1.0
            self.y = y
        elif self.y + BULLET_HEIGHT > y + height:
            self.step_y *= -1.0
            self.y = height - BULLET_HEIGHT
            return True
        return False

    def is_inside(self, other):
        d_dir = 0
        if self.x <= other.x:
            d_dir |= self.LEFT
        if self.x + BULLET_WIDTH >= other.x + other.width:
            d_dir |= self.RIGHT
        if self.y <= other.y:
            d_dir |= self.TOP
        if self.y + BULLET_HEIGHT >= other.y + other.height:
            d_dir |= self.BOTTOM
        return d_dir

    def test_hit(self, other):
        ox = other.x + other.width
        oy = other.y + other.height
        sx = self.x + BULLET_WIDTH
        sy = self.y + BULLET_HEIGHT
        if self.x < ox and sx > other.x and self.y < oy and sy > other.y:
            if self.hit_in:
                return False
            l = self.x - other.x
            r = (self.x + BULLET_WIDTH) - (other.x + other.width)
            t = self.y - other.y
            b = (self.y + BULLET_HEIGHT) - (other.y + other.height)
            sx = self.step_x + other.step_x
            sy = self.step_y + other.step_y
            inside = self.is_inside(other)

            self.hit_in = other
            if inside == 0:
                return False

            l = math.fabs(l)
            t = math.fabs(t)
            r = math.fabs(r)
            b = math.fabs(b)

            if (inside == self.LEFT) or (inside == self.RIGHT) or (
                    inside == (self.LEFT | self.TOP) and l > t and self.step_x > 0) or (
                    inside == (self.LEFT | self.BOTTOM) and l > b and self.step_x > 0) or (
                    inside == (self.RIGHT | self.TOP) and r > t and self.step_x < 0) or (
                    inside == (self.RIGHT | self.BOTTOM) and r > b and self.step_x < 0):
                self.step_x *= -1.0
            if inside == self.TOP or inside == self.BOTTOM or (
                    inside == (self.LEFT | self.TOP) and l < t and self.step_y > 0) or (
                    inside == (self.LEFT | self.BOTTOM) and l < b and self.step_y < 0) or (
                    inside == (self.RIGHT | self.TOP) and r < t and self.step_y > 0) or (
                    inside == (self.RIGHT | self.BOTTOM) and r < b and self.step_y < 0):
                self.step_y *= -1.0
            return True
        if self.hit_in == other:
            self.hit_in = None
        return False

    def draw(self, g, image):
        g.draw_image_rect(image, Gempyre.Rect(self.x, self.y, BULLET_WIDTH, BULLET_HEIGHT))


class Gun:
    def __init__(self, mx, my):
        self.mx = mx
        self.my = my
        self.x = self.mx - GUN_WIDTH / 2
        self.y = self.my - GUN_HEIGHT
        self.angle = self.my - GUN_HEIGHT
        self.width = GUN_WIDTH
        self.height = GUN_HEIGHT
        self.step_x = 0
        self.step_y = 0

    def draw(self, g, dome_image, barrel_image):
        g.draw_image_rect(dome_image, Gempyre.Rect(self.mx - GUN_WIDTH / 2, self.my - GUN_HEIGHT, GUN_WIDTH, GUN_HEIGHT))
        g.save()
        g.translate(self.mx, self.my - 20)
        g.rotate(self.angle)
        g.translate(-self.mx, -(self.my - 20))
        g.draw_image_rect(barrel_image, Gempyre.Rect(
            self.mx - BARREL_WIDTH / 2, self.my - (GUN_WIDTH * 0.9), BARREL_WIDTH, BARREL_HEIGHT))
        g.restore()

    def move(self, x, x_min, x_max):
        if (x < 0 and self.x > x_min) or (x > 0 and self.x + GUN_WIDTH < x_max):
            self.step_x = x
            self.mx += x
            self.x += x


class Ammo:
    def __init__(self, width, y_pos):
        self.width = width
        self.y_pos = y_pos
        self.count = MAX_AMMO
        self.max = MAX_AMMO
        self.gap = width / MAX_AMMO - BULLET_WIDTH

    def draw(self, g, image):
        pos = (self.gap + BULLET_WIDTH) * (self.max - self.count)
        for i in range(0, self.count):
            g.draw_image_rect(image, Gempyre.Rect(pos, self.y_pos, BULLET_WIDTH, BULLET_HEIGHT))
            pos += self.gap + BULLET_WIDTH


class Game:
    def __init__(self, ui, canvas, images):
        self.ui = ui
        self.canvas = canvas
        self.barrel = self._get("barrel", images)
        self.barrier = self._get("barrier", images)
        self.bullet = self._get("bullet", images)
        self.dome = self._get("dome", images)
        self.numbers = self._get("numbers", images)
        self.skull = self._get("skull", images)
        self.width = 0
        self.height = 0
        self.bullets = []
        self.monsters = []
        self.rect = None
        self.numberDrawer = None
        self.gun = None
        self.ammo = None
        self.tick = None
        self.hits = 0
        self.game_speed = GAME_SPEED
        self.wave = 0
        self.wave_count = 0
        self.restart = True
        self.on_draw = 0

    @staticmethod
    def _get(name, images):
        for im in images:
            if im[0].startswith(name):
                return im[1]
        return None

    def init(self):
        self.rect = self.canvas.rect()
        self.width = self.rect.width
        self.height = self.rect.height
        self.numberDrawer = Number(self.numbers)
        self.gun = Gun(self.width / 2, self.height - BULLET_HEIGHT - 4)
        self.ammo = Ammo(self.width, self.height - BULLET_HEIGHT - 2)

    def create_monster(self, x_pos):
        self.monsters.append(Monster(
            x_pos, -MONSTER_HEIGHT, MONSTER_WIDTH, MONSTER_HEIGHT, random.randint(1, 99), self.numberDrawer))

    def start(self):
        if self.tick:
            return
        if self.restart:
            self.hits = 0
            self.wave = 0
            self.game_speed = GAME_SPEED
            self.restart = False
        self.ammo.count = MAX_AMMO
        self.wave_count = 3 + self.wave * 1.5
        self.monsters = []
        self.bullets = []
        self.ammo.count = MAX_AMMO
        Gempyre.Element(self.ui, "game_over").set_attribute("style", "visibility:hidden")
        Gempyre.Element(self.ui, "wave_end").set_attribute("style", "visibility:hidden")
        Gempyre.Element(self.ui, "hits").set_html(str(self.hits))
        Gempyre.Element(self.ui, "waves").set_html(str(self.wave + 1))
        Gempyre.Element(self.ui, "monsters").set_html(str(int(self.wave_count + 0.5)))
        Gempyre.Element(self.ui, "instructions").set_attribute("style", "visibility:hidden")
        self.tick = self.ui.start_periodic(timedelta(milliseconds=TICK_SPEED), self.do_tick)
        if self.game_speed > GAME_SPEED / 10:
            self.game_speed -= 1
        self.canvas.draw_completed(lambda: self.draw_completed())
        self.draw_loop()

    def do_tick(self):
        self.game_loop()
        self.on_draw -= 1;
        if self.on_draw > 0:
            return;
        self.on_draw = 10
        self.draw_loop()

    def draw_completed(self):
        self.on_draw = 0

    def game_over(self):
        self.ui.cancel_timer(self.tick);
        self.canvas.draw_completed(None)
        self.tick = None
        Gempyre.Element(self.ui, "game_over").set_attribute("style", "visibility:visible")
        Gempyre.Element(self.ui, "instructions").set_attribute("style", "visibility:visible")
        self.restart = True
        self.draw_loop()

    def wave_end(self):
        self.ui.cancel_timer(self.tick)
        self.canvas.draw_completed(None)
        self.tick = None
        Gempyre.Element(self.ui, "wave_end").set_attribute("style", "visibility:visible")
        self.wave += 1
        self.draw_loop()

    def draw_loop(self):
        fc = Gempyre.FrameComposer()
        fc.clear_rect(Gempyre.Rect(0, 0, self.width, self.height))
        for bullet in self.bullets:
            bullet.draw(fc, self.bullet)
        for monster in self.monsters:
            monster.draw(fc, self.skull)
        self.gun.draw(fc, self.dome, self.barrel)
        self.ammo.draw(fc, self.bullet)
        self.canvas.draw_frame(fc)

    def game_loop(self):
        for bullet in self.bullets:
            bullet.step()
            to_delete = bullet.test_inside(0, 0, self.width, self.height)
            if to_delete:
                self.bullets.remove(bullet)
            else:
                bullet.step()
                bullet.test_hit(self.gun)
                for monster in self.monsters:
                    if bullet.test_hit(monster):
                        monster.endurance -= 1
                        self.hits += 1
                        Gempyre.Element(self.ui, "hits").set_html(str(self.hits))
                        if monster.endurance <= 0:
                            bullet.hit_in = None
                            self.monsters.remove(monster)
                            if len(self.monsters) == 0:
                                self.wave_end()
                                return
                            if self.ammo.count < self.ammo.max:
                                self.ammo.count += 1

                    bullet.step()
        gaps = []
        for monster in self.monsters:
            monster.step()
            if monster.y < 0:
                gaps.append(monster.x)
            to_delete = monster.test_inside(0, 0, self.width, self.height)
            if to_delete:
                self.monsters.remove(monster)
            if (monster.y + monster.height) > (self.height - BULLET_HEIGHT):
                self.game_over()
                return

        if self.wave_count > 0:
            if random.randint(0, self.game_speed) == 1:
                x_pos = random.randint(0, int(self.width - MONSTER_WIDTH))
                is_ok = True
                for x in gaps:
                    if (x_pos > x) or (x_pos < x + MONSTER_WIDTH):
                        is_ok = False
                        break
                if is_ok:
                    self.create_monster(x_pos)
                    self.wave_count -= 1

    def shoot(self):
        if not self.tick:
            return

        if self.ammo.count > 0:
            start_x = (self.gun.mx - 10) + 80 * math.sin(self.gun.angle)
            start_y = (self.height - 40 - 10) - 80 * math.cos(self.gun.angle)
            self.bullets.append(Bullet(math.pi - self.gun.angle, start_x, start_y))
            self.ammo.count -= 1

    def turret(self, angle):
        if angle > -math.pi and angle - math.pi:
            self.gun.angle = angle
        self.draw_loop()

    def turret_turn(self, angle):
        self.turret(self.gun.angle + angle)

    def gun_move(self, x):
        self.gun.move(x, 0, self.width)

def main():
    root = os.path.dirname(sys.argv[0]) + '/assets/'
    files = ["balls.html", "barrel.png", "barrier.png", "bullet.png", "dome.png", "numbers.png", "skull.png"]
    full_paths = list(map(lambda f: root + f, files))
    data_map, names = resource.from_file_list(full_paths)

    # make list of image URIs from names
    urls = []
    for i in range(1, len(full_paths)):
        urls.append(names[full_paths[i]])

    ui = Gempyre.Ui(data_map, names[full_paths[0]], "Balls", 720, 920)

    Gempyre.Element(ui, "game_over").set_attribute("style", "visibility:hidden")
    Gempyre.Element(ui, "wave_end").set_attribute("style", "visibility:hidden")

    canvas = Gempyre.CanvasElement(ui, 'canvas')

    images = [canvas.add_image(url, None) for url in urls]
    game = Game(ui, canvas, zip(files[1:], images))

    ui.on_open(lambda: game.init())

    canvas.subscribe("click", lambda _: game.shoot(), [], timedelta(milliseconds=200))

    def get_property(event):
        if event:
            nonlocal game
            x = float(event.properties["clientX"])
            y = float(event.properties["clientY"])
            mid_x = game.gun.x
            return math.atan2((game.rect.height - y), mid_x - x) - math.pi / 2
        return 0

    canvas.subscribe('mousemove', lambda e: game.turret(get_property(e)),
                     ["clientX", "clientY"], timedelta(milliseconds=100))

    def key_listen(e):
        code = int(float((e.properties['keyCode'])))
        if code == 37:  # left arrow
            game.gun_move(-GUN_SPEED)
        elif code == 39:  # right arrow
            game.gun_move(GUN_SPEED)
        elif code == ord('Z'):
            game.turret_turn(-TURRET_STEP)
        elif code == ord('X'):
            game.turret_turn(TURRET_STEP)
        elif code == ord('C'):
            game.shoot()
        elif code == ord('A'):
            game.start()

    # canvas is not focusable therefore we listen whole app
    ui.root().subscribe('keydown', key_listen, ['keyCode'])
    ui.run()

if __name__ == "__main__":
    #Gempyre.set_debug()
    main()
