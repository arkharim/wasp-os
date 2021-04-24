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
import math
import draw565

import time


class DrawLineApp():
    """Analog clock application."""

    NAME = 'Draw Line'
    #TODO New icon
    # ICON = icons.clock  # Optional

    def __init__(self):
        pass

    def foreground(self):
        """Activate the application."""
        self._draw()
        """ Register to receive an application tick and specify the tick frequency, in miliseconds. For an analog clock,
        the level need to be updated every second. So, we want that the system notify us every second.
        """

    def sleep(self):
        """#As we always see the wathface once the PT is wake. False for return to the default application
        (typically the default clock app)
        """
        return True

    def wake(self):
        self._draw()

    def tick(self, ticks):
        self._draw()

    def _draw(self):
        """Redraw the display from scratch."""
        # xstart= 120
        # ystart = 120
        # xend = 240
        # yend = 130

        # xstart = 120
        # ystart = 120
        # xend = 0
        # yend = 130

        # xstart = 120
        # ystart = 120
        # xend = 130
        # yend = 240

        xstart = 120
        ystart = 120
        xend = 110
        yend = 240

        self.plotLineWidth(0xffff, xstart, ystart, xend, yend, 2)
        self.plotLineWidth(0xffff, xstart, ystart, 240, 130, 2)
        self.plotLineWidth(0xffff, xstart, ystart, 0, 110, 2)
        self.plotLineWidth(0xffff, xstart, ystart, 0, 210, 2)
        self.plotLineWidth(0xffff, xstart, ystart, 240, 110, 2)
        self.plotLineWidth(0xffff, xstart, ystart, 240, 70, 2)
        self.plotLineWidth(0xffff, xstart, ystart, 0, 70, 2)
        self.plotLineWidth(0xffff, xstart, ystart, 140, 0, 2)

        # self.plotLine(0xffff, xstart, ystart, xend, yend)

        # self.plotLine3(0xffff, xstart, ystart-20, xend, yend-20)
        #
        # self.plotLine2(0xf800, xstart, ystart-40, xend, yend-40)

        # self.plotLine3(0xffff, xstart-20, ystart, xend-20, yend)
        #
        # self.plotLine2(0xf800, xstart-40, ystart, xend-40, yend)



        xstart = 120
        ystart = 120
        xend = 240
        yend = 130

        # starttime = time.process_time()
        #
        # self.plotLine2(0xffff, xstart, ystart, xend, yend)
        # # self.plotLine2(0xffff, xstart, ystart, xend, yend)
        #
        # self.plotLine2(0xffff, xstart, ystart, 240, 130)
        # self.plotLine2(0xffff, xstart, ystart, 0, 110)
        # self.plotLine2(0xffff, xstart, ystart, 0, 210)
        # self.plotLine2(0xffff, xstart, ystart, 240, 110)
        # self.plotLine2(0xffff, xstart, ystart, 240, 70)
        # self.plotLine2(0xffff, xstart, ystart, 0, 70)
        # self.plotLine2(0xffff, xstart, ystart, 140, 0)
        #
        # endtime = time.process_time()
        # fill_time = endtime - starttime
        # print("fill time total fill chemo: ", 10 * fill_time)
        # #


        # starttime = time.process_time()
        #
        # self.plotLine(0xffff, xstart, ystart, xend, yend)
        # # self.plotLine2(0xffff, xstart, ystart, xend, yend)
        #
        # self.plotLine(0xffff, xstart, ystart, 240, 130)
        # self.plotLine(0xffff, xstart, ystart, 0, 110)
        # self.plotLine(0xffff, xstart, ystart, 0, 210)
        # self.plotLine(0xffff, xstart, ystart, 240, 110)
        # self.plotLine(0xffff, xstart, ystart, 240, 70)
        # self.plotLine(0xffff, xstart, ystart, 0, 70)
        # self.plotLine(0xffff, xstart, ystart, 140, 0)
        #
        # endtime = time.process_time()
        # fill_time = endtime - starttime
        # print("fill time total fill new optimized: ", 10 * fill_time)


        # starttime = time.process_time()
        #
        # self.plotLine3(0xffff, xstart, ystart, xend, yend)
        # # self.plotLine2(0xffff, xstart, ystart, xend, yend)
        #
        # self.plotLine3(0xffff, xstart, ystart, 240, 130)
        # self.plotLine3(0xffff, xstart, ystart, 0, 110)
        # self.plotLine3(0xffff, xstart, ystart, 0, 210)
        # self.plotLine3(0xffff, xstart, ystart, 240, 110)
        # self.plotLine3(0xffff, xstart, ystart, 240, 70)
        # self.plotLine3(0xffff, xstart, ystart, 0, 70)
        # self.plotLine3(0xffff, xstart, ystart, 140, 0)

        # endtime = time.process_time()
        # fill_time = endtime - starttime
        # print("fill time total fill new: ", 10 * fill_time)

        # """test de todo el anillo"""
        # starttime = time.process_time()
        # x_center = 120
        # y_center = 120
        # l = 120
        # dial_number = 60
        # for t in range(0, 60):
        #     angle = 90 - 360 / dial_number * t  # 90º to rotate. Negative angles for the correct rotation
        #     cos = math.cos(math.radians(angle))
        #     sin = math.sin(math.radians(angle))
        #     x0 = x_center
        #     x1 = x_center + int(l * cos)
        #     y0 = y_center
        #     y1 = y_center - int(l * sin)
        #     self.plotLineX(0xffff, x0, y0, x1, y1)
        # endtime = time.process_time()
        # fill_time = endtime - starttime
        # print("fill time total fill new: ", 10 * fill_time)


    """Es el que consigo dibujar mejor el reloj"""
    """el peor caso son los 45º, revisar si se puede mejorar de alguna manera el fill."""
    def plotLine(self, color, x0, y0, x1, y1):
        """Draw an straight line. Optimized for fill operation."""
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

    def plotLineLow(self, color, x0, y0, x1, y1):
        """Optimized for x filling as the filling direction preference"""
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

    def plotLineHigh(self, color, x0, y0, x1, y1):
        """Optimized for y filling as the filling direction preference"""
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

    """super parecido al chemo. realmente no se cual es más rapido. ambos tardan de media 3.0 en total"""
    def plotLine3(self, color, x0, y0, x1, y1):
        if abs(y1 - y0) < abs(x1 - x0):
            if x0 > x1:
                self.plotLineLow3(color, x1, y1, x0, y0)
            else:
                self.plotLineLow3(color, x0, y0, x1, y1)
        else:
            if y0 > y1:
                self.plotLineHigh3(color, x1, y1, x0, y0)
            else:
                self.plotLineHigh3(color, x0, y0, x1, y1)

    def plotLineLow3(self, color, x0, y0, x1, y1):
        draw = wasp.watch.drawable
        dx = x1 - x0
        dy = y1 - y0
        yi = 1
        if dy < 0:
            yi = -1
            dy = -dy
        D = (2 * dy) - dx
        y = y0

        for x in range(x0, x1):
            draw.fill(color, x, y, 1, 1)
            if D > 0:
                y = y + yi
                D = D + (2 * (dy - dx))
            else:
                D = D + 2 * dy

    def plotLineHigh3(self, color, x0, y0, x1, y1):
        draw = wasp.watch.drawable
        dx = x1 - x0
        dy = y1 - y0
        xi = 1
        if dx < 0:
            xi = -1
            dx = -dx
        D = (2 * dx) - dy
        x = x0

        for y in range(y0, y1):
            draw.fill(color, x, y, 1, 1)
            if D > 0:
                x = x + xi
                D = D + (2 * (dx - dy))
            else:
                D = D + 2*dx

    """No funciona. es muy complicado optimizar si pintar por las x o por las y"""
    def plotLineY(self, color, x0, y0, x1, y1):
        draw = wasp.watch.drawable
        fill_time = 0
        starttime = time.process_time()

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
            print("x0 ", x0)
            print("y0 ", y0)
            print("wx ", wx)
            print("wy ", wy)
            print()
            pintax = False
            pintay = True

            if x0 == x1 and y0 == y1:
                #optimizacion fill
                #TODO
                # if wx > 0:
                #     draw.fill(color, x0-wx, y0, abs(wx), abs(wy))  # TODO hardcodedf width = 2
                # else:
                #     draw.fill(color, x0, y0, abs(wx), abs(wy))

                break

            e2 = 2 * err
            if e2 >= dy:
                print("e2>=dy ", e2 >= dy)
                err += dy
                x0 += sx # / * e_xy+e_x > 0 * /
                #nuevo. optimizar el fill.
                # print(e2>dx)
                # wx = sx+wx if e2 > dx else sx
                wx = sx + wx
                # print(wx)

                # if e2 > dx:
                # print("wy ", wy)
                if not pintax:
                    if pintay:
                        print(("pinto por y"))
                        if wy > 0:
                            draw.fill(0xf800, x0 - 2 * sx, y0 - wy, abs(wx - sx), abs(wy))  # TODO hardcodedf width = 2
                        else:
                            # print("y0 ", y0)
                            # print("wy ", wy)
                            draw.fill(0xf800, x0 - 2 * sx, y0, abs(wx - sx), abs(wy))
                        wy = 0
                        pintay = False
                    else:
                        wy = 1
                        pintay = False

                # print(("pinto por y"))
                # if wy > 0:
                #     draw.fill(0xf800, x0-2*sx, y0-wy, abs(wx-sx), abs(wy))  # TODO hardcodedf width = 2
                # else:
                #     # print("y0 ", y0)
                #     # print("wy ", wy)
                #     draw.fill(0xf800, x0-2*sx, y0, abs(wx-sx), abs(wy))
                # wy = 0
                # pintay = False


            if e2 <= dx: #salta de linea
                print ("e2 <= dx ", e2 <= dx)
                # print("wx ", wx)
                if not pintay:
                    if pintax:
                        print("pinto por x")
                        if wx > 0:
                            draw.fill(color, x0-wx, y0, abs(wx), abs(wy))  # TODO hardcodedf width = 2
                        else:
                            draw.fill(color, x0, y0, abs(wx), abs(wy))
                        wx = sx
                    else:
                        wx = sx
                        pintax = True



                err += dx
                y0 += sy # / * e_xy+e_y < 0 * /

                wy = sy + wy

        print("fill time: ", 10 * fill_time)

    """Funciona pero solamente he optimizado el fill a traves de las X, el de las Y no."""
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
            # print("x0 ", x0)
            # print("y0 ", y0)
            # print("wx ", wx)
            # print("wy ", wy)
            # print()
            # pintax = False
            # pintay = True

            if x0 == x1 and y0 == y1:
                #optimizacion fill
                #TODO
                # if wx > 0:
                #     draw.fill(color, x0-wx, y0, abs(wx), abs(wy))  # TODO hardcodedf width = 2
                # else:
                #     draw.fill(color, x0, y0, abs(wx), abs(wy))

                break

            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx # / * e_xy+e_x > 0 * /
                #nuevo. optimizar el fill.
                # print(e2>dx)
                # wx = sx+wx if e2 > dx else sx
                wx = sx + wx
                # print(wx)

                # if e2 > dx:
                # print("wy ", wy)
                # print(("pinto por y"))
                # if wy > 0:
                #     draw.fill(0xf800, x0-2*sx, y0-wy, abs(wx-sx), abs(wy))  # TODO hardcodedf width = 2
                # else:
                #     # print("y0 ", y0)
                #     # print("wy ", wy)
                #     draw.fill(0xf800, x0-2*sx, y0, abs(wx-sx), abs(wy))
                # wy = 0
                # pintax = True


            if e2 <= dx: #salta de linea
                # print("wx ", wx)
                # if pintax:
                #     pintax = False
                # print("pinto por x")
                if wx > 0:
                    draw.fill(color, x0-wx, y0, abs(wx), abs(wy))  # TODO hardcodedf width = 2
                else:
                    draw.fill(color, x0, y0, abs(wx), abs(wy))
                wx = sx



                err += dx
                y0 += sy # / * e_xy+e_y < 0 * /

                # wy = sy + wy

        # print("fill time: ", 10 * fill_time)


    """Funciona pero se debe optimizar el fill. Basado en chello"""
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
            draw.fill(color, x0, y0, 1, 1) #TODO hardcodedf width = 1
            # endtime = time.process_time()
            # fill_time += endtime - starttime

            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:# / * e_xy+e_x > 0 * /
                err += dy
                x0 += sx
            if e2 <= dx:  # / * e_xy+e_y < 0 * /
                err += dx
                y0 += sy

        # print("fill time: ", 10 * fill_time)

    #TODO revisar. se puede optimizar? creo que no.
    # TODO hace el espesor doble porque se basa en el antilaiasing
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