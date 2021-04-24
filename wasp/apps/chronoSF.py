#TODO no va en la version 0.2 de waps-os. Copia de https://gitlab.com/purlupar/wasp-faces/-/tree/master/watchfaces

import watch
import widgets
import manager
import math

red, yellow, green, cyan, blue, magenta, whi, black = 0xf800, 0xffe0, 0x07e0, 0x07ff, 0x001f, 0xf81f, 0xffff, 0x0000
nudelholz = [(0.15, 0.85, 3), (0.18, 0.82, 4), (0.21, 0.79, 5)]
lupe = [(0.70, 0.85, 2),
        (0.73, 0.82, 3),
        (0.86, 0.79, 4)]


def makeshape(l, shape, u):
    shapelist = [0] * l
    for (start, stop, b) in shape:
        shapelist[int(start * l):int(stop * l)] = [b] * (int(stop * l) - int(start * l))
    z = [(0, h) for h in range(l)]  # zeiger
    newz = []
    for (x, y) in z:
        if shapelist[y] == 0:
            newz.append((x, y - u))  # -20 = überstand
        else:
            newz.append((x + shapelist[y], y - u))
            newz.append((x - shapelist[y], y - u))
    return (newz)


zh = makeshape(70, nudelholz, 0)
zm = makeshape(100, nudelholz, 0)
zs = makeshape(110, lupe, 20)

leftzs = makeshape(17, lupe, 0)


class Chrono3App(object):
    def __init__(self):
        self.meter = widgets.BatteryMeter()

    def handle_event(self, event_view):
        if event_view[0] == manager.EVENT_TICK:
            self.update()
        else:
            pass

    def foreground(self, manager, effect=None):
        self.on_screen = (-1, -1, -1, -1, -1, -1)
        self.draw(effect)
        manager.request_tick(1000)

    def tick(self, ticks):
        self.update()

    def background(self):
        pass

    def sleep(self):
        return True

    def wake(self):
        self.update()

    def drawmarks(self, settings):
        draw = watch.drawable
        for (mid, color, interval, inner, outer, width, a, z) in settings:
            for minute in range(a, z, interval):
                for pix in range(inner, outer):
                    x = mid[0] + math.cos(math.radians(6 * minute - 90)) * pix
                    y = mid[1] + math.sin(math.radians(6 * minute - 90)) * pix
                    draw.fill(color, int(x - width // 2), int(y - width // 2), int(width), int(width))

    def drawhand(self, mid, now, cyph, color, length, w, drawres, shape):
        draw = watch.drawable
        for pix in range(0, length, drawres):
            if cyph == 0:
                angle = 30 * (now[3] + now[4] / 60)
            elif cyph == 1:
                angle = 6 * now[4]
            elif cyph == 2:
                angle = 6 * now[5]
            thecos = math.cos(math.radians(angle))
            thesin = math.sin(math.radians(angle))
            x = mid[0] + thecos * pix
            y = mid[1] + thesin * pix

            for dot in shape[::drawres]:
                lettershift = -180
                thecos = math.cos(math.radians(angle + lettershift))
                thesin = math.sin(math.radians(angle + lettershift))
                newx = dot[0] * thecos - dot[1] * thesin
                newy = dot[0] * thesin + dot[1] * thecos
                draw.fill(color, int(x + newx), int(y + newy), int(w), int(w))

    def leftring(self, now):
        self.drawmarks([((65, 130), whi, 1, 30, 31, 1, 0, 60),
                        ((65, 130), whi, 5, 29, 31, 1, 0, 60),
                        ((65, 130), whi, 15, 27, 31, 1, 0, 60)])
        self.drawhand((65, 130), now, 0, whi, 1, 1, 1, leftzs)

    def draw(self, effect=None):
        now = watch.rtc.get_localtime()
        draw = watch.drawable

        draw.fill(black)
        mainring = [((120, 120), whi, 1, 117, 120, 1, 0, 60),
                    ((120, 120), whi, 5, 112, 120, 5, 0, 60),
                    ((120, 120), 0x3d9c, 15, 112, 120, 5, 0, 60)]
        self.drawmarks(mainring)
        weekday = ["Mon", "Die", "Mit", "Don", "Fre", "Sam", "Son"][now[6]]
        draw.set_color(0, bg=0xffff)
        draw.string(weekday, 175, 130)
        self.leftring(now)
        self.on_screen = (-1, -1, -1, -1, -1, -1)
        self.update()
        self.meter.draw()

    def update(self):
        now = watch.rtc.get_localtime()
        draw = watch.drawable
        if now[3] == self.on_screen[3] and now[4] == self.on_screen[4]:
            if now[5] != self.on_screen[5]:
                self.drawhand((120, 120), self.on_screen, 2, black, 1, 1, 3, zs)
                self.drawhand((120, 120), now, 2, 0xffff, 1, 1, 3, zs)
                self.leftring(now)  # make selective
                self.meter.update()
                self.on_screen = now
            return False
        self.drawhand((120, 120), self.on_screen, 2, black, 1, 1, 3, zs)
        self.drawhand((120, 120), now, 2, 0xffe0, 1, 1, 3, zs)
        self.drawhand((120, 120), self.on_screen, 1, black, 1, 2, 1, zm)
        self.drawhand((120, 120), now, 1, 0xffff, 1, 2, 1, zm)
        self.drawhand((120, 120), self.on_screen, 0, black, 1, 4, 1, zh)
        self.drawhand((120, 120), now, 0, 0x3d9c, 1, 4, 1, zh)

        self.on_screen = now

        self.meter.update()
        return True
