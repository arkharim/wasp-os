# to debug time
import time


#Copia de https://gitlab.com/purlupar/wasp-faces/-/tree/master/watchfaces. Uso interno

#This file is based onwasp - os's (default) clock.py, by Daniel Thompson:
# https://github.com/daniel-thompson/wasp-os/blob/master/wasp/clock.py

# ANALOGUE CLOCK

import wasp
# import watch
# import widgets
# import manager
import math


red, yellow, green, cyan, blue, magenta, white, black = 0xf800, 0xffe0, 0x07e0, 0x07ff, 0x001f, 0xf81f, 0xffff, 0x0000
hourhand, minutehand, secondhand, bezel = {}, {}, {}, {}

# using custom colors:
# algorithm based on https://stackoverflow.com/questions/13720937/c-defined-16bit-high-color
#
# def fromrgb(red, green, blue): # 255, 255, 255  --> "0xffff
#     red = 31*(red+4)
#     green = 63*(green+2)
#     blue = 31*(blue+4)
#     return hex(( int(red/255) << 11 ) | ( int(green/255) <<5) | int(blue/255))
#
# def fromhexrgb(rgb): # "FFFFFF" --> "0xffff
#     red = 31*(int(rgb[:2], 16)+4)
#     green = 63*(int(rgb[2:4], 16)+2)
#     blue = 31*(int(rgb[4:6], 16)+4)
#     return hex(( int(red/255) << 11 ) | ( int(green/255) <<5) | int(blue/255))


# Options
#TODO ya era parametrico:)
# TODO drawres son los pixels intermedios que no pinta.
bgcolor = black
bezel = True
hourhand["color"] = white
# hourhand["length"] = 75
hourhand["length"] = 100

hourhand["width"] = 1
hourhand["drawres"] = 1
minutehand["color"] = red
minutehand["length"] = 100
minutehand["width"] = 1
minutehand["drawres"] = 1
secondhand["color"] = white
# secondhand["length"] = 110
# secondhand["length"] = 100
secondhand["length"] = 105

# secondhand["width"] = 1
# secondhand["drawres"] = 5
secondhand["width"] = 2
secondhand["drawres"] = 1

# # 3-tuple key: (central/lower end, outer end, thickening factor)
# shapelist = { "chickenwing" : [ (0.00, 1.00, 2),
#                                 (0.15, 0.85, 3),
#                                 (0.18, 0.82, 4),
#                                 (0.21, 0.79, 5) ],
#               "fleecenter" : [ (0.00, 0.10, 0),
#                                (0.10, 1.00, 1) ]
# }

# TODO al final utiliza las manetas chickenwing
# Se debe poner en ancho creciente. Si no, al calcular la forma, se sobreescribe los siguientes espesores.
shapelist = [(0.00, 1.00, 2),
             (0.15, 0.85, 3),
             (0.18, 0.82, 4),
             (0.21, 0.79, 5)]

# initialize 1-px wide, straight hands
# TODO la longitud de las manetas
hourhand["shape"] = [1] * hourhand["length"]
minutehand["shape"] = [1] * minutehand["length"]
secondhand["shape"] = [1] * secondhand["length"]

# TODO Guarda la forma de las manetas.

# thicken hands at given radiuses
for s in shapelist:  # ["chickenwing"]:
    # TODO los convierte en int porque son pixels.
    start = int(hourhand["length"] * s[0])
    stop = int(hourhand["length"] * s[1])
    # TODo aqui aqui in slicing he inserta el nuevo ancho de las manetas. Sobreescribe el ancho anterior que existia.
    hourhand["shape"][start:stop] = [s[2]] * (stop - start)
    # print(hourhand)
    start = int(minutehand["length"] * s[0])
    stop = int(minutehand["length"] * s[1])
    minutehand["shape"][start:stop] = [s[2]] * (stop - start)
    # print(minutehand)

# for s in shapelist["fleecenter"]:
#     start = int(secondhand["length"]*s[0])
#     stop = int(secondhand["length"]*s[1])
#     secondhand["shape"][start:stop] = [s[2]]*(stop-start)


class AnalogueClockApp():
    NAME = 'AnalogClock'
    def __init__(self):
        self.meter = wasp.widgets.BatteryMeter()

    # TODO creo que no hace falta
    # def handle_event(self, event_view):
    #     """Process events that the app is subscribed to."""
    #     if event_view[0] == manager.EVENT_TICK:
    #         self.update()
    #     else:
    #         # TODO: Raise an unexpected event exception
    #         pass

    def foreground(self):
        """Activate the application."""
        self.on_screen = (-1, -1, -1, -1, -1, -1)
        self.draw()
        wasp.system.request_tick(1000)

    def tick(self, ticks):
        self.update()

    def background(self):
        """De-activate the application (without losing state)."""
        pass

    def sleep(self):
        return True

    def wake(self):
        self.update()

    def draw(self):
        draw = wasp.watch.drawable
        draw.fill(bgcolor)

        if bezel:
            for minute in range(0, 60):
                #TODO 4 pixels de largo.
                for pix in range(112, 118):  # 1-minute-step bezel
                    mid = 120 #centro del circulo
                    shift = -90 #Para empezar con las agujas arriba.
                    thecos = math.cos(math.radians(6 * minute + shift))#6 = grados que gira cada minuto.
                    thesin = math.sin(math.radians(6 * minute + shift))
                    x = mid + thecos * pix #mid es la translacion. cos*pix es el giro.
                    y = mid + thesin * pix
                    width = 2
                    draw.fill(white, int(x - width // 2), int(y - width // 2), int(width), int(width)) #TODO, no hace falta los int. Los pixel siemnpre son int.
            for minute in range(0, 60, 5): #TODO el tercero es cada cuanto salta el range.
                for pix in range(107, 118):  # 5-minunte-step bezel
                    mid = 120
                    shift = -90
                    thecos = math.cos(math.radians(6 * minute + shift))
                    thesin = math.sin(math.radians(6 * minute + shift))
                    x = mid + thecos * pix
                    y = mid + thesin * pix
                    width = 4
                    draw.fill(white, int(x - width // 2), int(y - width // 2), int(width), int(width))
            for minute in range(0, 60, 15):
                #TODO no funciona si son 120. tiene un problema con el width. error del simulador?
                for pix in range(107, 118):  # 15-minunte-step bezel
                    mid = 120
                    shift = -90
                    thecos = math.cos(math.radians(6 * minute + shift))
                    thesin = math.sin(math.radians(6 * minute + shift))
                    x = mid + thecos * pix
                    y = mid + thesin * pix
                    width = 6
                    draw.fill(red, int(x - width // 2), int(y - width // 2), int(width), int(width))

        self.on_screen = (-1, -1, -1, -1, -1, -1)
        self.update()
        self.meter.draw()

    def update(self):
        now = wasp.watch.rtc.get_localtime()
        if now[3] == self.on_screen[3] and now[4] == self.on_screen[4] and now[5] == self.on_screen[5]:
            if now[5] != self.on_screen[5]:
                self.meter.update()
                self.on_screen = now
                return False

        draw = wasp.watch.drawable

        # todo: drawhand(rank=rank, length, resolution, shape)
        #  eg:  drawhand(hour     , hourhand["length"], hourhand["drawres"], hourhand["shape"])
        #  eg:  drawhand(minute...
        #  eg:  drawhand(second...
        starttime = time.process_time()


        # for pix in range(0, hourhand["length"], hourhand["drawres"]):  # hour hand
        #     mid = 120
        #     shift = -90
        #     width = hourhand["shape"][pix] * hourhand["width"] #TODO multiplica la forma por el ancho.
        #     if (self.on_screen[3] > -1):  # clear previous position
        #         thecos = math.cos(math.radians(30 * (self.on_screen[3] + self.on_screen[4] / 60) + shift)) #TODO, esto tambien puede ser una funcion. le tienss que pasar los grados de giro.
        #         thesin = math.sin(math.radians(30 * (self.on_screen[3] + self.on_screen[4] / 60) + shift))
        #         #TODO esta parte la tiene repetica con el draw. se podria englobar en una misma funcion que pinta la anterior maneta o el bezel (si llega al bezel)
        #         x = mid - int(thecos) + thecos * pix
        #         y = mid - int(thesin) + thesin * pix
        #         draw.fill(bgcolor, int(x - width // 2), int(y - width // 2), int(width), int(width))
        #     # draw new position
        #     thecos = math.cos(math.radians(30 * (now[3] + now[4] / 60) + shift))
        #     thesin = math.sin(math.radians(30 * (now[3] + now[4] / 60) + shift))
        #     x = mid - int(thecos) + thecos * pix
        #     y = mid - int(thesin) + thesin * pix
        #     draw.fill(hourhand["color"], int(x - width // 2), int(y - width // 2), int(width), int(width))
        #
        # #TODO se repite para cada hand -> funcion.
        # for pix in range(0, minutehand["length"], minutehand["drawres"]):  # minute hand
        #     mid = 120
        #     shift = -90
        #     width = minutehand["shape"][pix] * minutehand["width"]
        #     if (self.on_screen[4] > -1):  # clear previous position
        #         thecos = math.cos(math.radians(6 * self.on_screen[4] + shift))
        #         thesin = math.sin(math.radians(6 * self.on_screen[4] + shift))
        #         x = mid + thecos * pix
        #         y = mid + thesin * pix
        #         draw.fill(bgcolor, int(x - width // 2), int(y - width // 2), int(width), int(width))
        #     thecos = math.cos(math.radians(6 * now[4] + shift))
        #     thesin = math.sin(math.radians(6 * now[4] + shift))
        #     x = mid + thecos * pix
        #     y = mid + thesin * pix
        #     draw.fill(minutehand["color"], int(x - width // 2), int(y - width // 2), int(width), int(width))

        for pix in range(0, secondhand["length"], secondhand["drawres"]):  # second hand
            mid = 120
            shift = -90
            width = secondhand["width"]  # secondhand["shape"][pix]*secondhand["width"]
            if (self.on_screen[5] > -1):  # clear previous position
                thecos = math.cos(math.radians(6 * self.on_screen[5] + shift))
                thesin = math.sin(math.radians(6 * self.on_screen[5] + shift))
                x = mid + thecos * pix
                y = mid + thesin * pix
                draw.fill(bgcolor, int(x - width // 2), int(y - width // 2), int(width), int(width))
            thecos = math.cos(math.radians(6 * now[5] + shift))
            thesin = math.sin(math.radians(6 * now[5] + shift))
            x = mid + thecos * pix
            y = mid + thesin * pix
            draw.fill(secondhand["color"], int(x - width // 2), int(y - width // 2), int(width), int(width))

        endtime = time.process_time()
        print(10*(endtime - starttime))

        self.on_screen = now
        self.meter.update()
        return True
