# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson
# Based on clock.py by Daniel Thompson
# Based on analog.py and chrono24.py by purpular: https://gitlab.com/purlupar/wasp-faces/-/tree/master/watchfaces

"""Analog clock
~~~~~~~~~~~~~~~~

Shows a time together with a battery meter and the date.
"""

import wasp

import icons
import fonts.clock as digits
import math
import draw565
import micropython

import time

#TODO need to be implemented to display de date.
_MONTH = 'JanFebMarAprMayJunJulAugSepOctNovDec'

red, yellow, green, cyan, blue, magenta, white, black = 0xf800, 0xffe0, 0x07e0, 0x07ff, 0x001f, 0xf81f, 0xffff, 0x0000

_hour_hand_shape = [red, (0, 70, 1, 2)]  # color, (initial, final, xresolution, width)
_minuter_hand_shape = [red, (0, 95, 1, 2)]  # color, (initial, final, xresolution, width)
_second_hand_shape = [green, (0, 105, 1, 2)]  # color, (initial, final, xresolution, width)


def _hand_generator(hand_shape):
    l_hand = 0
    for i in hand_shape[1:]:
        # l_hand += ((i[1]-i[0])//i[2] + (i[1]-i[0]) % i[2])*i[3]
        l_hand += ((i[1] - i[0]) // i[2] + (i[1] - i[0]) % i[2])
    hand = [0]*l_hand
    i = 0
    for shape in hand_shape[1:]:
        # for y in range(shape[3]):
        #     y = y-shape[3]//2-shape[3] % 2 + 1
        for x in range(shape[0], shape[1], shape[2]):
                hand[i] = [x, shape[3]] # en vez las y, pongo el espesor.
                i += 1
    return hand

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

_hour_hand = _hand_generator(_hour_hand_shape)
_minute_hand = _hand_generator(_minuter_hand_shape)
_second_hand = _hand_generator(_second_hand_shape)

#TODO oto be implemented.
# Background images. Only 240x240px.
# _bg_image = icons.pine64_logo
# _bg_image = icons.pine64_rainbow

#Background color. Only used when no background image is drawn.
_bg = black

# Bezel colors
bz_1 = white  # 1minute marks
bz_5 = white  # 5minute marks
bz_15 = red  # 15minute marks


class AnalogSinCosClock():
    """Analog clock application."""

    NAME = 'A. sincos Clock'
    #TODO New icon
    ICON = icons.clock  # Optional

    def __init__(self):
        self._meter = wasp.widgets.BatteryMeter()  # Add battery widget
        self._notifier = wasp.widgets.StatusBar()  # Add notifications bar. For example, bluetooth
        #TODO configuration can be outside of class?
        # self._bg_image = False  # True to draw a background image
        self._heart = False  # True for draw heart rate
        self._steps = False  # True for draw steps counter
        self._on_screen = (-1, -1, -1, -1, -1, -1)  # Time displayed in the screen (yyy, mm, dd, HH, MM, SS)
        if self._heart:
            self._on_screen_heart = -1
        if self._steps:
            self._on_screen_steps = -1
        self._old_hand_hours = [0]*len(_hour_hand)
        self._old_hand_minutes = [0]*len(_minute_hand)
        self._old_hand_second = [0]*len(_second_hand)

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

        #TODO to be implemented
        """Draw the background.
        For a background without image, we want to draw a rectangle. We will use the drawing.fill() method. See fill()
        reference manual for more info.
        If none arguments are provided, the whole display will be filled with the background color (typically black).
        """

        # # Draw the background
        # if self._bg_image:
        #     draw.blit(_bg_image, 0, 0)
        # else:
        #     draw.fill(_bg)
        draw.fill(_bg)

        # Draw the clock
        self._draw_analog_clock()

        # We are drawing from the start the whole screen so we need to restart _on_screen variable.
        self._on_screen = (-1, -1, -1, -1, -1, -1)
        if self._heart:
            self._on_screen_heart = -1
        if self._steps:
            self._on_screen_steps = -1

        # Draw the widgets
        self._meter.draw()
        # self._notifier.draw() # Not required. update() and draw() is the same for this widget.

        # Update the screen
        self._update()

    def _draw_analog_clock(self):
        self._draw_bezel(120, 120, 112, 118, 2, 1, bz_1)  # 1 minutes marks
        self._draw_bezel(120, 120, 107, 118, 3, 5, bz_5)  # 5 minutes marks
        self._draw_bezel(120, 120, 107, 118, 4, 15, bz_15)  # 15 minutes marks

        # Reset the on screen hand
        for i in range(len(_hour_hand)):
            self._old_hand_hours[i] = [5, 5]

        for i in range(len(_minute_hand)):
            self._old_hand_minutes[i] = [5, 5]

        for i in range(len(_second_hand)):
            self._old_hand_second[i] = [5, 5]

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
        for time in range(0, 60, time_label):
            angle = 6 * time
            cos = math.cos(math.radians(angle))
            sin = math.sin(math.radians(angle))
            for pix in range(inner_radius, out_radius):
                # TODO Not correct, the image is not rotating
                draw.fill(color, int(x_center + cos * pix - w2), int(y_center + sin * pix - w2), width, width)

    def _update(self):
        """Update the display (if needed).

        The updates are a lazy as possible and rely on an prior call to
        draw() to ensure the screen is suitably prepared.
        """

        # Updated the widgets
        # TODO, removed temporaly
        # self._meter.update()
        # self._notifier.update()

        # Get current time
        now = wasp.watch.rtc.get_localtime()  # Wall time formatted as (yyyy, mm, dd, HH, MM, SS, wday, yday)
        self._update_analog_clock(now)
        self._on_screen = now

    def _update_analog_clock(self, now):
        starttime = time.process_time()
        # Draw the new _hand: Hours, Minutes, Seconds
        #TODO need to only update to be lazy. Check configutrable clock.

        #TODO currently only second hand works
        if self._on_screen[5] != now[5]:
            self._update_hand(now[5], 60, 120, 120, _second_hand, self._old_hand_second, _second_hand_shape[0])
            # Erase old hand
            # self._update_hand_bresenham(now[5]-1, 60, 120, 120, _second_hand, self._old_hand_second, black)
            # Draw new hand
            # self._update_hand_bresenham(now[5], 60, 120, 120, _second_hand, self._old_hand_second, _second_hand_shape[0])

        # if now[4] != self._on_screen[4] or self._on_screen[5] == self._on_screen[4]:
        #     self._update_hand(now[4], 60, 120, 120, _minute_hand, self._old_hand_minutes, _minuter_hand_shape[0])

        endtime = time.process_time()
        print(10*(endtime-starttime))

    def _update_hand(self, time, dial_number, x_center, y_center, hand, on_screen_hand, color):
        #TODO harcodeado con el _second_hand_shape
        # TODO need to be optimized. Use a buffer with all modifications before to update the screen.
        draw = wasp.watch.drawable
        display = draw._display
        quick_write = display.quick_write
        set_window = display.set_window
        _fill = draw565._fill
        angle = 90 - 360/dial_number * time # 90º to rotate. Negative angles for the correct rotation

        cos = math.cos(math.radians(angle))
        sin = math.sin(math.radians(angle))

        # TODO support background image
        # TODO use fill instead of _fill. See configurable clock. Performance is very similar.
        for i in range(len(on_screen_hand)):
            # Erase old hand
            # Don't work well with background image and hand drawn from the middle. On_screen_hand don't have all
            # pixels
            draw.fill(_bg, on_screen_hand[i][1] - hand[i][1] // 2, on_screen_hand[i][0] - hand[i][1] // 2,
                      hand[i][1],
                      hand[i][1])
            # Calculated the new hand
            on_screen_hand[i] = [y_center + int(hand[i][0] * sin),
                                 x_center + int(hand[i][0] * cos)]
            # Paint the new hand
            draw.fill(color, on_screen_hand[i][1] - hand[i][1] // 2, on_screen_hand[i][0] - hand[i][1] // 2,
                      hand[i][1], hand[i][1])
