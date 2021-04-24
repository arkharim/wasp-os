#TODO no va en la version 0.2 de waps-os. Copia de https://gitlab.com/purlupar/wasp-faces/-/tree/master/watchfaces

import watch
import manager
import widgets
import math

acc = 0x07e0  # fe40 # honey
clr = 0xffff  # white
bgc = 0

z1 = [(0, 70, 0), (86, 100, 0), (70, 85, 2), (73, 82, 3), (86, 79, 4)]  # lupe
z2 = [(0, 15, 0), (15, 18, 2), (15, 18, 3), (18, 21, 4), (21, 79, 5), (79, 82, 4), (82, 85, 3), (82, 85, 2),
      (85, 100, 0)]  # nudelholz #


class Chrono20App(object):
    def __init__(self):
        pass

    def handle_event(self, event_view):
        if event_view[0] == manager.EVENT_TICK:
            self.update()
        else:
            pass

    def foreground(self, manager, effect=None):
        self.ons = (-1, -1, -1, -1, -1, -1)
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

    def mark(self, z, c, v, i, o, w, a, b):
        d = watch.drawable
        for m in range(a, b, v):
            co = math.cos(math.radians(6 / 10 * m - 90))
            si = math.sin(math.radians(6 / 10 * m - 90))
            for p in range(i, o):
                d.fill(c, int(z[0] + co * p - w // 2), int(z[1] + si * p - w // 2), int(w), int(w))

    def hand(self, m, t, cy, c, l, w, r, s):
        d = watch.drawable
        for p in range(0, -l, -r):
            for u in s:
                if -l * u[0] / 100 > p > -l * u[1] / 100:
                    if cy == 0:
                        an = 30 * (t[3] + t[4] / 60)
                    elif cy == 1:
                        an = 6 * t[4]
                    elif cy == 2:
                        an = 6 * t[5]
                    o = math.cos(math.radians(an))
                    i = math.sin(math.radians(an))
                    d.fill(c, int(m[0] + u[2] * o - p * i), int(m[1] + u[2] * i + p * o), int(w), int(w))
                    d.fill(c, int(m[0] - u[2] * o - p * i), int(m[1] - u[2] * i + p * o), int(w), int(w))

    def draw(self, effect=None):
        now = watch.rtc.get_localtime()
        draw = watch.drawable

        draw.fill(0)
        self.mark((120, 120), clr, 10, 117, 120, 1, 0, 600)  #
        self.mark((120, 120), clr, 50, 112, 120, 5, 0, 600)  #
        self.mark((120, 120), acc, 150, 112, 120, 5, 0, 600)  #

        #        draw.set_color(0, bg=0xffff)
        #        draw.string(["Mon", "Die", "Mit", "Don", "Fre", "Sam", "Son"][now[6]], 175, 130)

        self.ons = (-1, -1, -1, -1, -1, -1)
        self.update()

    def update(self):
        now = watch.rtc.get_localtime()
        draw = watch.drawable
        if now[3] == self.ons[3] and now[4] == self.ons[4]:
            if now[5] != self.ons[5]:
                #                self.hand((120, 120), self.ons, 2, bgc, 80, 1, 3, z1)
                #                self.hand((120, 120), now, 2, clr, 80, 1, 3, z1)
                self.mark((120, 120), bgc, 1, 100, 105, 1, self.ons[5] * 10, (self.ons[5] + 1) * 10)
                self.mark((120, 120), acc, 1, 100, 105, 1, now[5] * 10, (now[5] + 1) * 10)
                self.ons = now
            return False
        self.mark((120, 120), bgc, 1, 100, 105, 1, self.ons[5] * 10, (self.ons[5] + 1) * 10)
        self.mark((120, 120), acc, 1, 100, 105, 1, now[5] * 10, (now[5] + 1) * 10)
        self.hand((120, 120), self.ons, 0, bgc, 80, 3, 1, z2)
        self.hand((120, 120), self.ons, 1, bgc, 100, 3, 1, z2)
        self.hand((120, 120), now, 0, acc, 80, 3, 1, z2)
        self.hand((120, 120), now, 1, clr, 100, 3, 1, z2)
        self.mark((100, 65), clr, 10, 30, 31, 1, 0, 600)
        self.mark((100, 65), clr, 50, 29, 31, 1, 0, 600)
        self.mark((100, 65), clr, 150, 27, 31, 1, 0, 600)
        self.hand((100, 65), now, 0, clr, 31, 1, 1, z1)
        self.mark((100, 175), clr, 10, 30, 31, 1, 0, 600)
        self.mark((100, 175), clr, 50, 29, 31, 1, 0, 600)
        self.mark((100, 175), clr, 150, 27, 31, 1, 0, 600)
        self.hand((100, 175), now, 0, clr, 31, 1, 1, z1)
        self.mark((55, 120), clr, 10, 37, 38, 1, 0, 600)
        self.mark((55, 120), clr, 50, 36, 38, 1, 0, 600)
        self.mark((55, 120), clr, 150, 34, 38, 1, 0, 600)
        self.hand((55, 120), (0, 0, 0, 0, abs(watch.battery.level()) / 100 * 60, 0), 1, clr, 38, 1, 1, z1)
        draw.set_color(0, bg=0xffff)
        draw.string(["Mon", "Die", "Mit", "Don", "Fre", "Sam", "Son"][now[6]], 135, 130)

        #        self.hand((120, 120), self.ons, 2, bgc, 80, 1, 3, z1)
        #        self.hand((120, 120), now, 2, clr, 80, 1, 3, z1)

        # self.mark((120,120), bgc, 1, 117, 120, 1, self.ons[5], self.ons[5]+1)
        # self.mark((120,120), acc, 1, 117, 120, 1, now[5], now[5]+1)
        # self.hand((120, 120), self.ons, 1, bgc, 1, 2, 1, z2)
        # self.hand((120, 120), now           , 1, clr, 1, 2, 1, z2)
        # self.hand((120, 120), self.ons, 0, bgc, 1, 4, 1, z2)
        # self.hand((120, 120), now           , 0, acc, 1, 4, 1, z2)
        self.ons = now
        return True
