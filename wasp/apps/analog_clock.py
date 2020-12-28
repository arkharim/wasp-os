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


class AnalogClock():
    """Analog clock application."""

    NAME = 'Analog Clock'
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
            # self._update_hand(now[5], 60, 120, 120, _second_hand, self._old_hand_second, _second_hand_shape[0])
            # Erase old hand
            self._update_hand_bresenham(now[5]-1, 60, 120, 120, _second_hand, self._old_hand_second, black)
            # Draw new hand
            self._update_hand_bresenham(now[5], 60, 120, 120, _second_hand, self._old_hand_second, _second_hand_shape[0])

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
        # angle = -90 - 360/dial_number * time # 90º to rotate. Negative angles for the correct rotation
        angle = 90 - 360/dial_number * time # 90º to rotate. Negative angles for the correct rotation

        cos = math.cos(math.radians(angle))
        sin = math.sin(math.radians(angle))
        tan = math.tan(math.radians(angle))

        # TODO support background image
        # TODO use fill instead of _fill. See configurable clock. Performance is very similar.
        # _second_hand_shape = [green, (0, 105, 1, 2)]  # color, (initial, final, xresolution, width)

        # p1x = x_center + _second_hand_shape[1][0]
        # p2x = x_center - int(_second_hand_shape[1][1] * cos)
        # p1y = y_center + _second_hand_shape[1][0]
        # p2y = y_center + int(_second_hand_shape[1][1] * sin)

        #px/py bien calciulados.
        p1x = x_center - _second_hand_shape[1][0]
        p2x = x_center + int(_second_hand_shape[1][1] * cos)
        p1y = y_center + _second_hand_shape[1][0]
        p2y = y_center - int(_second_hand_shape[1][1] * sin)
        # TODO suport xresolution



        print("time ", time)
        print("angel ", angle)
        # print(sin)
        # print(cos)
        # print(tan)

        if angle == 0 or angle == -90 or angle == -180 or angle == -270 or angle == -360:
            # Para que el range funcione de una valor pequeño a uno grande.
            ytop = min(p1y, p2y)
            ybottom = max(p1y, p2y)
            xleft = min(p1x, p2x)
            xright = max(p1x, p2x)
            draw.fill(color, xleft, ytop, max(xright-xleft, _second_hand_shape[1][3]), max(ybottom-ytop, _second_hand_shape[1][3]))
        else:
            # # Draw region1
            # # h = int(_second_hand_shape[1][3])
            # hp = _second_hand_shape[1][3]/2*cos #Creo que la anterior h era incorrecta igualmente. 0.669
            # # hp = h
            # # w = max(int(h * sin), 1)
            # w = max(int(_second_hand_shape[1][3]/2*sin + hp/tan), 1)
            # # w = _second_hand_shape[1][3] / 2 * sin + hp / tan
            # # if w > 0:
            # #     w = math.ceil(w)
            # # else:
            # #     w = math.floor(w)
            # # print("w ", w) #debe dar 1
            # p11y = p1y + int(hp) #=p1y
            # p21y = p2y - int(hp) #=p2y
            #
            #
            # # dx = max(int(hp / tan), 1)
            # dx = hp / tan
            # if dx > 0:
            #     dx = math.ceil(dx)
            # else:
            #     dx = math.floor(dx)
            # p11x = p1x + dx
            # p11xi = p11x - dx
            # Para que el range funcione de una valor pequeño a uno grande.
            # yhigher = max(p11y, p21y)
            # ylower = min(p11y, p21y)


            # TODO tengo el problema que no sumo/resto bien dependiendo el cuadrante.
            h = _second_hand_shape[1][3]
            hp = h/2*cos #Creo que la anterior h era incorrecta igualmente. 0.669
            dx = hp / tan
            w = int(h/2*sin + dx)
            p11y = p1y + int(hp)
            p21y = p2y - int(hp)
            if p11y < p21y:
                ylower= p11y
                yhigher = p21y
                pxtop = p1x
            else:
                ylower = p21y
                yhigher = p11y
                pxtop = p2x
                if -90 < angle < -270:
                    dx = -dx

            p11x = int(pxtop+dx-h/2*sin)
            if w < 0: #para el lado izquierdo
                p11x -=w
                w = abs(w)
            # if dx > 0:
            #     dx = math.ceil(dx)
            # else:
            #     dx = math.floor(dx)
            pix = p11x - dx

            print("dx ", dx)
            # print(h)
            # print(w)
            # print(h * sin)
            print("hp ", hp)
            print("p1x ", p1x)
            print("p11x ", p11x)
            print("p2x ", p2x)
            print("p1y ", p1y)
            print("p11y ", p11y)
            print("p2y ", p2y)
            print("p21y ", p21y)

            for y in range(ylower, yhigher-1): #-1  por el xnext
                # print(" y ", y)
                # print(int(p11x-(y-p11y)/tan))
                x = int(p11x-(y-p11y)/tan)
                x_next = int(p11x-(y+1-p11y)/tan)
                # print(x)
                # print(max(w, abs(x_next - x)))
                #TODO problema con los decimales. A veces las x saltan mucho y entonces el w no es suficiente grueso y el resultado es no continuo.
                # Si se utiliza max(w, abs(x_next - x)) tampco funciona bien en los tramos verticales. existe algun glich
                # draw.fill(color, int(p11x-(y-p11y)/tan), y, w, 1)

                # p11xi = p11xi - dx
                pix += dx
                # print("p11xi ", p11xi)
                print ("y ", y)
                print("pix ", pix)
                print(color, pix, y, w, 1)
                # draw.fill(color, int(p11x-(y-p11y)/tan), y, w, 1) #necesito calcularlo cada vez el px
                # draw.fill(color, p11xi, y, w, 1) #necesito calcularlo cada vez el px

                #TODO ojo con el truncamiento.
                draw.fill(color, int(pix), y, w, 1)
                # pix = pix - dx
                # if dx > 0:
                #     draw.fill(color, math.ceil(pix), y, w, 1)  # necesito calcularlo cada vez el px
                # else:
                #     draw.fill(color, math.floor(pix), y, w, 1) #necesito calcularlo cada vez el px





        # for i in range(len(on_screen_hand)):
        #     # Erase old hand
        #     # Don't work well with background image and hand drawn from the middle. On_screen_hand don't have all
        #     # pixels
        #     draw.fill(_bg, on_screen_hand[i][1] - hand[i][1] // 2, on_screen_hand[i][0] - hand[i][1] // 2,
        #               hand[i][1],
        #               hand[i][1])
        #     # Calculated the new hand
        #     on_screen_hand[i] = [y_center + int(hand[i][0] * sin),
        #                          x_center + int(hand[i][0] * cos)]
        #     # Paint the new hand
        #     draw.fill(color, on_screen_hand[i][1] - hand[i][1] // 2, on_screen_hand[i][0] - hand[i][1] // 2,
        #               hand[i][1], hand[i][1])
        #

    def _update_hand_bresenham(self, time, dial_number, x_center, y_center, hand, on_screen_hand, color):
        angle = 90 - 360 / dial_number * time  # 90º to rotate. Negative angles for the correct rotation

        cos = math.cos(math.radians(angle))
        sin = math.sin(math.radians(angle))

        p1x = x_center - _second_hand_shape[1][0]
        p2x = x_center + int(_second_hand_shape[1][1] * cos)
        p1y = y_center + _second_hand_shape[1][0]
        p2y = y_center - int(_second_hand_shape[1][1] * sin)
        # print("p1x ", p1x)
        # print("p2x ", p2x)
        # print("p1y ", p1y)
        # print("p2y ", p2y)
        # self.plotLine(color, p1x, p1y, p2x, p2y)
        self.plotLineWidth(color, p1x, p1y, p2x, p2y, 2) # solo si w > 1



    def plotLineX(self, color, x0, y0, x1, y1):
        draw = wasp.watch.drawable
        # fill_time = 0
        # starttime = time.process_time()

        dx = abs(x1 - x0)
        sx = 1 if x0 < x1 else -1
        dy = -abs(y1 - y0)
        sy = 1 if y0 < y1 else -1
        err = dx + dy # error value e_xy
        # e2 = 0

        wx = sx #optim<zar el fill
        wy = sy

        while True: # / * loop * /
            # setPixel(x0, y0)
            # draw.fill(color, x0, y0, 1, 1)
            # starttime = time.process_time()
            # draw.fill(color, x0-1, y0, 2, 1) #TODO hardcodedf width = 2
            # endtime = time.process_time()
            # fill_time += endtime - starttime

            if x0 == x1 and y0 == y1:
                if wx > 0:
                    draw.fill(color, x0-wx, y0, abs(wx), abs(wy))  # TODO hardcodedf width = 2
                else:
                    draw.fill(color, x0, y0, abs(wx), abs(wy))
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx # / * e_xy+e_x > 0 * /
                #nuevo. optimizar el fill.
                # wx = sx+wx if e2 > dx else sx
                wx = sx + wx

            if e2 <= dx: #salta de linea
                if wx > 0:
                    draw.fill(color, x0-wx, y0, abs(wx), abs(wy))  # TODO hardcodedf width = 2
                else:
                    draw.fill(color, x0, y0, abs(wx), abs(wy))
                wx = sx

                err += dx
                y0 += sy # / * e_xy+e_y < 0 * /

        # print("fill time: ", 10 * fill_time)


    """Funciona pero se debe optimizar el fill"""
    def plotLine2(self, color, x0, y0, x1, y1):
        draw = wasp.watch.drawable
        # fill_time = 0
        # starttime = time.process_time()

        dx = abs(x1 - x0)
        sx = 1 if x0 < x1 else -1
        dy = -abs(y1 - y0)
        sy = 1 if y0 < y1 else -1
        err = dx + dy # error value e_xy
        # e2 = 0

        while True: # / * loop * /
            # setPixel(x0, y0)
            # draw.fill(color, x0, y0, 1, 1)
            # starttime = time.process_time()
            draw.fill(color, x0, y0, 1, 1) #TODO hardcodedf width = 2
            # endtime = time.process_time()
            # fill_time += endtime - starttime

            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx # / * e_xy+e_x > 0 * /
            if e2 <= dx:
                err += dx
                y0 += sy # / * e_xy+e_y < 0 * /

        # print("fill time: ", 10 * fill_time)

    # #TODO. no va
    # def plotLineWidth(self, color, x0, y0, x1, y1, wd):
    #     """/* plot an anti-aliased line of width wd */"""
    #     draw = wasp.watch.drawable
    #     fill_time = 0
    #     starttime = time.process_time()
    #
    #     dx = abs(x1-x0)
    #     sx = 1 if x0 < x1 else -1
    #     dy = abs(y1-y0)
    #     sy = 1 if y0 < y1 else -1
    #     err = dx-dy
    #     # e2, x2, y2;                           /* error value e_xy */
    #     ed = 1 if dx+dy == 0 else math.sqrt(dx*dx+dy*dy)
    #
    #     wd = (wd + 1) / 2
    #     while True:  #/* pixel loop */
    #         # print (wd)
    #         # print(int(max(0,255*(abs(err-dx+dy)/ed-wd+1))))
    #         starttime = time.process_time()
    #         draw.fill(color, x0, y0, 1, 1)
    #         endtime = time.process_time()
    #         fill_time += endtime - starttime
    #         # draw.fill(color, x0, y0, int(max(0,255*(abs(err-dx+dy)/ed-wd+1))), 1)
    #         # setPixelColor(x0, y0, max(0,255*(abs(err-dx+dy)/ed-wd+1)));
    #         e2 = err
    #         x2 = x0
    #         if 2*e2 >= -dx: #   /* x step */
    #             e2 += dy
    #             y2 = y0
    #             while e2 < ed*wd and (y1 != y2 or dx > dy):
    #                 y2 += sy
    #                 print(x0)
    #                 print(y2)
    #                 print(int(max(0,255*(abs(e2)/ed-wd+1))))
    #                 starttime = time.process_time()
    #                 draw.fill(color, x0, y2, 1, 1)
    #                 endtime = time.process_time()
    #                 fill_time += endtime-starttime
    #                 # draw.fill(color, x0, y2, int(max(0,255*(abs(e2)/ed-wd+1))), 1)
    #                 # setPixelColor(x0, y2 += sy, max(0,255*(abs(e2)/ed-wd+1)))
    #                 e2 += dx
    #             if x0 == x1:
    #                 break
    #             e2 = err
    #             err -= dy
    #             x0 += sx
    #
    #         if 2*e2 <= dy: #  /* y step */
    #             e2 = dx - e2
    #             while e2 < ed*wd and (x1 != x2 or dx < dy):
    #                 x2 += sx
    #                 starttime = time.process_time()
    #                 draw.fill(color, sx, y0, 1, 1)
    #                 endtime = time.process_time()
    #                 fill_time += endtime - starttime
    #                 # draw.fill(color, sx, y0, int(max(0,255*(abs(e2)/ed-wd+1))), 1)
    #                 # setPixelColor(x2 += sx, y0, max(0,255*(abs(e2)/ed-wd+1)));
    #                 e2 += dy
    #
    #             if y0 == y1:
    #                 break
    #             err += dx
    #             y0 += sy
    #
    #     print("fill time: ",10 * fill_time)
    #
    # def plotLineWidth(self, color, x0, y0, x1, y1, wd):
    #     """/* plot an anti-aliased line of width wd */"""
    #     draw = wasp.watch.drawable
    #
    #     dx = abs(x1-x0)
    #     sx = 1 if x0 < x1 else -1
    #     dy = abs(y1-y0)
    #     sy = 1 if y0 < y1 else -1
    #     err = dx-dy
    #     # e2, x2, y2;                           /* error value e_xy */
    #     ed = 1 if dx+dy == 0 else math.sqrt(dx*dx+dy*dy)
    #
    #     wd = (wd + 1) / 2
    #     while True:  #/* pixel loop */
    #         # print (wd)
    #         # print(int(max(0,255*(abs(err-dx+dy)/ed-wd+1))))
    #         draw.fill(color, x0, y0, int(max(0,255*(abs(err-dx+dy)/ed-wd+1))), 1)
    #         # setPixelColor(x0, y0, max(0,255*(abs(err-dx+dy)/ed-wd+1)));
    #         e2 = err
    #         x2 = x0
    #         if 2*e2 >= -dx: #   /* x step */
    #             e2 += dy
    #             y2 = y0
    #             while e2 < ed*wd and (y1 != y2 or dx > dy):
    #                 y2 += sy
    #                 print(x0)
    #                 print(y2)
    #                 print(int(max(0,255*(abs(e2)/ed-wd+1))))
    #                 # draw.fill(color, x0, y2, int(max(0,255*(abs(e2)/ed-wd+1))), 1)
    #                 # setPixelColor(x0, y2 += sy, max(0,255*(abs(e2)/ed-wd+1)))
    #                 e2 += dx
    #             if x0 == x1:
    #                 break
    #             e2 = err
    #             err -= dy
    #             x0 += sx
    #
    #         if 2*e2 <= dy: #  /* y step */
    #             e2 = dx - e2
    #             while e2 < ed*wd and (x1 != x2 or dx < dy):
    #                 x2 += sx
    #                 # draw.fill(color, sx, y0, int(max(0,255*(abs(e2)/ed-wd+1))), 1)
    #                 # setPixelColor(x2 += sx, y0, max(0,255*(abs(e2)/ed-wd+1)));
    #                 e2 += dy
    #
    #             if y0 == y1:
    #                 break
    #             err += dx
    #             y0 += sy


    """Optimizado para el fill. No es perfecto aun! falta opimitzarlo por el low y y el high x. dependiendo de la zona, varia más las x o las y (la frontera son los 45º de cada cuadrante)"""
    def plotLine(self, color, x0, y0, x1, y1):
        if abs(y1 - y0) < abs(x1 - x0):
            if x0 > x1:
                self.plotLineLow(color, x1, y1, x0, y0)
            else:
                self.plotLineLow(color, x0, y0, x1, y1)
        else:
            if y0 > y1:
                self.plotLineHigh(color, x1, y1, x0, y0)
            else:
                self.plotLineHigh(color, x0, y0, x1, y1)

    """Solo optimizo por x"""
    def plotLineLow(self, color, x0, y0, x1, y1):
        draw = wasp.watch.drawable
        dx = x1 - x0
        dy = y1 - y0
        yi = 1
        if dy < 0:
            yi = -1
            dy = -dy
        D = (2 * dy) - dx
        y = y0

        wx = 1
        for x in range(x0, x1):
            # draw.fill(color, x, y, 1, 1)
            if D > 0:
                draw.fill(color, x-wx+1, y, wx, 1)
                wx = 1
                y = y + yi
                D = D + (2 * (dy - dx))
            else:
                wx += 1
                D = D + 2 * dy
        draw.fill(color, x1 - wx+1, y, wx, 1)

    """Solo optimizo por y"""
    def plotLineHigh(self, color, x0, y0, x1, y1):
        draw = wasp.watch.drawable
        dx = x1 - x0
        dy = y1 - y0
        xi = 1
        if dx < 0:
            xi = -1
            dx = -dx
        D = (2 * dx) - dy
        x = x0

        wy = 1
        for y in range(y0, y1):
            # draw.fill(color, x, y, 1, 1)
            if D > 0:
                draw.fill(color, x, y-wy+1, 1, wy)
                wy = 1
                x = x + xi
                D = D + (2 * (dx - dy))
            else:
                wy +=1
                D = D + 2*dx
        draw.fill(color, x, y1-wy+1, 1, wy)

    """demasiado lenta"""
    def plotLineWidth(self, color, x0, y0, x1, y1, wd):
        """/* plot non anti-aliased line of width wd */"""
        draw = wasp.watch.drawable

        dx = abs(x1-x0)
        sx = 1 if x0 < x1 else -1
        dy = abs(y1-y0)
        sy = 1 if y0 < y1 else -1
        err = dx-dy
        # e2, x2, y2;                           /* error value e_xy */
        ed = 1 if dx+dy == 0 else math.sqrt(dx*dx+dy*dy)

        wd = (wd + 1) / 2
        while True:  #/* pixel loop */
            # print (wd)
            # print(int(max(0,255*(abs(err-dx+dy)/ed-wd+1))))
            # draw.fill(color, x0, y0, int(max(0,255*(abs(err-dx+dy)/ed-wd+1))), 1)
            # setPixelColor(x0, y0, max(0,255*(abs(err-dx+dy)/ed-wd+1)));
            #No le pongo antialiasing
            draw.fill(color, x0, y0, 1, 1)
            e2 = err
            x2 = x0
            if 2*e2 >= -dx: #   /* x step */
                e2 += dy
                y2 = y0
                while e2 < ed*wd and (y1 != y2 or dx > dy):
                    y2 += sy
                    # print(x0)
                    # print(y2)
                    # print(int(max(0,255*(abs(e2)/ed-wd+1))))
                    # draw.fill(color, x0, y2, int(max(0,255*(abs(e2)/ed-wd+1))), 1)
                    # setPixelColor(x0, y2 += sy, max(0,255*(abs(e2)/ed-wd+1)))
                    # No le pongo antialiasing
                    draw.fill(color, x0, y2, 1, 1)
                    e2 += dx
                if x0 == x1:
                    break
                e2 = err
                err -= dy
                x0 += sx

            if 2*e2 <= dy: #  /* y step */
                e2 = dx - e2
                while e2 < ed*wd and (x1 != x2 or dx < dy):
                    x2 += sx
                    # draw.fill(color, sx, y0, int(max(0,255*(abs(e2)/ed-wd+1))), 1)
                    # setPixelColor(x2 += sx, y0, max(0,255*(abs(e2)/ed-wd+1)));
                    # No le pongo antialiasing
                    draw.fill(color, x2, y0, 1, 1)
                    e2 += dy

                if y0 == y1:
                    break
                err += dx
                y0 += sy