# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson
# Based on clock.py by Daniel Thompson
# Based on analog.py and chrono24.py by purpular: https://gitlab.com/purlupar/wasp-faces/-/tree/master/watchfaces

"""Analog and Digital clock
~~~~~~~~~~~~~~~~

Shows a time together with a battery meter and the date.
"""
# TODO quite slow.

import wasp

import icons
import fonts.clock as digits
import math

_DIGITS = (
        digits.clock_0,
        digits.clock_1,
        digits.clock_2,
        digits.clock_3,
        digits.clock_4,
        digits.clock_5,
        digits.clock_6,
        digits.clock_7,
        digits.clock_8,
        digits.clock_9
)

_MONTH = 'JanFebMarAprMayJunJulAugSepOctNovDec'

_hand_shape = [(0, 100, 2, 1)]  # initial, final, xresolution, width

# Hand definition. Don't hesiated with the memory fragmentation
# _hand = []
# for i in _hand_shape:
#     for y in range(i[3]):
#         y = y-i[3]//2-i[3] % 2 + 1
#         _hand += [[x, y] for x in range(i[0], i[1], i[2])]

# Hand definition. Same output the previous commented code but try to reduce the ram memory fragmentation.
_l_hand = 0
for i in _hand_shape:
    _l_hand += (i[1]-i[0])//i[2] + (i[1]-i[0]) % i[2]
_hand = [0]*_l_hand
_i = 0
for shape in _hand_shape:
    for y in range(shape[3]):
        y = y-shape[3]//2-shape[3] % 2 + 1
        for x in range(shape[0], shape[1], shape[2]):
            _hand[_i] = [x,y]
            _i += 1

#TODO se puede hacer con bytes, así ocupa menos pero entonces el maximo de valores es 256. Se queda corto para representar las agujas. Se debería pensar en un metodo de compresion...
#Código para guardarlo en bytes (no soportan listas multidimensionales y guardo la x, y seguidas:
# _bhand = bytearray([0]*_l_hand*2)
# _i = 0
# for shape in _hand_shape:
#     for y in range(shape[3]):
#         y = y-shape[3]//2-shape[3] % 2 + 1
#         for x in range(shape[0], shape[1], shape[2]):
#             _bhand[_i] = x
#             _bhand[_i+1] = y
#             _i += 2

#_bg_image = icons.pine64_logo
_bg_image = icons.pine64_rainbow


class ConfigurableClockAppSlow():
    """Configurable clock application."""

    NAME = 'Slow Clock'
    #TODO New icon
    ICON = icons.clock  # Optional

    def __init__(self):
        self._meter = wasp.widgets.BatteryMeter()  # Add battery widget
        self._notifier = wasp.widgets.StatusBar()  # Add notifications bar. For example, bluetooth
        #TODO configuration can be outside of class?
        self._analog_clock = True  # True for draw analog clock
        self._digital_clock = False  # True for draw digital clock
        self._heart = False  # True for draw heart rate
        self._steps = False  # True for draw steps counter
        self._on_screen = (-1, -1, -1, -1, -1, -1)  # Time displayed in the screen (yyy, mm, dd, HH, MM, SS)
        if self._heart:
            self._on_screen_heart = -1
        if self._steps:
            self._on_screen_steps = -1

    def foreground(self):
        """Activate the application."""
        self._draw()
        """ Register to receive an application tick and specify the tick frequency, in miliseconds. For an analog clock,
        the level need to be updated every second. So, we want that the system notify us every second.
        """

        wasp.system.request_tick(1000)  # Time passed is in milliseconds, 1second = 1000 mseconds.

    def sleep(self):
        """#As we always see the wathface once the PT is wake. False for return to the default application
        (typically the default clock app)
        """
        return True

    def wake(self):
        self._update()

    def tick(self, ticks):
        self._update()

    def _draw(self):
        """Redraw the display from scratch."""
        draw = wasp.watch.drawable

        """Draw the background.
        For a background without image, we want to draw a rectangle. We will use the drawing.fill() method. See fill()
        reference manual for more info.
        If none arguments are provided, the whole display will be filled with the background color (typically black).
        """
        draw.fill(bg=0x0000)  # Black background
        # TODO support background image.
        #draw.blit(icons.pine64_logo,0,0,fg=0xffff)
        #draw.blit(icons.pine64_rainbow, 0, 0)
        draw.blit(_bg_image, 0, 0)
        #draw.blit(icons.app, 120, 120)

        if self._analog_clock:
            self._draw_analog_clock()

        if self._digital_clock:
            self._draw_digital_clock()

        # We are drawing from the start the whole screen so we need to restart _on_screen variable.
        self._on_screen = (-1, -1, -1, -1, -1, -1)
        if self._heart:
            self._on_screen_heart = -1
        if self._steps:
            self._on_screen_steps = -1

        self._update()
        self._meter.draw()
        # self._notifier.draw() # Not required. update() and draw() is the same for this widget.

    def _draw_analog_clock(self):
        self._draw_bezel(120, 120, 118, 120, 2, 1, 0xF800)  # 1 minutes marks
        self._draw_bezel(120, 120, 115, 120, 2, 5, 0xFFFF)  # 5 minutes marks
        self._draw_bezel(120, 120, 100, 110, 6, 5, 0x70AD)  # 15 minutes marks

    def _draw_digital_clock(self):
        draw = wasp.watch.drawable
        #TODO configurable color
        draw.blit(digits.clock_colon, 2 * 48, 80, fg=0xb5b6)  # 48 it's the width of the colons.

    def _update(self):
        """Update the display (if needed).

        The updates are a lazy as possible and rely on an prior call to
        draw() to ensure the screen is suitably prepared.
        """

        # Updated the widgets
        self._meter.update()
        self._notifier.update()

        # Get current time
        now = wasp.watch.rtc.get_localtime()  # Wall time formatted as (yyyy, mm, dd, HH, MM, SS, wday, yday)
        if self._analog_clock:
            self._update_analog_clock_slow(now)

        if self._digital_clock:
            self._update_digital_clock(now)

        self._on_screen = now

    def _update_analog_clock(self, now):
        # Wipe the old _hand.
        #TODO hackeado que busca la imagen siempre.
        #draw = wasp.watch.drawable
        # TODO soportar imagenes rle1bit.
        #color = draw.get_blit_color(icons.pine64_rainbow, 165, 40)
        #color = draw.get_blit_color(icons.pine64_rainbow, 120, 120)
        #color = draw.get_blit_color(icons.pine64_rainbow, 101, 159)

        #color = draw.get_blit_color(icons.app, 73, 55)
        #color = draw.get_blit_color(icons.app, 35, 29)

        #color = draw.get_blit_color(icons.pine64_logo, 165, 40)

        #color = draw.get_blit_color(_bg_image, 165, 40)


        #for x in range(140,180):
        #    draw.fill(color, x, 100, 1, 1)

        #draw = wasp.watch.drawable
        #draw.blit(icons.pine64_logo,0,0,fg=0xffff)
        #draw.blit(icons.pine64_rainbow, 0, 0)
        #draw.blit(_bg_image, 0, 0)
        #draw.blit(icons.app, 120, 120)
        #Wipe the old _hand
        if self._on_screen != -1:
            self._draw_hand(self._on_screen[5], 60, 120, 120, _hand)
            self._draw_hand(self._on_screen[4], 60, 120, 120, _hand)
            self._draw_hand(self._on_screen[3] + self._on_screen[4] / 60, 12, 120, 120, _hand)

        # Draw the new _hand
        self._draw_hand(now[5], 60, 120, 120, _hand, 0x27E0) #Seconds
        self._draw_hand(now[4], 60, 120, 120, _hand, 0xffff) #Minutes
        self._draw_hand(now[3]+now[4]/60, 12, 120, 120, _hand, 0xF800) #Hours

    def _update_analog_clock_slow(self, now):
        #TODO es demasiado lento. no es capaz de borrar los 3 a la vez. se nota. Aunque sea solo la maneta de los segundos. Se podria mejorar un poco pero al final se veria en un cierto moento.

        # Wipe the old _hand.
        #TODO hackeado que busca la imagen siempre.
        #draw = wasp.watch.drawable
        # TODO soportar imagenes rle1bit.
        #color = draw.get_blit_color(icons.pine64_rainbow, 165, 40)
        #color = draw.get_blit_color(icons.pine64_rainbow, 120, 120)
        #color = draw.get_blit_color(icons.pine64_rainbow, 101, 159)

        #color = draw.get_blit_color(icons.app, 73, 55)
        #color = draw.get_blit_color(icons.app, 35, 29)

        #color = draw.get_blit_color(icons.pine64_logo, 165, 40)

        #color = draw.get_blit_color(_bg_image, 165, 40)


        #for x in range(140,180):
        #    draw.fill(color, x, 100, 1, 1)

        #Wipe the old _hand
        if self._on_screen != -1:
            self._draw_hand_slow(self._on_screen[5], 60, 120, 120, _hand)
            self._draw_hand_slow(self._on_screen[4], 60, 120, 120, _hand)
            self._draw_hand_slow(self._on_screen[3] + self._on_screen[4] / 60, 12, 120, 120, _hand)

        # Draw the new _hand
        self._draw_hand_slow(now[5], 60, 120, 120, _hand, 0x27E0) #Seconds
        self._draw_hand_slow(now[4], 60, 120, 120, _hand, 0xffff) #Minutes
        self._draw_hand_slow(now[3] + now[4] / 60, 12, 120, 120, _hand, 0xF800) #Hours

    def _update_digital_clock(self, now):
        # The digital clock don't show seconds. If the hours and minutes didn't change, only update the widgets.
        if now[3] != self._on_screen[3] or now[4] != self._on_screen[4]:
            # In case that time changes, updated the clock
            draw = wasp.watch.drawable
            # Update time
            # TODO configurable color
            draw.blit(_DIGITS[now[4] % 10], 4*48, 80, fg=0x27E0)  # Second digit minute
            draw.blit(_DIGITS[now[4] // 10], 3*48, 80, fg=0xFFFF)  # First digit minute
            draw.blit(_DIGITS[now[3] % 10], 1*48, 80, fg=0xF800)  # Second digit hour
            draw.blit(_DIGITS[now[3] // 10], 0*48, 80, fg=0x70AD)  # First digit hour

            # Update date
            if now[2] != self._on_screen[2]:
                month = now[1] - 1
                month = _MONTH[month*3:(month+1)*3]
                draw.string('{} {} {}'.format(now[2], month, now[0]), 0, 180, width=240)

    def _draw_bezel(self, x_center, y_center, inner_radius, out_radius, width, time_label=1, color=0xffff):
        """
        x_center : 0 to 120
        y_center : 0 to 120
        inner_radius : 0 to 120
        out_radius: 0 to 120
        width : 2 to 120?

        Must center + max(inner,out_radious) <=240
        """
        draw = wasp.watch.drawable
        w2 = width // 2
        length = out_radius - inner_radius
        for time in range(0, 60, time_label):
            angle = 6 * time
            cos = math.cos(math.radians(angle))
            sin = math.sin(math.radians(angle))
            for pix in range(inner_radius, out_radius):
                # TODO no calculo bien el ancho. no estoy rotando la imagen
                draw.fill(color, int(x_center + cos * pix - w2), int(y_center + sin * pix - w2), width, width)

    def _draw_hand(self, time, dial_number, x_center, y_center, hand, color=None):
        #TODO si no hago un fill, solamente se llena la parte que pintas nueva. la antigua now -> "soportamos background
        draw = wasp.watch.drawable
        angle = 360/dial_number * time - 90
        cos = math.cos(math.radians(-angle))
        sin = math.sin(math.radians(-angle))
        bg_color = color
        for pix in hand:
            u = int(pix[0] * cos + pix[1] * sin)
            v = int(pix[1] * cos - pix[0] * sin)
            if color is None:
                #TODO sopopratar imganes con translacion. que no son 240x240 px.
                #bg_color = draw.get_blit_color(_bg_image, int(x_center + u), int(y_center + v))
                #draw.fill(bg_color, int(x_center + u), int(y_center + v), 1, 1)
                draw._redraw_rle2bit(_bg_image, [[int(x_center + u), int(y_center + v)]])
            else:
                draw.fill(color, int(x_center + u), int(y_center + v), 1, 1)

    def _draw_hand_slow(self, time, dial_number, x_center, y_center, hand, color=None):
        #TODO si no hago un fill, solamente se llena la parte que pintas nueva. la antigua now -> "soportamos background
        draw = wasp.watch.drawable
        angle = 360/dial_number * time - 90
        cos = math.cos(math.radians(-angle))
        sin = math.sin(math.radians(-angle))
        bg_color = color
        for pix in hand:
            u = int(pix[0] * cos + pix[1] * sin)
            v = int(pix[1] * cos - pix[0] * sin)
            if color is None:
                #TODO sopopratar imganes con translacion. que no son 240x240 px.
                bg_color = draw.get_blit_color(_bg_image, int(x_center + u), int(y_center + v))
                draw.fill(bg_color, int(x_center + u), int(y_center + v), 1, 1)
            else:
                draw.fill(color, int(x_center + u), int(y_center + v), 1, 1)


    # def _draw_hand(self, time, dial_number, x_center, y_center, _hand, color=0xffff):
    #     draw = wasp.watch.drawable
    #     angle = 360/dial_number * time - 90
    #     cos = math.cos(math.radians(angle))
    #     sin = math.sin(math.radians(angle))
    #     for pix in range(_hand[0], _hand[1], _hand[2]):
    #         w2 = _hand[3]//2
    #         draw.fill(color, int(x_center + cos * pix - w2), int(y_center + sin * pix - w2), _hand[3], _hand[3])

    def _draw_hand2(self, time, dial_number, x_center, y_center, hand, color=0xffff):
        angle = 360 / dial_number * time - 90

        #TODO solo in tipo. axctulizar para mas longitudes.
        for pix in range(hand[0], hand[1], hand[2]):
            buf = [[x for x in range(hand[0], hand[1], hand[2])] for x in [x for x in range(hand[0], hand[1], hand[2])]]
            w2 = hand[3] // 2 #TODO espesor siempre impar.
            for line in buf:
                for pix in line:
                    draw.fill(color, int(x_center + cos * pix - w2), int(y_center + sin * pix - w2), hand[3], hand[3])

    def _rotate(self, pixel, angle, color):
        """Image = vector [(x1,y1),....]

        http://pippin.gimp.org/image_processing/chap_resampling.html

        """
        draw = wasp.watch.drawable
        for y in range(img[1]):
            for x in range(img[0]):
                u = x * math.cos(-angle) + y * math.sin(-angle)
                v = y * math.cos(-angle) - x * math.sin(-angle)
                #TODO buscar pintaR DIRECTAMENTE PIXEL A PIXEL
                draw.fill(color, u, v, 1, 1)

    def hand(self, m, t, cy, c, l, w, r, s, prev):
        d = wasp.watch.drawable
        if cy == 0:
            an = 30 * (t[3] + t[4] / 60)
        else:  # for 1 and 2
            an = 6 * t[3 + cy]
        o = math.cos(math.radians(an))
        i = math.sin(math.radians(an))
        ue = int(s[0] / 100 * l)
        if prev == True:
            try:
                if cy == 0:
                    anold = 30 * (self.ons[3] + self.ons[4] / 60)
                else:  # for 1 and 2
                    anold = 6 * self.ons[3 + cy]
                oold = math.cos(math.radians(anold))
                iold = math.sin(math.radians(anold))
            except:
                pass
        oc = c
        for u in s[1:]:
            c = oc
            for p in range(int(-l * (u[0] - ue) / 100), int(-l * (u[1] - ue) / 100), -r):
                try:
                    c = u[3]
                    w = u[4]
                except:
                    pass
                of = int(u[2] * l / 100)  # normalize offset to length
                if prev:
                    d.fill(bgc, int(m[0] + of * oold - p * iold), int(m[1] + of * iold + p * oold), int(w), int(w))
                    d.fill(bgc, int(m[0] - of * oold - p * iold), int(m[1] - of * iold + p * oold), int(w), int(w))
                d.fill(c, int(m[0] + of * o - p * i), int(m[1] + of * i + p * o), int(w), int(w))
                d.fill(c, int(m[0] - of * o - p * i), int(m[1] - of * i + p * o), int(w), int(w))