import sys

#_hand_shape = [(0, 100, 1, 2),(0, 100, 2, 2) , (0, 300, 1, 1)]  # initial, final, xresolution, width
_hand_shape = [(0, 100, 20, 2)]  # initial, final, xresolution, width


_hand1 = []
for i in _hand_shape:
    for y in range(i[3]):
        y = y-i[3]//2-i[3] % 2 + 1
        _hand1 += [[x, y] for x in range(i[0], i[1], i[2])]



# _l_hand = 0
# for i in _hand_shape:
#     _l_hand += (i[1]-i[0])//i[2] +(i[1]-i[0])%i[2]
#
# _bhand = bytearray([0]*_l_hand*2)
# _i = 0
# for shape in _hand_shape:
#     for y in range(shape[3]):
#         y = y-shape[3]//2-shape[3] % 2 + 1
#         for x in range(shape[0], shape[1], shape[2]):
#             _bhand[_i] = x
#             _bhand[_i+1] = y
#             _i += 2

#_bhand = bytearray(x for x in _hand_optimized)

_l_hand = 0
for i in _hand_shape:
    _l_hand += ((i[1]-i[0])//i[2] + (i[1]-i[0]) % i[2])*i[3]
_hand_optimized = [0] * _l_hand
_hand_optimized2 = [[0,0]] * _l_hand
_i = 0
for shape in _hand_shape:
    for y in range(shape[3]):
        y = y-shape[3]//2-shape[3] % 2 + 1
        for x in range(shape[0], shape[1], shape[2]):
            _hand_optimized[_i] = [x, y]
            _hand_optimized2[_i] = [x, y]
            _i += 1
print(sys.getsizeof(_hand1))
print(sys.getsizeof(_hand_optimized))
print(sys.getsizeof(_hand_optimized2))

import math
dial_number = 60
time = 20
x_center= 120
y_center = 120
angle = 360/dial_number * time - 90
cos = math.cos(math.radians(-angle))
sin = math.sin(math.radians(-angle))

on_screen_hand = [0]*_l_hand

hand = _hand_optimized
for i in range(len(hand)):
        on_screen_hand[i] = [int(y_center + int(hand[i][1] * cos - hand[i][0] * sin)),
                         int(x_center + int(hand[i][0] * cos + hand[i][1] * sin))]

sortedhand = sorted(_hand_optimized)
print()

import micropython

#@micropython.native
def _fill(mv, color: int, count: int, offset: int):
#llena el buffer que despues escribira en pantalla con el color que quiere. dentro del rango seleccionado.
    #p = ptr16(mv) #Points to a 16 bit half-word.
    p = mv
    color = (color >> 8) + ((color & 0xff) << 8)

    for x in range(offset, offset+count):
        p[x] = color


buf = memoryview(bytearray(2 * 240))[0:2]
bp = 20

_fill(buf, 0xffff, 1, 0)
print()